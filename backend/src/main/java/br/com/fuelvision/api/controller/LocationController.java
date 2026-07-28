package br.com.fuelvision.api.controller;

import br.com.fuelvision.api.dto.CityResponse;
import br.com.fuelvision.api.dto.StateResponse;
import br.com.fuelvision.api.service.LocationService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.media.Content;
import io.swagger.v3.oas.annotations.media.Schema;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.constraints.Pattern;
import java.util.List;
import org.springframework.http.ProblemDetail;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@Validated
@RestController
@RequestMapping("/api/locations")
@Tag(name = "Locations", description = "Localidades que possuem observações de preço")
public class LocationController {

    private final LocationService service;

    public LocationController(LocationService service) {
        this.service = service;
    }

    @GetMapping("/states")
    @Operation(summary = "Lista estados presentes nos dados")
    @ApiResponses({
        @ApiResponse(responseCode = "200", description = "Estados encontrados"),
        @ApiResponse(
                responseCode = "503",
                description = "Banco de dados indisponível",
                content = @Content(
                        mediaType = "application/problem+json",
                        schema = @Schema(implementation = ProblemDetail.class)))
    })
    public List<StateResponse> findStates() {
        return service.findStates();
    }

    @GetMapping("/cities")
    @Operation(summary = "Lista municípios presentes em uma UF")
    @ApiResponses({
        @ApiResponse(responseCode = "200", description = "Municípios encontrados"),
        @ApiResponse(
                responseCode = "400",
                description = "Sigla da UF inválida",
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
    public List<CityResponse> findCities(
            @RequestParam @Pattern(regexp = "(?i)[a-z]{2}") String state) {
        return service.findCities(state);
    }
}
