import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import App from "./App";
import * as api from "./api/fuelVisionApi";

vi.mock("./api/fuelVisionApi");
vi.mock("./components/PriceHistoryChart", () => ({
  PriceHistoryChart: () => <div>Evolução histórica</div>,
}));
vi.mock("./components/LocationComparisonChart", () => ({
  LocationComparisonChart: () => <div>Comparação entre estados</div>,
}));
vi.mock("./components/PredictionPanel", () => ({
  PredictionPanel: ({ selectedProduct }: { selectedProduct: string }) => (
    <div>Estimativa para {selectedProduct}</div>
  ),
}));

const summary = {
  product: "GNV",
  unit: "BRL/m3",
  observationCount: 12,
  averageSalePrice: 4.935,
  minimumSalePrice: 4.79,
  maximumSalePrice: 5.09,
  priceRange: 0.3,
  firstCollectionDate: "2026-01-01",
  lastCollectionDate: "2026-01-07",
};

const historyPoint = {
  collectionDate: "2026-01-07",
  product: "GNV",
  unit: "BRL/m3",
  observationCount: 2,
  averageSalePrice: 4.935,
  minimumSalePrice: 4.89,
  maximumSalePrice: 4.98,
  priceRange: 0.09,
};

describe("App", () => {
  beforeEach(() => {
    vi.mocked(api.getSummaries).mockResolvedValue([summary]);
    vi.mocked(api.getStates).mockResolvedValue([
      { code: "RJ", name: "RIO DE JANEIRO" },
    ]);
    vi.mocked(api.getCities).mockResolvedValue([
      { id: 1, name: "MACAE", stateCode: "RJ" },
    ]);
    vi.mocked(api.getHistory).mockResolvedValue({
      items: [historyPoint],
      totalItems: 1,
      totalPages: 1,
      page: 0,
      size: 100,
    });
    vi.mocked(api.getStateComparison).mockResolvedValue([
      {
        stateCode: "RJ",
        stateName: "RIO DE JANEIRO",
        averageSalePrice: 4.935,
        observationCount: 12,
      },
    ]);
  });

  it("apresenta carregamento e depois os indicadores reais da API", async () => {
    render(<App />);

    expect(screen.getByText("Preparando o painel")).toBeInTheDocument();
    expect(await screen.findByText("R$ 4,935/m³")).toBeInTheDocument();
    expect(await screen.findByText("Evolução histórica")).toBeInTheDocument();
    expect(
      await screen.findByText("Comparação entre estados"),
    ).toBeInTheDocument();
  });

  it("carrega municípios somente após a escolha do estado", async () => {
    const user = userEvent.setup();
    render(<App />);

    const stateSelect = await screen.findByLabelText("Estado");
    await user.selectOptions(stateSelect, "RJ");

    await waitFor(() =>
      expect(api.getCities).toHaveBeenCalledWith("RJ", expect.any(AbortSignal)),
    );
    expect(
      await screen.findByRole("option", { name: "MACAE" }),
    ).toBeInTheDocument();
  });

  it("informa quando a lista de municípios não pode ser carregada", async () => {
    vi.mocked(api.getCities).mockRejectedValueOnce(
      new Error("Serviço temporariamente indisponível."),
    );
    const user = userEvent.setup();
    render(<App />);

    await user.selectOptions(await screen.findByLabelText("Estado"), "RJ");

    expect(await screen.findByRole("alert")).toHaveTextContent(
      "Não foi possível carregar os municípios",
    );
  });

  it("impede a aplicação de um período invertido", async () => {
    render(<App />);

    await screen.findByText("R$ 4,935/m³");
    fireEvent.change(screen.getByLabelText("Data inicial"), {
      target: { value: "2026-01-08" },
    });
    fireEvent.change(screen.getByLabelText("Data final"), {
      target: { value: "2026-01-01" },
    });
    fireEvent.submit(
      screen.getByRole("button", { name: "Aplicar filtros" }).closest("form")!,
    );

    expect(
      screen.getByText("A data inicial não pode ser posterior à data final."),
    ).toBeInTheDocument();
  });

  it("mostra uma falha da API e permite tentar novamente", async () => {
    vi.mocked(api.getStates).mockRejectedValueOnce(
      new Error("Não foi possível acessar a API."),
    );
    const user = userEvent.setup();
    render(<App />);

    expect(await screen.findByRole("alert")).toHaveTextContent(
      "Não foi possível acessar a API.",
    );
    await user.click(screen.getByRole("button", { name: "Tentar novamente" }));

    expect(await screen.findByText("R$ 4,935/m³")).toBeInTheDocument();
  });

  it("diferencia resposta vazia de erro", async () => {
    vi.mocked(api.getSummaries).mockResolvedValueOnce([]);
    render(<App />);

    expect(
      await screen.findByText("Nenhum combustível disponível"),
    ).toBeInTheDocument();
    expect(screen.queryByRole("alert")).not.toBeInTheDocument();
  });
});
