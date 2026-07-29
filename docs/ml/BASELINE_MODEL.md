# Baseline de Machine Learning

## O que foi construído

O Módulo 8 criou um experimento reproduzível para estimar o preço de venda de
uma observação futura de combustível líquido. O resultado previsto é expresso em
reais por litro (`BRL/liter`).

O experimento compara duas abordagens:

1. um baseline que prevê a média histórica de cada produto;
2. uma regressão Ridge que utiliza produto, região, bandeira e dia da coleta.

Ele treina, avalia e imprime um relatório JSON. Nenhum modelo é salvo, publicado
ou integrado à API. Essas responsabilidades pertencem a módulos posteriores.

## Por que isso é necessário

Uma previsão não deve ser avaliada apenas por parecer plausível. É necessário
definir o problema, separar dados que o modelo pode estudar de dados usados para
avaliá-lo e comparar o erro com uma referência simples.

Sem essa referência, um algoritmo mais complexo poderia receber o nome de
Machine Learning sem produzir ganho real. Neste módulo, o resultado mostrou
justamente o contrário: a regressão Ridge teve erro de teste maior que o baseline.

## Definição do problema

| Elemento | Definição do experimento |
| --- | --- |
| Problema | regressão supervisionada |
| Unidade de previsão | uma observação individual de preço |
| **Target** | `sale_price` |
| Unidade do target | `BRL/liter` |
| **Features** | `product`, `region_code`, `brand`, `collection_day` |
| Treino | observações líquidas de 01/01/2026 |
| Teste | observações líquidas de 02/01/2026 |
| Baseline | média de `sale_price` por produto, calculada só no treino |
| Modelo | regressão Ridge, `alpha=1.0`, solver `lsqr` |
| Métricas | MAE e RMSE |

O experimento não pretende prever a média nacional nem o preço exato de uma
revenda específica. Ele estima o preço de uma linha posterior usando somente os
campos selecionados.

## Conceitos utilizados

### Feature e target

Uma **feature** é uma informação fornecida ao modelo para produzir a previsão.
No FuelVision, o produto é uma feature porque gasolina, etanol e diesel têm
faixas de preço diferentes. Região e bandeira fornecem contexto adicional. A
data é convertida em um número ordinal chamado `collection_day`.

O **target** é o valor que o modelo deve aprender a estimar. Aqui, o target é
`sale_price`. Ele nunca é incluído entre as features.

### Treino e teste temporal

O conjunto de **treino** contém dados usados para calcular médias e coeficientes.
O conjunto de **teste** contém dados posteriores, não usados no ajuste, que
simulam a avaliação de uma previsão futura.

O FuelVision separa datas completas:

```text
01/01/2026 → treino → ajuste
02/01/2026 → teste  → avaliação
```

Uma separação aleatória misturaria linhas dos mesmos dias. Para um problema que
pretende olhar para frente no tempo, isso criaria uma avaliação menos realista.

### Baseline

Um **baseline** é uma solução simples usada como referência mínima. Neste
experimento, cada combustível recebe a média observada para aquele produto no
treino. Se surgir um produto não visto, usa-se a média global do treino.

Exemplo simplificado: se a gasolina no treino custou R$ 5,90 e R$ 6,10, o
baseline prevê R$ 6,00 para uma nova linha de gasolina. Um modelo útil deveria
apresentar erro menor que essa regra no mesmo teste.

### Regressão Ridge

A **regressão Ridge** é um modelo linear com regularização. Um modelo linear
combina as features por meio de coeficientes. A regularização reduz coeficientes
excessivos, ajudando a controlar o ajuste exagerado quando existem muitas
colunas em relação à quantidade de linhas.

O parâmetro `alpha=1.0` controla essa regularização. O solver `lsqr` é o método
numérico usado para encontrar os coeficientes. Ele foi escolhido porque eliminou
avisos numéricos observados com o solver automático neste ambiente.

### Codificação e escala

`product`, `region_code` e `brand` são categorias, não quantidades. O
**One-hot encoding** cria colunas binárias, como “é gasolina” ou “é região Sul”,
sem inventar uma ordem entre categorias. Categorias desconhecidas no teste são
ignoradas de forma controlada.

A **padronização** ajusta a escala de `collection_day`. O `Pipeline` garante que
codificação, padronização e Ridge sejam ajustados somente sobre o treino.

### Erro, MAE e RMSE

O **erro de previsão** é a diferença entre o preço real e o previsto.

A **MAE**, ou erro absoluto médio, calcula a média do tamanho dos erros,
ignorando o sinal. Uma MAE de `0,57` significa erro absoluto médio aproximado de
R$ 0,57 por litro nesta amostra.

