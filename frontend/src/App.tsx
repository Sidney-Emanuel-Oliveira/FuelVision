import { lazy, Suspense, useEffect, useMemo, useState } from "react";
import "./App.css";
import {
  getCities,
  getHistory,
  getStateComparison,
  getStates,
  getSummaries,
} from "./api/fuelVisionApi";
import { DashboardFilters } from "./components/DashboardFilters";
import { AnomalyPanel } from "./components/AnomalyPanel";
import { MetricCard } from "./components/MetricCard";
import { PredictionPanel } from "./components/PredictionPanel";
import { StatusPanel } from "./components/StatusPanel";
import type {
  CityLocation,
  LocationComparisonPoint,
  PriceFilters,
  PriceHistoryPoint,
  PriceSummary,
  StateLocation,
} from "./types/api";
import { formatDate, formatPrice } from "./utils/formatters";

const PriceHistoryChart = lazy(() =>
  import("./components/PriceHistoryChart").then((module) => ({
    default: module.PriceHistoryChart,
  })),
);
const LocationComparisonChart = lazy(() =>
  import("./components/LocationComparisonChart").then((module) => ({
    default: module.LocationComparisonChart,
  })),
);

const EMPTY_FILTERS: PriceFilters = {
  product: "",
  state: "",
  municipality: "",
  startDate: "",
  endDate: "",
};

function errorMessage(error: unknown) {
  return error instanceof Error
    ? error.message
    : "Ocorreu um erro inesperado ao carregar os dados.";
}

function isAbortError(error: unknown) {
  return error instanceof DOMException && error.name === "AbortError";
}

