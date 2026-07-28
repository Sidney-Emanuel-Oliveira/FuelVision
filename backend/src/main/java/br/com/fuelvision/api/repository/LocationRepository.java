package br.com.fuelvision.api.repository;

import br.com.fuelvision.api.domain.CityLocation;
import br.com.fuelvision.api.domain.StateLocation;
import java.util.List;
import java.util.Map;
import org.springframework.jdbc.core.namedparam.NamedParameterJdbcTemplate;
import org.springframework.stereotype.Repository;

@Repository
public class LocationRepository {

    private final NamedParameterJdbcTemplate jdbc;

    public LocationRepository(NamedParameterJdbcTemplate jdbc) {
        this.jdbc = jdbc;
    }

    public List<StateLocation> findStatesWithPrices() {
        String sql = """
                SELECT states.code, states.name
                FROM fuelvision.states AS states
                WHERE EXISTS (
                    SELECT 1
                    FROM fuelvision.municipalities AS municipalities
                    JOIN fuelvision.retailers AS retailers
                      ON retailers.municipality_id = municipalities.id
                    JOIN fuelvision.price_observations AS observations
                      ON observations.retailer_id = retailers.id
                    WHERE municipalities.state_code = states.code
                )
                ORDER BY states.name
                """;
        return jdbc.query(sql, Map.of(), (resultSet, rowNumber) ->
                new StateLocation(
                        resultSet.getString("code").trim(),
                        resultSet.getString("name")));
    }

    public List<CityLocation> findCitiesWithPrices(String stateCode) {
        String sql = """
                SELECT municipalities.id,
                       municipalities.name,
                       municipalities.state_code
                FROM fuelvision.municipalities AS municipalities
                WHERE municipalities.state_code = :stateCode
                  AND EXISTS (
                      SELECT 1
                      FROM fuelvision.retailers AS retailers
                      JOIN fuelvision.price_observations AS observations
                        ON observations.retailer_id = retailers.id
                      WHERE retailers.municipality_id = municipalities.id
                  )
                ORDER BY municipalities.name
                """;
        return jdbc.query(sql, Map.of("stateCode", stateCode), (resultSet, rowNumber) ->
                new CityLocation(
                        resultSet.getLong("id"),
                        resultSet.getString("name"),
                        resultSet.getString("state_code").trim()));
    }
}
