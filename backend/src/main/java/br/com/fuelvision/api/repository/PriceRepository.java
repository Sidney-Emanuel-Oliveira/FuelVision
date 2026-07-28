package br.com.fuelvision.api.repository;

import br.com.fuelvision.api.domain.AnomalyDirection;
import br.com.fuelvision.api.domain.PageResult;
import br.com.fuelvision.api.domain.PriceAnomaly;
import br.com.fuelvision.api.domain.PriceFilter;
import br.com.fuelvision.api.domain.PriceHistoryPoint;
import br.com.fuelvision.api.domain.PriceObservation;
import br.com.fuelvision.api.domain.PriceSummary;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import org.springframework.jdbc.core.namedparam.NamedParameterJdbcTemplate;
import org.springframework.stereotype.Repository;

@Repository
public class PriceRepository {

    private static final int MINIMUM_REFERENCE_OBSERVATIONS = 4;

    private static final String BASE_FROM = """
            FROM fuelvision.price_observations AS observations
            JOIN fuelvision.products AS products
              ON products.id = observations.product_id
            JOIN fuelvision.retailers AS retailers
              ON retailers.id = observations.retailer_id
            JOIN fuelvision.municipalities AS municipalities
              ON municipalities.id = retailers.municipality_id
            JOIN fuelvision.states AS states
              ON states.code = municipalities.state_code
            """;

    private final NamedParameterJdbcTemplate jdbc;

    public PriceRepository(NamedParameterJdbcTemplate jdbc) {
        this.jdbc = jdbc;
    }

    public PageResult<PriceObservation> findPrices(
            PriceFilter filter, int page, int size) {
        QueryParts queryParts = buildFilters(filter);
        Map<String, Object> parameters = withPagination(queryParts.parameters(), page, size);

        String dataSql = """
                SELECT observations.id,
                       observations.collection_date,
                       observations.sale_price,
                       observations.purchase_price,
                       products.name AS product,
                       products.unit,
                       retailers.name AS retailer,
                       retailers.brand,
                       states.code AS state_code,
                       municipalities.name AS municipality
                """ + BASE_FROM + queryParts.whereClause() + """
                ORDER BY observations.collection_date DESC, observations.id
                LIMIT :limit OFFSET :offset
                """;

        List<PriceObservation> items = jdbc.query(dataSql, parameters, (resultSet, rowNumber) ->
                new PriceObservation(
                        resultSet.getLong("id"),
                        resultSet.getObject("collection_date", java.time.LocalDate.class),
                        resultSet.getBigDecimal("sale_price"),
                        resultSet.getBigDecimal("purchase_price"),
                        resultSet.getString("product"),
                        resultSet.getString("unit"),
                        resultSet.getString("retailer"),
                        resultSet.getString("brand"),
                        resultSet.getString("state_code").trim(),
                        resultSet.getString("municipality")));

        Long total = jdbc.queryForObject(
                "SELECT count(*) " + BASE_FROM + queryParts.whereClause(),
                queryParts.parameters(),
                Long.class);

        return new PageResult<>(items, total == null ? 0 : total, page, size);
    }

    public List<PriceSummary> summarize(PriceFilter filter) {
        QueryParts queryParts = buildFilters(filter);
        String sql = """
                SELECT products.name AS product,
                       products.unit,
                       count(*) AS observation_count,
                       round(avg(observations.sale_price), 3) AS average_sale_price,
                       min(observations.sale_price) AS minimum_sale_price,
                       max(observations.sale_price) AS maximum_sale_price,
                       max(observations.sale_price) - min(observations.sale_price) AS price_range,
                       min(observations.collection_date) AS first_collection_date,
                       max(observations.collection_date) AS last_collection_date
                """ + BASE_FROM + queryParts.whereClause() + """
                GROUP BY products.id, products.name, products.unit
                ORDER BY products.name
                """;

        return jdbc.query(sql, queryParts.parameters(), (resultSet, rowNumber) ->
                new PriceSummary(
                        resultSet.getString("product"),
                        resultSet.getString("unit"),
                        resultSet.getLong("observation_count"),
                        resultSet.getBigDecimal("average_sale_price"),
                        resultSet.getBigDecimal("minimum_sale_price"),
                        resultSet.getBigDecimal("maximum_sale_price"),
                        resultSet.getBigDecimal("price_range"),
                        resultSet.getObject("first_collection_date", java.time.LocalDate.class),
                        resultSet.getObject("last_collection_date", java.time.LocalDate.class)));
    }