A **RMSE**, ou raiz do erro quadrático médio, aumenta o peso dos erros maiores.
Ela também permanece na unidade `BRL/liter`, facilitando a comparação com a MAE.

MAPE não foi adotada neste primeiro experimento. MAE e RMSE já informam o erro
na unidade do problema, enquanto uma porcentagem poderia desviar a atenção das
fortes limitações da amostra.

### Overfitting e leakage

**Overfitting**, ou sobreajuste, ocorre quando o modelo aprende detalhes do
treino que não se repetem em novos dados. Um erro de treino muito menor que o de
teste é um sinal a investigar, mas não uma prova isolada.

**Data leakage**, ou vazamento de dados, ocorre quando informação que deveria
estar indisponível durante o treino influencia o ajuste. O FuelVision evita um
tipo importante de leakage ao ajustar médias, codificação, escala e Ridge
somente com linhas anteriores ao teste.

## Como o fluxo funciona

```text
CSV processado
  → validação de colunas, datas, preços e unidades
  → seleção de linhas em BRL/liter
  → separação temporal por datas completas
  → treino do baseline e do Pipeline Ridge
  → previsões no treino e no teste
  → MAE e RMSE
  → comparação em JSON
```

## Preparação dos dados

O arquivo processado contém 60 linhas. Dez linhas de GNV usam `BRL/m3` e foram
excluídas. Misturar reais por litro com reais por metro cúbico daria ao target
duas unidades incompatíveis.

Restaram 50 observações líquidas. A amostra possui somente duas datas para esses
produtos:

- 16 linhas em 01/01/2026, usadas no treino;
- 34 linhas em 02/01/2026, usadas no teste.

A proporção configurada é aplicada sobre datas distintas, não diretamente sobre
linhas. Como existem apenas duas datas elegíveis, uma fica em cada conjunto.

## Arquivos envolvidos

| Arquivo | Responsabilidade |
| --- | --- |
| `ml/data.py` | ler, validar, filtrar unidades e separar datas |
| `ml/baseline.py` | aprender médias somente no treino |
| `ml/evaluation.py` | calcular MAE e RMSE |
| `ml/train_evaluate.py` | coordenar baseline, Ridge, comparação e CLI |
| `ml/requirements.txt` | fixar dependências de execução |
| `ml/requirements-dev.txt` | adicionar ferramenta de qualidade |
| `ml/pyproject.toml` | configurar Ruff e compatibilidade com Python 3.11 |
| `tests/test_ml_baseline.py` | verificar dados, split, baseline, métricas e fluxo |

## Código por blocos

### Leitura e validação

**Entrada:** caminho do CSV processado.

**Processamento:** confirma a existência do arquivo, as sete colunas necessárias,
valores obrigatórios, datas ISO, preços positivos e unidades permitidas. Depois,
mantém apenas `BRL/liter` e cria `collection_day`.

**Saída:** DataFrame validado e contagens de linhas incluídas e excluídas.

**Possíveis erros:** arquivo ausente, coluna faltante, preço inválido, unidade
inesperada ou menos de duas datas elegíveis.

### Separação temporal

**Entrada:** observações validadas e fração de datas para teste.

**Processamento:** ordena as datas e reserva as mais recentes. Uma validação
confirma que a maior data do treino é menor que a menor data do teste.

**Saída:** conjuntos de treino e teste com datas completas e sem sobreposição.

### Baseline

**Entrada:** produto e preço das linhas de treino.

**Processamento:** calcula média por produto e média global.

**Saída:** uma previsão para cada linha. Nenhum valor do teste altera as médias.

### Pipeline Ridge

**Entrada:** features e target de treino.

**Processamento:** transforma categorias com `OneHotEncoder`, padroniza o dia e
ajusta o Ridge. O mesmo transformador treinado é aplicado ao teste.

**Saída:** previsões numéricas. O objeto treinado existe somente em memória.

### Avaliação

**Entrada:** preços reais e previstos, com o mesmo número de elementos.

**Processamento:** valida valores finitos e calcula MAE e RMSE.

**Saída:** métricas de treino e teste e redução percentual relativa ao baseline.
Uma redução negativa significa que o modelo piorou.

## Resultados observados

Resultados reproduzidos em 28/07/2026 sobre a amostra processada local:

| Abordagem | Conjunto | MAE (BRL/litro) | RMSE (BRL/litro) |
| --- | --- | ---: | ---: |
| Baseline por produto | treino | 0,130729 | 0,170686 |
| Ridge | treino | 0,139671 | 0,183393 |
| Baseline por produto | teste | 0,527108 | 0,810756 |
| Ridge | teste | 0,571978 | 0,816480 |

Comparado ao baseline no teste, o Ridge apresentou:

