package br.com.fuelvision.api.service;

import br.com.fuelvision.api.domain.AnomalyDirection;
import br.com.fuelvision.api.domain.PageResult;
import br.com.fuelvision.api.domain.PriceAnomaly;
import br.com.fuelvision.api.domain.PriceFilter;
import br.com.fuelvision.api.dto.PageResponse;
import br.com.fuelvision.api.dto.PriceAnomalyResponse;
import br.com.fuelvision.api.repository.PriceRepository;
import java.time.LocalDate;
import java.util.List;
import org.springframework.stereotype.Service;

@Service
public class AnomalyService {

    static final String DETECTION_METHOD = "IQR_1_5";
    static final String ANALYSIS_NOTICE =
            "Comportamento estatisticamente atípico que merece análise.";

    private final PriceRepository repository;

    public AnomalyService(PriceRepository repository) {
        this.repository = repository;
    }

    public PageResponse<PriceAnomalyResponse> findAnomalies(
            String product,
            String state,
            String municipality,
            LocalDate startDate,
            LocalDate endDate,
            int page,
            int size) {
        PriceFilter filter = PriceFilterFactory.create(
                product, state, municipality, startDate, endDate);
        PageResult<PriceAnomaly> result = repository.findAnomalies(filter, page, size);
        List<PriceAnomalyResponse> items = result.items().stream()
                .map(this::toResponse)
                .toList();
        return new PageResponse<>(
                items, result.totalItems(), result.totalPages(), result.page(), result.size());
    }

    private PriceAnomalyResponse toResponse(PriceAnomaly anomaly) {
        return new PriceAnomalyResponse(
                anomaly.id(),
                anomaly.collectionDate(),
                anomaly.salePrice(),
                anomaly.product(),
                anomaly.unit(),
                anomaly.retailer(),
                anomaly.stateCode(),
                anomaly.municipality(),
                anomaly.referenceObservationCount(),
                anomaly.firstQuartile(),
                anomaly.thirdQuartile(),
                anomaly.interquartileRange(),
                anomaly.lowerBound(),
                anomaly.upperBound(),
                anomaly.direction(),
                DETECTION_METHOD,
                reason(anomaly.direction()));
    }

    private String reason(AnomalyDirection direction) {
        String boundary = direction == AnomalyDirection.BELOW_EXPECTED_RANGE
                ? "abaixo do limite inferior"
                : "acima do limite superior";
        return "Preço " + boundary + " calculado pelo método IQR. " + ANALYSIS_NOTICE;
    }
}
