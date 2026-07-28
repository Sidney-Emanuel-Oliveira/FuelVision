package br.com.fuelvision.api.service;

import br.com.fuelvision.api.client.PredictionClient;
import br.com.fuelvision.api.dto.PredictionModelResponse;
import br.com.fuelvision.api.dto.PredictionRequest;
import br.com.fuelvision.api.dto.PredictionResponse;
import java.util.Locale;
import org.springframework.stereotype.Service;

@Service
public class PredictionService {

    private final PredictionClient client;

    public PredictionService(PredictionClient client) {
        this.client = client;
    }

    public PredictionModelResponse getModelInfo() {
        return client.getModelInfo();
    }

    public PredictionResponse predict(PredictionRequest request) {
        PredictionRequest normalized = new PredictionRequest(
                request.product().trim().toUpperCase(Locale.ROOT),
                request.collectionDate());
        return client.predict(normalized);
    }
}
