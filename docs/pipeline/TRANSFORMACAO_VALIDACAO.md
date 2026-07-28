# Limpeza, transformação e validação

## 1. Propósito

O Módulo 3 converte um CSV da camada raw em uma saída processada com formato previsível. Registros que não atendem às regras não desaparecem: eles são gravados separadamente com seus motivos.

**Transformação** altera a representação do dado para um formato padronizado. **Validação** verifica se o registro atende às regras definidas. Transformar `02/01/2026` em `2026-01-02` muda o formato; rejeitar `31/02/2026` aplica uma validação.

## 2. Fluxo

```text
raw CSV
→ esquema completo
→ leitura linha a linha
→ normalização
→ conversão
→ validações
→ chave de negócio
├── válido e único → processed CSV
└── inválido ou duplicado → rejected CSV
→ manifest JSON
→ log
```

O processamento é feito uma linha por vez. Esse modelo reduz o uso de memória quando o arquivo cresce.

## 3. Diferenças importantes

### Dado bruto

É a entrada preservada byte a byte pelo Módulo 2. Pode conter espaços, datas brasileiras, pontuação em identificadores e valores ausentes.

### Dado processado

É um registro aceito, com nomes e valores padronizados. Ele ainda não está em banco de dados, mas possui um contrato estável para o módulo seguinte.

### Registro inválido

É uma linha que viola ao menos uma regra. Ela é copiada para a saída de rejeitados com número da linha e motivos.

### Duplicidade

É a repetição da chave CNPJ da revenda + produto + data. Se todo o registro processado for igual, o motivo é `duplicate_record`. Se a chave for igual e algum outro valor mudar, o motivo é `conflicting_duplicate`.

### Validação

É uma regra explícita que produz aprovação ou um motivo de rejeição. Uma validação não corrige silenciosamente um valor desconhecido.

## 4. Contrato de entrada

O CSV deve possuir exatamente as 16 colunas oficiais conhecidas, sem nomes duplicados ou adicionais. A ordem pode mudar porque a leitura associa valores pelos nomes.

Essa regra evita ignorar silenciosamente uma coluna nova da fonte. Quando o esquema oficial mudar, o projeto deverá analisar a mudança antes de atualizar o contrato.

## 5. Padronizações

| Origem                         | Processado                   | Regra                                                |
| ------------------------------ | ---------------------------- | ---------------------------------------------------- |
| nomes em português com espaços | nomes em inglês `snake_case` | esquema em `pipeline/schema.py`                      |
| espaços externos e repetidos   | espaço simples               | aplicado aos textos                                  |
| estado, região e município     | maiúsculas                   | acentos preservados                                  |
| CNPJ formatado                 | 14 dígitos                   | pontuação removida e dígitos verificadores validados |
| CEP formatado                  | 8 dígitos                    | pontuação removida                                   |
| `dd/mm/aaaa`                   | `aaaa-mm-dd`                 | data ISO                                             |
| decimal com vírgula            | decimal com ponto            | `Decimal`, sem `float`                               |
| produto da fonte               | nome canônico                | tabela explícita de aliases                          |
| unidade da fonte               | `BRL/liter` ou `BRL/m3`      | tabela explícita de aliases                          |

## 6. Valores ausentes

Campos opcionais:

- `Complemento` → `address_complement` vazio;
- `Valor de Compra` → `purchase_price` vazio.

Esses valores não são preenchidos com zero porque vazio e zero possuem significados diferentes.

Os demais campos textuais necessários geram motivos como `missing_municipality` ou `missing_retailer_name`.

## 7. Validações aplicadas

- região pertencente a `N`, `NE`, `CO`, `SE` ou `S`;
- estado pertencente às 27 siglas brasileiras;
- estado correspondente à região;
- campos textuais necessários não vazios;
- CNPJ com 14 dígitos e dois dígitos verificadores corretos;
- CEP com 8 dígitos;
- produto conhecido;
- data real no formato esperado;
- preços informados positivos, finitos e decimais;
- unidade conhecida e compatível com o produto;
- linha sem valores adicionais além do cabeçalho.

Uma linha pode registrar vários motivos simultaneamente. Isso reduz ciclos de correção, pois a investigação recebe todos os problemas encontrados naquela execução.

## 8. Motivos de rejeição

Os motivos atuais incluem:

- `invalid_region_code`;
- `invalid_state_code`;
- `state_region_mismatch`;
- `missing_<campo>`;
- `invalid_retailer_cnpj`;
- `invalid_postal_code`;
- `invalid_product`;
- `invalid_collection_date`;
- `invalid_sale_price`;
- `invalid_purchase_price`;
- `invalid_unit`;
- `product_unit_mismatch`;
- `unexpected_extra_values`;
- `duplicate_record`;
- `conflicting_duplicate`.

O CSV rejeitado mantém as 16 colunas originais e acrescenta:

- `source_row_number`;
- `rejection_reasons`.

## 9. Saídas

Para a entrada `arquivo.csv`, a versão `v1` produz:

```text
arquivo__v1__processed.csv
arquivo__v1__rejected.csv
arquivo__v1__manifest.json
```

O processado contém somente registros aceitos. O rejeitado sempre possui cabeçalho, mesmo quando não há rejeições.

O **manifesto** é um JSON determinístico com:

- versão da transformação;
- nome e SHA-256 da origem;
- contagens de lidos, aceitos, rejeitados e duplicados;
- nomes e SHA-256 das duas saídas CSV.

Ele não contém horário. Horários ficam no log, pois não devem mudar uma saída reproduzível.

## 10. Proteção das saídas

As três saídas usam nomes determinísticos e não são sobrescritas:

- mesmo nome e mesmo conteúdo → `already_exists`;
- mesmo nome e conteúdo diferente → erro de conflito;
- conflitos preexistentes nas três saídas → detectados antes da publicação;
- falha antes da publicação → temporários removidos.

## 11. Como executar

Primeiro, crie ou confirme o raw:

```bash
python3 -m pipeline.ingest_raw data/samples/precos-combustiveis-amostra.csv
```

Depois, transforme:

```bash
python3 -m pipeline.transform_data \
  data/raw/precos-combustiveis-amostra__d5dd2159be5b.csv
```

Também é possível escolher saída e log:

```bash
python3 -m pipeline.transform_data caminho/raw.csv \
  --output-dir caminho/processed \
  --log-file caminho/logs/transformation.log
```

## 12. Resultado real da amostra

```text
status=created
rows_read=60
accepted=60
rejected=0
```

Na segunda execução, `status=already_exists`.

Hashes observados:

- origem: `d5dd2159be5bd72228393f18b60a0c6eeccd061b9870fe3f0542b1a7a1620b23`;
- processado: `e20b51bbe82e1f43bd410085a254fdf081bf7390d8317369f3da84b67156a67c`;
- rejeitados: `cc955eb6c05982d4f19e0561de9df3bbd4ad2ed637f6f04310e13647e10c8bbb`.

## 13. Como testar

```bash
python3 -m unittest discover -s tests -v
PYTHONPYCACHEPREFIX=/tmp/fuelvision-module-03-pycache \
  python3 -m py_compile pipeline/schema.py pipeline/ingest_raw.py pipeline/transform_data.py tests/test_transform_data.py
```

## 14. Limitações

- regras construídas a partir do esquema conhecido da ANP;
- conjunto de aliases de produto limitado aos valores estudados;
- duplicidade definida por uma chave de negócio inicial;
- processamento local e sequencial;
- sem banco de dados ou restrições SQL;
- sem correção automática de registros rejeitados;
- sem análise estatística sobre a população completa.
