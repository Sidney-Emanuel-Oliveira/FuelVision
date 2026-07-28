# Análises e consultas SQL

## 1. Propósito

O Módulo 5 transforma observações armazenadas em indicadores descritivos reutilizáveis. As consultas respondem perguntas como:

- quantas observações existem para cada produto;
- qual foi a média, o mínimo e o máximo observado;
- como os grupos da amostra se distribuem por estado e município;
- quais indicadores aparecem em cada data disponível;
- como restringir a análise por produto, localidade e período.

Esses resultados descrevem somente a amostra controlada de 60 registros. Eles não estimam o preço do Brasil, não medem causalidade e não representam Big Data.

## 2. Conceitos

### Agregação

**Agregação** reúne várias linhas e produz um valor resumido. `avg(sale_price)` calcula a média dos preços pertencentes ao grupo atual. No FuelVision, as agregações sempre mantêm produto e unidade para não misturar combustível por litro com GNV por metro cúbico.

### Agrupamento

**GROUP BY** define quais linhas pertencem ao mesmo grupo. Agrupar por produto gera seis grupos na amostra; agrupar também por estado gera 39 grupos.

### Filtro

**Filtro** seleciona linhas antes do cálculo. `WHERE state_code = 'RJ'` faz com que apenas observações relacionadas ao Rio de Janeiro participem dos indicadores.

### Indicador

**Indicador** é uma medida resumida usada para responder uma pergunta definida. O módulo utiliza:

- `observation_count`: quantidade de observações;
- `average_sale_price`: média aritmética;
- `minimum_sale_price`: menor valor observado;
- `maximum_sale_price`: maior valor observado;
- `price_range`: máximo menos mínimo;
- primeira e última datas, quando aplicável.

### View

**View** é uma consulta salva com nome. Ela não copia as observações: executa a consulta sobre as tabelas atuais. Isso permite reutilizar o mesmo contrato em relatórios futuros sem duplicar SQL.

## 3. Views criadas

| View                         | Grupo principal     | Pergunta respondida                               |
| ---------------------------- | ------------------- | ------------------------------------------------- |
| `product_price_summary`      | produto             | quais indicadores aparecem por combustível?       |
| `state_price_summary`        | estado + produto    | como os grupos estaduais da amostra se comparam?  |
| `municipality_price_summary` | município + produto | como os grupos municipais da amostra se comparam? |
| `daily_price_history`        | data + produto      | quais indicadores aparecem em cada data?          |

As quatro views incluem produto, unidade, quantidade, média, mínimo, máximo e amplitude. A view por produto também apresenta a primeira e a última data.

## 4. Fluxo

```text
price_observations
→ JOIN com produto e localização
→ WHERE opcional
→ GROUP BY
→ count / avg / min / max
→ ordenação
→ relatório ou view reutilizável
```

O filtro ocorre antes da agregação. Portanto, a média de um recorte é recalculada somente com as linhas que permaneceram.

## 5. Arquivos

### `004_create_analytics_views.sql`

Cria ou atualiza as quatro views. `CREATE OR REPLACE VIEW` permite repetir o comando sem acumular objetos duplicados.

### `005_analysis_report.sql`

Cria uma view temporária com os filtros recebidos e produz quatro blocos de relatório. A view temporária desaparece quando a conexão termina.

### `006_validate_analytics.sql`

Compara contagens agregadas com a tabela-base, confere limites matemáticos e verifica o intervalo de datas. Uma divergência interrompe a execução.

### Scripts Shell

- `create_analytics_views.sh`: publica as views no banco local;
- `run_analytics.sh`: interpreta filtros e executa o relatório;
- `validate_analytics.sh`: executa as verificações SQL.

## 6. Como executar

Crie as views:

```bash
database/scripts/create_analytics_views.sh
```

Valide os resultados:

```bash
database/scripts/validate_analytics.sh
```

Execute o relatório completo:

```bash
database/scripts/run_analytics.sh
```

## 7. Filtros

Os filtros são opcionais e podem ser combinados:

```bash
database/scripts/run_analytics.sh \
  --product GNV \
  --state RJ \
  --municipality MACAE \
  --start-date 2026-01-01 \
  --end-date 2026-01-07
```

Opções:

- `--product`: nome canônico do produto;
- `--state`: sigla da UF;
- `--municipality`: município;
- `--start-date`: início inclusivo em `AAAA-MM-DD`;
- `--end-date`: fim inclusivo em `AAAA-MM-DD`.

