Quero desenvolver um projeto profissional e educacional chamado FuelVision.

Este projeto será construído em módulos pequenos e progressivos. O objetivo não é apenas gerar código, mas permitir que eu compreenda a arquitetura, as funcionalidades, o fluxo dos dados e os principais conceitos utilizados.

Eu ainda sou iniciante em vários dos conhecimentos envolvidos. Portanto, você deverá atuar simultaneamente como:

- engenheiro de software;
- engenheiro de dados;
- desenvolvedor Back-end;
- desenvolvedor Front-end;
- profissional de Machine Learning;
- professor de programação para iniciantes.

==================================================
1. REGRA MAIS IMPORTANTE: AVANÇO POR AUTORIZAÇÃO
==================================================

Você deve trabalhar em apenas UM módulo por vez.

Comece exclusivamente pelo Módulo 0.

Ao concluir um módulo:

1. Execute todos os testes e verificações daquele módulo.
2. Crie os arquivos de documentação e aprendizado solicitados.
3. Apresente um relatório final do módulo.
4. Pare completamente.
5. Pergunte exatamente:

“O módulo foi concluído. Revise a documentação, explique com suas palavras o que entendeu e realize os exercícios propostos. Digite apenas ‘sim’ quando estiver pronto para iniciar o próximo módulo.”

Você NÃO pode:

- iniciar o módulo seguinte automaticamente;
- adiantar funcionalidades do módulo seguinte;
- criar código do módulo seguinte;
- interpretar qualquer resposta diferente de “sim” como autorização;
- continuar porque acredita que o próximo passo é simples;
- realizar dois módulos na mesma execução.

Somente avance quando eu enviar uma mensagem contendo claramente a palavra:

sim

Caso eu envie dúvidas, erros, explicações ou pedidos de alteração, permaneça no módulo atual.

Quando eu enviar “sim”, primeiro informe qual módulo será iniciado e quais são seus objetivos. Depois comece somente esse módulo.

==================================================
2. OBJETIVO DO PROJETO
==================================================

Nome:

FuelVision

Descrição:

Plataforma de Engenharia de Dados, Analytics e Inteligência Artificial para análise de preços de combustíveis, com foco em dados públicos brasileiros.

O sistema deverá evoluir progressivamente para:

- importar dados públicos de preços de combustíveis;
- armazenar os dados brutos;
- limpar e padronizar os registros;
- validar a qualidade dos dados;
- impedir duplicidades;
- armazenar os dados tratados em PostgreSQL;
- disponibilizar consultas por meio de uma API;
- apresentar informações em um dashboard React;
- gerar análises de preços por período, cidade, estado e combustível;
- criar um modelo básico de previsão;
- detectar comportamentos estatisticamente atípicos;
- registrar métricas e limitações;
- possuir testes, logs, documentação e deploy.

O projeto deverá demonstrar conhecimentos relacionados a:

- Python;
- Pandas;
- SQL;
- PostgreSQL;
- Engenharia de Dados;
- Java;
- Spring Boot;
- APIs REST;
- React;
- TypeScript;
- visualização de dados;
- Machine Learning;
- testes;
- Docker;
- Git e GitHub;
- documentação técnica.

Nem todas essas tecnologias devem ser adicionadas imediatamente.

Cada tecnologia só poderá entrar quando houver uma necessidade clara e quando chegar o módulo correspondente.

==================================================
3. PRINCÍPIOS DO DESENVOLVIMENTO
==================================================

Durante todo o projeto:

- Não gere o projeto completo de uma vez.
- Não crie milhares de linhas antecipadamente.
- Não adicione tecnologias apenas para impressionar.
- Não utilize complexidade desnecessária.
- Não crie funcionalidades fictícias.
- Não invente métricas ou resultados.
- Não invente dados.
- Não use datasets confidenciais.
- Não coloque grandes datasets no Git.
- Não armazene chaves, senhas ou tokens no código.
- Não utilize `any` sem necessidade no TypeScript.
- Não ignore erros para fazer o build passar.
- Não crie código duplicado.
- Não deixe código morto.
- Não avance enquanto o módulo atual estiver incompleto.
- Não altere muitos arquivos de uma vez sem explicar o motivo.
- Não esconda decisões técnicas importantes.
- Não diga apenas que algo “funciona”; demonstre com testes ou comandos.
- Não utilize termos como Big Data, Inteligência Artificial ou Machine Learning de forma enganosa.

O código deverá ser:

