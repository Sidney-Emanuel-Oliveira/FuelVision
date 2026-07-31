package br.com.fuelvision.api.client;

import br.com.fuelvision.api.dto.PredictionModelResponse;
import br.com.fuelvision.api.dto.PredictionRequest;
import br.com.fuelvision.api.dto.PredictionResponse;
import br.com.fuelvision.api.exception.InvalidPredictionException;
import br.com.fuelvision.api.exception.PredictionServiceUnavailableException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Component;
import org.springframework.web.client.HttpClientErrorException;
import org.springframework.web.client.RestClient;
import org.springframework.web.client.RestClientException;

@Component
public class PredictionClient {

    private static final Logger LOGGER = LoggerFactory.getLogger(PredictionClient.class);

    private final RestClient restClient;

    public PredictionClient(
            RestClient.Builder builder,
            @Value("${fuelvision.prediction.base-url}") String baseUrl) {
        this.restClient = builder.baseUrl(baseUrl).build();
        LOGGER.info(
                "Prediction service client configured: localTarget={}",
                baseUrl.startsWith("http://localhost")
                        || baseUrl.startsWith("http://127.0.0.1"));
    }

    public PredictionModelResponse getModelInfo() {
        try {
            PredictionModelResponse response = restClient.get()
                    .uri("/model-info")
                    .accept(MediaType.APPLICATION_JSON)
                    .retrieve()
                    .body(PredictionModelResponse.class);
            return requireResponse(response);
        } catch (RestClientException exception) {
            logFailure("model-info", exception);
            throw unavailable(exception);
        }
    }

    public PredictionResponse predict(PredictionRequest request) {
        try {
            PredictionResponse response = restClient.post()
                    .uri("/predict")
                    .contentType(MediaType.APPLICATION_JSON)
                    .accept(MediaType.APPLICATION_JSON)
                    .body(request)
                    .retrieve()
                    .body(PredictionResponse.class);
            return requireResponse(response);
        } catch (HttpClientErrorException exception) {
            throw new InvalidPredictionException(
                    "Os dados informados não são aceitos pela versão atual do modelo.");
        } catch (RestClientException exception) {
            logFailure("predict", exception);
            throw unavailable(exception);
        }
    }

    private <T> T requireResponse(T response) {
        if (response == null) {
            throw unavailable(new IllegalStateException("Empty prediction response"));
        }
        return response;
    }

    private void logFailure(String operation, RestClientException exception) {
        Throwable rootCause = exception;
        while (rootCause.getCause() != null) {
            rootCause = rootCause.getCause();
        }
        LOGGER.warn(
                "Prediction service request failed: operation={}, exception={}, rootCause={}",
                operation,
                exception.getClass().getSimpleName(),
                rootCause.getClass().getSimpleName());
    }

    private PredictionServiceUnavailableException unavailable(Throwable cause) {
        return new PredictionServiceUnavailableException(
                "O serviço de estimativas não está disponível.", cause);
    }
}
