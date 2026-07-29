# Instalação do FuelVision

## O que será instalado

O caminho recomendado executa os quatro serviços do FuelVision com Docker
Compose. Isso evita instalar Python, Java, Node.js e PostgreSQL separadamente.

**Imagem de contêiner** é um pacote imutável com aplicação e dependências.
**Contêiner** é um processo criado a partir dessa imagem. No FuelVision, cada
serviço possui sua própria imagem para manter as responsabilidades separadas.

## Pré-requisitos

- Git;
- Docker Engine ou Docker Desktop;
- plugin Docker Compose;
- aproximadamente alguns minutos para o primeiro build, dependendo da máquina e
  da conexão.

Confirme as ferramentas:

```bash
git --version
docker --version
docker compose version
```

## Obter o projeto

```bash
git clone https://github.com/Sidney-Emanuel-Oliveira/FuelVision.git
cd FuelVision
```

Se o repositório já estiver no computador, apenas entre em sua pasta.

## Configurar o ambiente local

Crie o arquivo local a partir do modelo:

```bash
cp .env.example .env
```

Substitua pelo menos:

```env
POSTGRES_PASSWORD=uma_senha_local_da_aplicacao
POSTGRES_ADMIN_PASSWORD=outra_senha_local_administrativa
```

O `.env` é ignorado pelo Git. Não reutilize senhas pessoais ou de outros
sistemas. As portas podem ser ajustadas no mesmo arquivo se já estiverem em uso.

## Construir e iniciar

```bash
docker compose config --quiet
docker compose build
docker compose up --detach --wait
docker compose ps
```

O estado esperado é `healthy` para `postgres`, `prediction`, `backend` e
`frontend`.

Abra:

```text
http://localhost:5173
```

## Verificação rápida

```bash
scripts/deploy_smoke.sh http://localhost:5173
```

Esse **smoke test** verifica rapidamente página inicial, resumo, metadados do
estimador e uma estimativa. Ele não substitui a suíte automatizada completa.

Também é possível consultar manualmente:

```bash
curl --fail http://localhost:5173/api/prices/summary
curl --fail http://localhost:5173/api/predictions/model
```

## Logs

```bash
docker compose logs --tail=100
docker compose logs --follow backend
```

Use `Ctrl+C` para sair do acompanhamento. Isso não encerra os serviços.

## Encerrar

Preservar o volume do banco:

```bash
docker compose down
```

Apagar também o banco criado pelo Compose:

```bash
docker compose down --volumes
```

O segundo comando é destrutivo apenas para os volumes deste projeto. Ele é útil
quando as credenciais de um banco já inicializado foram alteradas.

## Desenvolvimento sem contêineres

Para trabalhar diretamente nas tecnologias, consulte:

- [pipeline de dados](pipeline/INGESTAO_RAW.md);
- [PostgreSQL local](database/POSTGRESQL_LOCAL.md);
- [Back-end](backend/API_BACKEND.md);
- [Front-end](frontend/DASHBOARD.md);
- [serviço de estimativas](ml/MODEL_SERVING.md).

Esse caminho requer Python 3.11, PostgreSQL 17, Java 21, Maven, Node.js 24 e npm.
Ambientes virtuais antigos precisam ser recriados; atualizar somente os pacotes
dentro de um `.venv` criado pelo Python 3.9 não muda o interpretador.

## Erros comuns

### Porta ocupada

Altere no `.env` somente a porta publicada correspondente, como
`FUELVISION_FRONTEND_PORT=5174`, e suba os serviços novamente.

### Serviço `unhealthy`

```bash
docker compose ps
docker compose logs --tail=200 nome-do-servico
```

Investigue o primeiro serviço que ficou não saudável; os demais podem estar
apenas aguardando a dependência.

### Senha alterada depois da primeira subida

O PostgreSQL preserva a credencial no volume. Em desenvolvimento, remova o
volume e recrie a amostra:

```bash
docker compose down --volumes
docker compose up --detach --build --wait
```

Não use essa solução em um banco que contenha dados que precisam ser preservados.
