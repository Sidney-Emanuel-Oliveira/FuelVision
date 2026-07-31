package br.com.fuelvision.api.client;

import java.io.IOException;
import java.io.InputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.security.GeneralSecurityException;
import java.security.KeyStore;
import java.security.cert.Certificate;
import java.security.cert.CertificateException;
import java.security.cert.CertificateFactory;
import java.security.cert.X509Certificate;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collection;
import java.util.List;
import javax.net.ssl.SSLContext;
import javax.net.ssl.TrustManager;
import javax.net.ssl.TrustManagerFactory;
import javax.net.ssl.X509TrustManager;

final class RuntimeCaSslContext {

    private RuntimeCaSslContext() {}

    static LoadedSslContext load(Path pemBundle) throws IOException, GeneralSecurityException {
        Collection<? extends Certificate> certificates;
        try (InputStream input = Files.newInputStream(pemBundle)) {
            certificates = CertificateFactory.getInstance("X.509")
                    .generateCertificates(input);
        }

        if (certificates.isEmpty()) {
            throw new CertificateException("The runtime CA bundle contains no certificates");
        }

        KeyStore runtimeTrustStore = KeyStore.getInstance(KeyStore.getDefaultType());
        runtimeTrustStore.load(null, null);

        int certificateCount = 0;
        for (Certificate certificate : certificates) {
            if (certificate instanceof X509Certificate x509Certificate) {
                runtimeTrustStore.setCertificateEntry(
                        "runtime-ca-" + certificateCount, x509Certificate);
                certificateCount++;
            }
        }

        if (certificateCount == 0) {
            throw new CertificateException("The runtime CA bundle contains no X.509 certificates");
        }

        X509TrustManager defaultTrustManager = trustManager(null);
        X509TrustManager runtimeTrustManager = trustManager(runtimeTrustStore);
        X509TrustManager compositeTrustManager =
                new CompositeX509TrustManager(defaultTrustManager, runtimeTrustManager);

        SSLContext sslContext = SSLContext.getInstance("TLS");
        sslContext.init(null, new TrustManager[] {compositeTrustManager}, null);
        return new LoadedSslContext(sslContext, certificateCount);
    }

    private static X509TrustManager trustManager(KeyStore trustStore)
            throws GeneralSecurityException {
        TrustManagerFactory factory =
                TrustManagerFactory.getInstance(TrustManagerFactory.getDefaultAlgorithm());
        factory.init(trustStore);

        return Arrays.stream(factory.getTrustManagers())
                .filter(X509TrustManager.class::isInstance)
                .map(X509TrustManager.class::cast)
                .findFirst()
                .orElseThrow(() -> new GeneralSecurityException(
                        "No X.509 trust manager is available"));
    }

    record LoadedSslContext(SSLContext sslContext, int certificateCount) {}

    private static final class CompositeX509TrustManager implements X509TrustManager {

        private final List<X509TrustManager> delegates;

        private CompositeX509TrustManager(X509TrustManager... delegates) {
            this.delegates = List.of(delegates);
        }

        @Override
        public void checkClientTrusted(X509Certificate[] chain, String authenticationType)
                throws CertificateException {
            checkTrusted(chain, authenticationType, true);
        }

        @Override
        public void checkServerTrusted(X509Certificate[] chain, String authenticationType)
                throws CertificateException {
            checkTrusted(chain, authenticationType, false);
        }

        @Override
        public X509Certificate[] getAcceptedIssuers() {
            return delegates.stream()
                    .flatMap(delegate -> Arrays.stream(delegate.getAcceptedIssuers()))
                    .toArray(X509Certificate[]::new);
        }

        private void checkTrusted(
                X509Certificate[] chain, String authenticationType, boolean client)
                throws CertificateException {
            List<CertificateException> failures = new ArrayList<>();
            for (X509TrustManager delegate : delegates) {
                try {
                    if (client) {
                        delegate.checkClientTrusted(chain, authenticationType);
                    } else {
                        delegate.checkServerTrusted(chain, authenticationType);
                    }
                    return;
                } catch (CertificateException exception) {
                    failures.add(exception);
                }
            }

            CertificateException failure =
                    new CertificateException("No configured trust manager accepted the certificate");
            failures.forEach(failure::addSuppressed);
            throw failure;
        }
    }
}