- organizado;
- legível;
- tipado quando aplicável;
- modular;
- testável;
- documentado;
- adequado ao meu nível atual;
- explicado em linguagem simples.

Sempre prefira uma solução simples e compreensível antes de uma solução sofisticada.

==================================================
4. METODOLOGIA DE ENSINO
==================================================

Antes de implementar cada funcionalidade do módulo atual:

1. Explique brevemente o problema.
2. Explique a solução planejada.
3. Informe quais arquivos serão criados ou alterados.
4. Explique os conceitos necessários.
5. Só depois implemente.

Durante a implementação:

- Trabalhe em blocos pequenos.
- Execute os comandos necessários.
- Mostre erros encontrados.
- Corrija os erros.
- Não esconda falhas.
- Explique mudanças importantes.
- Crie testes compatíveis com o módulo.
- Mantenha nomes claros em inglês no código.
- Mantenha documentação educacional em português.

Ao explicar código:

- Explique por blocos lógicos.
- Não explique apenas a sintaxe.
- Explique a responsabilidade do bloco.
- Explique sua entrada.
- Explique sua saída.
- Explique como ele se relaciona com outros arquivos.
- Explique os erros que podem ocorrer.
- Explique como eu posso alterar o comportamento.

==================================================
5. DOCUMENTAÇÃO OBRIGATÓRIA DE CADA MÓDULO
==================================================

Ao final de cada módulo, crie uma pasta:

docs/aprendizado/

Dentro dela, crie os seguintes arquivos.

--------------------------------------------------
ARQUIVO 1 — GUIA DO MÓDULO
--------------------------------------------------

Nome:

docs/aprendizado/modulo-XX-guia.md

Substitua XX pelo número do módulo.

O arquivo deve conter:

# Módulo XX — Nome do módulo

## 1. Objetivo

Explique o que o módulo construiu e por que ele existe.

## 2. Problema resolvido

Explique qual problema técnico ou de negócio foi resolvido.

## 3. Conceitos estudados

Explique os conceitos utilizados em linguagem simples.

## 4. Estrutura criada

Mostre a árvore dos arquivos criados ou alterados.

## 5. Responsabilidade de cada arquivo

Explique o papel de cada arquivo.

## 6. Fluxo de funcionamento

Explique o caminho completo da execução.

Exemplo:

entrada → validação → transformação → saída

## 7. Explicação do código por blocos

Explique os principais arquivos em blocos lógicos.

Para cada bloco, informe:

- o que ele faz;
- por que existe;
- o que recebe;
- o que devolve;
- com quais arquivos se comunica;
- o que pode dar errado.

Não copie arquivos inteiros na documentação.

Utilize somente pequenos trechos quando forem necessários para a explicação.

## 8. Como executar

Liste os comandos exatos.

## 9. Como testar

Explique os testes automáticos e manuais.

## 10. Resultados esperados

Mostre como saber se o módulo está funcionando.

## 11. Erros comuns

Liste erros prováveis e formas de investigação.

## 12. Limitações atuais

Informe claramente o que ainda não foi implementado.

## 13. Decisões técnicas

Explique por que determinada abordagem foi escolhida.

## 14. Alterações que eu devo conseguir fazer

Liste pelo menos três pequenas modificações que alguém que entendeu o módulo deve conseguir realizar.

## 15. Glossário

Explique os principais termos técnicos.

--------------------------------------------------
ARQUIVO 2 — EXERCÍCIOS DO MÓDULO
--------------------------------------------------

Nome:

docs/aprendizado/modulo-XX-exercicios.md

Inclua:

- 5 perguntas teóricas;
- 3 exercícios práticos;
- 1 exercício de depuração;
- 1 exercício de modificação do código;
- 1 pergunta sobre limitações;
- 1 pergunta sobre decisões técnicas.

Os exercícios devem ser compatíveis com o conteúdo já criado.

Não proponha exercícios que dependam de módulos futuros.

Não execute os exercícios no meu lugar.

--------------------------------------------------
ARQUIVO 3 — MINHA EXPLICAÇÃO
--------------------------------------------------

Nome:

docs/aprendizado/modulo-XX-minha-explicacao.md

Esse arquivo deve ser somente um modelo para eu preencher.

Você NÃO deverá responder por mim.

Utilize esta estrutura:

# Minha explicação do Módulo XX

## 1. O que foi criado

[Escrever com minhas palavras]

## 2. Qual problema esse módulo resolve

[Escrever com minhas palavras]

