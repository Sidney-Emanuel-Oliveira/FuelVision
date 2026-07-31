package br.com.fuelvision.api.client;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

import java.net.URISyntaxException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.security.cert.CertificateException;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

class RuntimeCaSslContextTest {

    @TempDir
    private Path temporaryDirectory;

    @Test
    void loadsX509CertificatesWithoutReplacingTheDefaultTrustManager()
            throws Exception {
        Path bundle = resourcePath("runtime-ca-test.pem");

        RuntimeCaSslContext.LoadedSslContext loaded =
                RuntimeCaSslContext.load(bundle);

        assertThat(loaded.sslContext()).isNotNull();
        assertThat(loaded.sslContext().getProtocol()).isEqualTo("TLS");
        assertThat(loaded.certificateCount()).isEqualTo(1);
    }

    @Test
    void rejectsAFileThatDoesNotContainCertificates() throws Exception {
        Path invalidBundle = temporaryDirectory.resolve("invalid-ca.pem");
        Files.writeString(invalidBundle, "not a certificate");

        assertThatThrownBy(() -> RuntimeCaSslContext.load(invalidBundle))
                .isInstanceOf(CertificateException.class);
    }

    private Path resourcePath(String resourceName) throws URISyntaxException {
        return Path.of(getClass().getClassLoader().getResource(resourceName).toURI());
    }
}
