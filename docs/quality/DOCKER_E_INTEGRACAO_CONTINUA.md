# Qualidade, Docker e integração contínua

## 1. O que foi construído

O Módulo 11 criou uma forma reproduzível de verificar e executar o FuelVision.
O projeto agora possui:

- lint e formatação centralizados para o código Python;
- um comando local que reúne testes e builds;
- quatro imagens Docker, uma para cada serviço executável;
- um Docker Compose que conecta e ordena os serviços;
- health checks para detectar quando cada serviço está pronto;
- um proxy Nginx que entrega o Front-end e encaminha `/api` ao Back-end;
- um workflow do GitHub Actions para repetir as verificações a cada alteração.

O propósito não é simular uma infraestrutura de produção. É garantir que outra
pessoa consiga construir o mesmo ambiente e descobrir falhas cedo.

## 2. Por que isso é necessário

Até o Módulo 10, o fluxo completo dependia de vários programas instalados e de
três processos iniciados manualmente. Pequenas diferenças de versão ou ordem de
inicialização poderiam fazer o projeto funcionar em um computador e falhar em
outro.

O Módulo 11 reduz esse problema de duas maneiras:

1. o Docker descreve o ambiente de execução dos serviços;
2. a integração contínua executa as verificações em uma máquina nova do GitHub.

Isso não elimina todos os problemas ambientais, mas torna as dependências e os
comandos visíveis e repetíveis.

## 3. Conceitos utilizados

**Imagem Docker** é um pacote imutável que contém aplicação, runtime e arquivos
necessários para iniciar um serviço. No FuelVision, a imagem `prediction`
contém Python 3.9, dependências fixadas e o artefato treinado com a amostra.
Ela é importante porque define o que será executado, sem depender do Python
global do computador.

**Contêiner** é uma execução isolada de uma imagem. A imagem funciona como um
molde; o contêiner é o processo criado a partir desse molde. O Compose inicia
quatro contêineres do FuelVision.

**Dockerfile** é a receita usada para construir uma imagem. Cada Dockerfile
informa a imagem-base, os arquivos copiados, o build, a porta e o comando de
inicialização.

**Build em múltiplos estágios** separa a compilação da execução. O Back-end usa
Maven e o JDK no primeiro estágio, mas a imagem final recebe somente o JRE e o
arquivo JAR. Isso reduz ferramentas desnecessárias na execução.

**Docker Compose** descreve vários serviços que precisam trabalhar juntos. No
FuelVision, `compose.yaml` define rede, variáveis, portas, volume, dependências
e health checks.

**Health check** é uma verificação periódica da saúde de um serviço. O banco só
fica saudável quando existem 60 observações; o serviço Python consulta
`/model-info`; o Back-end verifica Actuator e o modelo; o Front-end consulta o
Nginx. Um processo iniciado ainda pode não estar pronto, por isso essa diferença
é importante.

**Volume** é um armazenamento mantido fora do ciclo de vida do contêiner. O
volume `fuelvision_postgres_data` preserva o banco quando o contêiner é recriado.

**Proxy reverso** recebe uma requisição e a encaminha a outro serviço. O Nginx
recebe `/api/...` na porta do Front-end e encaminha para `backend:8080`. Assim,
o navegador usa a mesma origem para a página e para a API.

**Lint** é a análise estática que procura problemas no código sem executá-lo. O
Ruff verifica Python, o Oxlint verifica TypeScript e o ShellCheck verifica Bash.
Lint complementa testes: ele encontra classes de problema diferentes.

**Integração contínua**, ou CI, é a execução automática de verificações em cada
push e pull request. O arquivo `quality.yml` prepara uma máquina limpa, executa
lint, testes, builds, contêineres e testes de fumaça.

**Teste de fumaça** é uma verificação curta do caminho mais importante da
aplicação. Ele não substitui os testes detalhados. Aqui, confirma que o Nginx
entrega a página e encaminha consultas de preços e informações do modelo.

## 4. Como o fluxo funciona

### Inicialização

```text
docker compose up
→ PostgreSQL e serviço Python iniciam em paralelo
→ PostgreSQL cria papel restrito, esquema, 60 linhas e views
→ health checks dos dois serviços passam
→ Back-end inicia e conecta banco + serviço Python
→ health check do Back-end passa
→ Nginx inicia e entrega o Front-end
→ todos os serviços ficam healthy
```

### Requisição pelo navegador

```text
navegador :5173
→ Nginx
→ /api é encaminhado para Spring Boot :8080
→ consulta PostgreSQL :5432 ou serviço Python :8000
→ resposta retorna pelo Nginx
→ React apresenta o resultado
```

Dentro da rede Docker, os serviços usam os nomes `postgres`, `prediction` e
`backend`. `localhost` dentro de um contêiner aponta para o próprio contêiner,
não para os demais.

## 5. Serviços e portas

