package br.com.fuelvision.api.config;

import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.Info;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class OpenApiConfig {

    @Bean
    OpenAPI fuelVisionOpenApi() {
        return new OpenAPI()
                .info(new Info()
                        .title("FuelVision API")
                        .version("1.0.0")
                        .description("Consultas de preços de combustíveis da amostra FuelVision."));
    }
}
