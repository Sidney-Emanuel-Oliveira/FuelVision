# Dicionário de dados da amostra

## 1. Propósito

Um **dicionário de dados** descreve o significado, o formato e os cuidados associados a cada coluna. No FuelVision, ele conecta os metadados oficiais ao que foi observado no CSV de 2026.

Os tipos abaixo são **tipos semânticos**, isto é, representam como cada valor deve ser interpretado. O CSV armazena tudo como texto; o programa decide quando interpretar um texto como data ou número.

## 2. Campos

| Campo               | Tipo semântico      | Pode estar vazio? | Significado e observações                                                                                                                                            |
| ------------------- | ------------------- | ----------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `Regiao - Sigla`    | texto categórico    | não esperado      | Sigla da região da revenda. Na amostra: `N`, `NE`, `CO`, `SE` e `S`.                                                                                                 |
| `Estado - Sigla`    | texto categórico    | não esperado      | Sigla da Unidade Federativa da revenda, como `AC` ou `SP`.                                                                                                           |
| `Municipio`         | texto               | não esperado      | Nome do município pesquisado. Acentuação e grafia devem ser preservadas no dado bruto.                                                                               |
| `Revenda`           | texto               | não esperado      | Nome da revenda pesquisada.                                                                                                                                          |
| `CNPJ da Revenda`   | texto identificador | não esperado      | CNPJ formatado. Embora o metadado oficial o classifique como numérico, o CSV usa pontuação e pode conter espaço inicial; por isso não deve ser convertido em número. |
| `Nome da Rua`       | texto               | não esperado      | Nome do logradouro. Foram observados espaços externos em alguns valores da amostra.                                                                                  |
| `Numero Rua`        | texto identificador | pode variar       | Número ou marcador do endereço, como `440`, `SN` ou `S/N`; não é adequado tratá-lo como número.                                                                      |
| `Complemento`       | texto               | sim               | Complemento do endereço. Há 43 ausências na amostra.                                                                                                                 |
| `Bairro`            | texto               | pode variar       | Bairro da revenda.                                                                                                                                                   |
| `Cep`               | texto identificador | pode variar       | CEP formatado. Deve permanecer texto para conservar hífen e possíveis zeros iniciais.                                                                                |
| `Produto`           | texto categórico    | não esperado      | Combustível pesquisado. A amostra contém seis categorias.                                                                                                            |
| `Data da Coleta`    | data                | não esperado      | Data da observação, escrita como `dd/mm/aaaa`.                                                                                                                       |
| `Valor de Venda`    | decimal monetário   | não esperado      | Preço ao consumidor final na data da coleta. Usa vírgula decimal no CSV.                                                                                             |
| `Valor de Compra`   | decimal monetário   | sim               | Preço de distribuição. Os metadados indicam disponibilidade somente até agosto de 2020; os 60 valores da amostra de 2026 estão vazios.                               |
| `Unidade de Medida` | texto categórico    | não esperado      | Unidade do preço: `R$ / litro` para combustíveis líquidos e `R$ / m³` para GNV na amostra.                                                                           |
| `Bandeira`          | texto categórico    | não esperado      | Marca comercial exibida pela revenda ou indicação de bandeira branca.                                                                                                |

## 3. Diferença entre identificador e quantidade

Um **identificador** distingue uma entidade, mas não representa uma quantidade calculável. CNPJ, CEP e número do endereço possuem dígitos, porém somar ou calcular média desses campos não tem significado.

Exemplo no FuelVision: preservar o CNPJ como texto mantém pontuação e zeros; convertê-lo em número poderia remover informação de formatação sem oferecer benefício analítico.

## 4. Tipos aplicados no script

O script interpreta somente:

- `Data da Coleta` como `datetime`, para verificar formato e período;
- `Valor de Venda` como `Decimal`, para verificar formato e intervalo.

Os demais campos permanecem textos. `Valor de Compra` não é convertido porque está ausente em toda a amostra.

## 5. Regras que ainda não foram implementadas

Este módulo identifica problemas, mas não limpa ou padroniza registros. Regras para remover espaços, normalizar textos, validar CNPJ, tratar ausências e rejeitar registros pertencem ao Módulo 3.
