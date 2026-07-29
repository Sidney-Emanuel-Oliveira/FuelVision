import { useEffect, useState } from "react";
import { getAnomalies } from "../api/fuelVisionApi";
import type { PageResponse, PriceAnomaly, PriceFilters } from "../types/api";
import { formatDate, formatPrice } from "../utils/formatters";

interface AnomalyPanelProps {
  filters: PriceFilters;
}

function isAbortError(error: unknown) {
  return error instanceof DOMException && error.name === "AbortError";
}

function errorMessage(error: unknown) {
  return error instanceof Error
    ? error.message
    : "Não foi possível consultar os alertas estatísticos.";
}

function directionLabel(anomaly: PriceAnomaly) {
  return anomaly.direction === "ABOVE_EXPECTED_RANGE"
    ? "Acima do intervalo esperado"
    : "Abaixo do intervalo esperado";
}

export function AnomalyPanel({ filters }: AnomalyPanelProps) {
  const [result, setResult] = useState<PageResponse<PriceAnomaly> | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [attempt, setAttempt] = useState(0);

  useEffect(() => {
    const controller = new AbortController();
    setLoading(true);
    setError(null);
    setResult(null);

    getAnomalies(filters, controller.signal)
      .then(setResult)
      .catch((requestError: unknown) => {
        if (!isAbortError(requestError)) setError(errorMessage(requestError));
      })
      .finally(() => {
        if (!controller.signal.aborted) setLoading(false);
      });

    return () => controller.abort();
  }, [attempt, filters]);

  return (
    <section className="anomaly-panel" aria-labelledby="anomaly-title">
      <div className="anomaly-panel__heading">
        <div>
          <span className="eyebrow">Revisão estatística</span>
          <h2 id="anomaly-title">Comportamentos atípicos</h2>
        </div>
        {result && (
          <span className="anomaly-panel__count">
            {result.totalItems} {result.totalItems === 1 ? "alerta" : "alertas"}
          </span>
        )}
      </div>

      <p className="anomaly-panel__intro">
        O método IQR compara preços do mesmo combustível e unidade. Um alerta
        não comprova fraude ou irregularidade: indica um comportamento
        estatisticamente atípico que merece análise.
      </p>

      {loading && <p role="status">Calculando limites estatísticos…</p>}

      {!loading && error && (
        <div className="anomaly-panel__error" role="alert">
          <p>{error}</p>
          <button
            className="button button--secondary"
            type="button"
            onClick={() => setAttempt((current) => current + 1)}
          >
            Tentar novamente
          </button>
        </div>
      )}

      {!loading && !error && result?.items.length === 0 && (
        <p className="anomaly-panel__empty" role="status">
          Nenhuma observação deste recorte ficou fora dos limites do IQR.
        </p>
      )}

      {!loading && !error && result && result.items.length > 0 && (
        <div className="anomaly-list">
          {result.items.map((anomaly) => (
            <article className="anomaly-card" key={anomaly.id}>
              <div className="anomaly-card__heading">
                <div>
                  <span>{directionLabel(anomaly)}</span>
                  <h3>{anomaly.product}</h3>
                </div>
                <strong>{formatPrice(anomaly.salePrice, anomaly.unit)}</strong>
              </div>
              <p>
                {anomaly.retailer} · {anomaly.municipality} —{" "}
                {anomaly.stateCode} · {formatDate(anomaly.collectionDate)}
              </p>
              <dl className="anomaly-card__limits">
                <div>
                  <dt>Limite inferior</dt>
                  <dd>{formatPrice(anomaly.lowerBound, anomaly.unit)}</dd>
                </div>
                <div>
                  <dt>Limite superior</dt>
                  <dd>{formatPrice(anomaly.upperBound, anomaly.unit)}</dd>
                </div>
                <div>
                  <dt>Referência</dt>
                  <dd>{anomaly.referenceObservationCount} observações</dd>
                </div>
              </dl>
              <p className="anomaly-card__reason">{anomaly.reason}</p>
              <small>Método {anomaly.detectionMethod}</small>
            </article>
          ))}
        </div>
      )}
    </section>
  );
}
