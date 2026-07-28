package br.com.fuelvision.api.exception;

import java.io.Serial;

public class InvalidFilterException extends RuntimeException {

    @Serial
    private static final long serialVersionUID = 1L;

    public InvalidFilterException(String message) {
        super(message);
    }
}