| Serviço | Responsabilidade | Porta interna | Porta local padrão |
| --- | --- | ---: | ---: |
| `postgres` | armazenar esquema, views e 60 observações | 5432 | 5433 |
| `prediction` | carregar o artefato e calcular estimativas | 8000 | 8000 |
| `backend` | oferecer a API REST e integrar os dados | 8080 | 8080 |
| `frontend` | servir React e encaminhar `/api` | 80 | 5173 |

O PostgreSQL do Compose usa `5433` no computador para não disputar a porta
`5432` normalmente usada pelo PostgreSQL instalado localmente.

## 6. Arquivos envolvidos

| Arquivo | Responsabilidade |
| --- | --- |
| `.dockerignore` | impedir que segredos, caches e arquivos gerados entrem no contexto de build |
| `compose.yaml` | descrever os quatro serviços, rede, portas, volume e dependências |
| `database/Dockerfile` | transformar a amostra e montar a imagem PostgreSQL |
| `database/docker/init-fuelvision.sh` | criar o papel restrito, o esquema, a carga e as views |
| `database/sql/docker_create_role.sql` | criar `fuelvision_app` sem privilégios administrativos |
| `ml/Dockerfile` | instalar dependências, treinar o artefato e montar a imagem de inferência |
| `backend/Dockerfile` | compilar o JAR com Java 21 e criar a imagem de execução |
| `frontend/Dockerfile` | construir o React e copiar o resultado para o Nginx |
| `frontend/nginx.conf` | servir a SPA e encaminhar chamadas `/api` |
| `pyproject.toml` | definir a base de Ruff para todo o Python |
| `ml/pyproject.toml` | preservar regras adicionais de modernização e simplificação no ML |
| `scripts/quality.sh` | reunir lint, testes, builds e revisão de whitespace |
| `.github/workflows/quality.yml` | repetir a qualidade em uma máquina do GitHub |

## 7. Código por blocos

### Bloco de construção das imagens

- **Responsabilidade:** transformar o código-fonte em quatro imagens;
- **Entrada:** código versionado, lockfiles, amostra e dependências fixadas;
- **Processamento:** transformação da amostra, treino, Maven e Vite;
- **Saída:** imagens locais `fuelvision-*`;
- **Comunicação:** o Compose cria contêineres a partir dessas imagens;
- **Possíveis erros:** rede indisponível, versão inexistente ou build quebrado;
- **Verificação:** `docker compose build` deve terminar sem erro.

O artefato de ML é gerado durante o build a partir da amostra controlada. Ele
continua fora do Git e não é apresentado como modelo representativo.

### Bloco de inicialização do banco

- **Responsabilidade:** criar um banco utilizável sem tornar a aplicação superusuária;
- **Entrada:** credenciais locais, SQL versionado e CSV processado no build;
- **Processamento:** criação do papel, esquema, carga idempotente e views;
- **Saída:** 60 observações consultáveis pelo Back-end;
- **Comunicação:** Spring Boot usa `fuelvision_app` pela rede do Compose;
- **Possíveis erros:** senha ausente, SQL inválido ou carga inconsistente;
- **Verificação:** o health check exige exatamente 60 observações.

A senha administrativa é usada apenas pela inicialização do contêiner. A
aplicação usa outro papel com `rolsuper = false`.

### Bloco de saúde e ordem

- **Responsabilidade:** impedir que um serviço dependente comece cedo demais;
- **Entrada:** respostas HTTP ou consulta SQL;
- **Processamento:** repetição com intervalo, timeout e limite de tentativas;
- **Saída:** estado `healthy` ou `unhealthy`;
- **Comunicação:** `depends_on` espera o estado saudável;
- **Possíveis erros:** processo ativo com dependência indisponível;
- **Verificação:** `docker compose ps` deve mostrar quatro estados `healthy`.

### Bloco de integração contínua

- **Responsabilidade:** executar a mesma barreira de qualidade no GitHub;
- **Entrada:** commit ou pull request;
- **Processamento:** ambientes, lint, banco, testes, builds, Compose e smoke;
- **Saída:** workflow aprovado ou falho com logs;
- **Comunicação:** o resultado aparece na aba Actions e no commit;
- **Possíveis erros:** teste, build, health check ou download de dependência;
- **Verificação:** o job `Testes, builds e contêineres` precisa ficar verde.

O workflow tem somente permissão de leitura do conteúdo. Ele não publica
imagem, não executa deploy e não recebe credenciais de produção.

## 8. Configuração local

Copie o modelo e substitua as senhas apenas no arquivo ignorado:

```bash
cp .env.example .env
```

Variáveis principais do Compose:

- `POSTGRES_PASSWORD`: senha do papel `fuelvision_app`;
- `POSTGRES_ADMIN_PASSWORD`: senha administrativa somente do contêiner;
- `FUELVISION_DOCKER_POSTGRES_PORT`: porta publicada, padrão `5433`;
- `FUELVISION_PREDICTION_PORT`: porta do serviço Python, padrão `8000`;
- `FUELVISION_BACKEND_PORT`: porta do Back-end, padrão `8080`;
- `FUELVISION_FRONTEND_PORT`: porta do dashboard, padrão `5173`.

