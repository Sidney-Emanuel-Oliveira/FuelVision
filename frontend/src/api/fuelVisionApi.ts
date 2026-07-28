import type {
  CityLocation,
  LocationComparisonPoint,
  PageResponse,
  PredictionEstimate,
  PredictionModelInfo,
  PredictionRequest,
  PriceFilters,
  PriceHistoryPoint,
  PriceSummary,
  StateLocation,
} from "../types/api";

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL ?? "").replace(
  /\/$/,
  "",
);

type FilterParameters = Partial<PriceFilters>;

export class ApiError extends Error {
  readonly status: number | undefined;

  constructor(message: string, status?: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

function buildQuery(parameters: Record<string, string | number | undefined>) {
  const query = new URLSearchParams();

  Object.entries(parameters).forEach(([key, value]) => {
    if (value !== undefined && value !== "") {
      query.set(key, String(value));
    }
  });

  const serialized = query.toString();
  return serialized ? `?${serialized}` : "";
}

async function request<T>(
  path: string,
  signal?: AbortSignal,
  options: RequestInit = {},
): Promise<T> {
  let response: Response;

  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      ...options,
      headers: { Accept: "application/json", ...options.headers },
      signal,
    });
  } catch (error) {
    if (error instanceof DOMException && error.name === "AbortError") {
      throw error;
    }
    throw new ApiError(
      "Não foi possível acessar a API. Confirme se o Back-end está em execução.",
    );
  }

  if (!response.ok) {
    const problem = (await response.json().catch(() => null)) as {
      detail?: string;
    } | null;
    throw new ApiError(
      problem?.detail ?? "A API não conseguiu concluir a consulta.",
      response.status,
    );
  }

  return response.json() as Promise<T>;
}

export function getPredictionModel(signal?: AbortSignal) {
  return request<PredictionModelInfo>("/api/predictions/model", signal);
}

export function requestPrediction(
  prediction: PredictionRequest,
  signal?: AbortSignal,
) {
  return request<PredictionEstimate>("/api/predictions", signal, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(prediction),
  });
}

export function getSummaries(filters: FilterParameters, signal?: AbortSignal) {
  return request<PriceSummary[]>(
    `/api/prices/summary${buildQuery(filters)}`,
    signal,
  );
}

export function getHistory(filters: FilterParameters, signal?: AbortSignal) {
  return request<PageResponse<PriceHistoryPoint>>(
    `/api/prices/history${buildQuery({ ...filters, page: 0, size: 100 })}`,
    signal,
  );
}

export function getStates(signal?: AbortSignal) {
  return request<StateLocation[]>("/api/locations/states", signal);
}

export function getCities(state: string, signal?: AbortSignal) {
  return request<CityLocation[]>(
    `/api/locations/cities${buildQuery({ state })}`,
    signal,
  );
}

export async function getStateComparison(
  states: StateLocation[],
  filters: FilterParameters,
  signal?: AbortSignal,
): Promise<LocationComparisonPoint[]> {
  const summaries = await Promise.all(
    states.map(async (state) => {
      const [summary] = await getSummaries(
        { ...filters, state: state.code, municipality: "" },
        signal,
      );
      return summary
        ? {
            stateCode: state.code,
            stateName: state.name,
            averageSalePrice: summary.averageSalePrice,
            observationCount: summary.observationCount,
          }
        : null;
    }),
  );

  return summaries.filter(
    (summary): summary is LocationComparisonPoint => summary !== null,
  );
}
