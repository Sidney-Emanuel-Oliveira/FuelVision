package br.com.fuelvision.api.exception;

import java.io.Serial;

public class PredictionServiceUnavailableException extends RuntimeException {

    @Serial
    private static final long serialVersionUID = 1L;

    public PredictionServiceUnavailableException(String message, Throwable cause) {
        super(message, cause);
    }
}
