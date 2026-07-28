package br.com.fuelvision.api.domain;

import java.math.BigDecimal;
import java.time.LocalDate;

public record PriceHistoryPoint(
        LocalDate collectionDate,
        String product,
        String unit,
        long observationCount,
        BigDecimal averageSalePrice,
        BigDecimal minimumSalePrice,
        BigDecimal maximumSalePrice,
        BigDecimal priceRange) {
}
