package br.com.fuelvision.api.controller;

import br.com.fuelvision.api.dto.PageResponse;
import br.com.fuelvision.api.dto.PriceHistoryResponse;
import br.com.fuelvision.api.dto.PriceResponse;
import br.com.fuelvision.api.dto.PriceSummaryResponse;
import br.com.fuelvision.api.service.PriceQueryService;
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
import java.util.List;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.http.ProblemDetail;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@Validated
@RestController
@RequestMapping("/api/prices")
@Tag(name = "Prices", description = "Consultas de observações e indicadores de preço")
public class PriceController {

    private final PriceQueryService service;

    public PriceController(PriceQueryService service) {
        this.service = service;
    }

    @GetMapping
    @Operation(summary = "Lista observações de preço com filtros e paginação")
    @ApiResponses({
        @ApiResponse(responseCode = "200", description = "Observações encontradas"),
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
    public PageResponse<PriceResponse> findPrices(
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
        return service.findPrices(
                product, state, municipality, startDate, endDate, page, size);
    }

    @GetMapping("/summary")
    @Operation(summary = "Calcula indicadores agrupados por produto")
    @ApiResponses({
        @ApiResponse(responseCode = "200", description = "Indicadores calculados"),
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
    public List<PriceSummaryResponse> summarize(
            @RequestParam(required = false) @Size(max = 40) String product,
            @RequestParam(required = false) @Pattern(regexp = "(?i)[a-z]{2}") String state,
            @RequestParam(required = false) @Size(max = 120) String municipality,
            @RequestParam(required = false)
                    @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate startDate,
            @RequestParam(required = false)
                    @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate endDate) {
        return service.summarize(product, state, municipality, startDate, endDate);
    }

    @GetMapping("/history")
    @Operation(summary = "Lista a evolução diária dos indicadores")
    @ApiResponses({
        @ApiResponse(responseCode = "200", description = "Pontos históricos encontrados"),
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
    public PageResponse<PriceHistoryResponse> findHistory(
            @RequestParam(required = false) @Size(max = 40) String product,
            @RequestParam(required = false) @Pattern(regexp = "(?i)[a-z]{2}") String state,
            @RequestParam(required = false) @Size(max = 120) String municipality,
            @RequestParam(required = false)
                    @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate startDate,
            @RequestParam(required = false)
                    @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate endDate,
            @RequestParam(defaultValue = "0") @Min(0) @Max(1_000_000) int page,
            @RequestParam(defaultValue = "20") @Min(1) @Max(100) int size) {
        return service.findHistory(
                product, state, municipality, startDate, endDate, page, size);
    }
}
