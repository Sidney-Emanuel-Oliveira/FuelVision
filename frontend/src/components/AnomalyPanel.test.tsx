import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import * as api from "../api/fuelVisionApi";
import type { PriceFilters } from "../types/api";
import { AnomalyPanel } from "./AnomalyPanel";

vi.mock("../api/fuelVisionApi");

const filters: PriceFilters = {
  product: "GASOLINA COMUM",
  state: "AC",
  municipality: "",
  startDate: "",
  endDate: "",
};

const anomaly = {
  id: 1,
  collectionDate: "2026-01-02",
  salePrice: 7.97,
  product: "GASOLINA COMUM",
  unit: "BRL/liter",
  retailer: "REVENDA EXEMPLO",
  stateCode: "AC",
  municipality: "CRUZEIRO DO SUL",
  referenceObservationCount: 10,
  firstQuartile: 6.2825,
  thirdQuartile: 6.59,
  interquartileRange: 0.3075,
  lowerBound: 5.82125,
  upperBound: 7.05125,
  direction: "ABOVE_EXPECTED_RANGE" as const,
  detectionMethod: "IQR_1_5" as const,
  reason:
    "Preço acima do limite superior calculado pelo método IQR. " +
    "Comportamento estatisticamente atípico que merece análise.",
};

describe("AnomalyPanel", () => {
  beforeEach(() => {
    vi.mocked(api.getAnomalies).mockResolvedValue({
      items: [anomaly],
      totalItems: 1,
      totalPages: 1,
      page: 0,
      size: 20,
    });
  });

  it("consulta o recorte e explica o alerta sem acusação", async () => {
    render(<AnomalyPanel filters={filters} />);

    expect(await screen.findByText("R$ 7,970/L")).toBeInTheDocument();
    expect(screen.getByText("Acima do intervalo esperado")).toBeInTheDocument();
    expect(screen.getAllByText(/estatisticamente atípico/)).toHaveLength(2);
    expect(screen.getByText("10 observações")).toBeInTheDocument();
    expect(screen.getByText("Método IQR_1_5")).toBeInTheDocument();
    expect(api.getAnomalies).toHaveBeenCalledWith(
      filters,
      expect.any(AbortSignal),
    );
  });

  it("diferencia um recorte sem alertas de uma falha", async () => {
    vi.mocked(api.getAnomalies).mockResolvedValueOnce({
      items: [],
      totalItems: 0,
      totalPages: 0,
      page: 0,
      size: 20,
    });

    render(<AnomalyPanel filters={filters} />);

    expect(await screen.findByText(/Nenhuma observação/)).toBeInTheDocument();
    expect(screen.queryByRole("alert")).not.toBeInTheDocument();
  });

  it("isola a falha e permite tentar novamente", async () => {
    vi.mocked(api.getAnomalies)
      .mockRejectedValueOnce(
        new Error("Consulta temporariamente indisponível."),
      )
      .mockResolvedValueOnce({
        items: [anomaly],
        totalItems: 1,
        totalPages: 1,
        page: 0,
        size: 20,
      });
    const user = userEvent.setup();

    render(<AnomalyPanel filters={filters} />);

    expect(await screen.findByRole("alert")).toHaveTextContent(
      "Consulta temporariamente indisponível.",
    );
    await user.click(screen.getByRole("button", { name: "Tentar novamente" }));
    expect(await screen.findByText("R$ 7,970/L")).toBeInTheDocument();
  });
});
