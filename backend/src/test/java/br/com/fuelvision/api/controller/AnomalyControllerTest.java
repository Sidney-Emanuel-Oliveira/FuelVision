package br.com.fuelvision.api.controller;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyInt;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import br.com.fuelvision.api.domain.AnomalyDirection;
import br.com.fuelvision.api.dto.PageResponse;
import br.com.fuelvision.api.dto.PriceAnomalyResponse;
import br.com.fuelvision.api.exception.ApiExceptionHandler;
import br.com.fuelvision.api.exception.InvalidFilterException;
import br.com.fuelvision.api.service.AnomalyService;
import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.List;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.webmvc.test.autoconfigure.WebMvcTest;
import org.springframework.context.annotation.Import;
import org.springframework.test.context.bean.override.mockito.MockitoBean;
import org.springframework.test.web.servlet.MockMvc;

@WebMvcTest(controllers = AnomalyController.class, properties = "debug=false")
@Import(ApiExceptionHandler.class)
class AnomalyControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockitoBean
    private AnomalyService service;

    @Test
    void returnsAStatisticallyQualifiedAlert() throws Exception {
        PriceAnomalyResponse item = new PriceAnomalyResponse(
                1L,
                LocalDate.of(2026, 1, 2),
                new BigDecimal("7.970"),
                "GASOLINA COMUM",
                "BRL/liter",
                "REVENDA EXEMPLO",
                "AC",
                "CRUZEIRO DO SUL",
                10,
                new BigDecimal("6.2825"),
                new BigDecimal("6.5900"),
                new BigDecimal("0.3075"),
                new BigDecimal("5.82125"),
                new BigDecimal("7.05125"),
                AnomalyDirection.ABOVE_EXPECTED_RANGE,
                "IQR_1_5",
                "Preço acima do limite superior calculado pelo método IQR. "
                        + "Comportamento estatisticamente atípico que merece análise.");
        when(service.findAnomalies(any(), any(), any(), any(), any(), anyInt(), anyInt()))
                .thenReturn(new PageResponse<>(List.of(item), 1, 1, 0, 20));

        mockMvc.perform(get("/api/prices/anomalies").param("product", "GASOLINA COMUM"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.totalItems").value(1))
                .andExpect(jsonPath("$.items[0].detectionMethod").value("IQR_1_5"))
                .andExpect(jsonPath("$.items[0].direction")
                        .value("ABOVE_EXPECTED_RANGE"))
                .andExpect(jsonPath("$.items[0].reason")
                        .value(org.hamcrest.Matchers.endsWith(
                                "Comportamento estatisticamente atípico que merece análise.")));
    }

    @Test
    void rejectsInvalidPaginationBeforeCallingTheService() throws Exception {
        mockMvc.perform(get("/api/prices/anomalies").param("size", "101"))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.title").value("Parâmetro inválido"));
    }

    @Test
    void mapsAnInvertedPeriodToABadRequest() throws Exception {
        when(service.findAnomalies(any(), any(), any(), any(), any(), anyInt(), anyInt()))
                .thenThrow(new InvalidFilterException(
                        "startDate deve ser anterior ou igual a endDate."));

        mockMvc.perform(get("/api/prices/anomalies")
                        .param("startDate", "2026-01-08")
                        .param("endDate", "2026-01-01"))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.detail")
                        .value("startDate deve ser anterior ou igual a endDate."));
    }
}