O `.env` nunca deve ser adicionado ao Git. Os valores padrão do Compose são
adequados apenas a desenvolvimento local e CI efêmera.

## 9. Como executar e testar

### Aplicação completa

```bash
docker compose config --quiet
docker compose build
docker compose up --detach --wait
docker compose ps
```

Abra `http://localhost:5173`.

Testes de fumaça:

```bash
curl --fail http://localhost:5173/
curl --fail http://localhost:5173/api/prices/summary
curl --fail http://localhost:5173/api/predictions/model
```

Logs de um serviço:

```bash
docker compose logs --follow backend
```

Encerrar preservando o banco:

```bash
docker compose down
```

Encerrar e apagar somente o volume Docker do FuelVision:

```bash
docker compose down --volumes
```

O último comando remove os dados do banco em contêiner e força a inicialização
da amostra na próxima subida. Ele não remove o PostgreSQL instalado no sistema.

### Qualidade local

Depois de instalar as dependências documentadas:

```bash
scripts/quality.sh
scripts/quality.sh --with-postgres
```

O segundo comando usa o PostgreSQL definido em `.env`. Ele executa Ruff, 81
testes Python, 29 testes Java, TypeScript, Oxlint, Prettier, 20 testes de
Front-end e os builds Maven/Vite.

O ShellCheck pode ser executado sem instalação global:

```bash
docker run --rm \
  --volume "$PWD:/workspace" \
  --workdir /workspace \
  koalaman/shellcheck:v0.11.0 \
  --external-sources \
  --source-path=SCRIPTDIR \
  backend/scripts/*.sh database/scripts/*.sh database/docker/*.sh scripts/*.sh
```

## 10. GitHub Actions

O workflow é acionado em:

- push para `main`;
- qualquer pull request.

Ordem resumida:

```text
checkout
→ Python 3.9 + Ruff
→ Java 21 + Maven
→ Node 24 + npm ci
→ PostgreSQL em contêiner
→ testes Python e Java com banco
→ testes e build do Front-end
→ build das quatro imagens
→ aplicação completa healthy
→ testes de fumaça pelo Nginx
→ remoção dos contêineres e volume efêmero
```

As credenciais presentes no workflow têm nomes e valores exclusivos para o
banco efêmero da CI. Elas não concedem acesso a um ambiente externo.

## 11. Decisões técnicas

### Quatro imagens em vez de uma

- **Escolha:** um contêiner por serviço;
- **Vantagem:** saúde, logs e dependências ficam separados;
- **Desvantagem:** existem mais arquivos e mais imagens para construir;
- **Motivo:** cada processo já possui runtime e responsabilidade diferentes.

### Amostra dentro do banco Docker

- **Escolha:** transformar a amostra versionada durante o build e carregá-la na
  primeira criação do volume;
- **Alternativa:** montar um CSV processado local;
- **Vantagem:** ambiente reproduzível sem depender de arquivo ignorado;
- **Desvantagem:** qualquer mudança na amostra exige reconstruir a imagem;
- **Motivo:** o projeto não versiona dados processados nem baixa datasets na CI.

### Nginx como entrada do usuário

- **Escolha:** mesma origem para arquivos do React e `/api`;
- **Alternativa:** expor React e API em origens diferentes com CORS;
- **Vantagem:** configuração mais simples para o navegador;
- **Desvantagem:** adiciona uma regra de proxy;
- **Motivo:** representa a integração real sem criar configuração prematura de CORS.

## 12. Limitações atuais

- o Compose é destinado a desenvolvimento e validação, não a produção;
- as imagens são locais e não são publicadas em registry;
- não há TLS, domínio, autenticação, backup ou rotação de segredos;
- o banco Docker recebe apenas a amostra não representativa de 60 observações;
- o artefato continua limitado às 50 observações líquidas do experimento;
- o health check confirma disponibilidade, não desempenho ou correção completa;
- a CI ainda depende da disponibilidade do GitHub, Docker Hub, Maven Central e npm;
- não há deploy automático, Kubernetes ou observabilidade de produção;
- o volume local não substitui uma política de backup.

## 13. O que precisa ser compreendido agora

- diferença entre imagem, contêiner e volume;
- por que cada serviço possui uma imagem própria;
- como os nomes dos serviços funcionam na rede do Compose;
- diferença entre processo iniciado e serviço saudável;
- por que lint, testes, build e smoke test são verificações complementares;
- como a CI impede que uma falha conhecida seja integrada sem aviso.

## 14. O que poderá ser aprofundado depois

- assinatura e análise de vulnerabilidades de imagens;
- cache avançado de camadas e dependências na CI;
- imagens sem privilégios para todos os processos;
- gestão profissional de segredos;
- observabilidade, métricas e tracing;
- estratégia de backup e restauração;
- implantação, TLS e rollback.

Esses assuntos são importantes, mas pertencem a uma etapa posterior. Kubernetes
não foi adicionado porque não resolve uma necessidade atual do FuelVision.
