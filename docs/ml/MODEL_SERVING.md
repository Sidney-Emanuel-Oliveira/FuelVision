# Persistência e serviço de estimativas

## O que foi construído

O Módulo 9 tornou uma estimativa de preço acessível pela aplicação completa. O
fluxo possui quatro partes:

```text
CSV processado
→ treinamento e artefato Joblib local
→ serviço FastAPI
→ API Spring Boot
→ painel React
```

O estimador publicado é o baseline pela média do produto, versão
`product-mean-baseline-v1`. Ele foi escolhido porque apresentou MAE temporal
menor que o Ridge no Módulo 8. A interface usa sempre as palavras
“estimativa experimental” e informa que o valor não é garantido.

## Por que isso é necessário

No módulo anterior, o estimador existia apenas durante a execução do experimento.
A aplicação não conseguia reutilizá-lo e cada processo de previsão teria que
treinar novamente.

A **persistência de modelo** transforma o objeto ajustado em um arquivo que pode
ser carregado depois. A **inferência** é a utilização desse objeto para calcular
uma estimativa sobre uma nova entrada. Separar treinamento e inferência reduz
trabalho repetido e permite identificar exatamente qual versão respondeu.

## Seleção do estimador

O Ridge não foi promovido apenas por ser um algoritmo de Machine Learning. A
comparação temporal já registrada mostrou:

| Candidato | MAE de teste | RMSE de teste |
| --- | ---: | ---: |
| média por produto | 0,527108 | 0,810756 |
| Ridge | 0,571978 | 0,816480 |

Como erro menor é melhor, a média por produto foi selecionada. Depois da seleção,
ela foi novamente ajustada sobre as 50 observações líquidas disponíveis. Esse
novo ajuste usa todos os dados elegíveis porque a avaliação comparativa já foi
realizada; o artefato guarda as métricas obtidas na separação temporal anterior.

Essa escolha tem uma consequência importante: o preço estimado depende do
produto, mas não muda entre datas. A data informa que se trata de uma solicitação
posterior ao treino e é limitada a uma janela de 30 dias; ela não representa uma
tendência aprendida.

## Conceitos utilizados

### Artefato de modelo

Um **artefato de modelo** é o arquivo que reúne o estimador ajustado e os
metadados necessários para utilizá-lo corretamente. No FuelVision, o arquivo
local é:

```text
ml/artifacts/fuel-price-baseline-v1.joblib
```

Ele contém o estimador, versão, unidade, produtos permitidos, período de treino,
janela de previsão, métricas, versões das bibliotecas e aviso de limitação.

O diretório é ignorado pelo Git. Cada ambiente deve gerar seu próprio artefato a
partir do dado processado conhecido.

### Versionamento de modelo

O **versionamento de modelo** identifica o conjunto de regra, dados e contrato
usado para responder. A versão `product-mean-baseline-v1` aparece no artefato,
no serviço Python, na API Java e no dashboard.

Alterar o algoritmo, os campos obrigatórios ou o significado da resposta exige
uma nova versão. Apenas sobrescrever um arquivo mantendo o mesmo nome tornaria
as respostas difíceis de auditar.

### Serialização

**Serialização** converte um objeto em uma representação armazenável. Joblib é
adequado a objetos Python com estruturas NumPy e scikit-learn. Porém, ele usa o
modelo de segurança do `pickle`: carregar um arquivo malicioso pode executar
código. Por isso, `joblib.load` só recebe um artefato gerado localmente pelo
FuelVision. Arquivos enviados por usuários ou baixados de fontes desconhecidas
não devem ser carregados.

### Inferência

**Inferência** é o cálculo feito por um estimador já ajustado. O serviço carrega
o artefato uma vez durante sua inicialização e reutiliza o mesmo objeto em todas
as requisições. Ele não retreina e não altera o arquivo.

### Metadados

**Metadados** são dados que descrevem outros dados ou objetos. Neste módulo,
informam como o modelo pode ser usado: cinco produtos aceitos, unidade
`BRL/liter`, treino até 02/01/2026, janela entre 03/01 e 01/02/2026 e MAE
temporal de 0,527108.

### Timeout

**Timeout** é o tempo máximo de espera por uma operação externa. O cliente Java
usa dois segundos para conexão e cinco segundos para leitura. Se o FastAPI não
responder, o Spring devolve `503` e o dashboard continua apresentando as análises
históricas.

## Contrato de entrada

O endpoint público recebe `POST /api/predictions`:

```json
{
  "product": "GASOLINA COMUM",
  "collectionDate": "2026-01-03"
}
```

Regras:

- `product` é obrigatório, possui até 40 caracteres e é normalizado para
  maiúsculas pelo Spring;
- o produto precisa estar nos metadados do artefato;
- `collectionDate` é obrigatória e usa o formato ISO `AAAA-MM-DD`;
- a data precisa estar entre `predictionStart` e `predictionEnd`;
- GNV não é aceito porque seu preço usa `BRL/m3`, enquanto o estimador usa
  `BRL/liter`.

