package br.com.fuelvision.api.service;

import br.com.fuelvision.api.domain.PageResult;
import br.com.fuelvision.api.domain.PriceFilter;
import br.com.fuelvision.api.domain.PriceHistoryPoint;
import br.com.fuelvision.api.domain.PriceObservation;
import br.com.fuelvision.api.dto.PageResponse;
import br.com.fuelvision.api.dto.PriceHistoryResponse;
import br.com.fuelvision.api.dto.PriceResponse;
import br.com.fuelvision.api.dto.PriceSummaryResponse;
import br.com.fuelvision.api.exception.InvalidFilterException;
import br.com.fuelvision.api.repository.PriceRepository;
import java.time.LocalDate;
import java.util.List;
import java.util.Locale;
import org.springframework.stereotype.Service;

@Service
public class PriceQueryService {

    private final PriceRepository repository;

    public PriceQueryService(PriceRepository repository) {
        this.repository = repository;
    }

    public PageResponse<PriceResponse> findPrices(
            String product,
            String state,
            String municipality,
            LocalDate startDate,
            LocalDate endDate,
            int page,
            int size) {
        PriceFilter filter = createFilter(product, state, municipality, startDate, endDate);
        PageResult<PriceObservation> result = repository.findPrices(filter, page, size);
        List<PriceResponse> items = result.items().stream()
                .map(item -> new PriceResponse(
                        item.id(),
                        item.collectionDate(),
                        item.salePrice(),
                        item.purchasePrice(),
                        item.product(),
                        item.unit(),
                        item.retailer(),
                        item.brand(),
                        item.stateCode(),
                        item.municipality()))
                .toList();
        return new PageResponse<>(
                items, result.totalItems(), result.totalPages(), result.page(), result.size());
    }

    public List<PriceSummaryResponse> summarize(
            String product,
            String state,
            String municipality,
            LocalDate startDate,
            LocalDate endDate) {
        PriceFilter filter = createFilter(product, state, municipality, startDate, endDate);
        return repository.summarize(filter).stream()
                .map(summary -> new PriceSummaryResponse(
                        summary.product(),
                        summary.unit(),
                        summary.observationCount(),
                        summary.averageSalePrice(),
                        summary.minimumSalePrice(),
                        summary.maximumSalePrice(),
                        summary.priceRange(),
                        summary.firstCollectionDate(),
                        summary.lastCollectionDate()))
                .toList();
    }

    public PageResponse<PriceHistoryResponse> findHistory(
            String product,
            String state,
            String municipality,
            LocalDate startDate,
            LocalDate endDate,
            int page,
            int size) {
        PriceFilter filter = createFilter(product, state, municipality, startDate, endDate);
        PageResult<PriceHistoryPoint> result = repository.findHistory(filter, page, size);
        List<PriceHistoryResponse> items = result.items().stream()
                .map(item -> new PriceHistoryResponse(
                        item.collectionDate(),
                        item.product(),
                        item.unit(),
                        item.observationCount(),
                        item.averageSalePrice(),
                        item.minimumSalePrice(),
                        item.maximumSalePrice(),
                        item.priceRange()))
                .toList();
        return new PageResponse<>(
                items, result.totalItems(), result.totalPages(), result.page(), result.size());
    }

    PriceFilter createFilter(
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

    private String normalize(String value) {
        if (value == null || value.isBlank()) {
            return null;
        }
        return value.strip().toUpperCase(Locale.ROOT);
    }
}