    public PageResult<PriceHistoryPoint> findHistory(
            PriceFilter filter, int page, int size) {
        QueryParts queryParts = buildFilters(filter);
        Map<String, Object> parameters = withPagination(queryParts.parameters(), page, size);
        String grouping = """
                GROUP BY observations.collection_date,
                         products.id,
                         products.name,
                         products.unit
                """;
        String dataSql = """
                SELECT observations.collection_date,
                       products.name AS product,
                       products.unit,
                       count(*) AS observation_count,
                       round(avg(observations.sale_price), 3) AS average_sale_price,
                       min(observations.sale_price) AS minimum_sale_price,
                       max(observations.sale_price) AS maximum_sale_price,
                       max(observations.sale_price) - min(observations.sale_price) AS price_range
                """ + BASE_FROM + queryParts.whereClause() + grouping + """
                ORDER BY observations.collection_date, products.name
                LIMIT :limit OFFSET :offset
                """;

        List<PriceHistoryPoint> items = jdbc.query(dataSql, parameters, (resultSet, rowNumber) ->
                new PriceHistoryPoint(
                        resultSet.getObject("collection_date", java.time.LocalDate.class),
                        resultSet.getString("product"),
                        resultSet.getString("unit"),
                        resultSet.getLong("observation_count"),
                        resultSet.getBigDecimal("average_sale_price"),
                        resultSet.getBigDecimal("minimum_sale_price"),
                        resultSet.getBigDecimal("maximum_sale_price"),
                        resultSet.getBigDecimal("price_range")));

        String countSql = "SELECT count(*) FROM (SELECT 1 "
                + BASE_FROM + queryParts.whereClause() + grouping + ") AS grouped_history";
        Long total = jdbc.queryForObject(countSql, queryParts.parameters(), Long.class);

        return new PageResult<>(items, total == null ? 0 : total, page, size);
    }

    public PageResult<PriceAnomaly> findAnomalies(
            PriceFilter filter, int page, int size) {
        QueryParts queryParts = buildFilters(filter);
        Map<String, Object> parameters = withPagination(queryParts.parameters(), page, size);
        parameters.put("minimumReferenceObservations", MINIMUM_REFERENCE_OBSERVATIONS);

        String detectedAnomalies = anomalyCandidatesSql(queryParts.whereClause());
        String anomalyCondition = """
                WHERE sale_price < lower_bound OR sale_price > upper_bound
                """;
        String dataSql = "SELECT * FROM (" + detectedAnomalies + ") AS detected "
                + anomalyCondition
                + " ORDER BY collection_date DESC, product, id LIMIT :limit OFFSET :offset";

        List<PriceAnomaly> items = jdbc.query(dataSql, parameters, (resultSet, rowNumber) ->
                new PriceAnomaly(
                        resultSet.getLong("id"),
                        resultSet.getObject("collection_date", java.time.LocalDate.class),
                        resultSet.getBigDecimal("sale_price"),
                        resultSet.getString("product"),
                        resultSet.getString("unit"),
                        resultSet.getString("retailer"),
                        resultSet.getString("state_code").trim(),
                        resultSet.getString("municipality"),
                        resultSet.getLong("reference_observation_count"),
                        resultSet.getBigDecimal("first_quartile"),
                        resultSet.getBigDecimal("third_quartile"),
                        resultSet.getBigDecimal("interquartile_range"),
                        resultSet.getBigDecimal("lower_bound"),
                        resultSet.getBigDecimal("upper_bound"),
                        AnomalyDirection.valueOf(resultSet.getString("direction"))));

        Map<String, Object> countParameters = new HashMap<>(queryParts.parameters());
        countParameters.put("minimumReferenceObservations", MINIMUM_REFERENCE_OBSERVATIONS);
        Long total = jdbc.queryForObject(
                "SELECT count(*) FROM (" + detectedAnomalies + ") AS detected "
                        + anomalyCondition,
                countParameters,
                Long.class);

        return new PageResult<>(items, total == null ? 0 : total, page, size);
    }

