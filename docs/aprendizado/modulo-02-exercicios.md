# Exercícios do Módulo 02 — Ingestão da Camada Raw

Não há respostas neste arquivo. Os exercícios podem ser realizados posteriormente sem bloquear a progressão funcional.

## 1. Perguntas teóricas

1. Qual é a diferença entre camada raw e dado processado?
2. Por que o pipeline calcula SHA-256 antes e depois da cópia?
3. O que significa uma ingestão ser idempotente?
4. Por que colunas adicionais são aceitas, mas colunas mínimas ausentes são rejeitadas?
5. Qual é a diferença entre um log e um teste automatizado?

## 2. Exercícios práticos

1. Execute a ingestão duas vezes e compare os status apresentados.
2. Use `shasum -a 256` para comparar manualmente a amostra e sua cópia raw.
3. Execute o pipeline com `--output-dir` e `--log-file` apontando para uma pasta temporária e inspecione os resultados.

## 3. Exercício de depuração

Crie em uma pasta temporária um CSV que possua apenas `Municipio;Produto`. Execute o pipeline, identifique as colunas relatadas como ausentes e explique por que nenhum arquivo raw deve ser criado.

## 4. Exercício de modificação do código

Crie um teste que confirma a aceitação da extensão `.CSV` em letras maiúsculas. Não altere a validação antes de executar o novo teste e observar o comportamento atual.

## 5. Pergunta sobre limitações

Por que um arquivo pode passar pela ingestão raw e ainda conter datas, preços ou registros de negócio inválidos?

## 6. Pergunta sobre decisões técnicas

Quais são a vantagem e a desvantagem de usar parte do SHA-256 no nome em vez de data e hora?
