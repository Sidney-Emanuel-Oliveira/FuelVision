# FuelVision

O FuelVision é um projeto educacional e profissional que evoluirá para uma plataforma de análise de preços de combustíveis baseada em dados públicos brasileiros.

O **Módulo 9 — Previsão Disponível pela Aplicação** tornou o baseline por média de produto acessível no dashboard. O estimador aprovado no Módulo 8 agora é persistido com metadados, carregado por uma API FastAPI, intermediado pelo Back-end Spring Boot e apresentado como **estimativa**, com versão, período de treino, MAE e aviso de limitação.

## Propósito

O projeto pretende reunir, de forma gradual:

- Engenharia de Dados para obtenção, validação e preparação dos dados;
- Analytics para produzir consultas e indicadores;
- uma API para disponibilizar informações;
- uma interface para apresentar resultados;
- Machine Learning para experimentos de previsão e detecção de comportamentos atípicos.

Cada capacidade será construída somente no módulo correspondente. A ordem oficial está em [`docs/PLANO_FUELVISION.md`](docs/PLANO_FUELVISION.md).

## Estado atual

Consulte:

- [`docs/PROPOSTA_DO_PROJETO.md`](docs/PROPOSTA_DO_PROJETO.md): problema, objetivos e limites;
- [`docs/arquitetura/ARQUITETURA_PLANEJADA.md`](docs/arquitetura/ARQUITETURA_PLANEJADA.md): evolução planejada;
- [`docs/STATUS_DO_PROJETO.md`](docs/STATUS_DO_PROJETO.md): progresso dos módulos;
- [`docs/dados/FONTE_DADOS_ANP.md`](docs/dados/FONTE_DADOS_ANP.md): origem e processo de amostragem;
- [`docs/dados/DICIONARIO_DADOS.md`](docs/dados/DICIONARIO_DADOS.md): significado dos 16 campos;
- [`docs/dados/RELATORIO_EXPLORACAO.md`](docs/dados/RELATORIO_EXPLORACAO.md): resultados e limitações;
- [`docs/pipeline/INGESTAO_RAW.md`](docs/pipeline/INGESTAO_RAW.md): operação e regras da ingestão raw;
- [`docs/pipeline/TRANSFORMACAO_VALIDACAO.md`](docs/pipeline/TRANSFORMACAO_VALIDACAO.md): limpeza, validações e rejeições;
- [`docs/dados/DICIONARIO_DADOS_PROCESSADOS.md`](docs/dados/DICIONARIO_DADOS_PROCESSADOS.md): esquema da saída processada;
- [`docs/database/MODELO_RELACIONAL.md`](docs/database/MODELO_RELACIONAL.md): tabelas, chaves e relacionamentos;
- [`docs/database/POSTGRESQL_LOCAL.md`](docs/database/POSTGRESQL_LOCAL.md): configuração, carga e testes do banco local;
- [`docs/database/ANALISES_SQL.md`](docs/database/ANALISES_SQL.md): indicadores, filtros, resultados e limitações analíticas.
- [`docs/backend/API_BACKEND.md`](docs/backend/API_BACKEND.md): arquitetura, endpoints, execução, testes e limites da API.
- [`docs/frontend/DASHBOARD.md`](docs/frontend/DASHBOARD.md): componentes, integração, filtros, gráficos, execução e testes do dashboard.
- [`docs/ml/BASELINE_MODEL.md`](docs/ml/BASELINE_MODEL.md): problema preditivo, preparação temporal, baseline, Ridge, métricas e limitações.
- [`docs/ml/MODEL_SERVING.md`](docs/ml/MODEL_SERVING.md): seleção, persistência, inferência, versionamento e integração da estimativa.

## Pré-requisitos atuais

Para executar o projeto até o Módulo 9, é necessário ter:

- um editor de texto;
- Git para consultar o estado do repositório;
- Python 3.9 ou compatível;
- PostgreSQL 17 com `psql`, `createdb` e `createuser`;
- Java 21 ou mais recente;
- Maven 3.6.3 ou mais recente;
- Node.js compatível com Vite 8 e npm;
- um terminal para executar os comandos documentados.

O serviço de estimativas requer um ambiente virtual com as versões de pandas, scikit-learn, joblib, FastAPI e Uvicorn fixadas em `ml/requirements.txt`. Não foi adicionado driver Python de PostgreSQL porque a carga continua utilizando o cliente oficial `psql`.

## Como executar

Na raiz do projeto, execute:

```bash
python3 exploration/explore_sample.py
python3 -m pipeline.ingest_raw data/samples/precos-combustiveis-amostra.csv
python3 -m pipeline.transform_data data/raw/precos-combustiveis-amostra__d5dd2159be5b.csv
database/scripts/create_schema.sh
database/scripts/load_processed.sh \
  data/processed/precos-combustiveis-amostra__d5dd2159be5b__v1__processed.csv
database/scripts/run_initial_queries.sh
database/scripts/create_analytics_views.sh
database/scripts/validate_analytics.sh
database/scripts/run_analytics.sh
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r ml/requirements-dev.txt
.venv/bin/python -m unittest discover -s tests -v
FUELVISION_RUN_DB_TESTS=1 .venv/bin/python -m unittest discover -s tests -v
.venv/bin/python -m ml.train_evaluate \
  --input data/processed/precos-combustiveis-amostra__d5dd2159be5b__v1__processed.csv
.venv/bin/python -m ml.artifact \
  --input data/processed/precos-combustiveis-amostra__d5dd2159be5b__v1__processed.csv
.venv/bin/python -m uvicorn ml.inference_api:app --host 127.0.0.1 --port 8000 --ws none
backend/scripts/test.sh
backend/scripts/test.sh --with-postgres
backend/scripts/run.sh
cd frontend
npm install
npm run typecheck
npm run lint
npm run format:check
npm test
npm run build
npm run dev
```

Antes dos comandos de banco, copie `.env.example` para `.env`, substitua os valores locais e crie o papel e o banco conforme `docs/database/POSTGRESQL_LOCAL.md`. Os comandos com `FUELVISION_RUN_DB_TESTS=1` e `--with-postgres` ativam os testes que exigem PostgreSQL. Para usar todo o dashboard, mantenha o serviço Python, `backend/scripts/run.sh` e `npm run dev` em três terminais separados. O artefato em `ml/artifacts/` é gerado localmente e não é versionado.

Leia os documentos técnicos nesta ordem:

1. `docs/pipeline/INGESTAO_RAW.md`;
2. `docs/pipeline/TRANSFORMACAO_VALIDACAO.md`;
3. `docs/dados/DICIONARIO_DADOS_PROCESSADOS.md`;
4. `docs/database/MODELO_RELACIONAL.md`;
5. `docs/database/POSTGRESQL_LOCAL.md`;
6. `docs/database/ANALISES_SQL.md`;
7. `docs/backend/API_BACKEND.md`.
8. `docs/frontend/DASHBOARD.md`.
9. `docs/ml/BASELINE_MODEL.md`.
10. `docs/ml/MODEL_SERVING.md`.

## Limitações atuais

- somente uma amostra não representativa foi versionada;
- a carga no banco foi validada somente sobre a amostra processada;
- as análises descrevem somente 60 observações controladas e não representam o mercado brasileiro;
- muitos grupos por localidade possuem apenas uma ou duas observações;
- a evolução diária não acompanha o mesmo conjunto de revendas em todas as datas;
- o modelo guarda o estado atual da revenda, não seu histórico de alterações;
- ainda não há ferramenta de migração ou histórico de lotes carregados;
- a API é somente leitura e ainda não possui autenticação, CORS de produção, cache ou limite por cliente;
- a comparação do dashboard realiza uma consulta de resumo por estado;
- o histórico exibido pelo dashboard está limitado a 100 pontos por consulta;
- não houve auditoria completa de acessibilidade com tecnologia assistiva;
- o primeiro Ridge não superou o baseline por média de produto no teste temporal;
- o experimento usa apenas 50 observações líquidas, com uma data de treino e uma de teste;
- GNV não participa do baseline porque utiliza `BRL/m3`;
- a estimativa usa o baseline simples por produto, não o Ridge, e só aceita datas entre 03/01/2026 e 01/02/2026;
- o artefato é gerado a partir de apenas 50 observações líquidas e precisa ser criado localmente antes de iniciar o serviço;
- o serviço de inferência não possui autenticação, monitoramento, implantação produtiva ou atualização automática;
- a estimativa é pontual e não possui intervalo de incerteza;
- não existem conclusões estatísticas ou métricas de negócio.

Essas limitações são intencionais e preservam a progressão definida no plano.

## Regras de contribuição

- trabalhar em apenas um módulo por vez;
- não versionar `.env`, credenciais, datasets grandes ou artefatos gerados;
- executar e registrar as verificações aplicáveis;
- documentar decisões e limitações;
- executar commit e push somente após a conclusão e aprovação das verificações do módulo.