    private String anomalyCandidatesSql(String whereClause) {
        String boundsJoin = """
                JOIN (
                    SELECT reference.product_id,
                           count(*) AS reference_observation_count,
                           CAST(percentile_cont(0.25) WITHIN GROUP (
                               ORDER BY reference.sale_price
                           ) AS numeric) AS first_quartile,
                           CAST(percentile_cont(0.75) WITHIN GROUP (
                               ORDER BY reference.sale_price
                           ) AS numeric) AS third_quartile
                    FROM fuelvision.price_observations AS reference
                    GROUP BY reference.product_id
                    HAVING count(*) >= :minimumReferenceObservations
                ) AS bounds ON bounds.product_id = observations.product_id
                """;
        return """
                SELECT observations.id,
                       observations.collection_date,
                       observations.sale_price,
                       products.name AS product,
                       products.unit,
                       retailers.name AS retailer,
                       states.code AS state_code,
                       municipalities.name AS municipality,
                       bounds.reference_observation_count,
                       bounds.first_quartile,
                       bounds.third_quartile,
                       bounds.third_quartile - bounds.first_quartile
                           AS interquartile_range,
                       bounds.first_quartile - 1.5 * (
                           bounds.third_quartile - bounds.first_quartile
                       ) AS lower_bound,
                       bounds.third_quartile + 1.5 * (
                           bounds.third_quartile - bounds.first_quartile
                       ) AS upper_bound,
                       CASE
                           WHEN observations.sale_price < bounds.first_quartile - 1.5 * (
                               bounds.third_quartile - bounds.first_quartile
                           ) THEN 'BELOW_EXPECTED_RANGE'
                           ELSE 'ABOVE_EXPECTED_RANGE'
                       END AS direction
                """ + BASE_FROM + boundsJoin + whereClause;
    }

    private QueryParts buildFilters(PriceFilter filter) {
        List<String> conditions = new ArrayList<>();
        Map<String, Object> parameters = new HashMap<>();

        addFilter(conditions, parameters, "products.name = :product", "product", filter.product());
        addFilter(conditions, parameters, "states.code = :state", "state", filter.state());
        addFilter(
                conditions,
                parameters,
                "municipalities.name = :municipality",
                "municipality",
                filter.municipality());
        addFilter(
                conditions,
                parameters,
                "observations.collection_date >= :startDate",
                "startDate",
                filter.startDate());
        addFilter(
                conditions,
                parameters,
                "observations.collection_date <= :endDate",
                "endDate",
                filter.endDate());

        String whereClause = conditions.isEmpty()
                ? ""
                : " WHERE " + String.join(" AND ", conditions) + " ";
        return new QueryParts(whereClause, parameters);
    }

    private void addFilter(
            List<String> conditions,
            Map<String, Object> parameters,
            String condition,
            String parameterName,
            Object value) {
        if (value != null) {
            conditions.add(condition);
            parameters.put(parameterName, value);
        }
    }

    private Map<String, Object> withPagination(
            Map<String, Object> filterParameters, int page, int size) {
        Map<String, Object> parameters = new HashMap<>(filterParameters);
        parameters.put("limit", size);
        parameters.put("offset", Math.multiplyExact(page, size));
        return parameters;
    }

    private record QueryParts(String whereClause, Map<String, Object> parameters) {
    }
}
