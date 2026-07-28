# API Back-end do FuelVision

## 1. O que foi construído

O Módulo 6 criou uma API REST somente para leitura, desenvolvida com Java e Spring Boot. Ela consulta as observações e os indicadores que já existem no PostgreSQL e devolve respostas JSON.

O Módulo 6 disponibilizou cinco endpoints analíticos. O Módulo 9 acrescentou dois endpoints que integram o serviço Python de inferência:

| Método | Caminho                         | Responsabilidade                                  |
| ------ | ------------------------------- | ------------------------------------------------- |
| GET    | `/api/prices`                   | listar observações com filtros e paginação        |
| GET    | `/api/prices/summary`           | calcular indicadores agrupados por produto        |
| GET    | `/api/prices/history`           | listar indicadores diários com paginação          |
| GET    | `/api/locations/states`         | listar UFs que possuem preços na amostra           |
| GET    | `/api/locations/cities?state=RJ`| listar municípios com preços em uma UF             |
| GET    | `/api/predictions/model`        | consultar metadados do estimador ativo             |
| POST   | `/api/predictions`              | solicitar uma estimativa para produto e data       |

A API não altera o banco e não cria dados fictícios.

## 2. Por que isso é necessário

Até o Módulo 5, uma pessoa precisava executar SQL ou scripts no terminal para consultar os preços. A API cria um contrato HTTP que poderá ser consumido por outros programas sem permitir acesso direto ao banco.

```text
cliente → requisição HTTP → API → PostgreSQL → DTO → JSON → cliente
```

O dashboard consome esse contrato sem acessar diretamente o PostgreSQL nem o serviço Python.

## 3. Conceitos utilizados

### API REST e requisição

**API REST** é uma interface que disponibiliza recursos por meio de endereços HTTP. No FuelVision, `/api/prices` representa a consulta de preços. Uma **requisição** contém o método `GET`, o caminho e filtros opcionais.

### Resposta e código HTTP

**Resposta** é o resultado devolvido pela API. O corpo usa JSON, enquanto o **código HTTP** informa a categoria do resultado:

- `200 OK`: a consulta foi processada, mesmo quando a lista está vazia;
- `400 Bad Request`: algum parâmetro possui formato, limite ou combinação inválida;
- `503 Service Unavailable`: o PostgreSQL não pôde atender à consulta.

### Controller

**Controller** recebe a requisição HTTP, valida formatos básicos e encaminha os dados ao serviço. `PriceController` não escreve SQL e não contém cálculos de negócio.

### Service

**Service** aplica regras do caso de uso. `PriceQueryService` transforma filtros em maiúsculas, converte valores em DTOs e impede que a data inicial seja posterior à final.

### Repository

**Repository** concentra o acesso ao banco. `PriceRepository` monta somente as condições necessárias e entrega os valores ao JDBC como parâmetros separados do SQL.

### Entidade de domínio

**Entidade de domínio** representa uma informação importante do problema dentro do código. `PriceObservation` representa uma observação identificável por `id`. Neste módulo ela é somente leitura e não usa anotações de ORM.

### DTO

**DTO**, ou objeto de transferência de dados, define o formato que atravessa a fronteira da API. `PriceResponse` expõe os campos necessários ao cliente sem obrigar o banco e o JSON a possuírem a mesma estrutura interna.

### JDBC e SQL parametrizado

**JDBC** é a API padrão do Java para conversar com bancos relacionais. As consultas usam parâmetros nomeados, como `:product`. A entrada do usuário nunca é concatenada diretamente ao SQL, o que reduz o risco de injeção de SQL.

### Injeção de dependência

**Injeção de dependência** significa que uma classe recebe os componentes de que precisa em vez de criá-los internamente. O Spring fornece `PriceQueryService` ao controller e `PriceRepository` ao service. Isso permite substituir dependências reais por mocks nos testes.

### OpenAPI e Swagger UI

**OpenAPI** é uma descrição estruturada do contrato HTTP. **Swagger UI** apresenta esse contrato em uma página interativa. No ambiente local:

- JSON OpenAPI: `http://localhost:8080/v3/api-docs`;
- interface Swagger: `http://localhost:8080/swagger-ui.html`.

## 4. Como o fluxo funciona

Exemplo para `GET /api/prices?product=gnv&state=rj&size=10`:

```text
PriceController
→ valida UF e paginação
→ PriceQueryService normaliza GNV e RJ
→ PriceRepository cria filtros parametrizados
→ PostgreSQL executa JOIN, WHERE, ORDER BY, LIMIT e OFFSET
→ PriceObservation
→ PriceResponse
→ PageResponse em JSON
```

Se `startDate=2026-01-08` e `endDate=2026-01-01`, o service lança `InvalidFilterException`. `ApiExceptionHandler` converte essa exceção em uma resposta padronizada `400`.

## 5. Arquivos envolvidos

