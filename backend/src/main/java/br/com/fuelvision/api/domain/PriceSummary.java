package br.com.fuelvision.api.domain;

import java.math.BigDecimal;
import java.time.LocalDate;

public record PriceSummary(
        String product,
        String unit,
        long observationCount,
        BigDecimal averageSalePrice,
        BigDecimal minimumSalePrice,
        BigDecimal maximumSalePrice,
        BigDecimal priceRange,
        LocalDate firstCollectionDate,
        LocalDate lastCollectionDate) {
}
