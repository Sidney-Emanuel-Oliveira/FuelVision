# Arquitetura progressiva planejada

## 1. Propósito

Este documento descreve como o FuelVision poderá crescer. Ele não afirma que os componentes já foram implementados.

**Arquitetura de software** é a organização das partes de um sistema, de suas responsabilidades e das formas de comunicação entre elas. Ela é importante porque evita misturar, por exemplo, preparação de dados com apresentação de gráficos.

## 2. Estado real no Módulo 0

Existem apenas arquivos de planejamento, aprendizado, status e configuração do Git. Não existem componentes executáveis da plataforma.

Fluxo atual:

```text
plano oficial → documentação da proposta → arquitetura planejada → status e aprendizado
```

## 3. Visão futura

Quando os módulos correspondentes forem autorizados e concluídos, o fluxo poderá evoluir para:

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

Os experimentos de Machine Learning dependerão de dados tratados e avaliados. Seus resultados poderão ser integrados à aplicação somente em módulos posteriores.

## 4. Responsabilidades futuras

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

Estas responsabilidades são somente planejamento. Pastas e códigos correspondentes serão criados apenas nos módulos oficiais.

## 5. Dependências entre etapas

Uma etapa posterior depende de resultados confiáveis da etapa anterior:

- a limpeza depende do conhecimento das colunas da fonte;
- o banco depende da definição dos dados tratados;
- a API depende das consultas e do modelo de dados;
- o dashboard depende dos contratos da API;
- o Machine Learning depende de dados preparados e de um problema definido.

**Contrato** é uma definição de entrada e saída que permite a comunicação entre componentes. Por exemplo, futuramente a API definirá quais campos uma consulta recebe e quais campos devolve. Esse contrato ainda não será criado.

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

## 8. Limitações deste documento

Esta é uma visão inicial. Formatos de dados, tabelas, endpoints, componentes visuais e algoritmos ainda não foram definidos porque dependem de descobertas e decisões dos módulos futuros.
