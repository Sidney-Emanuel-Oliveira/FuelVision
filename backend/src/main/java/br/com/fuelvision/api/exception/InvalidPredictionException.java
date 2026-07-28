package br.com.fuelvision.api.exception;

import java.io.Serial;

public class InvalidPredictionException extends RuntimeException {

    @Serial
    private static final long serialVersionUID = 1L;

    public InvalidPredictionException(String message) {
        super(message);
    }
}
