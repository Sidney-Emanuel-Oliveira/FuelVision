# Dashboard React e TypeScript do FuelVision

## 1. O que foi construído

O Módulo 7 criou um dashboard Web responsivo que consulta a API do FuelVision e apresenta:

- preço médio, mínimo e máximo;
- evolução diária dos três indicadores;
- comparação do preço médio entre estados;
- filtros por combustível, estado, município e período;
- mensagens específicas para carregamento, erro e consulta vazia;
- tabelas alternativas com os valores utilizados nos gráficos;
- painel de estimativa com produto, data, versão, MAE e limitações do estimador;
- painel de anomalias com preço, limites, referência e motivo do alerta.

O dashboard não cria observações nem possui uma base fictícia de reserva. Se a API estiver indisponível, a interface informa o erro.

## 2. Por que isso é necessário

Nos módulos anteriores, os indicadores já podiam ser consultados com SQL ou JSON. O dashboard transforma esses contratos técnicos em uma interface que ajuda uma pessoa a explorar os recortes sem escrever comandos.

```text
usuário → filtros React → cliente HTTP → API Spring Boot → PostgreSQL
        ← componentes e gráficos ← JSON validado pelo contrato

usuário → painel de estimativa → API Spring Boot → serviço Python → artefato
        ← estimativa identificada por versão, período e MAE

usuário → filtros aplicados → API Spring Boot → PostgreSQL calcula IQR
        ← alertas com limites e linguagem responsável
```

A interface não recalcula média, mínimo ou máximo. Esses valores continuam sob responsabilidade da API e do banco, evitando regras duplicadas em duas aplicações.

## 3. Conceitos utilizados

### Componente

**Componente** é uma função que representa uma parte reutilizável da interface. Neste módulo, `MetricCard` recebe rótulo, valor, detalhe e cor. O mesmo componente exibe os três indicadores, o que mantém estrutura e acessibilidade consistentes.

### Props

**Props** são as entradas de um componente React. `DashboardFilters` recebe a lista de produtos, os filtros atuais e funções para comunicar alterações ao `App`. Elas são importantes porque tornam as dependências do componente explícitas.

### Estado

**Estado** é uma informação que pode mudar durante o uso e provocar uma nova renderização. O FuelVision mantém filtros em edição, filtros aplicados, dados, carregamento e erros. A separação entre filtro em edição e filtro aplicado impede uma nova consulta a cada tecla.

### Hook

**Hook** é uma função do React que permite usar recursos como estado e efeitos. `useState` guarda valores, `useEffect` executa consultas quando uma dependência muda e `useMemo` deriva o texto do recorte atual.

### TypeScript

**TypeScript** adiciona tipos estáticos ao JavaScript. Interfaces como `PriceSummary` documentam o formato esperado da API e fazem o compilador apontar usos incompatíveis antes da aplicação chegar ao navegador. Tipos ajudam, mas não substituem uma validação de dados em tempo de execução quando a fonte não é confiável.

### Cliente HTTP

**Cliente HTTP** é o bloco que monta endereços, envia requisições e interpreta respostas. `fuelVisionApi.ts` centraliza essas tarefas. Assim, componentes não repetem `fetch`, query parameters ou mensagens de conectividade.

### Renderização condicional

**Renderização condicional** decide qual conteúdo aparece de acordo com o estado. O painel mostra carregamento durante a consulta, erro quando ela falha, vazio quando a resposta não possui dados e os indicadores quando existe resultado.

### Responsividade

**Responsividade** é a adaptação do layout a diferentes larguras. As grades usam CSS Grid e mudam de três colunas para uma em telas menores. Esse conceito é importante porque o mesmo conteúdo precisa continuar utilizável em computador e celular.

### Proxy de desenvolvimento

**Proxy de desenvolvimento** é um intermediário local. O navegador chama `/api` na porta 5173 e o Vite encaminha para a API na porta 8080. Isso resolve a integração local sem liberar origens no Back-end. Não é um mecanismo de produção.

### Mock

**Mock** é um substituto controlado utilizado em teste. Os testes simulam respostas HTTP para reproduzir sucesso e erro de forma determinística. Isso não cria dados fictícios no dashboard em produção: os mocks não entram no pacote gerado pelo build.

## 4. Como o fluxo funciona

### Inicialização

