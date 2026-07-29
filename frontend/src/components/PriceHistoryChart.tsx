import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { PriceHistoryPoint } from "../types/api";
import { formatCompactPrice, formatDate } from "../utils/formatters";

interface PriceHistoryChartProps {
  data: PriceHistoryPoint[];
}

export function PriceHistoryChart({ data }: PriceHistoryChartProps) {
  return (
    <article className="chart-card">
      <div className="chart-card__heading">
        <div>
          <span className="eyebrow">Comportamento no tempo</span>
          <h2>Evolução histórica</h2>
        </div>
        <span className="chart-card__meta">{data.length} pontos diários</span>
      </div>

      <div
        className="chart"
        role="img"
        aria-label="Gráfico de evolução histórica dos preços"
      >
        <ResponsiveContainer width="100%" height="100%">
          <LineChart
            data={data}
            margin={{ top: 8, right: 12, left: 0, bottom: 8 }}
          >
            <CartesianGrid strokeDasharray="4 4" stroke="#dfe7e5" />
            <XAxis
              dataKey="collectionDate"
              tickFormatter={formatDate}
              tick={{ fill: "#526260", fontSize: 12 }}
            />
            <YAxis
              tickFormatter={formatCompactPrice}
              tick={{ fill: "#526260", fontSize: 12 }}
              width={54}
            />
            <Tooltip
              labelFormatter={(label) => formatDate(String(label))}
              formatter={(value, name) => [
                `R$ ${formatCompactPrice(Number(value))}`,
                name,
              ]}
            />
            <Legend />
            <Line
              type="monotone"
              dataKey="averageSalePrice"
              name="Preço médio"
              stroke="#0b806f"
              strokeWidth={3}
              dot={{ r: 3 }}
              activeDot={{ r: 5 }}
            />
            <Line
              type="monotone"
              dataKey="minimumSalePrice"
              name="Preço mínimo"
              stroke="#e19a22"
              strokeWidth={2}
              dot={false}
            />
            <Line
              type="monotone"
              dataKey="maximumSalePrice"
              name="Preço máximo"
              stroke="#d96459"
              strokeWidth={2}
              dot={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <details className="data-details">
        <summary>Consultar dados do gráfico em tabela</summary>
        <div className="table-wrapper">
          <table>
            <thead>
              <tr>
                <th scope="col">Data</th>
                <th scope="col">Médio</th>
                <th scope="col">Mínimo</th>
                <th scope="col">Máximo</th>
                <th scope="col">Observações</th>
              </tr>
            </thead>
            <tbody>
              {data.map((point) => (
                <tr key={`${point.collectionDate}-${point.product}`}>
                  <td>{formatDate(point.collectionDate)}</td>
                  <td>{formatCompactPrice(point.averageSalePrice)}</td>
                  <td>{formatCompactPrice(point.minimumSalePrice)}</td>
                  <td>{formatCompactPrice(point.maximumSalePrice)}</td>
                  <td>{point.observationCount}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </details>
    </article>
  );
}