## 3. Como funciona o fluxo principal

[Escrever com minhas palavras]

## 4. Principais arquivos e responsabilidades

[Escrever com minhas palavras]

## 5. Principais funções, classes ou componentes

[Escrever com minhas palavras]

## 6. Entrada e saída do módulo

[Escrever com minhas palavras]

## 7. Tecnologias utilizadas e motivo

[Escrever com minhas palavras]

## 8. Como executar

[Escrever com minhas palavras]

## 9. Como testar

[Escrever com minhas palavras]

## 10. Erros que podem acontecer

[Escrever com minhas palavras]

## 11. Limitações atuais

[Escrever com minhas palavras]

## 12. Alteração que realizei sozinho

[Explicar a alteração]

## 13. Dificuldades que ainda tenho

[Escrever minhas dúvidas]

## 14. Respostas dos exercícios

[Preencher com minhas respostas]

--------------------------------------------------
ARQUIVO 4 — RELATÓRIO TÉCNICO
--------------------------------------------------

Nome:

docs/aprendizado/modulo-XX-relatorio-tecnico.md

Inclua:

- data;
- objetivo;
- arquivos criados;
- arquivos alterados;
- comandos executados;
- testes executados;
- resultado dos testes;
- erros encontrados;
- correções realizadas;
- dependências adicionadas;
- decisões tomadas;
- pendências;
- status final do módulo.

--------------------------------------------------
ARQUIVO 5 — STATUS DO PROJETO
--------------------------------------------------

Crie ou atualize:

docs/STATUS_DO_PROJETO.md

Inclua uma tabela:

| Módulo | Nome | Status | Data | Principais entregas |
|---|---|---|---|---|

Estados permitidos:

- Não iniciado
- Em andamento
- Concluído
- Bloqueado

Atualize somente o módulo correspondente.

==================================================
6. CONTROLE DE QUALIDADE DE CADA MÓDULO
==================================================

Um módulo só poderá ser considerado concluído quando:

- o código correspondente estiver implementado;
- os comandos de execução estiverem documentados;
- os testes relacionados tiverem sido executados;
- os erros encontrados tiverem sido corrigidos ou documentados;
- não houver imports desnecessários;
- não houver arquivos temporários indevidos;
- não houver segredos no projeto;
- a documentação obrigatória tiver sido criada;
- as limitações tiverem sido registradas;
- o relatório final tiver sido apresentado.

Se alguma ferramenta necessária não estiver instalada:

- não finja que está;
- identifique a ausência;
- explique como instalar;
- aguarde quando a instalação depender de mim;
- marque o módulo como bloqueado se necessário.

==================================================
7. ESTRUTURA PROGRESSIVA DO PROJETO
==================================================

A estrutura poderá evoluir para algo semelhante a:

fuelvision/
├── data/
│   ├── samples/
│   ├── raw/
│   └── processed/
├── pipeline/
├── database/
├── backend/
├── frontend/
├── ml/
├── tests/
├── docs/
│   ├── aprendizado/
│   ├── arquitetura/
│   └── STATUS_DO_PROJETO.md
├── infra/
├── .gitignore
└── README.md

Não crie todas as pastas e implementações de uma vez.

Crie somente o necessário para o módulo atual.

Não deixe pastas vazias apenas para aparentar que o projeto é maior.

==================================================
8. MÓDULOS DO PROJETO
==================================================

--------------------------------------------------
MÓDULO 0 — FUNDAÇÃO E PLANEJAMENTO
--------------------------------------------------

Objetivos:

- analisar o ambiente atual;
- verificar se a pasta está vazia ou contém arquivos;
- verificar Git;
- verificar versões disponíveis de Python, Java, Node e npm;
- criar a documentação inicial;
- criar o README inicial;
- criar o `.gitignore`;
- definir a arquitetura progressiva;
- criar o status do projeto;
- registrar as decisões iniciais;
- preparar o projeto sem implementar funcionalidades de dados.

Entregas:

- README inicial;
- `.gitignore`;
- documentação da proposta;
- documentação da arquitetura planejada;
- status dos módulos;
- guia e exercícios do Módulo 0.

Não implemente pipeline, API, banco, Front-end ou Machine Learning neste módulo.

--------------------------------------------------
MÓDULO 1 — FONTE DE DADOS E EXPLORAÇÃO
--------------------------------------------------

Objetivos:

