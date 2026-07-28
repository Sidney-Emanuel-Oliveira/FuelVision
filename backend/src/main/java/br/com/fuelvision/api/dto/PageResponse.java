package br.com.fuelvision.api.dto;

import java.util.List;

public record PageResponse<T>(
        List<T> items,
        long totalItems,
        int totalPages,
        int page,
        int size) {
}
