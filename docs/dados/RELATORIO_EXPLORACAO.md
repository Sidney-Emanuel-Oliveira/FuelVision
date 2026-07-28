# Relatório de exploração da amostra ANP

## 1. Objetivo

Verificar se uma amostra pequena da fonte oficial pode ser lida e descrever sua estrutura, tipos e sinais iniciais de qualidade antes da criação de um pipeline.

**Análise exploratória** é a observação inicial de um conjunto de dados para entender sua estrutura e levantar perguntas ou problemas. Ela não corrige os registros e não prova conclusões sobre toda a população.

## 2. Amostra analisada

- arquivo: `data/samples/precos-combustiveis-amostra.csv`;
- origem: combustíveis automotivos do 1º semestre de 2026, ANP;
- método: dois primeiros registros de cada combinação região–produto;
- registros: 60;
- colunas: 16;
- regiões: `CO`, `N`, `NE`, `S` e `SE`;
- produtos: `DIESEL`, `DIESEL S10`, `ETANOL`, `GASOLINA`, `GASOLINA ADITIVADA` e `GNV`;
- período observado: 01/01/2026 a 07/01/2026.

## 3. Estrutura e tipos

O cabeçalho da amostra corresponde aos 16 campos documentados pela ANP. O CSV usa `;` como separador. Datas e preços são armazenados como texto e interpretados pelo script somente durante a verificação.

Resultados:

- datas inválidas: 0;
- valores de venda inválidos: 0;
- incompatibilidades entre produto e unidade: 0.

Esses resultados valem apenas para os 60 registros da amostra.

## 4. Valores ausentes

**Valor ausente** é um campo sem conteúdo. Ele pode indicar informação inexistente, não coletada ou não aplicável; não deve ser preenchido sem regra e justificativa.

| Coluna            | Ausências | Percentual na amostra | Interpretação inicial                                                                    |
| ----------------- | --------: | --------------------: | ---------------------------------------------------------------------------------------- |
| `Complemento`     |        43 |                71,67% | Muitos endereços não possuem ou não informam complemento.                                |
| `Valor de Compra` |        60 |               100,00% | Compatível com a nota oficial de que a série está disponível somente até agosto de 2020. |

As outras colunas não apresentaram valores vazios na amostra.

## 5. Duplicidades

**Duplicidade exata** ocorre quando todos os campos de duas linhas são iguais. O script encontrou 0 duplicidades exatas.

Isso não exclui duplicidades de negócio. Dois registros podem representar a mesma coleta mesmo com pequenas diferenças de grafia. A definição de chave e o tratamento de duplicidades pertencem aos módulos de transformação e banco.

## 6. Inconsistências observadas

Foram encontrados espaços no início ou no fim de valores:

- `CNPJ da Revenda`: 60 registros;
- `Nome da Rua`: 3 registros.

Também há um contraste importante: os metadados classificam o CNPJ como numérico, mas o arquivo contém pontuação e espaços. Para preservar o identificador, o FuelVision o trata como texto nesta exploração.

Esses sinais foram apenas registrados. Nenhum valor foi limpo ou alterado.

## 7. Intervalo de preços

Na amostra, `Valor de Venda` variou de `3,99` a `8,17`. Os produtos possuem unidades diferentes: GNV usa metro cúbico, enquanto os demais usam litro. Portanto, o intervalo não deve ser usado como comparação direta entre todos os produtos.

Não foram calculadas médias por localidade ou combustível. A amostra não preserva as proporções do conjunto completo e não é apropriada para conclusões de mercado.

## 8. Principais conclusões

- o arquivo pode ser lido com a biblioteca padrão do Python;
- o esquema observado corresponde aos metadados oficiais;
- datas e valores de venda da amostra possuem formatos interpretáveis;
- ausências podem ser esperadas e precisam de contexto antes de qualquer tratamento;
- espaços externos deverão ser avaliados no módulo de limpeza;
- identificadores com dígitos devem permanecer textos;
- ausência de duplicidade exata na amostra não garante ausência no arquivo completo.

## 9. Limitações

- amostra determinística e não aleatória;
- apenas 60 dos 422.418 registros do recurso identificado;
- poucos dias do início de 2026;
- duas observações por combinação região–produto, sem proporcionalidade;
- nenhuma limpeza ou validação de negócio completa;
- nenhuma conclusão estatística sobre preços brasileiros;
- resultados podem mudar quando outra versão da fonte for utilizada.