- identificar uma fonte oficial de dados públicos da ANP;
- documentar a fonte;
- analisar colunas, tipos e qualidade;
- trabalhar inicialmente com uma amostra pequena;
- criar um dicionário de dados;
- não baixar ou versionar arquivos excessivamente grandes;
- criar uma análise exploratória inicial;
- identificar dados ausentes, duplicados e inconsistentes.

Entregas possíveis:

- amostra de dados;
- script simples de leitura;
- relatório de exploração;
- dicionário de dados;
- testes básicos de leitura.

Caso o download automático não seja possível, explique como eu devo baixar manualmente o arquivo e onde colocá-lo.

--------------------------------------------------
MÓDULO 2 — INGESTÃO DA CAMADA RAW
--------------------------------------------------

Objetivos:

- criar o primeiro pipeline Python;
- receber um arquivo de entrada;
- verificar sua existência;
- validar extensão e colunas mínimas;
- copiar ou registrar o dado bruto;
- evitar sobrescrita indevida;
- criar logs;
- produzir uma saída reproduzível.

O módulo deverá focar apenas na ingestão bruta.

Não faça ainda todas as transformações.

--------------------------------------------------
MÓDULO 3 — LIMPEZA, TRANSFORMAÇÃO E VALIDAÇÃO
--------------------------------------------------

Objetivos:

- padronizar nomes de colunas;
- converter datas;
- converter preços;
- tratar valores ausentes;
- remover ou sinalizar duplicidades;
- padronizar estados, municípios e combustíveis;
- gerar dados processados;
- criar validações;
- registrar registros rejeitados;
- testar as transformações.

Explique claramente a diferença entre:

- dado bruto;
- dado processado;
- registro inválido;
- duplicidade;
- validação.

--------------------------------------------------
MÓDULO 4 — POSTGRESQL E MODELAGEM DE DADOS
--------------------------------------------------

Objetivos:

- criar o modelo de dados;
- explicar tabelas, colunas e relacionamentos;
- configurar PostgreSQL;
- utilizar variáveis de ambiente corretamente;
- criar scripts de criação das tabelas;
- carregar dados tratados;
- impedir duplicidades;
- criar consultas SQL iniciais;
- testar inserções e consultas.

Não coloque senhas no repositório.

Crie `.env.example`, mas não versione `.env`.

--------------------------------------------------
MÓDULO 5 — ANÁLISES E CONSULTAS SQL
--------------------------------------------------

Objetivos:

- calcular preço médio;
- calcular mínimo e máximo;
- comparar estados e municípios;
- analisar evolução temporal;
- criar consultas reutilizáveis;
- explicar agrupamentos, filtros e agregações;
- criar indicadores;
- validar os resultados.

As análises devem usar dados reais disponíveis.

Não invente números.

--------------------------------------------------
MÓDULO 6 — API BACK-END COM JAVA E SPRING BOOT
--------------------------------------------------

Objetivos:

- criar uma API principal em Java e Spring Boot;
- conectar com PostgreSQL;
- criar estrutura organizada por responsabilidades;
- disponibilizar poucos endpoints úteis;
- utilizar DTOs;
- validar parâmetros;
- tratar erros;
- documentar com OpenAPI ou Swagger;
- criar testes.

Endpoints iniciais possíveis:

- GET /api/prices
- GET /api/prices/summary
- GET /api/prices/history
- GET /api/locations/states
- GET /api/locations/cities

Não crie dezenas de endpoints.

Explique:

- controller;
- service;
- repository;
- entity;
- DTO;
- requisição;
- resposta;
- códigos HTTP.

--------------------------------------------------
MÓDULO 7 — DASHBOARD REACT E TYPESCRIPT
--------------------------------------------------

Objetivos:

- criar o Front-end;
- conectar com a API;
- apresentar indicadores;
- mostrar gráficos;
- adicionar filtros;
- tratar carregamento;
- tratar erros;
- manter responsividade;
- utilizar componentes reutilizáveis;
- não criar dados falsos quando a API estiver disponível.

Dashboard inicial:

- preço médio;
- preço mínimo;
- preço máximo;
- evolução histórica;
- comparação entre localidades;
- filtros por combustível, estado, município e período.

--------------------------------------------------
MÓDULO 8 — MACHINE LEARNING: BASELINE
--------------------------------------------------

Objetivos:

- definir claramente o problema de previsão;
- selecionar a variável alvo;
- preparar os dados;
- separar treino e teste respeitando a ordem temporal;
- criar um baseline simples;
- treinar um primeiro modelo compreensível;
- calcular métricas;
- comparar o modelo com o baseline;
- documentar limitações.

