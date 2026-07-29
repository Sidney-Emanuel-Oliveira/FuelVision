# Dados, métricas e limitações

## Propósito

Esta página reúne os números que podem ser apresentados sobre o FuelVision e o
contexto necessário para não interpretá-los incorretamente.

## Fonte e recorte

- fonte: Série Histórica de Preços de Combustíveis e de GLP da ANP;
- recurso identificado: combustíveis automotivos do primeiro semestre de 2026;
- registros no CSV completo identificado: 422.418;
- registros versionados na amostra: 60;
- período da amostra: 01/01/2026 a 07/01/2026;
- seleção: dois primeiros registros de cada combinação região–produto;
- regiões: cinco;
- produtos: seis.

A amostra é determinística, pequena e não aleatória. Os números abaixo são
verificações do software sobre essa amostra, não indicadores do Brasil.

## Linhagem

**Linhagem de dados** é o registro do caminho percorrido pelo dado e das
operações aplicadas.

```text
ANP
→ amostra versionada
→ ingestão raw com hash
→ transformação e validação
→ CSV processado e rejeitados
→ seis tabelas PostgreSQL
→ quatro views analíticas
→ API e dashboard
```

O arquivo completo não é versionado. Dados raw, processados e artefatos gerados
continuam ignorados pelo Git.

## Qualidade verificada na amostra

- 60 registros e 16 colunas de origem;
- 0 datas inválidas;
- 0 preços de venda inválidos;
- 0 incompatibilidades entre produto e unidade;
- 0 duplicidades exatas na exploração inicial;
- 43 ausências em `Complemento`;
- 60 ausências em `Valor de Compra`, compatíveis com a nota da fonte;
- 60 observações carregadas sem duplicação no banco.

Ausência de erro nessa amostra não garante que outro arquivo da ANP terá a
mesma qualidade. O pipeline rejeita estruturas e valores que violem seus
contratos atuais.

## Métricas do experimento de Machine Learning

| Abordagem | Conjunto | MAE | RMSE |
| --- | --- | ---: | ---: |
| baseline por produto | treino | 0,130729 | 0,170686 |
| Ridge | treino | 0,139671 | 0,183393 |
| baseline por produto | teste | 0,527108 | 0,810756 |
| Ridge | teste | 0,571978 | 0,816480 |

O Ridge não superou o baseline. O serviço publica o baseline simples porque ele
teve o menor MAE temporal entre as duas opções avaliadas. Consulte o
[model card](ml/MODEL_CARD.md) antes de apresentar esses valores.

## Detecção de anomalias na amostra

- oito preços acima do limite superior do IQR;
- nenhum preço abaixo do limite inferior;
- dez observações na referência de cada produto;
- os oito alertas estão na UF AC dentro do recorte disponível.

Esses alertas indicam valores estatisticamente atípicos. Eles não identificam
fraude, erro ou causa e precisam de investigação humana.

## Limitações de dados

- amostra não proporcional e não representativa;
- somente dois primeiros registros de cada combinação selecionada;
- poucas datas e pouca continuidade entre revendas;
- grupos por município ou estado podem ter uma ou duas observações;
- atualização da fonte pode mudar esquema, links e conteúdo;
- CNPJ e endereço são campos públicos da fonte, mas não devem receber
  enriquecimento ou exposição adicional sem finalidade e revisão.

## Limitações do sistema

- importação depende de um arquivo fornecido; não há atualização automática;
- não existe histórico de lotes ou ferramenta de migração do banco;
- API pública é somente leitura e não possui autenticação ou limite por cliente;
- publicação preparada usa uma instância de cada serviço;
- não há backup automático, SLA ou monitoramento de produção;
- o dashboard limita o histórico a 100 pontos por consulta;
- não foi realizado teste formal com pessoas usuárias ou tecnologia assistiva;
- a licença do código ainda precisa ser escolhida pelo proprietário.

## Linguagem correta para o portfólio

Adequado:

> Plataforma full stack que demonstra ingestão, validação, PostgreSQL, API,
> dashboard, baseline de ML, detecção IQR, Docker e CI sobre amostra pública
> controlada da ANP.

Inadequado:

> Inteligência artificial que prevê os preços brasileiros e detecta fraudes.

A segunda frase afirma capacidades que os dados e as métricas não sustentam.
