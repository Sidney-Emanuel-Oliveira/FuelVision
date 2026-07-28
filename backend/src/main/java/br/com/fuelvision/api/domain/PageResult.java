package br.com.fuelvision.api.domain;

import java.util.List;

public record PageResult<T>(List<T> items, long totalItems, int page, int size) {

    public int totalPages() {
        if (totalItems == 0) {
            return 0;
        }
        return (int) Math.ceil((double) totalItems / size);
    }
}