## Contrato de saída

Resposta real verificada para gasolina comum:

```json
{
  "product": "GASOLINA COMUM",
  "collectionDate": "2026-01-03",
  "estimatedPrice": 6.594,
  "unit": "BRL/liter",
  "modelVersion": "product-mean-baseline-v1",
  "modelType": "ProductMeanBaseline",
  "trainedThrough": "2026-01-02",
  "evaluationMae": 0.5271078431372549,
  "warning": "Estimativa experimental baseada em uma amostra pequena e não representativa; não deve ser tratada como preço garantido."
}
```

`estimatedPrice` é uma estimativa pontual, não um intervalo nem uma promessa de
preço. `evaluationMae` descreve o teste temporal da versão e não garante que todo
novo erro ficará próximo desse número.

## Endpoints

### Serviço interno Python

| Método | Caminho | Responsabilidade |
| --- | --- | --- |
| GET | `/model-info` | informar versão, produtos, datas e métricas |
| POST | `/predict` | validar a entrada e calcular a estimativa |

### API pública Spring Boot

| Método | Caminho | Responsabilidade |
| --- | --- | --- |
| GET | `/api/predictions/model` | encaminhar metadados seguros ao dashboard |
| POST | `/api/predictions` | normalizar, validar e encaminhar a estimativa |

O navegador não acessa o FastAPI diretamente. O Spring mantém o contrato público
e esconde a localização interna do serviço Python.

## Como o fluxo funciona

### Treinamento e persistência

```text
CSV processado
→ validação dos dados do Módulo 8
→ avaliação temporal do baseline e Ridge
→ seleção documentada do menor MAE
→ ajuste da média por produto nas 50 linhas
→ metadados e versões
→ gravação temporária
→ substituição atômica do caminho final
```

A **gravação atômica** publica o arquivo completo de uma só vez. Se a gravação
falhar antes da substituição, um arquivo parcial não assume o caminho oficial. A
sobrescrita exige `--overwrite` explícito.

### Inicialização do serviço

```text
Uvicorn inicia
→ lifespan do FastAPI
→ caminho vindo de FUELVISION_MODEL_PATH ou valor padrão
→ Joblib carrega arquivo confiável
→ valida formato, classe e versão do scikit-learn
→ serviço começa a aceitar requisições
```

Se o artefato estiver ausente, corrompido ou incompatível, o serviço não inicia.
Falhar cedo é mais seguro que responder com uma versão desconhecida.

### Requisição da aplicação

```text
PredictionPanel
→ fetch /api/predictions
→ PredictionController
→ PredictionService normaliza o produto
→ PredictionClient aplica timeout
→ FastAPI/Pydantic valida JSON
→ ModelPredictor valida domínio
→ ProductMeanBaseline.predict
→ resposta com estimativa, versão, MAE e aviso
```

## Arquivos envolvidos

| Arquivo | Responsabilidade |
| --- | --- |
| `ml/artifact.py` | treinar, montar metadados, salvar e validar o artefato |
| `ml/inference.py` | validar o domínio e executar o estimador em memória |
| `ml/inference_api.py` | contratos Pydantic e endpoints FastAPI |
| `tests/test_ml_serving.py` | testar persistência, incompatibilidade, entrada e HTTP |
| `PredictionClient.java` | comunicar Spring e FastAPI com timeout |
| `PredictionService.java` | normalizar a entrada |
| `PredictionController.java` | publicar os dois endpoints Java |
| `Prediction*.java` em `dto` | definir o contrato JSON tipado |
| `PredictionPanel.tsx` | coletar produto/data e mostrar estimativa e limitações |
| `fuelVisionApi.ts` | enviar GET de metadados e POST de previsão |

## Código por blocos

### Persistência

- **Entrada:** caminho do CSV e caminho `.joblib` de saída;
- **Processamento:** reutiliza a avaliação, ajusta o baseline completo, cria
  metadados e grava um temporário;
- **Saída:** artefato local ignorado;
- **Erros:** entrada inválida, extensão incorreta ou arquivo já existente;
- **Verificação:** testes recarregam o arquivo e conferem versão e classe.

### Validação do artefato

- **Entrada:** objeto desserializado;
- **Processamento:** verifica estrutura, campos, datas, produtos e versão exata do
  scikit-learn;
- **Saída:** objeto aceito para inferência;
- **Erros:** versão incompatível, intervalo inconsistente ou estimador inesperado;
- **Verificação:** um teste altera a versão gravada e espera rejeição.

### Serviço Python

- **Entrada:** JSON tipado por Pydantic;
- **Processamento:** remove espaços, valida produto e janela e calcula a média;
- **Saída:** JSON em camelCase compatível com Java e TypeScript;
- **Erros:** `422` para formato ausente/inválido e `400` para regra de domínio;
- **Verificação:** TestClient executa os endpoints com artefato temporário real.

### Integração Java

