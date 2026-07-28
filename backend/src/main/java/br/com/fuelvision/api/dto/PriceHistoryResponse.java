package br.com.fuelvision.api.dto;

import java.math.BigDecimal;
import java.time.LocalDate;

public record PriceHistoryResponse(
        LocalDate collectionDate,
        String product,
        String unit,
        long observationCount,
        BigDecimal averageSalePrice,
        BigDecimal minimumSalePrice,
        BigDecimal maximumSalePrice,
        BigDecimal priceRange) {
}
