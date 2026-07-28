# PostgreSQL local no FuelVision

## 1. O que foi configurado

O Módulo 4 utiliza PostgreSQL 17, um banco de dados relacional executado localmente. O ambiente verificado usa PostgreSQL 17.10 instalado pelo Homebrew no macOS.

O PostgreSQL 17 recebe suporte oficial até novembro de 2029. Consulte a [política de versões do PostgreSQL](https://www.postgresql.org/support/versioning/) e a [fórmula `postgresql@17` do Homebrew](https://formulae.brew.sh/formula/postgresql@17).

## 2. Por que o banco é necessário

O CSV processado possui um contrato, mas ainda não protege relacionamentos quando outro programa escreve dados. O PostgreSQL centraliza tipos, chaves, restrições e consultas.

```text
CSV processado → psql → staging → tabelas relacionais → consulta verificada
```

## 3. Ferramentas

- `postgres`: processo servidor;
- `psql`: cliente que envia SQL ao servidor;
- `createuser`: cria um papel de acesso;
- `createdb`: cria um banco;
- `pg_isready`: verifica se o servidor responde.

**Servidor** armazena e processa os dados. **Cliente** conecta-se ao servidor para enviar comandos. Instalar apenas um cliente não cria um banco em execução.

## 4. Instalação no macOS

```bash
brew install postgresql@17
brew services start postgresql@17
/opt/homebrew/opt/postgresql@17/bin/pg_isready -h localhost -p 5432
```

Resultado esperado do último comando:

```text
localhost:5432 - accepting connections
```

O projeto não utiliza Docker neste módulo. Docker e Compose serão estudados no módulo de infraestrutura.

## 5. Papel e banco

Crie um papel sem privilégios administrativos e um banco pertencente a ele. O usuário administrativo local costuma ser o usuário do macOS criado pelo Homebrew.

```bash
/opt/homebrew/opt/postgresql@17/bin/createuser \
  -h localhost -U "$USER" --login --pwprompt fuelvision_app

/opt/homebrew/opt/postgresql@17/bin/createdb \
  -h localhost -U "$USER" --owner=fuelvision_app fuelvision
```

`--pwprompt` solicita a senha sem colocá-la no histórico do terminal. Não conceda `SUPERUSER` ao papel da aplicação.

## 6. Variáveis de ambiente

**Variável de ambiente** é um valor de configuração fornecido fora do código. Ela permite trocar host, porta, banco e credenciais sem alterar scripts versionados.

```bash
cp .env.example .env
```

Depois, ajuste somente o arquivo `.env` local:

```dotenv
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=fuelvision
POSTGRES_USER=fuelvision_app
POSTGRES_PASSWORD=sua_senha_local
POSTGRES_SSLMODE=prefer
POSTGRES_BIN=/opt/homebrew/opt/postgresql@17/bin
```

`.env.example` contém apenas um modelo. `.env` é ignorado pelo Git e não deve ser enviado ao repositório.

O ambiente de teste deste módulo utilizou a autenticação local criada pelo Homebrew. Em ambientes compartilhados ou publicados, senha forte, regras de autenticação e TLS precisam ser configurados antes do uso.

## 7. Criar o esquema

```bash
database/scripts/create_schema.sh
```

O script lê `.env` e executa `database/sql/001_create_schema.sql`. Ele pode ser repetido porque utiliza `IF NOT EXISTS` e atualiza somente dados de referência conhecidos.

## 8. Carregar os dados processados

```bash
database/scripts/load_processed.sh \
  data/processed/precos-combustiveis-amostra__d5dd2159be5b__v1__processed.csv
```

Resultado real da primeira carga:

```text
COPY 60
INSERT 0 16
INSERT 0 27
INSERT 0 60
source_rows=60
total_observations=60
```

Na repetição, municípios, revendas e observações idênticos exibiram `INSERT 0 0`, e o total permaneceu 60.

## 9. Executar consultas iniciais

```bash
database/scripts/run_initial_queries.sh
```

O comando apresenta a quantidade de linhas por tabela e dez observações relacionadas. Ele comprova a conexão entre as tabelas, mas ainda não realiza as análises agregadas do Módulo 5.

## 10. Testar

Testes que não exigem banco ativo:

```bash
python3 -m unittest discover -s tests -v
```

Suíte completa, incluindo PostgreSQL:

```bash
FUELVISION_RUN_DB_TESTS=1 python3 -m unittest discover -s tests -v
```

Os testes de integração são ativados explicitamente porque uma pessoa pode executar o restante do projeto sem possuir PostgreSQL local.

## 11. Erros comuns

### `psql was not found`

Confirme a instalação e ajuste `POSTGRES_BIN` no `.env`.

### `connection refused` ou `no response`

```bash
brew services list
/opt/homebrew/opt/postgresql@17/bin/pg_isready -h localhost -p 5432
```

### `password authentication failed`

Confira `POSTGRES_USER` e `POSTGRES_PASSWORD` no `.env`. Não copie a senha para documentação ou commit.

### `database does not exist`

Crie o banco com `createdb` conforme a seção 5.

### `violates ... constraint`

Leia o nome da restrição. Ele indica se a falha envolve chave estrangeira, duplicidade, preço ou formato.

### `Processed CSV contains...`

Não remova a validação para forçar a carga. Investigue o CSV processado e a etapa que o produziu.

### `Processed CSV header does not match...`

O arquivo não possui exatamente as 16 colunas processadas, na ordem do contrato. Gere novamente a saída pelo Módulo 3 em vez de renomear o cabeçalho manualmente.

## 12. Segurança e limites

- não versionar `.env`;
- não usar papel `SUPERUSER` na aplicação;
- não expor a porta do banco à internet;
- não registrar senha em logs;
- realizar backup antes de operações destrutivas em dados importantes;
- o módulo não configura produção, backup automático, TLS obrigatório ou alta disponibilidade;
- o módulo não cria API, dashboard ou Machine Learning.
