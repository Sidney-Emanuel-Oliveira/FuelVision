import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { LocationComparisonPoint } from "../types/api";
import { formatCompactPrice } from "../utils/formatters";

interface LocationComparisonChartProps {
  data: LocationComparisonPoint[];
}

export function LocationComparisonChart({
  data,
}: LocationComparisonChartProps) {
  return (
    <article className="chart-card">
      <div className="chart-card__heading">
        <div>
          <span className="eyebrow">Visão geográfica</span>
          <h2>Comparação entre estados</h2>
        </div>
        <span className="chart-card__meta">Preço médio por UF</span>
      </div>

      <div
        className="chart"
        role="img"
        aria-label="Gráfico de comparação do preço médio entre estados"
      >
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={data}
            margin={{ top: 8, right: 12, left: 0, bottom: 8 }}
          >
            <CartesianGrid
              strokeDasharray="4 4"
              stroke="#dfe7e5"
              vertical={false}
            />
            <XAxis
              dataKey="stateCode"
              tick={{ fill: "#526260", fontSize: 12 }}
            />
            <YAxis
              tickFormatter={formatCompactPrice}
              tick={{ fill: "#526260", fontSize: 12 }}
              width={54}
            />
            <Tooltip
              formatter={(value) => [
                `R$ ${formatCompactPrice(Number(value))}`,
                "Preço médio",
              ]}
              labelFormatter={(code) => {
                const state = data.find((item) => item.stateCode === code);
                return state
                  ? `${state.stateName} (${state.stateCode})`
                  : String(code);
              }}
            />
            <Bar
              dataKey="averageSalePrice"
              fill="#0b806f"
              radius={[7, 7, 0, 0]}
            />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <details className="data-details">
        <summary>Consultar dados do gráfico em tabela</summary>
        <div className="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>Estado</th>
                <th>Preço médio</th>
                <th>Observações</th>
              </tr>
            </thead>
            <tbody>
              {data.map((state) => (
                <tr key={state.stateCode}>
                  <td>
                    {state.stateName} ({state.stateCode})
                  </td>
                  <td>{formatCompactPrice(state.averageSalePrice)}</td>
                  <td>{state.observationCount}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </details>
    </article>
  );
}
