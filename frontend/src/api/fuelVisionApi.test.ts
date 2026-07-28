import {
  ApiError,
  getCities,
  getHistory,
  getStateComparison,
  getSummaries,
} from "./fuelVisionApi";
import { afterEach, describe, expect, it, vi } from "vitest";

function jsonResponse(data: unknown, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

describe("fuelVisionApi", () => {
  afterEach(() => vi.restoreAllMocks());

  it("codifica filtros e paginação no histórico", async () => {
    const fetchMock = vi
      .spyOn(globalThis, "fetch")
      .mockResolvedValue(jsonResponse({ items: [], totalItems: 0 }));

    await getHistory({ product: "GASOLINA COMUM", municipality: "SÃO PAULO" });

    expect(fetchMock).toHaveBeenCalledWith(
      "/api/prices/history?product=GASOLINA+COMUM&municipality=S%C3%83O+PAULO&page=0&size=100",
      expect.objectContaining({ headers: { Accept: "application/json" } }),
    );
  });

  it("consulta municípios usando a UF selecionada", async () => {
    const fetchMock = vi
      .spyOn(globalThis, "fetch")
      .mockResolvedValue(jsonResponse([]));

    await getCities("RJ");

    expect(fetchMock).toHaveBeenCalledWith(
      "/api/locations/cities?state=RJ",
      expect.any(Object),
    );
  });

  it("preserva a mensagem segura devolvida pela API", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(
      jsonResponse({ detail: "O período informado é inválido." }, 400),
    );

    await expect(getSummaries({ startDate: "2026-02-01" })).rejects.toEqual(
      new ApiError("O período informado é inválido.", 400),
    );
  });

  it("explica quando o back-end não pode ser acessado", async () => {
    vi.spyOn(globalThis, "fetch").mockRejectedValue(
      new TypeError("fetch failed"),
    );

    await expect(getSummaries({})).rejects.toThrow(
      "Confirme se o Back-end está em execução",
    );
  });

  it("remove estados sem resumo da comparação", async () => {
    vi.spyOn(globalThis, "fetch")
      .mockResolvedValueOnce(
        jsonResponse([
          {
            averageSalePrice: 5.4,
            observationCount: 8,
          },
        ]),
      )
      .mockResolvedValueOnce(jsonResponse([]));

    const comparison = await getStateComparison(
      [
        { code: "RJ", name: "RIO DE JANEIRO" },
        { code: "SP", name: "SÃO PAULO" },
      ],
      { product: "ETANOL" },
    );

    expect(comparison).toEqual([
      {
        stateCode: "RJ",
        stateName: "RIO DE JANEIRO",
        averageSalePrice: 5.4,
        observationCount: 8,
      },
    ]);
  });
});