```text
App monta
→ consulta resumo sem filtro para descobrir produtos reais
→ consulta estados disponíveis
→ seleciona o primeiro produto devolvido
→ solicita resumo, histórico e comparação
→ renderiza indicadores e gráficos
```

### Aplicação de filtros

```text
usuário altera campos
→ draftFilters muda sem consultar a API
→ usuário seleciona “Aplicar filtros”
→ período é validado
→ appliedFilters recebe uma cópia
→ requisições anteriores são canceladas
→ novo recorte substitui o resultado
```

### Comparação regional

```text
estados disponíveis
→ uma consulta de resumo por UF
→ estados sem observações são removidos
→ gráfico de barras recebe preço médio e contagem
```

Esta decisão reutiliza o contrato existente e evita antecipar um endpoint do Back-end. A desvantagem é realizar várias requisições; ela está registrada nas limitações.

## 5. Arquivos envolvidos

| Caminho | Responsabilidade |
| --- | --- |
| `frontend/package.json` | dependências e comandos de desenvolvimento, teste e build |
| `frontend/vite.config.ts` | React, ambiente de teste e proxy local `/api` |
| `frontend/src/App.tsx` | coordenação dos estados, efeitos e blocos principais |
| `frontend/src/api/fuelVisionApi.ts` | cliente HTTP, query parameters e tratamento dos erros |
| `frontend/src/types/api.ts` | contratos TypeScript das respostas e filtros |
| `frontend/src/components/DashboardFilters.tsx` | formulário e comunicação dos filtros |
| `frontend/src/components/MetricCard.tsx` | cartão reutilizável de indicador |
| `frontend/src/components/PriceHistoryChart.tsx` | gráfico de linhas e tabela histórica |
| `frontend/src/components/LocationComparisonChart.tsx` | gráfico de barras e tabela por UF |
| `frontend/src/components/StatusPanel.tsx` | carregamento, erro, vazio e nova tentativa |
| `frontend/src/components/PredictionPanel.tsx` | formulário, metadados e resultado da estimativa |
| `frontend/src/components/AnomalyPanel.tsx` | alertas IQR, limites e estados independentes |
| `frontend/src/utils/formatters.ts` | formatação de moeda, unidade e data em pt-BR |
| `frontend/src/*.test.tsx` e `*.test.ts` | testes do fluxo da tela e do cliente HTTP |
| `frontend/src/App.css` e `index.css` | identidade visual, foco, grades e media queries |

## 6. Código por blocos

### Tipos e cliente HTTP

- **Responsabilidade:** transformar filtros em URLs e JSON em objetos tipados;
- **Entrada:** produto, UF, município, datas e `AbortSignal` opcional;
- **Processamento:** remove parâmetros vazios, codifica caracteres e verifica o status HTTP;
- **Saída:** `Promise` com resumo, histórico ou localidade;
- **Comunicação:** chama os endpoints analíticos, preditivos e de anomalias;
- **Possíveis erros:** API parada, resposta `400`, banco indisponível ou requisição cancelada;
- **Verificação:** `fuelVisionApi.test.ts` confere URLs, erro seguro e comparação.

### Estado e efeitos do App

- **Responsabilidade:** coordenar opções, filtros, consultas e resultados;
- **Entrada:** interações do usuário e respostas do cliente HTTP;
- **Processamento:** inicia carregamento, cancela a consulta anterior e separa erro de vazio;
- **Saída:** propriedades para componentes visuais;
- **Comunicação:** componentes informam eventos ao `App`, que chama o cliente;
- **Possíveis erros:** resposta atrasada sobrescrever um filtro novo;
- **Prevenção:** cada efeito cria um `AbortController` e cancela a requisição na limpeza.

### Filtros

- **Responsabilidade:** coletar o recorte desejado;
- **Entrada:** listas reais de produto, UF e município;
- **Processamento:** limpa município quando a UF muda e restringe as datas no HTML;
- **Saída:** novo `PriceFilters` e evento de aplicação;
- **Possíveis erros:** data inicial posterior à final ou municípios indisponíveis;
- **Verificação:** testes de período, seleção de UF e carregamento de município.

### Indicadores e gráficos

- **Responsabilidade:** apresentar os valores sem alterar os cálculos da API;
- **Entrada:** `PriceSummary`, pontos históricos e resumos por UF;
- **Processamento:** somente formatação para pt-BR;
- **Saída:** cartões, linhas, barras e tabelas;
- **Possíveis erros:** gráfico sem espaço ou lista vazia;
- **Prevenção:** contêiner com altura, layout responsivo e estado vazio independente.

