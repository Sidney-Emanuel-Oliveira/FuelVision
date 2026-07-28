import type { FormEvent } from "react";
import type { CityLocation, PriceFilters, StateLocation } from "../types/api";

interface DashboardFiltersProps {
  filters: PriceFilters;
  products: string[];
  states: StateLocation[];
  cities: CityLocation[];
  citiesLoading: boolean;
  disabled: boolean;
  onChange: (filters: PriceFilters) => void;
  onSubmit: () => void;
  onClear: () => void;
}

export function DashboardFilters({
  filters,
  products,
  states,
  cities,
  citiesLoading,
  disabled,
  onChange,
  onSubmit,
  onClear,
}: DashboardFiltersProps) {
  function updateFilter(field: keyof PriceFilters, value: string) {
    const next = { ...filters, [field]: value };
    if (field === "state") next.municipality = "";
    onChange(next);
  }

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    onSubmit();
  }

  return (
    <form className="filters" onSubmit={submit}>
      <div className="filters__heading">
        <div>
          <span className="eyebrow">Refine a análise</span>
          <h2>Filtros</h2>
        </div>
        <button className="text-button" type="button" onClick={onClear}>
          Limpar localização e período
        </button>
      </div>

      <div className="filters__grid">
        <label>
          Combustível
          <select
            value={filters.product}
            onChange={(event) => updateFilter("product", event.target.value)}
            required
          >
            <option value="" disabled>
              Selecione
            </option>
            {products.map((product) => (
              <option key={product} value={product}>
                {product}
              </option>
            ))}
          </select>
        </label>

        <label>
          Estado
          <select
            value={filters.state}
            onChange={(event) => updateFilter("state", event.target.value)}
          >
            <option value="">Todos os estados</option>
            {states.map((state) => (
              <option key={state.code} value={state.code}>
                {state.code} — {state.name}
              </option>
            ))}
          </select>
        </label>

        <label>
          Município
          <select
            value={filters.municipality}
            onChange={(event) =>
              updateFilter("municipality", event.target.value)
            }
            disabled={!filters.state || citiesLoading}
          >
            <option value="">
              {citiesLoading ? "Carregando..." : "Todos os municípios"}
            </option>
            {cities.map((city) => (
              <option key={city.id} value={city.name}>
                {city.name}
              </option>
            ))}
          </select>
        </label>

        <label>
          Data inicial
          <input
            type="date"
            value={filters.startDate}
            max={filters.endDate || undefined}
            onChange={(event) => updateFilter("startDate", event.target.value)}
          />
        </label>

        <label>
          Data final
          <input
            type="date"
            value={filters.endDate}
            min={filters.startDate || undefined}
            onChange={(event) => updateFilter("endDate", event.target.value)}
          />
        </label>

        <button
          className="button button--primary"
          type="submit"
          disabled={disabled}
        >
          {disabled ? "Atualizando..." : "Aplicar filtros"}
        </button>
      </div>
    </form>
  );
}
