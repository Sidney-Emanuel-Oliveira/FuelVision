package br.com.fuelvision.api.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import java.time.LocalDate;

public record PredictionRequest(
        @NotBlank @Size(max = 40) String product,
        @NotNull LocalDate collectionDate) {}