### Estados da interface

- **Responsabilidade:** dizer claramente o que está acontecendo;
- **Entrada:** booleanos de carregamento, mensagens e presença de dados;
- **Saída:** `role="status"` para carregamento/vazio e `role="alert"` para erros;
- **Possíveis erros:** tratar uma resposta vazia como falha;
- **Verificação:** testes diferentes para erro e lista sem produtos.

## 7. Como executar

Pré-requisitos:

- Node.js compatível com Vite 8; o ambiente validado utilizou Node.js 26.4.0;
- npm; o ambiente validado utilizou npm 11.18.0;
- API e PostgreSQL configurados conforme os módulos anteriores.

Terminal 1, na raiz:

```bash
backend/scripts/run.sh
```

Terminal 2:

```bash
cd frontend
npm install
npm run dev
```

Acesse `http://localhost:5173`.

Se a API estiver em outra origem, copie `frontend/.env.example` para `frontend/.env.local` e preencha:

```text
VITE_API_BASE_URL=https://api.exemplo.com
```

Nesse caso, a API publicada também precisará permitir a origem do Front-end. Essa configuração de produção ainda não pertence ao módulo atual.

## 8. Como testar

Na pasta `frontend`:

```bash
npm run typecheck
npm run lint
npm run format:check
npm test
npm run build
```

- `typecheck` procura incompatibilidades TypeScript;
- `lint` procura padrões problemáticos;
- `format:check` confirma a formatação;
- `test` executa testes determinísticos com mocks;
- `build` produz os arquivos estáticos em `dist/`.

`dist/`, `node_modules/` e arquivos `.env` locais não são versionados.

## 9. Decisões técnicas

### Vite em vez de Create React App

- escolha: Vite com modelo oficial React/TypeScript;
- alternativa: Create React App;
- vantagem: ambiente atual, inicialização rápida e build otimizado;
- desvantagem: o Vite transpila TypeScript, mas a checagem de tipos precisa de `tsc` separado;
- motivo: Create React App foi descontinuado e o Vite oferece o recorte necessário sem um framework de aplicação completo.

### Fetch nativo em vez de Axios

- escolha: `fetch` do navegador;
- alternativa: biblioteca Axios;
- vantagem: nenhuma dependência para uma necessidade pequena;
- desvantagem: tratamento de erro e montagem de URL precisam ser implementados;
- motivo: o contrato atual ainda é pequeno e não justifica uma abstração maior.

### Recharts em vez de SVG manual

- escolha: componentes Recharts;
- alternativa: construir eixos, escalas e interação diretamente em SVG;
- vantagem: gráficos responsivos e legíveis com menos código específico;
- desvantagem: aumenta o tamanho do JavaScript de produção;
- motivo: permite concentrar o módulo em componentes, dados e estados da interface.

Os componentes de gráfico usam `lazy` e `Suspense`. Isso é **carregamento sob demanda**: o navegador baixa o código de visualização apenas quando existe um resultado a apresentar. No build validado, o arquivo inicial caiu de aproximadamente 593 kB para 203 kB; os módulos de gráficos ficaram em arquivos separados.

### Proxy local em vez de CORS amplo

- escolha: proxy `/api` do Vite;
- alternativa: permitir `*` no Back-end;
- vantagem: integração local sem abrir a API para qualquer origem;
- desvantagem: uma implantação separada exigirá configuração explícita de CORS;
- motivo: ainda não existe arquitetura de deploy definida.

### Requisições por estado em vez de novo endpoint

- escolha: reutilizar `/api/prices/summary` para cada UF;
- alternativa: criar agora um endpoint agregado por localidade;
- vantagem: preserva o contrato aprovado no Módulo 6;
- desvantagem: quantidade de requisições cresce com o número de UFs;
- motivo: o volume inicial é pequeno e um novo endpoint deve surgir somente com necessidade e contrato próprios.

## 10. Acessibilidade e responsividade

- campos possuem rótulos associados;
- foco por teclado recebe contorno visível;
- carregamentos e erros usam regiões semânticas;
- cor não é o único meio de transmitir o nome de um indicador;
- gráficos possuem legenda, tooltip e tabela alternativa;
- a preferência `prefers-reduced-motion` reduz animações;
- a grade muda para uma coluna abaixo de 700 px.