- “redução” de MAE de `-8,5126%`, isto é, MAE 8,5126% maior;
- “redução” de RMSE de `-0,7060%`, isto é, RMSE 0,7060% maior.

Portanto, **o Ridge não superou o baseline**. O módulo está funcional porque o
experimento e a comparação foram implementados corretamente; o modelo não pode
ser classificado como bom ou pronto para uso.

## Como executar

Na raiz do projeto:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r ml/requirements-dev.txt
.venv/bin/python -m ml.train_evaluate \
  --input data/processed/precos-combustiveis-amostra__d5dd2159be5b__v1__processed.csv
```

No Windows PowerShell, o executável do ambiente virtual normalmente fica em
`.venv\Scripts\python.exe`.

O comando imprime JSON. Um caminho ausente ou dado inválido produz mensagem em
`stderr` e código de saída `1`.

## Como testar

```bash
.venv/bin/ruff format --check --config ml/pyproject.toml ml tests/test_ml_baseline.py
.venv/bin/ruff check --config ml/pyproject.toml ml tests/test_ml_baseline.py
.venv/bin/python -W error -m unittest tests.test_ml_baseline -v
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python -m pip check
```

O uso de `-W error` transforma avisos Python em falhas durante os testes
específicos. Isso ajuda a impedir que problemas numéricos sejam ignorados.

## Decisões técnicas

### Ridge em vez de um modelo mais sofisticado

- **Opção escolhida:** regressão Ridge.
- **Alternativa:** árvore, floresta aleatória ou boosting.
- **Vantagem:** fluxo e regularização mais fáceis de compreender e auditar.
- **Desvantagem:** relações não lineares e interações podem ficar sem
  representação.
- **Motivo:** este é o primeiro experimento e a amostra é pequena demais para
  justificar complexidade adicional.

### Separação temporal em vez de aleatória

- **Opção escolhida:** treino anterior e teste posterior.
- **Alternativa:** embaralhar linhas antes da divisão.
- **Vantagem:** aproxima o uso futuro e reduz leakage temporal.
- **Desvantagem:** com apenas duas datas, produz conjuntos muito pequenos e
  desbalanceados.
- **Motivo:** respeitar o tempo é mais importante que obter uma proporção de
  linhas visualmente equilibrada.

### Exclusão do GNV

- **Opção escolhida:** target único em `BRL/liter`.
- **Alternativa:** converter unidades ou criar modelos separados.
- **Vantagem:** a métrica mantém significado único.
- **Desvantagem:** o experimento não cobre GNV.
- **Motivo:** não há regra de conversão válida entre volume em litros e metros
  cúbicos neste módulo.

## Limitações atuais

- a amostra de 60 linhas é controlada e não representa o mercado brasileiro;
- somente 50 linhas possuem a unidade selecionada;
- há apenas 16 linhas de treino e 34 de teste;
- existe apenas uma data em cada conjunto para combustíveis líquidos;
- `collection_day` é constante no treino e, por isso, não oferece variação
  temporal suficiente para o Ridge aprender tendência;
- a seleção da amostra não garante continuidade das mesmas revendas entre datas;
- categorias e distribuições futuras podem diferir do treino;
- não houve validação cruzada temporal nem ajuste de hiperparâmetros;
- o resultado não sustenta conclusão estatística ou decisão de negócio;
- GNV não está coberto;
- persistência, versionamento, API e dashboard foram acrescentados no Módulo 9,
  conforme `docs/ml/MODEL_SERVING.md`; ainda não existe detecção de anomalias ou
  monitoramento do modelo.

## O que precisa ser compreendido agora

- diferença entre feature e target;
- razão de separar treino e teste no tempo;
- baseline como referência obrigatória;
- significado de MAE e RMSE;
- por que erro menor é melhor;
- como Pipeline reduz risco de leakage;
- por que um experimento correto pode concluir que o modelo não melhorou.

## O que poderá ser aprofundado depois

- validação cruzada temporal com histórico maior;
- engenharia de features de localização e tempo;
- interpretação detalhada de coeficientes;
- busca de hiperparâmetros;
- intervalos de confiança e testes estatísticos;
- algoritmos não lineares;
- atualização automática, detecção de drift e monitoramento operacional.

Esses assuntos não são necessários para compreender o baseline atual e não foram
implementados antecipadamente.

## Referências técnicas

- [Instalação e compatibilidade do scikit-learn](https://scikit-learn.org/stable/install.html)
- [Introdução a estimadores, transformadores e pipelines](https://scikit-learn.org/stable/getting_started.html)
- [Documentação do OneHotEncoder](https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.OneHotEncoder.html)
- [Modelos lineares e Ridge](https://scikit-learn.org/stable/modules/linear_model.html)
- [Documentação da MAE](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.mean_absolute_error.html)
