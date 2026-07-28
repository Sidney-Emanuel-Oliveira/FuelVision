package br.com.fuelvision.api.dto;

import java.math.BigDecimal;
import java.time.LocalDate;

public record PredictionResponse(
        String product,
        LocalDate collectionDate,
        BigDecimal estimatedPrice,
        String unit,
        String modelVersion,
        String modelType,
        LocalDate trainedThrough,
        BigDecimal evaluationMae,
        String warning) {}
