package br.com.fuelvision.api.client;

import static org.assertj.core.api.Assertions.assertThat;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;

@SpringBootTest(
        properties = {
            "debug=false",
            "fuelvision.prediction.base-url=http://localhost:8000"
        })
class PredictionClientConfigurationTest {

    @Autowired
    private PredictionClient client;

    @Test
    void createsThePredictionClientWithTheAutoConfiguredRestClientBuilder() {
        assertThat(client).isNotNull();
    }
}