Explique:

- feature;
- target;
- treino;
- teste;
- baseline;
- erro;
- MAE;
- RMSE ou MAPE;
- overfitting;
- vazamento de dados.

Não use um modelo sofisticado sem necessidade.

Não diga que o modelo é bom sem comparar métricas.

--------------------------------------------------
MÓDULO 9 — PREVISÃO DISPONÍVEL PELA APLICAÇÃO
--------------------------------------------------

Objetivos:

- salvar o modelo treinado;
- criar um serviço Python simples para inferência, caso necessário;
- integrar a previsão com a aplicação;
- validar entradas;
- retornar previsão e informações da versão do modelo;
- exibir a previsão no dashboard;
- deixar claro que se trata de uma estimativa.

Não apresente previsão como certeza.

--------------------------------------------------
MÓDULO 10 — DETECÇÃO DE ANOMALIAS
--------------------------------------------------

Objetivos:

- definir o que é comportamento atípico;
- identificar variações incomuns;
- sinalizar preços fora do comportamento esperado;
- registrar o motivo do alerta;
- evitar acusações de fraude;
- criar testes;
- exibir anomalias no dashboard.

Utilize linguagem como:

“Comportamento estatisticamente atípico que merece análise.”

--------------------------------------------------
MÓDULO 11 — QUALIDADE, DOCKER E INTEGRAÇÃO CONTÍNUA
--------------------------------------------------

Objetivos:

- revisar testes;
- adicionar Docker quando fizer sentido;
- criar Docker Compose;
- configurar serviços;
- adicionar health checks;
- configurar lint;
- configurar GitHub Actions;
- executar builds;
- documentar o ambiente.

Não adicione Kubernetes.

Não adicione infraestrutura excessiva.

--------------------------------------------------
MÓDULO 12 — DOCUMENTAÇÃO PROFISSIONAL E DEPLOY
--------------------------------------------------

Objetivos:

- revisar README;
- criar diagrama de arquitetura;
- documentar instalação;
- documentar API;
- documentar dados;
- criar model card;
- documentar métricas;
- documentar limitações;
- preparar imagens e demonstração;
- preparar publicação;
- revisar segurança;
- revisar acessibilidade;
- revisar o projeto para o currículo e portfólio.

==================================================
9. MÓDULOS OPCIONAIS FUTUROS
==================================================

Os itens abaixo não devem ser implementados antes da conclusão do núcleo principal:

- DBT;
- Power BI;
- MLflow;
- RAPIDS;
- CUDA;
- comparação CPU versus GPU;
- RAG;
- assistente com LLM;
- Kafka;
- processamento em tempo real;
- observabilidade avançada.

Ao concluir o Módulo 12, analise comigo quais desses módulos realmente agregariam valor.

Não implemente todos apenas para aumentar o número de tecnologias.

==================================================
10. GIT E COMMITS
==================================================

Antes de executar comandos Git:

- verifique o estado atual;
- não sobrescreva histórico;
- não force push;
- não apague branches;
- não envie arquivos grandes;
- não envie `.env`;
- não faça push sem minha autorização.

Ao final de cada módulo, sugira uma mensagem de commit, por exemplo:

feat: implementa ingestão inicial de dados da ANP

Mas não execute commit ou push sem minha autorização explícita.

==================================================
11. RELATÓRIO FINAL NO CHAT
==================================================

Ao concluir cada módulo, apresente:

# Módulo XX concluído

## O que foi criado

## Arquivos criados

## Arquivos alterados

## Conceitos abordados

## Comandos executados

## Testes executados

## Resultado dos testes

## Erros encontrados e correções

## Limitações atuais

## Exercício que devo realizar sozinho

## Arquivos que devo estudar

## Mensagem de commit sugerida

## Próximo módulo previsto

Depois, pare e escreva exatamente:

“O módulo foi concluído. Revise a documentação, explique com suas palavras o que entendeu e realize os exercícios propostos. Digite apenas ‘sim’ quando estiver pronto para iniciar o próximo módulo.”

==================================================
12. INÍCIO DA EXECUÇÃO
==================================================

Agora:

1. Analise a pasta aberta.
2. Inicie somente o Módulo 0.
3. Não implemente nenhum módulo posterior.
4. Crie toda a documentação obrigatória do Módulo 0.
5. Execute as verificações aplicáveis.
6. Apresente o relatório.
7. Pare e aguarde minha autorização.