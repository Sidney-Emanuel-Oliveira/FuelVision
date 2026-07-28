# Detecção de comportamentos estatisticamente atípicos

## O que foi construído

O Módulo 10 acrescentou uma regra estatística que identifica observações de
preço fora do intervalo esperado para o mesmo combustível e unidade. Os alertas
podem ser consultados em:

```text
GET /api/prices/anomalies
```

O dashboard apresenta o preço observado, os limites calculados, o tamanho da
referência, a direção do desvio e o motivo do alerta.

O resultado deve ser interpretado exclusivamente como:

> Comportamento estatisticamente atípico que merece análise.

Um alerta não comprova fraude, irregularidade, erro de coleta ou preço abusivo.
Ele apenas seleciona uma observação que merece investigação humana.

## Por que isso é necessário

Mínimo, máximo e média descrevem um conjunto, mas não definem sozinhos quando um
valor está distante da região central. A detecção oferece uma regra reproduzível
para priorizar observações durante uma revisão.

```text
preços do mesmo produto e unidade
→ quartis
→ intervalo interquartil
→ limites
→ comparação de cada preço
→ alerta acompanhado de justificativa
```

## Conceitos utilizados

### Comportamento atípico e anomalia

**Comportamento estatisticamente atípico** é uma observação distante do padrão
definido por uma regra estatística. No FuelVision, um preço é atípico quando fica
fora dos limites do IQR do mesmo produto e unidade.

**Anomalia** é o nome técnico dado ao sinal encontrado. Ela não explica a causa.
Por exemplo, um preço alto no Acre pode refletir logística regional legítima,
uma característica da amostra ou um problema de dado. A regra não consegue
distinguir essas hipóteses.

### Quartis

**Quartis** dividem valores ordenados em regiões. `Q1` representa o percentil 25
e `Q3` o percentil 75. Assim, metade das observações fica entre Q1 e Q3.

O PostgreSQL calcula esses valores com `percentile_cont`, que pode interpolar
entre observações vizinhas quando o percentil não coincide com uma posição
exata.

### Intervalo interquartil

O **intervalo interquartil**, ou **IQR**, mede a largura da região central:

```text
IQR = Q3 − Q1
```

Ele é menos influenciado por valores extremos que uma medida baseada diretamente
no mínimo e no máximo. Isso é importante porque os próprios extremos são os
valores que desejamos revisar.

### Limites do IQR

Os limites utilizados são:

```text
limite inferior = Q1 − 1,5 × IQR
limite superior = Q3 + 1,5 × IQR
```

Um preço menor que o limite inferior recebe a direção
`BELOW_EXPECTED_RANGE`. Um preço maior que o limite superior recebe
`ABOVE_EXPECTED_RANGE`.

O fator 1,5 é uma convenção exploratória utilizada em box plots. Ele não é uma
lei de negócio e não transforma o resultado em prova sobre a revenda.

### Falso positivo

**Falso positivo** é um alerta produzido para uma situação que, após análise,
é legítima. No FuelVision, uma diferença regional verdadeira pode ser marcada
porque o grupo de referência reúne estados diferentes. Por isso, remover dados
automaticamente ou acusar uma revenda seria tecnicamente incorreto.

### Grupo de referência

O **grupo de referência** reúne todas as observações do mesmo produto e unidade
presentes no banco. Um grupo precisa ter ao menos quatro linhas. A amostra atual
possui dez observações por produto.

Os filtros de produto, localidade e data escolhem quais alertas serão exibidos,
mas não recalculam os quartis. Essa decisão mantém os limites constantes quando
uma pessoa alterna entre recortes pequenos.

## Definição operacional

Uma definição operacional traduz o conceito em condições verificáveis. Neste
módulo, uma observação é sinalizada quando todas as regras abaixo são verdadeiras:

1. pertence a um produto com pelo menos quatro observações de referência;
2. foi comparada somente com o mesmo produto, que já possui uma unidade definida;
3. possui preço menor que `Q1 − 1,5 × IQR` ou maior que `Q3 + 1,5 × IQR`;
4. atende aos filtros de visualização informados;
5. permanece apenas como sinal para revisão.

Essa implementação é uma regra estatística determinística, não um modelo de
Machine Learning. A mesma entrada e a mesma base produzem o mesmo resultado.

## Como o fluxo funciona

### Cálculo no PostgreSQL

