# Proposta do projeto FuelVision

## 1. Visão geral

O FuelVision será uma plataforma educacional de Engenharia de Dados, Analytics e Inteligência Artificial para estudar preços de combustíveis com dados públicos brasileiros.

**Plataforma** é um conjunto de componentes que colaboram para resolver um problema. No FuelVision, esses componentes serão acrescentados gradualmente: dados, armazenamento, consultas, API, interface e modelos estatísticos. No Módulo 0, a plataforma existe apenas como proposta documentada.

## 2. Problema

Dados públicos de preços podem estar distribuídos em arquivos, possuir formatos que exigem preparação e ser difíceis de consultar diretamente. O projeto pretende transformar esse material, em módulos futuros, em informações organizadas e verificáveis.

Uma visualização ou previsão só é confiável quando sua origem, suas transformações e suas limitações podem ser explicadas. Por isso, o projeto começa pela fundação antes de implementar funcionalidades.

## 3. Objetivo geral

Construir progressivamente uma aplicação capaz de importar, validar, armazenar, consultar e apresentar dados públicos de preços de combustíveis e, posteriormente, realizar experimentos simples de Machine Learning com avaliação adequada.

## 4. Objetivos educacionais

- compreender a responsabilidade de cada parte de um sistema;
- aprender a evoluir software em entregas pequenas e verificáveis;
- relacionar Python, SQL, Java, React e Machine Learning a problemas concretos;
- praticar testes, documentação, Git e decisões de arquitetura;
- comunicar resultados sem inventar dados, métricas ou conclusões.

## 5. Usuários e usos previstos

O público inicial é o próprio estudante e pessoas interessadas em explorar preços de combustíveis. Quando os módulos correspondentes existirem, a plataforma poderá apoiar consultas por período, localidade e tipo de combustível.

O FuelVision terá finalidade educacional e analítica. Não será, por si só, uma fonte oficial, um mecanismo de fiscalização nem uma garantia de preços futuros.

## 6. Escopo progressivo

O desenvolvimento seguirá os módulos definidos no plano oficial. De forma resumida:

1. fundação e planejamento;
2. conhecimento da fonte de dados;
3. ingestão e preparação;
4. armazenamento e análises;
5. API e interface;
6. experimentos de Machine Learning;
7. qualidade, empacotamento e documentação profissional.

Essa lista resume a evolução; os nomes, números, entregas e autorizações válidos são os de `docs/PLANO_FUELVISION.md`.

## 7. Fora do escopo atual

No Módulo 0, não fazem parte da entrega:

- pesquisar ou baixar datasets da ANP;
- criar scripts de leitura ou pipelines;
- configurar PostgreSQL ou qualquer banco;
- criar API, endpoints ou aplicação Spring Boot;
- criar dashboard ou aplicação React;
- treinar, avaliar ou publicar modelos de Machine Learning;
- criar infraestrutura, containers ou integração contínua.

## 8. Princípios

- usar dados públicos e registrar sua origem;
- não versionar segredos nem grandes datasets;
- demonstrar resultados com verificações reproduzíveis;
- escolher tecnologias quando houver necessidade no módulo;
- tratar previsões como estimativas e anomalias como sinais estatísticos, não como acusações;
- registrar limitações técnicas e educacionais.

## 9. Critério de sucesso desta fundação

A fundação está pronta quando uma pessoa consegue entender o propósito, consultar a progressão planejada, identificar o estado dos módulos, conhecer os limites atuais e revisar os arquivos do repositório sem encontrar funcionalidades antecipadas.
