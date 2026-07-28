import { useEffect, useRef, useState, type FormEvent } from "react";
import { getPredictionModel, requestPrediction } from "../api/fuelVisionApi";
import type { PredictionEstimate, PredictionModelInfo } from "../types/api";
import { formatDate, formatPrice } from "../utils/formatters";

interface PredictionPanelProps {
  selectedProduct: string;
}

function safeErrorMessage(error: unknown) {
  return error instanceof Error
    ? error.message
    : "Não foi possível concluir a estimativa.";
}

export function PredictionPanel({ selectedProduct }: PredictionPanelProps) {
  const initialSelectedProduct = useRef(selectedProduct);
  const [modelInfo, setModelInfo] = useState<PredictionModelInfo | null>(null);
  const [product, setProduct] = useState("");
  const [collectionDate, setCollectionDate] = useState("");
  const [estimate, setEstimate] = useState<PredictionEstimate | null>(null);
  const [modelLoading, setModelLoading] = useState(true);
  const [predictionLoading, setPredictionLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const controller = new AbortController();
    setModelLoading(true);
    getPredictionModel(controller.signal)
      .then((info) => {
        setModelInfo(info);
        setProduct(
          info.supportedProducts.includes(initialSelectedProduct.current)
            ? initialSelectedProduct.current
            : (info.supportedProducts[0] ?? ""),
        );
        setCollectionDate(info.predictionStart);
      })
      .catch((requestError: unknown) => {
        if (!(
          requestError instanceof DOMException &&
          requestError.name === "AbortError"
        )) {
          setError(safeErrorMessage(requestError));
        }
      })
      .finally(() => {
        if (!controller.signal.aborted) setModelLoading(false);
      });
    return () => controller.abort();
  }, []);

  useEffect(() => {
    if (modelInfo?.supportedProducts.includes(selectedProduct)) {
      setProduct(selectedProduct);
      setEstimate(null);
    }
  }, [modelInfo, selectedProduct]);

  function submitPrediction(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!product || !collectionDate) return;

    const controller = new AbortController();
    setPredictionLoading(true);
    setError(null);
    setEstimate(null);
    requestPrediction({ product, collectionDate }, controller.signal)
      .then(setEstimate)
      .catch((requestError: unknown) =>
        setError(safeErrorMessage(requestError)),
      )
      .finally(() => setPredictionLoading(false));
  }

  return (
    <section className="prediction-panel" aria-labelledby="prediction-title">
      <div className="prediction-panel__heading">
        <div>
          <span className="eyebrow">Estimativa experimental</span>
          <h2 id="prediction-title">Preço futuro por combustível</h2>
        </div>
        {modelInfo && (
          <span className="prediction-panel__version">
            Versão {modelInfo.modelVersion}
          </span>
        )}
      </div>

      <p className="prediction-panel__intro">
        Esta estimativa usa a média histórica do produto porque ela obteve erro
        menor que o Ridge no teste temporal. O resultado não é uma certeza.
      </p>

      {modelLoading && (
        <p role="status">Carregando informações do estimador…</p>
      )}
      {error && (
        <p className="prediction-panel__error" role="alert">
          {error}
        </p>
      )}

      {!modelLoading && modelInfo && (
        <>
          <form className="prediction-form" onSubmit={submitPrediction}>
            <label>
              Combustível para estimativa
              <select
                value={product}
                onChange={(event) => setProduct(event.target.value)}
                disabled={predictionLoading}
                required
              >
                {modelInfo.supportedProducts.map((supportedProduct) => (
                  <option key={supportedProduct} value={supportedProduct}>
                    {supportedProduct}
                  </option>
                ))}
              </select>
            </label>
            <label>
              Data da estimativa
              <input
                type="date"
                min={modelInfo.predictionStart}
                max={modelInfo.predictionEnd}
                value={collectionDate}
                onChange={(event) => setCollectionDate(event.target.value)}
                disabled={predictionLoading}
                required
              />
            </label>
            <button
              className="button button--primary"
              type="submit"
              disabled={predictionLoading}
            >
              {predictionLoading ? "Calculando…" : "Calcular estimativa"}
            </button>
          </form>

          <p className="prediction-panel__metadata">
            Treinado com {modelInfo.trainingRows} observações até{" "}
            {formatDate(modelInfo.trainingEnd)} · janela disponível de{" "}
            {formatDate(modelInfo.predictionStart)} a{" "}
            {formatDate(modelInfo.predictionEnd)} · MAE temporal{" "}
            {formatPrice(modelInfo.evaluationMae, modelInfo.unit)}
          </p>

          {estimate && (
            <div className="prediction-result" role="status">
              <span>Estimativa para {formatDate(estimate.collectionDate)}</span>
              <strong>
                {formatPrice(estimate.estimatedPrice, estimate.unit)}
              </strong>
              <p>{estimate.warning}</p>
              <small>
                Modelo {estimate.modelType} · treinado até{" "}
                {formatDate(estimate.trainedThrough)}
              </small>
            </div>
          )}
        </>
      )}
    </section>
  );
}