```text
price_observations
→ GROUP BY product_id
→ count + percentile_cont(0,25) + percentile_cont(0,75)
→ grupos com pelo menos quatro observações
→ Q1, Q3, IQR e limites
→ comparação com cada observação
→ filtro dos valores externos
→ ordenação e paginação
```

O cálculo de referência usa todas as observações carregadas. Em seguida, os
filtros são aplicados às observações candidatas. Os valores enviados pelo cliente
continuam separados do SQL por parâmetros nomeados.

### Fluxo da aplicação

```text
AnomalyPanel
→ GET /api/prices/anomalies
→ AnomalyController
→ AnomalyService
→ PriceRepository
→ PostgreSQL
→ PriceAnomaly
→ PriceAnomalyResponse
→ painel com contexto e motivo
```

## Contrato da API

Filtros opcionais:

- `product`: nome do combustível;
- `state`: UF com duas letras;
- `municipality`: município;
- `startDate` e `endDate`: período inclusivo em `AAAA-MM-DD`;
- `page`: página iniciada em zero;
- `size`: de 1 a 100.

Exemplo:

```bash
curl 'http://localhost:8080/api/prices/anomalies?product=GASOLINA%20COMUM&state=AC&page=0&size=20'
```

Resposta resumida verificada:

```json
{
  "items": [
    {
      "salePrice": 7.97,
      "product": "GASOLINA COMUM",
      "unit": "BRL/liter",
      "referenceObservationCount": 10,
      "lowerBound": 5.82125,
      "upperBound": 7.05125,
      "direction": "ABOVE_EXPECTED_RANGE",
      "detectionMethod": "IQR_1_5",
      "reason": "Preço acima do limite superior calculado pelo método IQR. Comportamento estatisticamente atípico que merece análise."
    }
  ],
  "totalItems": 2,
  "page": 0,
  "size": 20
}
```

Os valores completos incluem identificação, data, revenda, município, UF, Q1,
Q3 e IQR.

## Arquivos envolvidos

| Arquivo | Responsabilidade |
| --- | --- |
| `domain/AnomalyDirection.java` | direções possíveis do desvio |
| `domain/PriceAnomaly.java` | resultado interno tipado da consulta |
| `dto/PriceAnomalyResponse.java` | contrato JSON público |
| `service/PriceFilterFactory.java` | normalização compartilhada dos filtros |
| `service/AnomalyService.java` | paginação, motivo e conversão do domínio |
| `controller/AnomalyController.java` | validação HTTP e endpoint |
| `repository/PriceRepository.java` | quartis, limites e consulta parametrizada |
| `AnomalyPanel.tsx` | estados visuais e apresentação dos alertas |
| `fuelVisionApi.ts` | montagem da requisição com filtros |
| `types/api.ts` | contrato TypeScript do alerta |

## Código por blocos

### Referência estatística

- **Responsabilidade:** calcular Q1 e Q3 por produto;
- **Entrada:** preços armazenados no PostgreSQL;
- **Processamento:** `percentile_cont`, agrupamento e mínimo de quatro linhas;
- **Saída:** quartis e quantidade da referência;
- **Possíveis erros:** base ausente, conexão indisponível ou grupo insuficiente;
- **Verificação:** teste de integração com as 60 observações.

### Detecção e paginação

- **Responsabilidade:** comparar preço e limites;
- **Entrada:** referência, observações e filtros;
- **Processamento:** calcula IQR, limites e direção;
- **Saída:** `PageResult<PriceAnomaly>`;
- **Comunicação:** repository entrega objetos ao service;
- **Possíveis erros:** página inválida ou intervalo de datas invertido;
- **Verificação:** testes de repository, service e controller.

### Motivo do alerta

- **Responsabilidade:** impedir interpretações acusatórias;
- **Entrada:** direção calculada;
- **Processamento:** escolhe limite inferior ou superior;
- **Saída:** texto seguro e código `IQR_1_5`;
- **Possíveis erros:** direção desconhecida é impedida pelo enum Java;
- **Verificação:** teste procura a frase obrigatória e ausência de acusações.

### Painel React

- **Responsabilidade:** consultar e explicar os alertas do recorte;
- **Entrada:** filtros já aplicados no dashboard;
- **Processamento:** controla carregamento, erro, vazio e sucesso;
- **Saída:** cartões com preço, limites e referência;
- **Comunicação:** usa o cliente HTTP existente;
- **Possíveis erros:** API indisponível ou consulta sem alertas;
- **Verificação:** testes reproduzem os estados com mocks.

## Como executar

Pré-requisitos dos módulos anteriores:

