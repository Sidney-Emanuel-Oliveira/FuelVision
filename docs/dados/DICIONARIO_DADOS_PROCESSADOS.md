# Dicionário dos dados processados

## 1. Propósito

Este dicionário descreve o contrato do CSV aceito pelo Módulo 3. Todos os campos são gravados como texto no CSV; a coluna “tipo semântico” indica como o valor deverá ser interpretado pelos próximos módulos.

## 2. Colunas

| Coluna               | Tipo semântico        | Obrigatória | Origem e regra                                                           |
| -------------------- | --------------------- | ----------- | ------------------------------------------------------------------------ |
| `region_code`        | categoria             | sim         | Região em maiúsculas: `N`, `NE`, `CO`, `SE` ou `S`.                      |
| `state_code`         | categoria             | sim         | Sigla da UF em maiúsculas e compatível com a região.                     |
| `municipality`       | texto categórico      | sim         | Município em maiúsculas, com espaços normalizados e acentos preservados. |
| `retailer_name`      | texto                 | sim         | Nome da revenda em maiúsculas e com espaços normalizados.                |
| `retailer_cnpj`      | identificador         | sim         | CNPJ com 14 dígitos e dígitos verificadores válidos.                     |
| `street_name`        | texto                 | sim         | Logradouro em maiúsculas e com espaços normalizados.                     |
| `street_number`      | identificador textual | sim         | Número ou marcador como `S/N`; não deve virar número.                    |
| `address_complement` | texto                 | não         | Complemento normalizado ou vazio.                                        |
| `neighborhood`       | texto                 | sim         | Bairro em maiúsculas e com espaços normalizados.                         |
| `postal_code`        | identificador         | sim         | CEP com 8 dígitos, sem pontuação.                                        |
| `product`            | categoria             | sim         | Produto canônico definido no Módulo 3.                                   |
| `collection_date`    | data ISO              | sim         | Data real em `AAAA-MM-DD`.                                               |
| `sale_price`         | decimal positivo      | sim         | Preço de venda com ponto decimal.                                        |
| `purchase_price`     | decimal positivo      | não         | Preço de compra com ponto decimal ou vazio.                              |
| `unit`               | categoria             | sim         | `BRL/liter` ou `BRL/m3`, compatível com o produto.                       |
| `brand`              | texto categórico      | sim         | Bandeira em maiúsculas e com espaços normalizados.                       |

## 3. Produtos canônicos

- `GASOLINA COMUM`;
- `GASOLINA ADITIVADA`;
- `ETANOL HIDRATADO`;
- `ÓLEO DIESEL`;
- `ÓLEO DIESEL S10`;
- `GNV`.

**Valor canônico** é uma representação escolhida como padrão. Ele permite que duas grafias conhecidas sejam tratadas como a mesma categoria sem adivinhar valores desconhecidos.

## 4. Chave de negócio inicial

```text
retailer_cnpj + product + collection_date
```

Essa combinação representa uma coleta de um produto em uma revenda numa data. Ela será reavaliada durante a modelagem de banco do Módulo 4 antes de virar uma restrição SQL.

## 5. Representação no CSV

- separador: `;`;
- codificação: UTF-8 sem BOM;
- final de linha: `LF`;
- decimal: ponto;
- ausente opcional: campo vazio;
- cabeçalho: nomes em inglês e `snake_case`.

## 6. Limites do contrato atual

O contrato não define ainda tipos PostgreSQL, tamanhos máximos ou relacionamentos entre tabelas. Essas decisões pertencem ao Módulo 4.
