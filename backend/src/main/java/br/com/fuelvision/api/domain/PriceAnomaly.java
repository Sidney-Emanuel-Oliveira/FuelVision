package br.com.fuelvision.api.domain;

import java.math.BigDecimal;
import java.time.LocalDate;

public record PriceAnomaly(
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
        AnomalyDirection direction) {}
