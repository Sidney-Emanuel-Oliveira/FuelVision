# Status do projeto FuelVision

Atualizado em: 30/07/2026.

| Módulo | Nome                                    | Status       | Data       | Principais entregas                                                              |
| ------ | --------------------------------------- | ------------ | ---------- | -------------------------------------------------------------------------------- |
| 0      | Fundação e Planejamento                 | Concluído    | 27/07/2026 | README, `.gitignore`, proposta, arquitetura planejada e documentação educacional |
| 1      | Fonte de Dados e Exploração             | Concluído    | 28/07/2026 | Fonte oficial, amostra controlada, dicionário, exploração e testes               |
| 2      | Ingestão da Camada Raw                  | Concluído    | 28/07/2026 | Pipeline raw idempotente, validações, integridade, logs e 11 testes              |
| 3      | Limpeza, Transformação e Validação      | Concluído    | 28/07/2026 | Padronização, validações, processados, rejeitados e 14 testes                    |
| 4      | PostgreSQL e Modelagem de Dados         | Concluído    | 28/07/2026 | PostgreSQL 17, seis tabelas, carga idempotente e 13 testes                       |
| 5      | Análises e Consultas SQL                | Concluído    | 28/07/2026 | Quatro views, indicadores, cinco filtros, validações e 10 testes                 |
| 6      | API Back-end com Java e Spring Boot     | Concluído    | 28/07/2026 | Cinco endpoints REST, JDBC, DTOs, validação, OpenAPI e 14 testes                  |
| 7      | Dashboard React e TypeScript            | Concluído    | 28/07/2026 | React, TypeScript, indicadores, gráficos, filtros, estados e 11 testes           |
| 8      | Machine Learning: Baseline              | Concluído    | 28/07/2026 | Split temporal, baseline, Ridge, MAE, RMSE, comparação e 13 testes               |
| 9      | Previsão Disponível pela Aplicação      | Concluído    | 28/07/2026 | Baseline persistido, FastAPI, integração Spring, painel preditivo e 47 testes     |
| 10     | Detecção de Anomalias                   | Concluído    | 28/07/2026 | IQR, endpoint paginado, motivos, painel responsável e 49 testes                   |
| 11     | Qualidade, Docker e Integração Contínua | Concluído    | 28/07/2026 | Quatro imagens, Compose, health checks, lint, CI e seis testes de infraestrutura  |
| 12     | Documentação Profissional e Deploy      | Concluído    | 28/07/2026 | Documentação profissional, deploy com HTTPS, segurança, acessibilidade e portfólio |

## Observação

Os Módulos 0 a 12 estão concluídos. O fluxo principal do plano oficial foi
implementado, testado e preparado para publicação em um servidor com domínio.

Em 30/07/2026, uma manutenção posterior ao Módulo 12 acrescentou um perfil para
Vercel Services: Vite público, Spring Boot em contêiner, FastAPI privado por
binding e PostgreSQL gerenciado externo. A configuração local e o procedimento
de inicialização do banco foram preparados. Os três serviços foram construídos
pela Vercel CLI 58.4.4 e o teste de fumaça integrado passou localmente. Nenhuma
conta, banco ou implantação externa foi criada. A disponibilidade pública
continua dependendo das credenciais e decisões do proprietário e da liberação
do recurso Services na conta da Vercel.

Possíveis módulos opcionais devem ser analisados separadamente; nenhum deles foi
iniciado automaticamente.
