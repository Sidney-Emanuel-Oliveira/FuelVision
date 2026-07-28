package br.com.fuelvision.api.dto;

import java.math.BigDecimal;
import java.time.LocalDate;

public record PriceResponse(
        long id,
        LocalDate collectionDate,
        BigDecimal salePrice,
        BigDecimal purchasePrice,
        String product,
        String unit,
        String retailer,
        String brand,
        String stateCode,
        String municipality) {
}
