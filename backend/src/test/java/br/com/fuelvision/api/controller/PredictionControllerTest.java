package br.com.fuelvision.api.controller;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import br.com.fuelvision.api.dto.PredictionModelResponse;
import br.com.fuelvision.api.dto.PredictionResponse;
import br.com.fuelvision.api.exception.ApiExceptionHandler;
import br.com.fuelvision.api.exception.PredictionServiceUnavailableException;
import br.com.fuelvision.api.service.PredictionService;
import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.List;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.webmvc.test.autoconfigure.WebMvcTest;
import org.springframework.context.annotation.Import;
import org.springframework.http.MediaType;
import org.springframework.test.context.bean.override.mockito.MockitoBean;
import org.springframework.test.web.servlet.MockMvc;

@WebMvcTest(controllers = PredictionController.class, properties = "debug=false")
@Import(ApiExceptionHandler.class)
class PredictionControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockitoBean
    private PredictionService service;

    @Test
    void returnsAnEstimateWithVersionAndWarning() throws Exception {
        when(service.predict(any())).thenReturn(prediction());

        mockMvc.perform(post("/api/predictions")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("""
                                {
                                  "product": "GASOLINA COMUM",
                                  "collectionDate": "2026-01-03"
                                }
                                """))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.estimatedPrice").value(6.077))
                .andExpect(jsonPath("$.modelVersion").value("product-mean-baseline-v1"))
                .andExpect(jsonPath("$.warning").value("Estimativa experimental."));
    }

    @Test
    void returnsModelLimitsAndSupportedProducts() throws Exception {
        when(service.getModelInfo()).thenReturn(modelInfo());

        mockMvc.perform(get("/api/predictions/model"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.supportedProducts[0]").value("GASOLINA COMUM"))
                .andExpect(jsonPath("$.predictionStart").value("2026-01-03"))
                .andExpect(jsonPath("$.ridgeBeatsBaseline").value(false));
    }

    @Test
    void rejectsAnIncompletePredictionRequest() throws Exception {
        mockMvc.perform(post("/api/predictions")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"product\":\"GASOLINA COMUM\"}"))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.title").value("Parâmetro inválido"));
    }

    @Test
    void hidesInternalDetailsWhenPredictionServiceIsUnavailable() throws Exception {
        when(service.getModelInfo()).thenThrow(new PredictionServiceUnavailableException(
                "internal URL", new IllegalStateException("connection refused")));

        mockMvc.perform(get("/api/predictions/model"))
                .andExpect(status().isServiceUnavailable())
                .andExpect(jsonPath("$.title").value("Serviço de estimativas indisponível"))
                .andExpect(jsonPath("$.detail")
                        .value("A estimativa não pôde ser calculada. Tente novamente mais tarde."));
    }

    private PredictionResponse prediction() {
        return new PredictionResponse(
                "GASOLINA COMUM",
                LocalDate.of(2026, 1, 3),
                new BigDecimal("6.077"),
                "BRL/liter",
                "product-mean-baseline-v1",
                "ProductMeanBaseline",
                LocalDate.of(2026, 1, 2),
                new BigDecimal("0.5271078431372549"),
                "Estimativa experimental.");
    }

    private PredictionModelResponse modelInfo() {
        return new PredictionModelResponse(
                "product-mean-baseline-v1",
                "ProductMeanBaseline",
                "BRL/liter",
                List.of("GASOLINA COMUM"),
                50,
                LocalDate.of(2026, 1, 1),
                LocalDate.of(2026, 1, 2),
                LocalDate.of(2026, 1, 3),
                LocalDate.of(2026, 2, 1),
                new BigDecimal("0.5271078431372549"),
                new BigDecimal("0.5719782379940552"),
                false,
                "Lower MAE.",
                "Estimativa experimental.");
    }
}
