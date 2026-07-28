package br.com.fuelvision.api.exception;

import jakarta.validation.ConstraintViolationException;
import org.springframework.dao.DataAccessException;
import org.springframework.http.HttpStatus;
import org.springframework.http.ProblemDetail;
import org.springframework.http.converter.HttpMessageNotReadableException;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.MissingServletRequestParameterException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import org.springframework.web.method.annotation.HandlerMethodValidationException;
import org.springframework.web.method.annotation.MethodArgumentTypeMismatchException;

@RestControllerAdvice
public class ApiExceptionHandler {

    @ExceptionHandler(InvalidFilterException.class)
    ProblemDetail handleInvalidFilter(InvalidFilterException exception) {
        return problem(HttpStatus.BAD_REQUEST, "Filtro inválido", exception.getMessage());
    }

    @ExceptionHandler(InvalidPredictionException.class)
    ProblemDetail handleInvalidPrediction(InvalidPredictionException exception) {
        return problem(HttpStatus.BAD_REQUEST, "Entrada de previsão inválida", exception.getMessage());
    }

    @ExceptionHandler({
        HandlerMethodValidationException.class,
        ConstraintViolationException.class,
        MethodArgumentTypeMismatchException.class,
        MissingServletRequestParameterException.class,
        MethodArgumentNotValidException.class,
        HttpMessageNotReadableException.class
    })
    ProblemDetail handleInvalidParameter(Exception exception) {
        return problem(
                HttpStatus.BAD_REQUEST,
                "Parâmetro inválido",
                "Revise os parâmetros, limites e formatos informados na requisição.");
    }

    @ExceptionHandler(DataAccessException.class)
    ProblemDetail handleDatabaseFailure(DataAccessException exception) {
        return problem(
                HttpStatus.SERVICE_UNAVAILABLE,
                "Banco de dados indisponível",
                "A consulta não pôde ser concluída. Tente novamente mais tarde.");
    }

    @ExceptionHandler(PredictionServiceUnavailableException.class)
    ProblemDetail handlePredictionServiceFailure(PredictionServiceUnavailableException exception) {
        return problem(
                HttpStatus.SERVICE_UNAVAILABLE,
                "Serviço de estimativas indisponível",
                "A estimativa não pôde ser calculada. Tente novamente mais tarde.");
    }

    private ProblemDetail problem(HttpStatus status, String title, String detail) {
        ProblemDetail problem = ProblemDetail.forStatusAndDetail(status, detail);
        problem.setTitle(title);
        return problem;
    }
}
