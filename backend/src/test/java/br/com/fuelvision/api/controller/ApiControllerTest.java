package br.com.fuelvision.api.controller;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyInt;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import br.com.fuelvision.api.dto.PageResponse;
import br.com.fuelvision.api.dto.PriceResponse;
import br.com.fuelvision.api.dto.StateResponse;
import br.com.fuelvision.api.exception.ApiExceptionHandler;
import br.com.fuelvision.api.service.LocationService;
import br.com.fuelvision.api.service.PriceQueryService;
import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.List;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.webmvc.test.autoconfigure.WebMvcTest;
import org.springframework.context.annotation.Import;
import org.springframework.dao.DataAccessResourceFailureException;
import org.springframework.test.context.bean.override.mockito.MockitoBean;
import org.springframework.test.web.servlet.MockMvc;

@WebMvcTest(
        controllers = {PriceController.class, LocationController.class},
        properties = "debug=false")
@Import(ApiExceptionHandler.class)
class ApiControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockitoBean
    private PriceQueryService priceService;

    @MockitoBean
    private LocationService locationService;

    @Test
    void returnsAPaginatedPriceResponse() throws Exception {
        PriceResponse item = new PriceResponse(
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
        when(priceService.findPrices(any(), any(), any(), any(), any(), anyInt(), anyInt()))
                .thenReturn(new PageResponse<>(List.of(item), 1, 1, 0, 20));

        mockMvc.perform(get("/api/prices").param("product", "GNV"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.totalItems").value(1))
                .andExpect(jsonPath("$.items[0].product").value("GNV"))
                .andExpect(jsonPath("$.items[0].salePrice").value(4.990));
    }

    @Test
    void rejectsInvalidPagination() throws Exception {
        mockMvc.perform(get("/api/prices").param("size", "101"))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.title").value("Parâmetro inválido"));
    }

    @Test
    void rejectsInvalidStateCode() throws Exception {
        mockMvc.perform(get("/api/locations/cities").param("state", "RIO"))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.status").value(400));
    }

    @Test
    void returnsStatesWithAvailablePrices() throws Exception {
        when(locationService.findStates())
                .thenReturn(List.of(new StateResponse("RJ", "RIO DE JANEIRO")));

        mockMvc.perform(get("/api/locations/states"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$[0].code").value("RJ"));
    }

    @Test
    void hidesDatabaseDetailsWhenTheDatabaseIsUnavailable() throws Exception {
        when(locationService.findStates())
                .thenThrow(new DataAccessResourceFailureException("internal connection detail"));

        mockMvc.perform(get("/api/locations/states"))
                .andExpect(status().isServiceUnavailable())
                .andExpect(jsonPath("$.title").value("Banco de dados indisponível"))
                .andExpect(jsonPath("$.detail")
                        .value("A consulta não pôde ser concluída. Tente novamente mais tarde."));
    }
}
