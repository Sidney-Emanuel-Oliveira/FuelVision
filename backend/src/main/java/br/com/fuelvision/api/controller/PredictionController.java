package br.com.fuelvision.api.controller;

import br.com.fuelvision.api.dto.PredictionModelResponse;
import br.com.fuelvision.api.dto.PredictionRequest;
import br.com.fuelvision.api.dto.PredictionResponse;
import br.com.fuelvision.api.service.PredictionService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.media.Content;
import io.swagger.v3.oas.annotations.media.Schema;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import org.springframework.http.ProblemDetail;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/predictions")
@Tag(name = "Predictions", description = "Estimativas experimentais de preço")
public class PredictionController {

    private final PredictionService service;

    public PredictionController(PredictionService service) {
        this.service = service;
    }

    @GetMapping("/model")
    @Operation(summary = "Descreve a versão e os limites do estimador disponível")
    @ApiResponse(responseCode = "200", description = "Metadados do estimador")
    public PredictionModelResponse getModelInfo() {
        return service.getModelInfo();
    }

    @PostMapping
    @Operation(summary = "Calcula uma estimativa experimental de preço")
    @ApiResponses({
        @ApiResponse(responseCode = "200", description = "Estimativa calculada"),
        @ApiResponse(
                responseCode = "400",
                description = "Entrada fora do contrato do estimador",
                content = @Content(
                        mediaType = "application/problem+json",
                        schema = @Schema(implementation = ProblemDetail.class))),
        @ApiResponse(
                responseCode = "503",
                description = "Serviço de estimativas indisponível",
                content = @Content(
                        mediaType = "application/problem+json",
                        schema = @Schema(implementation = ProblemDetail.class)))
    })
    public PredictionResponse predict(@Valid @RequestBody PredictionRequest request) {
        return service.predict(request);
    }
}
