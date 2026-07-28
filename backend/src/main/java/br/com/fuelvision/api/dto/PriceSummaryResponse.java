package br.com.fuelvision.api.dto;

import java.math.BigDecimal;
import java.time.LocalDate;

public record PriceSummaryResponse(
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