- **Entrada:** DTO validado com Bean Validation;
- **Processamento:** normaliza o produto e chama o serviço interno;
- **Saída:** DTO público sem detalhes da URL interna;
- **Erros:** entrada rejeitada vira `400`; indisponibilidade vira `503`;
- **Verificação:** testes de controller, service, cliente HTTP e contexto completo.

### Painel React

- **Entrada:** produto atual, metadados e data escolhida;
- **Processamento:** restringe campos, controla carregamento e chama a API;
- **Saída:** preço formatado, versão, MAE, período e aviso;
- **Erros:** falha da previsão aparece somente no painel experimental;
- **Verificação:** testes de produto inicial, janela, sucesso e indisponibilidade.

## Como executar

### 1. Instalar dependências

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r ml/requirements-dev.txt
```

### 2. Gerar o artefato local

```bash
.venv/bin/python -m ml.artifact \
  --input data/processed/precos-combustiveis-amostra__d5dd2159be5b__v1__processed.csv
```

Se o caminho já existir e a substituição for realmente desejada:

```bash
.venv/bin/python -m ml.artifact \
  --input data/processed/precos-combustiveis-amostra__d5dd2159be5b__v1__processed.csv \
  --overwrite
```

### 3. Iniciar o serviço Python

```bash
.venv/bin/uvicorn ml.inference_api:app \
  --host 127.0.0.1 \
  --port 8000 \
  --ws none
```

`--ws none` desativa WebSocket porque o contrato utiliza somente HTTP. Não use
`--reload` como configuração de produção; ele é apenas uma conveniência de
desenvolvimento.

### 4. Iniciar Spring e dashboard

Em outro terminal:

```bash
backend/scripts/run.sh
```

Em um terceiro terminal:

```bash
cd frontend
npm run dev
```

Acesse `http://localhost:5173`.

## Como consultar manualmente

```bash
curl 'http://localhost:8080/api/predictions/model'

curl -X POST 'http://localhost:8080/api/predictions' \
  -H 'Content-Type: application/json' \
  --data '{"product":"GASOLINA COMUM","collectionDate":"2026-01-03"}'
```

## Como testar

```bash
.venv/bin/ruff format --check --config ml/pyproject.toml ml tests/test_ml_baseline.py tests/test_ml_serving.py
.venv/bin/ruff check --config ml/pyproject.toml ml tests/test_ml_baseline.py tests/test_ml_serving.py
.venv/bin/python -W error -m unittest tests.test_ml_serving -v
backend/scripts/test.sh --with-postgres
cd frontend
npm run typecheck
npm run lint
npm run format:check
npm test
npm run build
```

## Segurança

- o artefato nunca vem de upload ou URL externa;
- `.joblib`, `ml/artifacts/` e `.env` não entram no Git;
- a URL interna é configurada por ambiente;
- erros do cliente Java não expõem corpo interno ou stack trace;
- timeout impede espera ilimitada;
- o dashboard não chama diretamente a porta 8000;
- produtos e datas são validados em mais de uma fronteira.

## Limitações atuais

- a versão usa somente 50 observações líquidas e não representa o Brasil;
- o estimador é uma média por produto, não uma tendência temporal;
- todas as datas aceitas para o mesmo produto recebem o mesmo valor;
- a janela de 30 dias é uma restrição operacional, não evidência estatística;
- GNV não é aceito;
- não há intervalo de confiança;
- o artefato precisa ser gerado manualmente em cada ambiente;
- FastAPI e Spring precisam estar ativos ao mesmo tempo;
- não existe autenticação, cache, limite por cliente ou monitoramento;
- não existe retreinamento automático, registro remoto ou rollback;
- a detecção estatística de anomalias foi implementada separadamente no Módulo
  10 e está documentada em `docs/analytics/ANOMALY_DETECTION.md`;
- não há Docker, CI ou deploy.

## O que precisa ser compreendido agora

- diferença entre treinamento, persistência e inferência;
- motivo de selecionar o candidato com menor erro;
- responsabilidade de versão e metadados;
- fronteiras entre React, Spring e FastAPI;
- diferença entre erro de entrada e serviço indisponível;
- risco de carregar artefato Joblib não confiável;
- motivo de apresentar o valor como estimativa.

## O que poderá ser aprofundado depois

- formatos de modelo com verificação mais forte;
- registro de modelos e rollback;
- intervalo de previsão;
- monitoramento de desvio dos dados;
- retreinamento controlado;
- autenticação e limites de uso;
- infraestrutura e deploy.

Esses itens não foram implementados porque pertencem a módulos posteriores ou
exigem uma base de dados mais representativa.

## Referências técnicas

- [FastAPI: corpo de requisição e validação](https://fastapi.tiangolo.com/tutorial/body/)
- [FastAPI: lifespan e carregamento de modelos](https://fastapi.tiangolo.com/advanced/events/)
- [Joblib: persistência e aviso de segurança](https://joblib.readthedocs.io/en/stable/persistence.html)
- [Uvicorn: configurações do servidor](https://www.uvicorn.org/settings/)
- [Spring Boot: clientes REST](https://docs.spring.io/spring-boot/4.0/reference/io/rest-client.html)
