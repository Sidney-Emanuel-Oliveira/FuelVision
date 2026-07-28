package br.com.fuelvision.api.dto;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.List;

public record PredictionModelResponse(
        String modelVersion,
        String modelType,
        String unit,
        List<String> supportedProducts,
        int trainingRows,
        LocalDate trainingStart,
        LocalDate trainingEnd,
        LocalDate predictionStart,
        LocalDate predictionEnd,
        BigDecimal evaluationMae,
        BigDecimal ridgeEvaluationMae,
        boolean ridgeBeatsBaseline,
        String selectionReason,
        String warning) {}