- PostgreSQL com a amostra carregada;
- Java e Maven;
- Node.js e npm;
- `.env` local preenchido e não versionado.

Na raiz:

```bash
backend/scripts/run.sh
```

Em outro terminal:

```bash
cd frontend
npm run dev
```

A consulta de anomalias não depende do FastAPI. O serviço Python continua sendo
necessário apenas para o painel de previsão.

## Como testar

```bash
backend/scripts/test.sh
backend/scripts/test.sh --with-postgres

cd frontend
npm run typecheck
npm run lint
npm run format:check
npm test
npm run build
```

## Resultados verificados

Na amostra controlada de 60 observações:

- oito preços ficaram acima do limite superior;
- nenhum preço ficou abaixo do limite inferior;
- Gasolina Comum, Gasolina Aditivada, Óleo Diesel e Óleo Diesel S10 tiveram
  dois alertas cada;
- Etanol Hidratado e GNV não tiveram alertas;
- cada referência possuía dez observações;
- os oito alertas pertencem à UF AC na amostra disponível.

Esses números são resultados da amostra local. Não descrevem o mercado
brasileiro e não permitem concluir que os preços ou revendas estejam errados.

## Decisões técnicas

### IQR em vez de z-score

- **Escolha:** limites baseados nos quartis;
- **Alternativa:** distância da média medida em desvios-padrão;
- **Vantagem:** o IQR é menos afetado pelos próprios valores extremos;
- **Desvantagem:** grupos pequenos ainda produzem limites instáveis;
- **Motivo:** a amostra é pequena e não há justificativa para assumir uma
  distribuição normal dos preços.

### PostgreSQL em vez do serviço Python

- **Escolha:** calcular sobre os dados já armazenados;
- **Alternativa:** copiar observações para um novo serviço Python;
- **Vantagem:** uma fonte de verdade e filtros integrados à API existente;
- **Desvantagem:** `percentile_cont` deixa a consulta ligada ao PostgreSQL;
- **Motivo:** não existe um modelo treinado nem necessidade de outra fronteira.

### Referência fixa durante os filtros

- **Escolha:** filtros não recalculam quartis;
- **Alternativa:** calcular limites apenas no recorte filtrado;
- **Vantagem:** os limites não mudam ao selecionar uma única cidade;
- **Desvantagem:** diferenças regionais legítimas podem ser sinalizadas;
- **Motivo:** recortes atuais possuem poucas linhas e seriam estatisticamente
  frágeis.

## Segurança e linguagem responsável

- os filtros usam parâmetros SQL;
- o endpoint é somente leitura;
- erros de banco são convertidos em resposta segura;
- o dashboard não remove nem altera observações;
- não existe ação automática baseada no alerta;
- nenhum texto usa o alerta como acusação.

## Limitações atuais

- a amostra não é representativa e possui somente dez preços por produto;
- quatro linhas é um mínimo operacional, não uma garantia estatística;
- a referência combina estados com condições logísticas diferentes;
- um preço regional legítimo pode gerar falso positivo;
- não há ajuste por município, revenda, marca, impostos ou distância logística;
- os limites mudam quando novos dados são carregados;
- não há histórico suficiente para detectar mudança temporal por revenda;
- o método não explica a causa do alerta;
- não existe validação humana registrada, feedback ou monitoramento;
- não há Docker, CI ou deploy.

## O que precisa ser compreendido agora

- diferença entre observação atípica e fraude;
- significado de Q1, Q3 e IQR;
- cálculo dos limites inferior e superior;
- motivo de comparar produtos e unidades compatíveis;
- diferença entre referência estatística e filtros de visualização;
- razão para manter contexto e motivo no contrato;
- importância de investigar falsos positivos.

## O que poderá ser aprofundado depois

- limites específicos por região com grupos maiores;
- janelas temporais móveis;
- métodos robustos multivariados;
- validação de alertas por especialistas;
- comparação entre métodos e métricas de detecção;
- monitoramento de mudança da distribuição.

Esses temas exigem mais dados ou pertencem a evoluções posteriores. Não são
necessários para compreender a regra atual.

## Referências técnicas

- [NIST: definição, investigação e limites de outliers](https://www.itl.nist.gov/div898/handbook/prc/section1/prc16.htm)
- [NIST: intervalo interquartil](https://www.itl.nist.gov/div898/software/dataplot/refman2/auxillar/iqrange.htm)
- [PostgreSQL 17: funções agregadas e `percentile_cont`](https://www.postgresql.org/docs/17/functions-aggregate.html)
