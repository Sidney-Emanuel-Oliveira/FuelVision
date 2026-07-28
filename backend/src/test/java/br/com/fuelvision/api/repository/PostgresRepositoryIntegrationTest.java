package br.com.fuelvision.api.repository;

import static org.assertj.core.api.Assertions.assertThat;

import br.com.fuelvision.api.domain.AnomalyDirection;
import br.com.fuelvision.api.domain.PageResult;
import br.com.fuelvision.api.domain.PriceAnomaly;
import br.com.fuelvision.api.domain.PriceFilter;
import br.com.fuelvision.api.domain.PriceHistoryPoint;
import br.com.fuelvision.api.domain.PriceObservation;
import java.time.LocalDate;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.condition.EnabledIfEnvironmentVariable;
import org.springframework.jdbc.core.namedparam.NamedParameterJdbcTemplate;
import org.springframework.jdbc.datasource.DriverManagerDataSource;

@EnabledIfEnvironmentVariable(named = "FUELVISION_RUN_DB_TESTS", matches = "1")
class PostgresRepositoryIntegrationTest {

    private static PriceRepository priceRepository;
    private static LocationRepository locationRepository;

    @BeforeAll
    static void connectToPostgres() {
        String host = environment("POSTGRES_HOST", "localhost");
        String port = environment("POSTGRES_PORT", "5432");
        String database = environment("POSTGRES_DB", "fuelvision");
        String sslMode = environment("POSTGRES_SSLMODE", "prefer");
        String url = "jdbc:postgresql://" + host + ":" + port + "/" + database
                + "?sslmode=" + sslMode;

        DriverManagerDataSource dataSource = new DriverManagerDataSource();
        dataSource.setDriverClassName("org.postgresql.Driver");
        dataSource.setUrl(url);
        dataSource.setUsername(environment("POSTGRES_USER", "fuelvision_app"));
        dataSource.setPassword(environment("POSTGRES_PASSWORD", ""));

        NamedParameterJdbcTemplate jdbc = new NamedParameterJdbcTemplate(dataSource);
        priceRepository = new PriceRepository(jdbc);
        locationRepository = new LocationRepository(jdbc);
    }

    @Test
    void readsTheSixtyLoadedObservations() {
        PageResult<PriceObservation> result = priceRepository.findPrices(
                emptyFilter(), 0, 20);

        assertThat(result.totalItems()).isEqualTo(60);
        assertThat(result.items()).hasSize(20);
        assertThat(result.totalPages()).isEqualTo(3);
    }

    @Test
    void reproducesTheValidatedMacaeSummary() {
        PriceFilter filter = new PriceFilter(
                "GNV",
                "RJ",
                "MACAE",
                LocalDate.of(2026, 1, 1),
                LocalDate.of(2026, 1, 7));

        assertThat(priceRepository.summarize(filter))
                .singleElement()
                .satisfies(summary -> {
                    assertThat(summary.observationCount()).isEqualTo(2);
                    assertThat(summary.averageSalePrice()).isEqualByComparingTo("4.935");
                    assertThat(summary.minimumSalePrice()).isEqualByComparingTo("4.880");
                    assertThat(summary.maximumSalePrice()).isEqualByComparingTo("4.990");
                });
    }

    @Test
    void readsTheFourteenDailyProductGroups() {
        PageResult<PriceHistoryPoint> history = priceRepository.findHistory(
                emptyFilter(), 0, 20);

        assertThat(history.totalItems()).isEqualTo(14);
        assertThat(history.items()).hasSize(14);
    }

    @Test
    void listsOnlyLocationsThatHavePrices() {
        assertThat(locationRepository.findStatesWithPrices())
                .anySatisfy(state -> assertThat(state.code()).isEqualTo("RJ"));
        assertThat(locationRepository.findCitiesWithPrices("RJ"))
                .anySatisfy(city -> assertThat(city.name()).isEqualTo("MACAE"));
    }

    @Test
    void detectsTheEightIqrAlertsFromTheControlledSample() {
        PageResult<PriceAnomaly> result =
                priceRepository.findAnomalies(emptyFilter(), 0, 20);

        assertThat(result.totalItems()).isEqualTo(8);
        assertThat(result.items()).hasSize(8).allSatisfy(anomaly -> {
            assertThat(anomaly.referenceObservationCount()).isEqualTo(10);
            assertThat(anomaly.direction()).isEqualTo(AnomalyDirection.ABOVE_EXPECTED_RANGE);
            assertThat(anomaly.salePrice()).isGreaterThan(anomaly.upperBound());
        });
    }

    @Test
    void appliesFiltersWithoutRecalculatingTheReferenceDistribution() {
        PriceFilter filter = new PriceFilter(
                "GASOLINA COMUM", "AC", null, null, null);

        PageResult<PriceAnomaly> result =
                priceRepository.findAnomalies(filter, 0, 20);

        assertThat(result.totalItems()).isEqualTo(2);
        assertThat(result.items()).hasSize(2).allSatisfy(anomaly ->
                assertThat(anomaly.referenceObservationCount()).isEqualTo(10));
    }

    private static PriceFilter emptyFilter() {
        return new PriceFilter(null, null, null, null, null);
    }

    private static String environment(String name, String defaultValue) {
        return System.getenv().getOrDefault(name, defaultValue);
    }
}