export default function App() {
  const [draftFilters, setDraftFilters] = useState(EMPTY_FILTERS);
  const [appliedFilters, setAppliedFilters] = useState(EMPTY_FILTERS);
  const [products, setProducts] = useState<string[]>([]);
  const [states, setStates] = useState<StateLocation[]>([]);
  const [cities, setCities] = useState<CityLocation[]>([]);
  const [summary, setSummary] = useState<PriceSummary | null>(null);
  const [history, setHistory] = useState<PriceHistoryPoint[]>([]);
  const [comparison, setComparison] = useState<LocationComparisonPoint[]>([]);
  const [optionsLoading, setOptionsLoading] = useState(true);
  const [citiesLoading, setCitiesLoading] = useState(false);
  const [dashboardLoading, setDashboardLoading] = useState(false);
  const [optionsError, setOptionsError] = useState<string | null>(null);
  const [citiesError, setCitiesError] = useState<string | null>(null);
  const [dashboardError, setDashboardError] = useState<string | null>(null);
  const [validationError, setValidationError] = useState<string | null>(null);
  const [optionsAttempt, setOptionsAttempt] = useState(0);
  const [dashboardAttempt, setDashboardAttempt] = useState(0);

  useEffect(() => {
    const controller = new AbortController();
    setOptionsLoading(true);
    setOptionsError(null);

    Promise.all([
      getSummaries({}, controller.signal),
      getStates(controller.signal),
    ])
      .then(([availableSummaries, availableStates]) => {
        const availableProducts = availableSummaries.map(
          (item) => item.product,
        );
        const firstProduct = availableProducts[0] ?? "";
        const initialFilters = { ...EMPTY_FILTERS, product: firstProduct };
        setProducts(availableProducts);
        setStates(availableStates);
        setDraftFilters(initialFilters);
        setAppliedFilters(initialFilters);
      })
      .catch((error: unknown) => {
        if (!isAbortError(error)) setOptionsError(errorMessage(error));
      })
      .finally(() => {
        if (!controller.signal.aborted) setOptionsLoading(false);
      });

    return () => controller.abort();
  }, [optionsAttempt]);

  useEffect(() => {
    if (!draftFilters.state) {
      setCities([]);
      setCitiesLoading(false);
      setCitiesError(null);
      return;
    }

    const controller = new AbortController();
    setCitiesLoading(true);
    setCitiesError(null);
    getCities(draftFilters.state, controller.signal)
      .then(setCities)
      .catch((error: unknown) => {
        if (!isAbortError(error)) {
          setCities([]);
          setCitiesError(errorMessage(error));
        }
      })
      .finally(() => {
        if (!controller.signal.aborted) setCitiesLoading(false);
      });

    return () => controller.abort();
  }, [draftFilters.state]);

  useEffect(() => {
    if (!appliedFilters.product || states.length === 0) return;

    const controller = new AbortController();
    setDashboardLoading(true);
    setDashboardError(null);

    Promise.all([
      getSummaries(appliedFilters, controller.signal),
      getHistory(appliedFilters, controller.signal),
      getStateComparison(states, appliedFilters, controller.signal),
    ])
      .then(([summaries, historyPage, comparisonData]) => {
        setSummary(summaries[0] ?? null);
        setHistory(historyPage.items);
        setComparison(comparisonData);
      })
      .catch((error: unknown) => {
        if (!isAbortError(error)) {
          setDashboardError(errorMessage(error));
          setSummary(null);
          setHistory([]);
          setComparison([]);
        }
      })
      .finally(() => {
        if (!controller.signal.aborted) setDashboardLoading(false);
      });

    return () => controller.abort();
  }, [appliedFilters, states, dashboardAttempt]);

  const scopeLabel = useMemo(() => {
    const location = appliedFilters.municipality
      ? `${appliedFilters.municipality} — ${appliedFilters.state}`
      : appliedFilters.state || "Brasil disponível na amostra";
    return `${appliedFilters.product || "Combustível"} · ${location}`;
  }, [appliedFilters]);

  function applyFilters() {
    if (
      draftFilters.startDate &&
      draftFilters.endDate &&
      draftFilters.startDate > draftFilters.endDate
    ) {
      setValidationError("A data inicial não pode ser posterior à data final.");
      return;
    }
    setValidationError(null);
    setAppliedFilters({ ...draftFilters });
  }

  function clearOptionalFilters() {
    const cleared = { ...EMPTY_FILTERS, product: draftFilters.product };
    setDraftFilters(cleared);
    setValidationError(null);
  }

  return (
    <div className="app-shell">
      <a className="skip-link" href="#main-content">
        Pular para o conteúdo principal
      </a>
      <header className="topbar">
        <a className="brand" href="/" title="Página inicial">
          <span className="brand__mark">FV</span>
          <span>
            <strong>FuelVision</strong>
            <small>Inteligência sobre combustíveis</small>
          </span>
        </a>
        <span className="data-badge">Amostra pública · ANP</span>
      </header>

      <main id="main-content" tabIndex={-1}>
        <section className="hero">
          <div>
            <span className="eyebrow eyebrow--light">Painel analítico</span>
            <h1>Preços de combustíveis sob uma nova perspectiva.</h1>
            <p>
              Explore indicadores e diferenças regionais calculados pela API do
              FuelVision sobre a amostra disponível.
            </p>
          </div>
          <div className="hero__scope">
            <span>Recorte atual</span>
            <strong>{scopeLabel}</strong>
          </div>
        </section>

        {optionsLoading && (
          <StatusPanel
            kind="loading"
            title="Preparando o painel"
            message="Buscando combustíveis e localidades disponíveis na API."
          />
        )}

        {optionsError && (
          <StatusPanel
            kind="error"
            title="Não foi possível iniciar o painel"
            message={optionsError}
            onRetry={() => setOptionsAttempt((attempt) => attempt + 1)}
          />
        )}

        {!optionsLoading && !optionsError && products.length === 0 && (
          <StatusPanel
            kind="empty"
            title="Nenhum combustível disponível"
            message="A API respondeu corretamente, mas ainda não possui observações para exibir."
          />
        )}

        {!optionsLoading && !optionsError && products.length > 0 && (
          <>
            <DashboardFilters
              filters={draftFilters}
              products={products}
              states={states}
              cities={cities}
              citiesLoading={citiesLoading}
              disabled={dashboardLoading}
              onChange={setDraftFilters}
              onSubmit={applyFilters}
              onClear={clearOptionalFilters}
            />
            {validationError && (
              <p className="validation-error" role="alert">
                {validationError}
              </p>
            )}
            {citiesError && (
              <p className="validation-error" role="alert">
                Não foi possível carregar os municípios: {citiesError}
              </p>
            )}

            {dashboardLoading && (
              <StatusPanel
                kind="loading"
                title="Atualizando indicadores"
                message="Consultando resumo, histórico e comparação regional."
              />
            )}

            {!dashboardLoading && dashboardError && (
              <StatusPanel
                kind="error"
                title="Falha ao atualizar os indicadores"
                message={dashboardError}
                onRetry={() => setDashboardAttempt((attempt) => attempt + 1)}
              />
            )}

            {!dashboardLoading && !dashboardError && !summary && (
              <StatusPanel
                kind="empty"
                title="Nenhuma observação encontrada"
                message="Altere a localidade ou o período para ampliar a consulta."
              />
            )}

            {!dashboardLoading && !dashboardError && summary && (
              <section className="dashboard" aria-label="Resultados do painel">
                <div className="dashboard__intro">
                  <div>
                    <span className="eyebrow">Indicadores do recorte</span>
                    <h2>{summary.product}</h2>
                  </div>
                  <p>
                    {summary.observationCount} observações entre{" "}
                    {formatDate(summary.firstCollectionDate)} e{" "}
                    {formatDate(summary.lastCollectionDate)}
                  </p>
                </div>

                <div className="metrics-grid">
                  <MetricCard
                    label="Preço médio"
                    value={formatPrice(summary.averageSalePrice, summary.unit)}
                    detail="Média das observações filtradas"
                    accent="mint"
                  />
                  <MetricCard
                    label="Preço mínimo"
                    value={formatPrice(summary.minimumSalePrice, summary.unit)}
                    detail="Menor preço observado"
                    accent="amber"
                  />
                  <MetricCard
                    label="Preço máximo"
                    value={formatPrice(summary.maximumSalePrice, summary.unit)}
                    detail="Maior preço observado"
                    accent="coral"
                  />
                </div>

                <PredictionPanel selectedProduct={summary.product} />

                <AnomalyPanel filters={appliedFilters} />

                <Suspense
                  fallback={
                    <StatusPanel
                      kind="loading"
                      title="Preparando visualizações"
                      message="Carregando os componentes dos gráficos."
                    />
                  }
                >
                  {history.length > 0 ? (
                    <PriceHistoryChart data={history} />
                  ) : (
                    <StatusPanel
                      kind="empty"
                      title="Histórico vazio"
                      message="Não há pontos diários para esse recorte."
                    />
                  )}

                  {comparison.length > 0 ? (
                    <LocationComparisonChart data={comparison} />
                  ) : (
                    <StatusPanel
                      kind="empty"
                      title="Comparação indisponível"
                      message="Nenhum estado possui observações para esse combustível e período."
                    />
                  )}
                </Suspense>
              </section>
            )}
          </>
        )}
      </main>

      <footer>
        <p>FuelVision · Projeto educacional com dados públicos da ANP.</p>
        <p>
          Os resultados descrevem somente a amostra carregada e não representam
          todo o mercado.
        </p>
      </footer>
    </div>
  );
}
