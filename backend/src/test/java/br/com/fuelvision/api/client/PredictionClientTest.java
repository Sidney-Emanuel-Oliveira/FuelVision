package br.com.fuelvision.api.client;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.springframework.test.web.client.ExpectedCount.once;
import static org.springframework.test.web.client.match.MockRestRequestMatchers.content;
import static org.springframework.test.web.client.match.MockRestRequestMatchers.method;
import static org.springframework.test.web.client.match.MockRestRequestMatchers.requestTo;
import static org.springframework.test.web.client.response.MockRestResponseCreators.withBadRequest;
import static org.springframework.test.web.client.response.MockRestResponseCreators.withSuccess;

import br.com.fuelvision.api.dto.PredictionRequest;
import br.com.fuelvision.api.dto.PredictionResponse;
import br.com.fuelvision.api.exception.InvalidPredictionException;
import java.time.LocalDate;
import org.junit.jupiter.api.Test;
import org.springframework.http.HttpMethod;
import org.springframework.http.MediaType;
import org.springframework.test.web.client.MockRestServiceServer;
import org.springframework.web.client.RestClient;

class PredictionClientTest {

    @Test
    void sendsJsonAndMapsThePythonPredictionResponse() {
        RestClient.Builder builder = RestClient.builder();
        MockRestServiceServer server = MockRestServiceServer.bindTo(builder).build();
        PredictionClient client = new PredictionClient(builder, "http://prediction.test");
        server.expect(once(), requestTo("http://prediction.test/predict"))
                .andExpect(method(HttpMethod.POST))
                .andExpect(content().json("""
                        {
                          "product": "GASOLINA COMUM",
                          "collectionDate": "2026-01-03"
                        }
                        """))
                .andRespond(withSuccess("""
                        {
                          "product": "GASOLINA COMUM",
                          "collectionDate": "2026-01-03",
                          "estimatedPrice": 6.077,
                          "unit": "BRL/liter",
                          "modelVersion": "product-mean-baseline-v1",
                          "modelType": "ProductMeanBaseline",
                          "trainedThrough": "2026-01-02",
                          "evaluationMae": 0.5271078431372549,
                          "warning": "Estimativa experimental."
                        }
                        """, MediaType.APPLICATION_JSON));

        PredictionResponse response = client.predict(new PredictionRequest(
                "GASOLINA COMUM", LocalDate.of(2026, 1, 3)));

        server.verify();
        assertThat(response.estimatedPrice()).isEqualByComparingTo("6.077");
        assertThat(response.modelVersion()).isEqualTo("product-mean-baseline-v1");
    }

    @Test
    void convertsPythonClientErrorsToSafeDomainErrors() {
        RestClient.Builder builder = RestClient.builder();
        MockRestServiceServer server = MockRestServiceServer.bindTo(builder).build();
        PredictionClient client = new PredictionClient(builder, "http://prediction.test");
        server.expect(requestTo("http://prediction.test/predict"))
                .andRespond(withBadRequest());

        assertThatThrownBy(() -> client.predict(new PredictionRequest(
                        "GNV", LocalDate.of(2026, 1, 3))))
                .isInstanceOf(InvalidPredictionException.class)
                .hasMessage("Os dados informados não são aceitos pela versão atual do modelo.");
        server.verify();
    }
}
