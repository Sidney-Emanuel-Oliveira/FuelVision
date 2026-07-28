package br.com.fuelvision.api.service;

import br.com.fuelvision.api.domain.PriceFilter;
import br.com.fuelvision.api.exception.InvalidFilterException;
import java.time.LocalDate;
import java.util.Locale;

final class PriceFilterFactory {

    private PriceFilterFactory() {}

    static PriceFilter create(
            String product,
            String state,
            String municipality,
            LocalDate startDate,
            LocalDate endDate) {
        if (startDate != null && endDate != null && startDate.isAfter(endDate)) {
            throw new InvalidFilterException(
                    "startDate deve ser anterior ou igual a endDate.");
        }
        return new PriceFilter(
                normalize(product),
                normalize(state),
                normalize(municipality),
                startDate,
                endDate);
    }

    private static String normalize(String value) {
        if (value == null || value.isBlank()) {
            return null;
        }
        return value.strip().toUpperCase(Locale.ROOT);
    }
}