| Caminho                                  | Responsabilidade                                                |
| ---------------------------------------- | --------------------------------------------------------------- |
| `backend/pom.xml`                        | versões, dependências, compilação e testes Maven                |
| `FuelVisionApplication.java`             | ponto de entrada do Spring Boot                                 |
| `config/OpenApiConfig.java`              | título, versão e descrição OpenAPI                              |
| `controller/PriceController.java`        | três endpoints de preços                                        |
| `controller/LocationController.java`     | dois endpoints de localidades                                   |
| `controller/PredictionController.java`   | dois endpoints de metadados e estimativa                         |
| `client/PredictionClient.java`           | comunicação HTTP com o serviço Python                            |
| `service/PredictionService.java`         | normalização do produto antes da inferência                      |
| `service/PriceQueryService.java`         | filtros, regra de datas e conversão dos resultados               |
| `service/LocationService.java`           | normalização da UF e conversão das localidades                   |
| `repository/PriceRepository.java`        | SQL de observações, resumo e histórico                           |
| `repository/LocationRepository.java`     | SQL das UFs e municípios com preços                              |
| `domain/*.java`                          | objetos internos de observação, indicador, localidade e página   |
| `dto/*.java`                             | contrato JSON das respostas                                     |
| `exception/*.java`                       | erro de filtro e respostas HTTP padronizadas                     |
| `application.properties`                 | conexão por ambiente, pool, Swagger e segurança de erros         |
| `backend/scripts/*.sh`                   | carregar `.env`, executar e testar                               |
| `backend/src/test/**`                    | testes de service, controller e PostgreSQL                       |

## 6. Código por blocos

### Controllers

- responsabilidade: traduzir HTTP para chamadas Java;
- entrada: query parameters de texto, data e paginação;
- processamento: validações declarativas como `@Max(100)`;
- saída: DTOs serializados como JSON;
- comunicação: chamam somente services;
- erros: formato de data, UF, campo longo ou paginação inválida;
- verificação: `ApiControllerTest` envia requisições com `MockMvc`.

### Services

- responsabilidade: aplicar regras que não pertencem ao protocolo HTTP nem ao SQL;
- entrada: filtros recebidos dos controllers;
- processamento: remove espaços, converte texto para maiúsculas e valida o período;
- saída: DTOs prontos para a resposta;
- comunicação: chamam repositories;
- erros: período invertido;
- verificação: `PriceQueryServiceTest` e `LocationServiceTest`.

### Repositories

- responsabilidade: executar consultas somente de leitura;
- entrada: `PriceFilter`, página e tamanho;
- processamento: adiciona cláusulas `WHERE` apenas para filtros presentes;
- saída: entidades de domínio e metadados de paginação;
- comunicação: usa `NamedParameterJdbcTemplate` e PostgreSQL;
- erros: conexão indisponível, esquema ausente ou SQL incompatível;
- verificação: `PostgresRepositoryIntegrationTest` usa as 60 observações reais carregadas.

### Tratamento de erros

`ApiExceptionHandler` usa `ProblemDetail`, formato padronizado pelo protocolo HTTP. A resposta contém `title`, `detail`, `status` e `instance`, sem expor stack trace, senha ou SQL interno.

## 7. Filtros e paginação

Os três endpoints de preços aceitam:

- `product`: até 40 caracteres;
- `state`: exatamente duas letras;
- `municipality`: até 120 caracteres;
- `startDate`: data inicial inclusiva em `AAAA-MM-DD`;
- `endDate`: data final inclusiva em `AAAA-MM-DD`.

`/api/prices` e `/api/prices/history` também aceitam:

- `page`: começa em zero e aceita no máximo `1.000.000`;
- `size`: valor entre 1 e 100, com padrão 20.

**Paginação** limita quantos itens são devolvidos por requisição. Ela evita que uma futura carga maior tente retornar todas as observações de uma vez.

## 8. Como executar

Pré-requisitos:

- Java 21 ou mais recente;
- Maven 3.6.3 ou mais recente;
- PostgreSQL configurado conforme `docs/database/POSTGRESQL_LOCAL.md`;
- `.env` local preenchido e não versionado;
- esquema, dados e views dos módulos anteriores carregados.

Na raiz do projeto:

```bash
backend/scripts/run.sh
```

A aplicação usa a porta 8080 por padrão. Para usar outra porta:

```bash
SERVER_PORT=8081 backend/scripts/run.sh
```

## 9. Como consultar

```bash
curl 'http://localhost:8080/api/prices?product=GNV&state=RJ&size=10'

curl 'http://localhost:8080/api/prices/summary?product=GNV&state=RJ&municipality=MACAE&startDate=2026-01-01&endDate=2026-01-07'

curl 'http://localhost:8080/api/prices/history?product=GNV'

curl 'http://localhost:8080/api/locations/states'

curl 'http://localhost:8080/api/locations/cities?state=RJ'
```

## 10. Como testar

Testes que não exigem PostgreSQL:

```bash
backend/scripts/test.sh
```

Suíte completa:

```bash
backend/scripts/test.sh --with-postgres
```

O segundo comando lê o `.env` local e ativa quatro testes de integração. Nenhuma senha é escrita no relatório dos testes.

## 11. Resultados verificados

