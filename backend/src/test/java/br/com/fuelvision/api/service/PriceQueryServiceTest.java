package br.com.fuelvision.api.service;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import br.com.fuelvision.api.domain.PageResult;
import br.com.fuelvision.api.domain.PriceFilter;
import br.com.fuelvision.api.domain.PriceObservation;
import br.com.fuelvision.api.dto.PageResponse;
import br.com.fuelvision.api.dto.PriceResponse;
import br.com.fuelvision.api.exception.InvalidFilterException;
import br.com.fuelvision.api.repository.PriceRepository;
import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.List;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.ArgumentCaptor;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

@ExtendWith(MockitoExtension.class)
class PriceQueryServiceTest {

    @Mock
    private PriceRepository repository;

    @Test
    void normalizesFiltersAndMapsPagination() {
        PriceObservation observation = new PriceObservation(
                1L,
                LocalDate.of(2026, 1, 7),
                new BigDecimal("4.990"),
                null,
                "GNV",
                "BRL/m3",
                "REVENDA EXEMPLO",
                "BRANCA",
                "RJ",
                "MACAE");
        when(repository.findPrices(any(), any(Integer.class), any(Integer.class)))
                .thenReturn(new PageResult<>(List.of(observation), 21, 1, 10));
        PriceQueryService service = new PriceQueryService(repository);

        PageResponse<PriceResponse> response = service.findPrices(
                " gnv ", "rj", " macae ", null, null, 1, 10);

        ArgumentCaptor<PriceFilter> filterCaptor = ArgumentCaptor.forClass(PriceFilter.class);
        verify(repository).findPrices(filterCaptor.capture(), any(Integer.class), any(Integer.class));
        assertThat(filterCaptor.getValue())
                .isEqualTo(new PriceFilter("GNV", "RJ", "MACAE", null, null));
        assertThat(response.totalItems()).isEqualTo(21);
        assertThat(response.totalPages()).isEqualTo(3);
        assertThat(response.items()).hasSize(1);
        assertThat(response.items().getFirst().salePrice())
                .isEqualByComparingTo("4.990");
    }

    @Test
    void rejectsAnInvertedDateRange() {
        PriceQueryService service = new PriceQueryService(repository);

        assertThatThrownBy(() -> service.summarize(
                        null,
                        null,
                        null,
                        LocalDate.of(2026, 1, 8),
                        LocalDate.of(2026, 1, 1)))
                .isInstanceOf(InvalidFilterException.class)
                .hasMessage("startDate deve ser anterior ou igual a endDate.");
    }

    @Test
    void convertsBlankFiltersToAbsentFilters() {
        PriceQueryService service = new PriceQueryService(repository);
        when(repository.summarize(any())).thenReturn(List.of());

        service.summarize(" ", "", "   ", null, null);

        ArgumentCaptor<PriceFilter> filterCaptor = ArgumentCaptor.forClass(PriceFilter.class);
        verify(repository).summarize(filterCaptor.capture());
        assertThat(filterCaptor.getValue())
                .isEqualTo(new PriceFilter(null, null, null, null, null));
    }
}
