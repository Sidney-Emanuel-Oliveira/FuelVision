package br.com.fuelvision.api.domain;

import java.time.LocalDate;

public record PriceFilter(
        String product,
        String state,
        String municipality,
        LocalDate startDate,
        LocalDate endDate) {
}
