# Ingestão da camada raw

## 1. Propósito

A **camada raw** armazena o dado como ele foi recebido, antes de limpeza ou transformação. No FuelVision, o pipeline copia um CSV válido para `data/raw/` preservando exatamente seus bytes.

Isso cria uma evidência reproduzível da entrada. Se uma transformação futura produzir um resultado inesperado, será possível retornar ao arquivo preservado e investigar a origem.

## 2. O que o pipeline faz

```text
entrada CSV
→ existência e tipo do caminho
→ extensão .csv
→ cabeçalho UTF-8 separado por ;
→ colunas mínimas
→ SHA-256
→ cópia exclusiva
→ verificação de integridade
→ log e resumo no terminal
```

O pipeline não lê todas as linhas para analisar conteúdo. Ele lê somente o cabeçalho durante a validação e percorre os bytes para calcular o hash e copiar o arquivo.

## 3. Colunas mínimas

O cabeçalho deve conter:

- `Estado - Sigla`;
- `Municipio`;
- `Produto`;
- `Data da Coleta`;
- `Valor de Venda`;
- `Unidade de Medida`.

Essas colunas permitem reconhecer localidade, produto, data, preço e unidade. Colunas adicionais são aceitas e preservadas.

Esta é uma validação estrutural mínima. O pipeline não verifica ainda se estados, datas ou preços são válidos; essas regras pertencem ao módulo de transformação e validação.

## 4. Nome do arquivo raw

O destino segue o formato:

```text
<nome-original>__<12-primeiros-caracteres-do-sha256>.csv
```

Exemplo real:

```text
precos-combustiveis-amostra__d5dd2159be5b.csv
```

**Hash de conteúdo** é um identificador calculado a partir dos bytes. Usar parte do SHA-256 no nome permite que conteúdos diferentes recebam nomes diferentes mesmo quando o nome original é igual.

Os 12 primeiros caracteres são usados no nome para mantê-lo legível. O hash completo é exibido no terminal e no log. Se ocorrer uma colisão de nome, o conteúdo completo é conferido e o pipeline rejeita o conflito.

## 5. Proteção contra sobrescrita

O destino é aberto em modo exclusivo `xb`. Esse modo falha se o arquivo já existir.

Há três resultados possíveis:

| Situação                              | Status           | Comportamento                   |
| ------------------------------------- | ---------------- | ------------------------------- |
| destino não existe                    | `created`        | copia e verifica os bytes       |
| destino existe com o mesmo SHA-256    | `already_exists` | não copia nem sobrescreve       |
| destino existe com conteúdo diferente | erro             | interrompe e preserva o destino |

**Idempotência** significa que repetir uma operação com a mesma entrada não cria efeitos adicionais indevidos. No FuelVision, executar duas vezes a mesma ingestão mantém uma única cópia raw.

Se a cópia falhar no meio ou não passar na verificação final de hash, o arquivo parcial criado por aquela execução é removido.

## 6. Integridade

Antes da cópia, o pipeline calcula o SHA-256 da entrada. Depois, calcula o SHA-256 do destino.

```text
hash da entrada = hash do destino → cópia aceita
hash da entrada ≠ hash do destino → destino removido e erro informado
```

**Integridade** significa que o conteúdo chegou ao destino sem alteração. Essa comparação não confirma se os valores de negócio estão corretos; confirma somente igualdade de bytes.

## 7. Logs

Por padrão, o log é gravado em:

```text
logs/ingestion.log
```

Ele registra início, conclusão, status, destino, hash e tamanho. Falhas esperadas também são registradas.

**Log** é um registro cronológico de eventos da execução. Ele ajuda a responder quando uma ingestão ocorreu, qual entrada foi usada e por que uma execução falhou.

O log contém caminhos locais e horários, portanto não é uma saída determinística e não é versionado. O arquivo raw, por outro lado, possui nome e conteúdo determinados pela entrada.

## 8. Como executar

Na raiz do projeto:

```bash
python3 -m pipeline.ingest_raw data/samples/precos-combustiveis-amostra.csv
```

Para escolher outros diretórios:

```bash
python3 -m pipeline.ingest_raw caminho/entrada.csv \
  --output-dir caminho/raw \
  --log-file caminho/logs/ingestion.log
```

Saída esperada na primeira execução da amostra:

```text
status=created
destination=<caminho>/precos-combustiveis-amostra__d5dd2159be5b.csv
sha256=d5dd2159be5bd72228393f18b60a0c6eeccd061b9870fe3f0542b1a7a1620b23
bytes=9937
```

Na repetição, o status esperado é `already_exists`.

## 9. Códigos de saída

- `0`: ingestão criada ou conteúdo já existente;
- `1`: falha esperada de validação, leitura, cópia, diretório ou conflito;
- `2`: uso incorreto dos argumentos, gerado pelo `argparse`.

Um **código de saída** é um número devolvido ao sistema operacional. Zero representa sucesso; um valor diferente de zero permite que scripts e ferramentas detectem falhas.

## 10. Como testar

```bash
python3 -m unittest discover -s tests -v
PYTHONPYCACHEPREFIX=/tmp/fuelvision-module-02-pycache \
  python3 -m py_compile pipeline/ingest_raw.py tests/test_ingest_raw.py
```

Os testes usam diretórios temporários. Eles não escrevem seus arquivos de teste em `data/raw/`.

## 11. O que não pertence a este módulo

- download automático da ANP;
- conversão de datas ou preços no arquivo raw;
- remoção de espaços ou duplicidades;
- preenchimento de valores ausentes;
- geração de dados processados;
- banco, API, Front-end ou Machine Learning.
