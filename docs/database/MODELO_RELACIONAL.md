# Modelo relacional do FuelVision

## 1. Propósito

O Módulo 4 armazena os dados processados em PostgreSQL sem repetir todas as informações em cada observação de preço.

**Modelo relacional** é uma organização de dados em tabelas conectadas por chaves. No FuelVision, uma observação aponta para uma revenda e um produto. Esse modelo é importante porque o banco consegue impedir referências inexistentes e duplicidades de negócio.

## 2. Visão dos relacionamentos

```text
regions 1 ─── N states 1 ─── N municipalities 1 ─── N retailers
                                                            │
                                                            1
                                                            │
                                                            N
products 1 ─────────────────────────────── N price_observations
```

O símbolo `1 ─── N` significa **um para muitos**. Um estado pode possuir muitos municípios, mas cada município do modelo pertence a um estado.

## 3. Tabelas

### `regions`

Mantém os cinco códigos de região do Brasil. `code` é a chave primária.

### `states`

Mantém as 27 unidades federativas. `region_code` é uma chave estrangeira para `regions`, portanto um estado não pode apontar para uma região inexistente.

### `municipalities`

Mantém os municípios que aparecem nos dados carregados. A combinação `state_code + name` é única, porque municípios com o mesmo nome podem existir em estados diferentes.

### `products`

Mantém os seis combustíveis aceitos e sua unidade. A unidade faz parte do domínio do produto: GNV usa `BRL/m3`; os demais produtos atuais usam `BRL/liter`.

### `retailers`

Mantém CNPJ, nome, endereço, bandeira e município da revenda. O CNPJ é único e continua armazenado como texto para preservar zeros à esquerda.

### `price_observations`

Mantém data, preço de venda e preço de compra opcional. A tabela aponta para `retailers` e `products` por chaves estrangeiras.

A **chave de negócio** é:

```text
retailer_id + product_id + collection_date
```

O PostgreSQL aplica uma restrição `UNIQUE` sobre essa combinação. Uma segunda observação do mesmo produto, revenda e data é rejeitada mesmo que outro programa tente inseri-la.

## 4. Tipos de dados

| Dado             | Tipo PostgreSQL  | Motivo                                                    |
| ---------------- | ---------------- | --------------------------------------------------------- |
| identificadores  | `identity`       | o banco gera valores internos sem depender do CSV         |
| CNPJ e CEP       | `char`           | são identificadores, não números usados em cálculos       |
| data             | `date`           | valida datas e permite operações temporais futuras        |
| preços           | `numeric(10, 3)` | representa decimais com precisão, sem aproximação binária |
| campo opcional   | aceita `NULL`    | diferencia ausência de preço de compra do valor zero      |
| instante técnico | `timestamptz`    | registra data, hora e fuso da carga ou atualização        |

**NULL** representa ausência de valor. No FuelVision, `purchase_price` vazio vira `NULL`; ele não vira zero porque zero significaria um preço conhecido igual a zero.

## 5. Restrições

**Restrição** é uma regra aplicada pelo próprio banco. Ela continua protegendo os dados mesmo quando a inserção não vem do pipeline Python.

- `PRIMARY KEY`: identifica uma linha;
- `FOREIGN KEY`: exige que a linha relacionada exista;
- `UNIQUE`: impede repetição da chave de negócio e do CNPJ;
- `CHECK`: exige preços positivos e formatos básicos de CNPJ e CEP;
- `NOT NULL`: impede ausência em campos obrigatórios.

Exemplo: tentar inserir `sale_price = -1` viola `price_observations_sale_price_check`.

## 6. Índices

**Índice** é uma estrutura auxiliar usada pelo banco para localizar linhas sem percorrer a tabela inteira. O módulo cria índices para data e para produto + data porque esses caminhos serão úteis em consultas futuras.

Índices ocupam espaço e tornam escritas um pouco mais caras. Por isso foram criados somente os que correspondem a acessos já previstos, sem antecipar todas as análises do Módulo 5.

## 7. Fluxo de carga

```text
processed CSV
→ staging_prices temporária
→ validação de domínios e conflitos
→ municípios
→ revendas
→ observações de preço
→ COMMIT
```

**Staging** é uma área temporária de preparação. Ela recebe texto do CSV antes da conversão final para `date` e `numeric`. Se uma etapa falhar, a **transação** desfaz a carga completa.

Antes da cópia, o script também confere se o cabeçalho possui exatamente as 16 colunas processadas na ordem esperada.

## 8. Idempotência e conflitos

A mesma carga pode ser executada novamente:

- municípios existentes não são reinseridos;
- revendas idênticas não são atualizadas;
- observações existentes não são duplicadas;
- uma observação existente com preço diferente gera erro;
- duas chaves iguais dentro do CSV geram erro.

**Upsert** combina tentativa de inserção com tratamento de conflito. Ele é usado nas dimensões, mas somente atualiza uma revenda quando algum atributo realmente mudou.

## 9. Decisões e alternativas

### Tabelas relacionadas em vez de uma tabela única

- escolha: separar localização, produto, revenda e observação;
- vantagem: reduz repetição e protege relacionamentos;
- desvantagem: consultas precisam de `JOIN`;
- motivo: o projeto precisa crescer para consultas e API sem duplicar descrições em cada preço.

### SQL e `psql` em vez de ORM

- escolha: scripts SQL explícitos;
- vantagem: torna tabelas, tipos e restrições visíveis para estudo;
- desvantagem: exige conhecer comandos do PostgreSQL;
- motivo: ORM e Spring Data pertencem ao módulo do Back-end.

### Estado atual da revenda

- escolha: atualizar nome, endereço e bandeira quando mudarem;
- alternativa: guardar todas as versões históricas;
- vantagem: modelo inicial menor;
- desvantagem: não preserva o histórico cadastral da revenda;
- motivo: a fonte e a amostra atuais não foram estudadas como histórico de cadastro.

## 10. Resultado verificado

| Tabela               | Linhas |
| -------------------- | ------ |
| `regions`            | 5      |
| `states`             | 27     |
| `municipalities`     | 16     |
| `products`           | 6      |
| `retailers`          | 27     |
| `price_observations` | 60     |

A repetição da carga manteve 60 observações. Os testes também demonstraram rejeição de preço negativo, revenda inexistente e chave de negócio duplicada.

## 11. Limitações

- modelo validado com uma amostra pequena e não representativa;
- ausência de tabela de histórico dos arquivos carregados;
- ausência de versionamento automático de migrações;
- chave de negócio baseada no contrato inicial do Módulo 3;
- endereço e bandeira representam somente o estado atual da revenda;
- consultas analíticas completas pertencem ao Módulo 5;
- API, Front-end e Machine Learning ainda não existem.
