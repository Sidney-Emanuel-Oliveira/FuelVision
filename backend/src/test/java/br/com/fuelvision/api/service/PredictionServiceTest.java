package br.com.fuelvision.api.service;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import br.com.fuelvision.api.client.PredictionClient;
import br.com.fuelvision.api.dto.PredictionRequest;
import br.com.fuelvision.api.dto.PredictionResponse;
import java.math.BigDecimal;
import java.time.LocalDate;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.ArgumentCaptor;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

@ExtendWith(MockitoExtension.class)
class PredictionServiceTest {

    @Mock
    private PredictionClient client;

    @Test
    void normalizesProductBeforeCallingThePythonService() {
        PredictionRequest input = new PredictionRequest(
                " gasolina comum ", LocalDate.of(2026, 1, 3));
        PredictionResponse expected = new PredictionResponse(
                "GASOLINA COMUM",
                LocalDate.of(2026, 1, 3),
                new BigDecimal("6.077"),
                "BRL/liter",
                "product-mean-baseline-v1",
                "ProductMeanBaseline",
                LocalDate.of(2026, 1, 2),
                new BigDecimal("0.5271078431372549"),
                "Estimativa experimental.");
        when(client.predict(new PredictionRequest(
                        "GASOLINA COMUM", LocalDate.of(2026, 1, 3))))
                .thenReturn(expected);
        PredictionService service = new PredictionService(client);

        PredictionResponse actual = service.predict(input);

        ArgumentCaptor<PredictionRequest> captor = ArgumentCaptor.forClass(PredictionRequest.class);
        verify(client).predict(captor.capture());
        assertThat(captor.getValue().product()).isEqualTo("GASOLINA COMUM");
        assertThat(actual).isEqualTo(expected);
    }
}
