# Model card — FuelVision Product Mean Baseline v1

## Propósito

**Model card** é um documento que registra objetivo, dados, avaliação, usos e
limitações de um modelo. Ele ajuda uma pessoa a decidir se o modelo serve para
um contexto sem depender apenas do código.

Este model card descreve o artefato `product-mean-baseline-v1` usado pelo painel
experimental do FuelVision.

## Identificação

| Campo | Valor |
| --- | --- |
| versão | `product-mean-baseline-v1` |
| tipo | média por produto com fallback global |
| tarefa | regressão de preço de venda |
| unidade do alvo | `BRL/liter` |
| dados de treino | 50 observações de combustíveis líquidos |
| período de treino do artefato | 01/01/2026 a 02/01/2026 |
| última data conhecida | 02/01/2026 |
| janela aceita pela API | 03/01/2026 a 01/02/2026 |

## Uso pretendido

- demonstrar treinamento, persistência, carregamento e inferência;
- ensinar comparação obrigatória com baseline;
- integrar uma estimativa identificada como experimental ao dashboard;
- permitir testes reproduzíveis do contrato entre Python, Java e React.

## Usos não pretendidos

- definir preço de compra, venda ou política comercial;
- representar preços atuais do Brasil;
- orientar decisão financeira sem outra fonte;
- fiscalizar revendas ou prever irregularidades;
- estimar GNV, que utiliza `BRL/m3`;
- extrapolar para produtos, datas ou distribuições não aceitas pela API.

## Dados

A fonte original é a Série Histórica de Preços de Combustíveis e de GLP da
ANP. O experimento usa uma amostra determinística de 60 linhas; somente 50
linhas possuem unidade `BRL/liter`.

A amostra possui duas datas e foi construída para ensino de estrutura e
qualidade. Ela não é aleatória nem proporcional ao mercado. Consulte
[Fonte de dados da ANP](../dados/FONTE_DADOS_ANP.md).

## Preparação e separação

- alvo: `sale_price`;
- atributos avaliados no Ridge: produto, região, marca e dia da coleta;
- treino: 16 linhas da primeira data de combustíveis líquidos;
- teste: 34 linhas da data posterior;
- separação temporal: todas as linhas de uma data permanecem no mesmo conjunto;
- GNV excluído para não misturar litro com metro cúbico.

## Avaliação reproduzida em 28/07/2026

| Abordagem | Conjunto | MAE (BRL/litro) | RMSE (BRL/litro) |
| --- | --- | ---: | ---: |
| baseline por produto | treino | 0,130729 | 0,170686 |
| Ridge | treino | 0,139671 | 0,183393 |
| baseline por produto | teste | 0,527108 | 0,810756 |
| Ridge | teste | 0,571978 | 0,816480 |

**MAE** é a média do tamanho absoluto dos erros. **RMSE** também mede erro, mas
dá mais peso aos erros maiores. Nas duas métricas, menor é melhor.

No teste temporal, o Ridge teve MAE 8,5126% maior e RMSE 0,7060% maior que o
baseline. **O Ridge não superou o baseline.** Por isso, o artefato
disponibilizado usa a média por produto. Essa escolha não significa que o
baseline seja bom; significa apenas que foi menos ruim que o Ridge nesta
comparação limitada.

## Funcionamento da inferência

Para um produto conhecido, o estimador devolve a média calculada para esse
produto nas 50 linhas usadas no ajuste final. O campo de data limita o contrato,
mas não cria uma tendência temporal porque o baseline não aprende crescimento
ou queda ao longo do tempo.

A resposta inclui versão, tipo, data final de treino, MAE de avaliação e aviso.

## Riscos e limitações

- 50 observações são insuficientes para representar a diversidade nacional;
- há somente duas datas e não existe histórico contínuo por revenda;
- o erro foi medido em um único corte temporal pequeno;
- não há intervalo de incerteza;
- não há validação externa, monitoramento de drift ou retreinamento;
- categorias futuras podem ser diferentes;
- o valor previsto permanece constante por produto dentro da janela aceita;
- o artefato não deve ser chamado de modelo de previsão de mercado.

## Considerações de uso responsável

O dashboard usa as expressões “estimativa experimental” e “não é preço
garantido”. Uma aplicação derivada deve preservar esse contexto e não ocultar
as limitações para tornar o resultado mais convincente.

## Reprodutibilidade

```bash
.venv/bin/python -m ml.train_evaluate \
  --input data/processed/precos-combustiveis-amostra__d5dd2159be5b__v1__processed.csv

.venv/bin/python -m ml.artifact \
  --input data/processed/precos-combustiveis-amostra__d5dd2159be5b__v1__processed.csv
```

O Dockerfile do serviço Python transforma a amostra controlada e gera o
artefato durante o build. O arquivo `.joblib` continua fora do Git.

## Manutenção

Uma nova versão exige:

1. identificar e versionar a fonte sem colocar dataset grande no Git;
2. repetir validações e separação temporal;
3. comparar qualquer candidato com um baseline;
4. registrar métricas reais e limitações;
5. atualizar versão, testes, contrato e este model card;
6. não substituir o artefato atual se as verificações falharem.