Produto usa o nome canônico do banco. Estado e município são convertidos para maiúsculas pela consulta. Uma data inválida é rejeitada pelo PostgreSQL.

## 8. Resultados reais por produto

| Produto            | Unidade   | N   | Média | Mínimo | Máximo | Amplitude |
| ------------------ | --------- | --- | ----- | ------ | ------ | --------- |
| Etanol hidratado   | BRL/liter | 10  | 4,734 | 4,290  | 5,240  | 0,950     |
| Gasolina aditivada | BRL/liter | 10  | 6,696 | 6,290  | 7,390  | 1,100     |
| Gasolina comum     | BRL/liter | 10  | 6,594 | 5,960  | 7,970  | 2,010     |
| GNV                | BRL/m3    | 10  | 4,489 | 3,990  | 4,990  | 1,000     |
| Óleo diesel        | BRL/liter | 10  | 6,228 | 5,750  | 8,150  | 2,400     |
| Óleo diesel S10    | BRL/liter | 10  | 6,305 | 5,690  | 8,170  | 2,480     |

`N` é a quantidade de observações do grupo. A igualdade de dez registros por produto foi construída na amostra e não representa a distribuição da fonte completa.

Os valores de GNV não devem ser comparados numericamente com os produtos em litro sem converter unidades e definir uma pergunta válida.

## 9. Resultado real do filtro demonstrado

Filtro:

```text
produto = GNV
estado = RJ
município = MACAE
período = 2026-01-01 a 2026-01-07
```

Resultado:

| N   | Média | Mínimo | Máximo | Amplitude |
| --- | ----- | ------ | ------ | --------- |
| 2   | 4,935 | 4,880  | 4,990  | 0,110     |

Esse resultado descreve somente duas observações de Macaé presentes na amostra. Ele não representa todo o município nem permite afirmar tendência.

## 10. Comparações por localidade

Foram produzidos:

- 39 grupos por estado + produto;
- 42 grupos por município + produto.

Muitos grupos possuem apenas uma ou duas observações. Uma média com `N = 1` é igual ao próprio valor observado e não mede variação do grupo. Por isso, sempre leia `observation_count` junto com média, mínimo e máximo.

Ordenar médias não transforma a primeira linha em “melhor estado” ou “cidade mais barata”. A amostra não é representativa, os períodos e revendas podem diferir e os grupos têm tamanhos pequenos.

## 11. Evolução temporal

A view diária gerou 14 combinações de data + produto entre `2026-01-01` e `2026-01-07`. Existem datas sem observações e produtos que não aparecem em todos os dias.

Uma mudança na média diária pode ocorrer porque o conjunto de localidades e revendas mudou. Portanto, a consulta mostra **evolução dos registros disponíveis**, não uma série temporal representativa do mercado.

## 12. Validação

O comando `validate_analytics.sh` confirmou:

- 60 observações na tabela-base;
- soma das contagens igual a 60 em cada perspectiva;
- 6 grupos de produto;
- 39 grupos de estado + produto;
- 42 grupos de município + produto;
- 14 grupos de data + produto;
- média sempre entre mínimo e máximo;
- amplitude sempre igual a máximo menos mínimo;
- datas mínima e máxima preservadas.

Os testes automatizados também verificam os valores conhecidos de gasolina comum, GNV e o filtro de Macaé.

## 13. Decisões

### Views comuns em vez de materializadas

- escolha: views comuns;
- vantagem: refletem os dados atuais sem processo de atualização;
- desvantagem: recalculam a consulta a cada uso;
- motivo: existem apenas 60 observações e ainda não há problema de desempenho demonstrado.

### SQL em vez de ferramenta de BI

- escolha: SQL e `psql`;
- vantagem: ensina agrupamento, filtro e agregação diretamente;
- desvantagem: não há gráfico neste módulo;
- motivo: dashboard e ferramentas adicionais pertencem a etapas posteriores.

### Média com três casas decimais

- escolha: `round(avg(...), 3)`;
- vantagem: acompanha a precisão do tipo `numeric(10, 3)`;
- desvantagem: valores internos mais precisos são arredondados no indicador;
- motivo: produz um contrato estável e legível para o preço armazenado.

## 14. Limitações

- somente 60 observações controladas;
- distribuição construída para exploração e testes;
- poucos registros por grupo local;
- datas descontínuas;
- revendas diferentes entre grupos e datas;
- ausência de ponderação por população, consumo ou quantidade vendida;
- média de preços anunciados, não de volume comercializado;
- sem inferência estatística, previsão ou causalidade;
- sem API, Front-end ou gráficos.
