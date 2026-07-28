package br.com.fuelvision.api.dto;

import br.com.fuelvision.api.domain.AnomalyDirection;
import java.math.BigDecimal;
import java.time.LocalDate;

public record PriceAnomalyResponse(
        long id,
        LocalDate collectionDate,
        BigDecimal salePrice,
        String product,
        String unit,
        String retailer,
        String stateCode,
        String municipality,
        long referenceObservationCount,
        BigDecimal firstQuartile,
        BigDecimal thirdQuartile,
        BigDecimal interquartileRange,
        BigDecimal lowerBound,
        BigDecimal upperBound,
        AnomalyDirection direction,
        String detectionMethod,
        String reason) {}
