package br.com.fuelvision.api.domain;

import java.math.BigDecimal;
import java.time.LocalDate;

public record PriceObservation(
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