Essas medidas formam uma base, mas não substituem uma auditoria completa com leitores de tela e usuários reais.

## 11. Resultados verificados

Os números completos e comandos executados estão no relatório local do Módulo 7. A integração manual confirmou:

- documento HTML servido pelo Vite;
- proxy local entregando respostas `200` da API;
- resumo GNV + RJ + MACAE com 2 observações e média 4,935;
- histórico de GNV com 4 pontos;
- 13 estados disponíveis na amostra;
- inspeção visual em largura de desktop com Chrome headless.

Esses resultados descrevem a amostra local de 60 observações, não o mercado brasileiro.

## 12. Limitações atuais

- os dados continuam sendo uma amostra pequena e não representativa;
- a comparação regional realiza uma requisição de resumo por UF;
- o histórico solicita no máximo 100 pontos, limite atual da API;
- não existe autenticação, cache ou limite por cliente;
- uma implantação em origens diferentes exigirá CORS explícito;
- a auditoria Lighthouse atingiu 100/100 em acessibilidade, mas ainda não houve
  avaliação humana com leitor de tela ou outras tecnologias assistivas;
- Recharts aumenta o pacote JavaScript inicial;
- a previsão é uma estimativa simples, limitada aos produtos e às datas informados pelo modelo;
- uma falha preditiva não remove os indicadores analíticos já carregados;
- os alertas IQR podem representar diferenças regionais legítimas;
- uma anomalia não comprova fraude, erro ou irregularidade;
- não há intervalo de incerteza; Docker, CI e preparação de deploy foram
  acrescentados nos Módulos 11 e 12.

## Extensão do Módulo 9: painel de estimativa

O `PredictionPanel` consulta os metadados do estimador ao iniciar, restringe o formulário aos produtos e datas suportados e envia a solicitação somente após a ação do usuário. Ele não apresenta o número como certeza: o resultado inclui **estimativa**, unidade, versão, data final do treino, MAE e aviso de limitação.

```text
metadados do modelo
→ opções e limites do formulário
→ produto + data
→ POST /api/predictions
→ estimativa ou erro isolado no painel
```

Os testes verificam a seleção do produto atual, o corpo enviado, a apresentação da estimativa, os limites de data e a indisponibilidade do serviço. A suíte do Front-end possui 16 testes após essa extensão.

## Extensão do Módulo 10: painel de anomalias

O `AnomalyPanel` recebe os filtros aplicados, consulta `/api/prices/anomalies` e apresenta carregamento, erro, vazio ou cartões. Cada cartão informa preço, direção, localidade, data, limites, tamanho da referência, método e motivo.

```text
appliedFilters
→ getAnomalies
→ resposta paginada
→ preço e limites formatados
→ alerta acompanhado de contexto
```

Uma falha nesta consulta permanece isolada e não remove os indicadores, a previsão ou os gráficos. Os testes verificam os estados visuais, nova tentativa e codificação dos filtros. A suíte possui 20 testes após o Módulo 10.

## 13. O que compreender agora

- como componentes recebem props e comunicam eventos;
- por que estado em edição e estado aplicado são diferentes;
- como o cliente HTTP isola o acesso à API;
- como carregamento, erro e vazio representam situações diferentes;
- por que TypeScript e testes ajudam a preservar o contrato;
- como media queries e grades tornam a tela responsiva;
- por que mocks de teste não são dados falsos de produção.

## 14. O que poderá ser aprofundado depois

- cache de requisições com ferramentas especializadas;
- validação de resposta em tempo de execução;
- paginação completa do histórico;
- divisão do pacote por carregamento sob demanda;
- testes de ponta a ponta em navegador;
- auditoria WCAG completa;
- configuração de CORS e deploy.

Esses pontos não são necessários para compreender o fluxo atual e não devem ser confundidos com entregas já realizadas.

## 15. Referências oficiais

- [React: usando TypeScript](https://react.dev/learn/typescript)
- [React: componentes](https://react.dev/)
- [Vite: primeiros passos](https://vite.dev/guide/)
- [Vite: suporte a TypeScript](https://vite.dev/guide/features#typescript)
- [Vitest: guia](https://vitest.dev/guide/)
- [Testing Library: React](https://testing-library.com/docs/react-testing-library/intro/)
- [Recharts: instalação](https://recharts.github.io/en-US/guide/)
- [Recharts: primeiros passos](https://recharts.github.io/en-US/guide/getting-started/)
