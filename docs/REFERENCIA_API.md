# Referência da API FuelVision

## Propósito

A API disponibiliza consultas analíticas e uma estimativa experimental sem
permitir alteração dos dados. No ambiente Docker, use a mesma origem do
dashboard:

```text
http://localhost:5173/api
```

Em uma publicação, substitua por `https://seu-dominio.example/api`.

## Formato

- requisições e respostas usam HTTP;
- respostas de sucesso usam JSON;
- datas usam `AAAA-MM-DD`;
- preços informam sua unidade;
- erros usam `ProblemDetail`, sem stack trace ou SQL interno.

## Endpoints

| Método | Caminho | Descrição |
| --- | --- | --- |
| GET | `/api/prices` | observações paginadas |
| GET | `/api/prices/summary` | média, mínimo, máximo e período por produto |
| GET | `/api/prices/history` | indicadores diários paginados |
| GET | `/api/prices/anomalies` | observações fora dos limites do IQR |
| GET | `/api/locations/states` | estados presentes na amostra |
| GET | `/api/locations/cities` | municípios de um estado |
| GET | `/api/predictions/model` | versão, métricas e limites do estimador |
| POST | `/api/predictions` | estimativa experimental por produto e data |

## Filtros analíticos

Os endpoints de preços aceitam, quando aplicável:

| Parâmetro | Regra |
| --- | --- |
| `product` | texto com até 40 caracteres |
| `state` | sigla com exatamente duas letras |
| `municipality` | texto com até 120 caracteres |
| `startDate` | data inicial inclusiva |
| `endDate` | data final inclusiva e não anterior à inicial |
| `page` | inteiro a partir de zero |
| `size` | inteiro entre 1 e 100 |

Os filtros são parâmetros de URL e não devem ser concatenados manualmente sem
codificação.

## Exemplos de consulta

```bash
curl --fail \
  'http://localhost:5173/api/prices?product=GNV&state=RJ&size=10'

curl --fail \
  'http://localhost:5173/api/prices/summary?product=GNV&state=RJ&municipality=MACAE'

curl --fail \
  'http://localhost:5173/api/prices/history?product=GNV&page=0&size=20'

curl --fail \
  'http://localhost:5173/api/prices/anomalies?product=GASOLINA%20COMUM&state=AC'

curl --fail \
  'http://localhost:5173/api/locations/cities?state=RJ'
```

## Solicitar uma estimativa

```bash
curl --fail \
  --request POST \
  --header 'Content-Type: application/json' \
  --data '{"product":"GASOLINA COMUM","collectionDate":"2026-01-03"}' \
  http://localhost:5173/api/predictions
```

Resposta verificada com o artefato atual:

```json
{
  "product": "GASOLINA COMUM",
  "collectionDate": "2026-01-03",
  "estimatedPrice": 6.594,
  "unit": "BRL/liter",
  "modelVersion": "product-mean-baseline-v1",
  "modelType": "ProductMeanBaseline",
  "trainedThrough": "2026-01-02",
  "evaluationMae": 0.5271078431372549,
  "warning": "Estimativa experimental baseada em uma amostra pequena e não representativa; não deve ser tratada como preço garantido."
}
```

A data aceita fica entre 03/01/2026 e 01/02/2026. GNV não é aceito porque usa
`BRL/m3` e o estimador foi definido em `BRL/liter`.

## Paginação

Respostas paginadas contêm:

```json
{
  "items": [],
  "totalItems": 0,
  "totalPages": 0,
  "page": 0,
  "size": 20
}
```

**Paginação** limita a quantidade devolvida em uma requisição. Mesmo com a
amostra pequena, ela mantém o contrato adequado para volumes maiores.

## Erros

| Situação | Código esperado |
| --- | ---: |
| parâmetro ou corpo inválido | 400 |
| rota inexistente | 404 |
| serviço Python indisponível durante estimativa | 503 |
| falha interna não tratada | 500 |

Um `200` informa que a requisição foi processada; não prova que a amostra é
representativa nem que uma estimativa futura será precisa.

## OpenAPI local

Com o Back-end exposto localmente:

- Swagger UI: `http://localhost:8080/swagger-ui.html`;
- contrato JSON: `http://localhost:8080/v3/api-docs`;
- saúde: `http://localhost:8080/actuator/health`.

Essas rotas administrativas não são encaminhadas pelo gateway público padrão.

## Documentação detalhada

- [arquitetura do Back-end](backend/API_BACKEND.md);
- [serviço de estimativas](ml/MODEL_SERVING.md);
- [detecção de anomalias](analytics/ANOMALY_DETECTION.md).
