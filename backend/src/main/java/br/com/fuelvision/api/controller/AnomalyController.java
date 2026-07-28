package br.com.fuelvision.api.controller;

import br.com.fuelvision.api.dto.PageResponse;
import br.com.fuelvision.api.dto.PriceAnomalyResponse;
import br.com.fuelvision.api.service.AnomalyService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.media.Content;
import io.swagger.v3.oas.annotations.media.Schema;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.Pattern;
import jakarta.validation.constraints.Size;
import java.time.LocalDate;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.http.ProblemDetail;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@Validated
@RestController
@RequestMapping("/api/prices/anomalies")
@Tag(name = "Anomalies", description = "Sinais estatísticos para revisão")
public class AnomalyController {

    private final AnomalyService service;

    public AnomalyController(AnomalyService service) {
        this.service = service;
    }

    @GetMapping
    @Operation(summary = "Lista preços fora dos limites do intervalo interquartil")
    @ApiResponses({
        @ApiResponse(responseCode = "200", description = "Anomalias calculadas"),
        @ApiResponse(
                responseCode = "400",
                description = "Parâmetro inválido",
                content = @Content(
                        mediaType = "application/problem+json",
                        schema = @Schema(implementation = ProblemDetail.class))),
        @ApiResponse(
                responseCode = "503",
                description = "Banco de dados indisponível",
                content = @Content(
                        mediaType = "application/problem+json",
                        schema = @Schema(implementation = ProblemDetail.class)))
    })
    public PageResponse<PriceAnomalyResponse> findAnomalies(
            @RequestParam(required = false) @Size(max = 40)
                    @Parameter(description = "Nome do combustível") String product,
            @RequestParam(required = false) @Pattern(regexp = "(?i)[a-z]{2}")
                    @Parameter(description = "Sigla da UF") String state,
            @RequestParam(required = false) @Size(max = 120)
                    @Parameter(description = "Nome do município") String municipality,
            @RequestParam(required = false)
                    @DateTimeFormat(iso = DateTimeFormat.ISO.DATE)
                    @Parameter(description = "Data inicial inclusiva, no formato AAAA-MM-DD")
                    LocalDate startDate,
            @RequestParam(required = false)
                    @DateTimeFormat(iso = DateTimeFormat.ISO.DATE)
                    @Parameter(description = "Data final inclusiva, no formato AAAA-MM-DD")
                    LocalDate endDate,
            @RequestParam(defaultValue = "0") @Min(0) @Max(1_000_000) int page,
            @RequestParam(defaultValue = "20") @Min(1) @Max(100) int size) {
        return service.findAnomalies(
                product, state, municipality, startDate, endDate, page, size);
    }
}
