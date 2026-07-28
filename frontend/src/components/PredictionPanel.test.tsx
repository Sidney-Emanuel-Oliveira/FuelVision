import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import * as api from "../api/fuelVisionApi";
import { PredictionPanel } from "./PredictionPanel";

vi.mock("../api/fuelVisionApi");

const modelInfo = {
  modelVersion: "product-mean-baseline-v1",
  modelType: "ProductMeanBaseline",
  unit: "BRL/liter",
  supportedProducts: ["ETANOL HIDRATADO", "GASOLINA COMUM"],
  trainingRows: 50,
  trainingStart: "2026-01-01",
  trainingEnd: "2026-01-02",
  predictionStart: "2026-01-03",
  predictionEnd: "2026-02-01",
  evaluationMae: 0.5271078431372549,
  ridgeEvaluationMae: 0.5719782379940552,
  ridgeBeatsBaseline: false,
  selectionReason: "Lower temporal test MAE.",
  warning: "Estimativa experimental; não é preço garantido.",
};

describe("PredictionPanel", () => {
  beforeEach(() => {
    vi.mocked(api.getPredictionModel).mockResolvedValue(modelInfo);
    vi.mocked(api.requestPrediction).mockResolvedValue({
      product: "GASOLINA COMUM",
      collectionDate: "2026-01-03",
      estimatedPrice: 6.077,
      unit: "BRL/liter",
      modelVersion: "product-mean-baseline-v1",
      modelType: "ProductMeanBaseline",
      trainedThrough: "2026-01-02",
      evaluationMae: 0.5271078431372549,
      warning: "Estimativa experimental; não é preço garantido.",
    });
  });

  it("usa o produto atual quando ele é aceito pelo estimador", async () => {
    render(<PredictionPanel selectedProduct="GASOLINA COMUM" />);

    expect(
      await screen.findByLabelText("Combustível para estimativa"),
    ).toHaveValue("GASOLINA COMUM");
    expect(
      screen.getByText(/Versão product-mean-baseline-v1/),
    ).toBeInTheDocument();
    expect(screen.getByText(/MAE temporal/)).toBeInTheDocument();
  });

  it("calcula e identifica explicitamente uma estimativa", async () => {
    const user = userEvent.setup();
    render(<PredictionPanel selectedProduct="GASOLINA COMUM" />);

    await user.click(
      await screen.findByRole("button", { name: "Calcular estimativa" }),
    );

    expect(api.requestPrediction).toHaveBeenCalledWith(
      { product: "GASOLINA COMUM", collectionDate: "2026-01-03" },
      expect.any(AbortSignal),
    );
    expect(await screen.findByText(/6,077\/L/)).toBeInTheDocument();
    expect(screen.getByText(/não é preço garantido/)).toBeInTheDocument();
  });

  it("restringe a data à janela informada pelo modelo", async () => {
    render(<PredictionPanel selectedProduct="ETANOL HIDRATADO" />);

    const dateInput = await screen.findByLabelText("Data da estimativa");
    expect(dateInput).toHaveAttribute("min", "2026-01-03");
    expect(dateInput).toHaveAttribute("max", "2026-02-01");
  });

  it("mantém a análise disponível quando o serviço de estimativa falha", async () => {
    vi.mocked(api.getPredictionModel).mockRejectedValueOnce(
      new Error("Serviço de estimativas indisponível."),
    );

    render(<PredictionPanel selectedProduct="GASOLINA COMUM" />);

    expect(await screen.findByRole("alert")).toHaveTextContent(
      "Serviço de estimativas indisponível.",
    );
  });
});