- 22 testes Java aprovados com PostgreSQL ativado;
- 60 observações encontradas pelo repository;
- 14 grupos de data + produto no histórico completo;
- cinco endpoints responderam `200`;
- os dois endpoints de previsão responderam `200` na integração entre Python e Java;
- `size=101` respondeu `400` com `ProblemDetail`;
- filtro GNV + RJ + MACAE retornou 2 observações e média `4.935`;
- OpenAPI 3.1 foi gerado com os sete caminhos e esquemas de erro.

Esses números descrevem apenas a amostra controlada já documentada. Não representam o mercado brasileiro.

## 12. Decisões técnicas

### JDBC em vez de JPA/ORM

- escolha: JDBC com SQL explícito;
- alternativa: mapear as tabelas com JPA e Hibernate;
- vantagem: o SQL permanece visível e reutiliza o modelo já validado;
- desvantagem: o repository possui mais código de mapeamento;
- motivo: a API é somente leitura e não existe necessidade demonstrada de gerenciamento automático de entidades.

### Records para domínio e DTOs

- escolha: `record` do Java para objetos imutáveis;
- alternativa: classes com campos, construtor e getters;
- vantagem: menos código repetitivo e estado que não muda após a criação;
- desvantagem: exige Java moderno e não serve para todo tipo de entidade mutável;
- motivo: respostas e linhas consultadas representam fotografias imutáveis dos dados.

### Consultas dinâmicas parametrizadas

- escolha: montar somente as condições necessárias e separar os valores;
- alternativa: uma consulta diferente para cada combinação de filtros;
- vantagem: evita duplicação e mantém proteção contra injeção de SQL;
- desvantagem: exige cuidado ao montar a lista de condições;
- motivo: cinco filtros opcionais produziriam muitas combinações repetidas.

## 13. Erros comuns

### `Connection refused`

Confirme o serviço PostgreSQL e as variáveis do `.env`.

### `relation ... does not exist`

Execute os scripts dos Módulos 4 e 5 antes de iniciar a API.

### Resposta `400`

Confira formato de UF, datas, tamanho dos textos, `page` e `size`. O corpo informa que os parâmetros precisam ser revisados.

### Porta 8080 ocupada

Use `SERVER_PORT=8081 backend/scripts/run.sh`.

### Maven não encontrado

Instale Maven 3.6.3 ou mais recente. O ambiente validado utiliza Maven 3.9.16.

## 14. Segurança e limitações

- a API não possui autenticação nem autorização;
- CORS de produção ainda não foi configurado; no ambiente local, o Vite usa um proxy;
- não há limitação por cliente ou proteção contra excesso de requisições;
- Swagger está ativo no ambiente local e deverá ser revisto antes de produção;
- não existe cache;
- os endpoints são somente leitura;
- as consultas usam uma amostra de 60 registros;
- não existe garantia de representatividade estatística;
- não há deploy, container ou integração contínua;
- o serviço de inferência precisa estar ativo para os dois endpoints preditivos;
- indisponibilidade do serviço Python é convertida em `503`, sem expor detalhes internos;
- as estimativas herdam todas as limitações do baseline documentadas em `docs/ml/MODEL_SERVING.md`.

## Extensão do Módulo 9: cliente de inferência

**Cliente HTTP** é o componente que chama outro serviço por HTTP. `PredictionClient` usa `RestClient`, define tempo limite de conexão de 2 segundos e leitura de 5 segundos e converte falhas externas em erros seguros.

```text
dashboard → PredictionController → PredictionService → PredictionClient
          → FastAPI → artefato versionado → estimativa
```

Exemplos:

```bash
curl 'http://localhost:8080/api/predictions/model'

curl -X POST 'http://localhost:8080/api/predictions' \
  -H 'Content-Type: application/json' \
  -d '{"product":"GASOLINA COMUM","collectionDate":"2026-01-03"}'
```

Um produto incompatível ou uma data fora da janela retorna `400`. Se o serviço Python estiver parado, o Back-end retorna `503`. Os testes de `PredictionController`, `PredictionService`, `PredictionClient` e do contexto Spring verificam essas fronteiras.

## 15. O que compreender agora

- a separação entre controller, service e repository;
- por que DTO e entidade de domínio possuem responsabilidades diferentes;
- como filtros percorrem as camadas;
- por que parâmetros SQL não devem ser concatenados;
- o significado de `200`, `400` e `503`;
- como paginação protege a API contra respostas ilimitadas.

## 16. O que poderá ser aprofundado depois

- autenticação e autorização;
- cache e limites de requisição;
- observabilidade e métricas operacionais;
- migrações automatizadas do banco;
- paginação por cursor;
- deploy e configuração segura de produção.

Esses assuntos não são necessários para compreender o fluxo atual e pertencem a módulos futuros ou melhorias posteriores.

## 17. Referências oficiais

- [Requisitos do Spring Boot 4.1](https://docs.spring.io/spring-boot/system-requirements.html)
- [Acesso SQL com Spring Boot](https://docs.spring.io/spring-boot/reference/data/sql.html)
- [Spring MVC](https://docs.spring.io/spring-framework/reference/web/webmvc.html)
- [Springdoc OpenAPI para Spring Boot 4](https://springdoc.org/v4/index.html)
