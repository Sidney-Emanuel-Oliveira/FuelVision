package br.com.fuelvision.api.service;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyInt;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import br.com.fuelvision.api.domain.AnomalyDirection;
import br.com.fuelvision.api.domain.PageResult;
import br.com.fuelvision.api.domain.PriceAnomaly;
import br.com.fuelvision.api.domain.PriceFilter;
import br.com.fuelvision.api.dto.PageResponse;
import br.com.fuelvision.api.dto.PriceAnomalyResponse;
import br.com.fuelvision.api.repository.PriceRepository;
import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.List;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.ArgumentCaptor;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

@ExtendWith(MockitoExtension.class)
class AnomalyServiceTest {

    @Mock
    private PriceRepository repository;

    @Test
    void normalizesFiltersAndExplainsAnAboveRangeAlert() {
        PriceAnomaly anomaly = anomaly(AnomalyDirection.ABOVE_EXPECTED_RANGE);
        when(repository.findAnomalies(any(), anyInt(), anyInt()))
                .thenReturn(new PageResult<>(List.of(anomaly), 1, 0, 20));
        AnomalyService service = new AnomalyService(repository);

        PageResponse<PriceAnomalyResponse> response = service.findAnomalies(
                " gasolina comum ", "ac", " cruzeiro do sul ", null, null, 0, 20);

        ArgumentCaptor<PriceFilter> filterCaptor = ArgumentCaptor.forClass(PriceFilter.class);
        verify(repository).findAnomalies(filterCaptor.capture(), anyInt(), anyInt());
        assertThat(filterCaptor.getValue()).isEqualTo(new PriceFilter(
                "GASOLINA COMUM", "AC", "CRUZEIRO DO SUL", null, null));
        assertThat(response.items()).singleElement().satisfies(item -> {
            assertThat(item.detectionMethod()).isEqualTo("IQR_1_5");
            assertThat(item.reason())
                    .contains("acima do limite superior")
                    .endsWith("Comportamento estatisticamente atípico que merece análise.");
            assertThat(item.referenceObservationCount()).isEqualTo(10);
        });
    }

    @Test
    void explainsABelowRangeAlertWithoutClaimingFraud() {
        when(repository.findAnomalies(any(), anyInt(), anyInt()))
                .thenReturn(new PageResult<>(
                        List.of(anomaly(AnomalyDirection.BELOW_EXPECTED_RANGE)), 1, 0, 20));
        AnomalyService service = new AnomalyService(repository);

        PriceAnomalyResponse item = service.findAnomalies(
                null, null, null, null, null, 0, 20).items().getFirst();

        assertThat(item.reason()).contains("abaixo do limite inferior");
        assertThat(item.reason().toLowerCase()).doesNotContain("fraude", "irregularidade");
    }

    private PriceAnomaly anomaly(AnomalyDirection direction) {
        return new PriceAnomaly(
                1L,
                LocalDate.of(2026, 1, 2),
                new BigDecimal("7.970"),
                "GASOLINA COMUM",
                "BRL/liter",
                "REVENDA EXEMPLO",
                "AC",
                "CRUZEIRO DO SUL",
                10,
                new BigDecimal("6.2825"),
                new BigDecimal("6.5900"),
                new BigDecimal("0.3075"),
                new BigDecimal("5.82125"),
                new BigDecimal("7.05125"),
                direction);
    }
}
