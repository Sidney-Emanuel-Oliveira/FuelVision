# Arquitetura progressiva planejada

## 1. Propósito

Este documento descreve como o FuelVision poderá crescer. Ele não afirma que os componentes já foram implementados.

**Arquitetura de software** é a organização das partes de um sistema, de suas responsabilidades e das formas de comunicação entre elas. Ela é importante porque evita misturar, por exemplo, preparação de dados com apresentação de gráficos.

## 2. Estado real no Módulo 11

Os componentes planejados nos módulos anteriores foram implementados e agora
podem ser executados diretamente ou em contêineres.

Fluxo atual da aplicação:

```text
amostra controlada → transformação → PostgreSQL → Spring Boot → Nginx + React
                                              ↘ serviço Python de estimativas
```

O Docker Compose cria quatro serviços: `postgres`, `prediction`, `backend` e
`frontend`. Health checks controlam a ordem de inicialização. A integração
contínua repete lint, testes, builds, inicialização e smoke tests no GitHub.

## 3. Visão de evolução

O fluxo funcional já atingiu a seguinte arquitetura:

```text
fonte pública
    ↓
ingestão de dados brutos
    ↓
limpeza e validação
    ↓
PostgreSQL
    ↓
consultas e API
    ↓
dashboard
```

O modelo simples foi avaliado, persistido e integrado como estimativa
experimental. A detecção IQR também está disponível, sempre com linguagem que
não acusa fraude.

## 4. Responsabilidades atuais

### Dados

Receber arquivos públicos, preservar a versão bruta, padronizar registros e rejeitar entradas inválidas de maneira rastreável.

### Banco de dados

Armazenar dados tratados, aplicar restrições e oferecer consultas consistentes.

### Back-end

Aplicar regras de consulta, validar parâmetros e disponibilizar respostas por uma API.

### Front-end

Consumir a API e apresentar indicadores, filtros, estados de carregamento e erros.

### Machine Learning

Definir problemas mensuráveis, separar dados corretamente, comparar modelos com uma referência simples e comunicar incertezas.

Essas responsabilidades existem no repositório. O Módulo 12 poderá melhorar a
documentação profissional e tratar o deploy, mas não foi antecipado aqui.

## 5. Dependências entre etapas

Uma etapa posterior depende de resultados confiáveis da etapa anterior:

- a limpeza depende do conhecimento das colunas da fonte;
- o banco depende da definição dos dados tratados;
- a API depende das consultas e do modelo de dados;
- o dashboard depende dos contratos da API;
- o Machine Learning depende de dados preparados e de um problema definido.

**Contrato** é uma definição de entrada e saída que permite a comunicação entre
componentes. No estado atual, DTOs Java, modelos Pydantic e tipos TypeScript
representam os contratos usados pela API e pelo dashboard.

## 6. Decisões iniciais

### Desenvolvimento modular

Escolha: entregar uma capacidade de cada vez.

- vantagem: facilita estudo, revisão e correção;
- desvantagem: a aplicação completa demora mais para aparecer;
- motivo: reduz o risco de construir partes sobre fundamentos ainda não verificados.

### Documentação antes do código funcional

Escolha: registrar propósito, limites e progressão no Módulo 0.

- vantagem: oferece uma referência para decisões futuras;
- desvantagem: ainda não gera uma funcionalidade visível ao usuário final;
- motivo: evita antecipação e uso de tecnologias sem necessidade.

### Tecnologias somente no módulo necessário

Escolha: não instalar dependências agora.

- vantagem: mantém o ambiente simples e cada adoção justificável;
- desvantagem: versões atuais poderão precisar de ajuste quando forem realmente usadas;
- motivo: uma ferramenta disponível no computador não é automaticamente uma dependência do projeto.

## 7. Regras de segurança e versionamento

- credenciais devem ficar fora do repositório;
- `.env` não deve ser versionado;
- grandes arquivos brutos, processados e modelos gerados devem ficar fora do Git;
- resultados precisam indicar fonte, processo e limitações;
- nenhuma etapa deve ocultar erros para aparentar sucesso.

## 8. Limitações atuais

- a arquitetura executa somente a amostra controlada e não representativa;
- os contêineres são destinados a desenvolvimento e CI;
- não existem TLS, backup, registry de imagens ou gestão profissional de segredos;
- health checks indicam disponibilidade, não desempenho;
- a CI valida o sistema, mas não realiza deploy;
- o Módulo 12 ainda não foi iniciado.
