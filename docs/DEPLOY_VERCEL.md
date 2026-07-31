# Publicação completa do FuelVision na Vercel

## Resultado esperado

Este perfil publica o FuelVision como uma única aplicação web:

```text
pessoa usuária
      ↓
domínio HTTPS da Vercel
      ├── /api/* → Spring Boot → FastAPI privado
      └── /*      → React/Vite
                         ↓
               PostgreSQL gerenciado
```

O projeto está adequado para uma **demonstração de portfólio com baixo
tráfego**. Ele não deve ser apresentado como sistema empresarial, fonte oficial
da ANP ou previsão confiável do mercado brasileiro.

## Por que a publicação não contém um PostgreSQL em contêiner

**Contêiner sem estado** é um processo cujo disco pode desaparecer quando a
plataforma reduz ou substitui uma instância. Os contêineres da Vercel possuem
essa característica. Por isso, o Front-end, o Back-end e o serviço de previsão
podem executar na Vercel, mas os dados permanentes precisam ficar em um serviço
de banco gerenciado.

Para o FuelVision, uma opção compatível é um PostgreSQL do Marketplace da
Vercel, como Neon ou Supabase. O provedor, o plano, a região, os limites e
possíveis custos precisam ser escolhidos pelo proprietário.

## Conceitos utilizados

**Vercel Services** reúne mais de uma aplicação no mesmo projeto e encaminha
cada caminho HTTP ao serviço correto. No FuelVision, `/api/*` chega ao Spring
Boot e os outros caminhos chegam ao Vite.

**Service binding** é uma ligação privada entre dois serviços. O Back-end recebe
automaticamente a variável `FUELVISION_PREDICTION_URL`, que aponta para o
FastAPI da mesma implantação. O navegador não consegue chamar esse serviço
interno diretamente.

**Variável de ambiente** é uma configuração fornecida fora do código. As
credenciais do PostgreSQL ficam nas configurações protegidas da Vercel e nunca
no Git.

**Mesma origem** significa que página e API utilizam o mesmo protocolo, domínio
e porta. Essa decisão permite que o Front-end use `/api` sem uma liberação CORS
ampla.

## Arquivos envolvidos

- `vercel.json`: declara os três serviços, as rotas e os cabeçalhos de segurança;
- `frontend/`: serviço Vite servido nos caminhos públicos que não começam com
  `/api`;
- `backend/Dockerfile.vercel`: constrói o Spring Boot e utiliza a porta
  fornecida pela Vercel; o JAR é extraído em camadas para reduzir o custo de
  inicialização e gera um arquivo AppCDS com classes previamente preparadas;
- `backend/docker-entrypoint.vercel.sh`: inicia o Spring Boot e adapta apenas o
  binding local produzido por `vercel dev` no Docker Desktop; na Vercel, a
  criação tardia de componentes reduz o tempo necessário para abrir a porta;
- `Dockerfile.vercel`: gera o artefato reproduzível e inicia o FastAPI na
  porta fornecida pela Vercel;
- `deploy/vercel.env.example`: modelo local, sem credenciais reais, para
  preparar o banco;
- `scripts/prepare_vercel_database.sh`: cria o esquema, carrega a amostra e
  valida as views no PostgreSQL externo;
- `scripts/deploy_smoke.sh`: verifica a aplicação depois da publicação.

## O que precisa ser decidido antes

1. Qual conta ou equipe da Vercel será proprietária do projeto.
2. Qual provedor PostgreSQL será usado e qual é o limite do plano.
3. Se as prévias de pull requests usarão um banco separado.
4. Qual licença será aplicada ao código. O repositório público ainda não
   concede uma licença de reutilização.
5. Se será usado apenas o domínio gratuito `vercel.app` ou um domínio próprio.

Essas escolhas podem criar recursos externos ou cobrança e não são realizadas
automaticamente pelo repositório.

## Pré-requisitos

- conta na Vercel conectada ao GitHub;
- repositório `Sidney-Emanuel-Oliveira/FuelVision` atualizado;
- acesso ao recurso **Services** no painel da Vercel;
- PostgreSQL externo com SSL;
- para preparar o banco localmente: Python do projeto, `psql` e acesso de rede
  ao PostgreSQL;
- Docker apenas para validar os contêineres localmente.

O CLI da Vercel é opcional. A publicação pode ser realizada integralmente pelo
painel web.

### Validação local opcional com a CLI

Depois de disponibilizar um PostgreSQL acessível aos contêineres, o perfil pode
ser validado sem criar uma implantação:

```bash
npx --yes vercel@latest dev -L
```

Em outro terminal, use a URL informada pela CLI:

```bash
scripts/deploy_smoke.sh http://localhost:3000
```

O parâmetro `-L` executa somente com a configuração local. Esse teste utiliza
Docker e não cria projeto, conta ou recurso externo na Vercel. Se a CLI escolher
outra porta, substitua `3000` pela porta exibida.

## 1. Criar o PostgreSQL persistente

No Marketplace da Vercel, escolha um provedor PostgreSQL. Neon e Supabase são
exemplos disponíveis, não recomendações obrigatórias.

Prefira:

- região próxima da região de execução da aplicação;
- conexão com SSL;
- endpoint com pool de conexões, quando o provedor oferecer;
- plano cujo limite de armazenamento e conexões seja conhecido;
- credenciais exclusivas para o FuelVision.

Guarde os seguintes valores sem colocá-los em documentação ou commit:

```text
host
porta
nome do banco
usuário
senha
modo SSL
```

## 2. Preparar e validar a amostra no banco

Crie somente o arquivo local:

```bash
cp deploy/vercel.env.example deploy/.env.vercel
chmod 600 deploy/.env.vercel
```

Substitua os placeholders em `deploy/.env.vercel`. Depois execute:

```bash
scripts/prepare_vercel_database.sh
```

O fluxo executado é:

```text
amostra versionada
    → transformação temporária
    → criação do esquema
    → carga idempotente
    → criação das views
    → validação analítica
```

**Carga idempotente** é uma carga que pode ser repetida sem duplicar os mesmos
registros. O arquivo processado e o log são temporários e removidos ao final.

Resultado esperado:

```text
FuelVision sample database prepared and validated.
```

Se `psql` não estiver instalado, o script informa a ausência. No macOS com
Homebrew, o caminho também pode ser indicado em `POSTGRES_BIN`.

## 3. Enviar a preparação ao GitHub

Antes de qualquer commit:

```bash
git status --short
git diff --check
scripts/quality.sh
```

Revise cada arquivo preparado. Nunca inclua:

- `.env`;
- `deploy/.env`;
- `deploy/.env.vercel`;
- senhas, tokens ou URLs que contenham senha;
- `docs/aprendizado/`, que permanece apenas no ambiente local;
- artefatos em `ml/artifacts/`;
- dados gerados em `data/processed/`.

Use arquivos explícitos no `git add` em vez de adicionar tudo sem revisão. Uma
mensagem de commit possível é:

```text
feat: prepara deploy full stack na Vercel
```

Depois do commit local:

```bash
git push origin main
```

O push deve ser feito somente depois de a suíte de qualidade passar e de o diff
preparado não conter segredos.

## 4. Importar o repositório na Vercel

No painel da Vercel:

1. Entre com a conta conectada ao GitHub.
2. Escolha **Add New → Project**.
3. Importe `Sidney-Emanuel-Oliveira/FuelVision`.
4. Mantenha o **Root Directory** na raiz do repositório.
5. Selecione **Services** como Framework Preset.
6. Não mude os comandos definidos em `vercel.json`.
7. Cadastre as variáveis do PostgreSQL.
8. Inicie a implantação.

O projeto somente é construído como três serviços quando o preset **Services**
está selecionado e o arquivo `vercel.json` contém a seção `services`.

Se a opção Services não aparecer, não tente transformar o Spring Boot ou o
FastAPI em arquivos estáticos. Esse recurso está em beta e pode ainda não estar
habilitado para a conta. Nesse caso, publique somente o Front-end na Vercel e
mantenha os serviços em um host Docker conforme o [guia de servidor](DEPLOY.md),
ou aguarde a liberação do recurso.

## 5. Configurar as variáveis do projeto

Cadastre em **Project → Settings → Environment Variables**:

```text
POSTGRES_HOST
POSTGRES_PORT
POSTGRES_DB
POSTGRES_USER
POSTGRES_PASSWORD
POSTGRES_SSLMODE
```

Use `require` em `POSTGRES_SSLMODE` quando o provedor confirmar suporte a SSL.
Não cadastre `FUELVISION_PREDICTION_URL`: o binding do `vercel.json` fornece
esse valor internamente em cada implantação.

Uma alteração nas variáveis só afeta uma nova implantação. Depois de alterar
qualquer valor, faça um redeploy.

### Produção e Preview

Para uma primeira demonstração, configure as credenciais somente em
**Production**. Se habilitar **Preview**, não use o banco de produção em pull
requests não confiáveis. O correto é um banco ou uma branch de banco separada
para prévias.

## 6. Verificar a implantação

Copie a URL de produção mostrada pela Vercel e execute:

```bash
scripts/deploy_smoke.sh https://seu-projeto.vercel.app
```

Verifique também:

```bash
curl --fail https://seu-projeto.vercel.app/api/prices/summary
curl --fail https://seu-projeto.vercel.app/api/predictions/model
curl --head https://seu-projeto.vercel.app
```

No navegador:

1. confirme que indicadores e gráficos carregam;
2. altere produto e localidade;
3. solicite uma estimativa;
4. confira os avisos sobre a amostra e o baseline;
5. abra a tabela alternativa dos gráficos;
6. teste em uma largura semelhante à de um celular;
7. confira os logs dos serviços `backend` e `prediction` no painel.

Não considere a publicação concluída se o dashboard abrir, mas as chamadas
`/api` falharem.

## 7. Atualizações pelo GitHub

Depois que o projeto estiver conectado, novos commits em `main` geram novas
implantações de produção. Pull requests podem gerar prévias, dependendo das
configurações do projeto.

Antes de cada push:

```bash
scripts/quality.sh
git diff --check
git status --short
```

Depois de cada implantação:

```bash
scripts/deploy_smoke.sh https://seu-projeto.vercel.app
```

## Erros comuns

### O Front-end abre, mas `/api` devolve 404

Confirme que o Framework Preset é **Services** e que a raiz do projeto contém
`vercel.json`. A regra `/api/(.*)` precisa aparecer antes da regra geral.

### O Back-end não inicia

Confira as seis variáveis PostgreSQL, o modo SSL e os logs do serviço
`backend`. Não publique a senha para pedir ajuda.

### A previsão devolve indisponibilidade

Confira o build e os logs do serviço `prediction`. O serviço não possui rota
pública por decisão de segurança; a chamada correta passa pelo Spring Boot.

### A primeira chamada demora mais

**Cold start** é o tempo necessário para iniciar uma instância que estava
reduzida a zero. Os contêineres e o PostgreSQL serverless podem apresentar essa
demora depois de um período sem tráfego.

O serviço de previsão abre o servidor HTTP antes de importar o conjunto
completo de bibliotecas científicas e carregar o artefato. O modelo é carregado
uma única vez, de forma protegida contra chamadas concorrentes, quando a
primeira requisição realmente precisar dele. Assim, a Vercel consegue detectar
a porta rapidamente; a primeira consulta ao modelo assume o custo restante. O
Back-end aguarda até 20 segundos por essa primeira resposta, pois a criação de
uma nova instância na plataforma pode ultrapassar o tempo de uma chamada já
aquecida. Esse limite pode ser ajustado por
`FUELVISION_PREDICTION_READ_TIMEOUT` quando houver uma necessidade operacional
comprovada.

### O log informa `could not connect to $PORT=80`

Esse erro significa que a Vercel não encontrou o servidor HTTP antes do limite
de inicialização da instância. Ele é diferente de uma falha de banco: primeiro
confirme no log se o Spring Boot chegou a registrar `Tomcat started on port 80`.

O perfil da Vercel reduz esse risco de duas formas:

- usa o layout extraído recomendado pelo Spring Boot, evitando parte do custo
  de leitura de bibliotecas dentro de um único JAR;
- habilita **inicialização preguiçosa**, que abre o servidor primeiro e cria
  componentes somente quando a primeira requisição precisar deles;
- utiliza **AppCDS**, um arquivo criado durante o build com classes da aplicação
  em um formato que a JVM consegue carregar mais rapidamente.

A inicialização preguiçosa transfere parte do trabalho para a primeira chamada.
Por isso, os testes e o smoke test precisam acessar endpoints reais, e não
somente confirmar que a página estática abriu.

O AppCDS aumenta o tamanho da imagem porque adiciona o cache `application.jsa`.
Essa é uma troca consciente: um pouco mais de armazenamento para diminuir o
tempo de inicialização. O cache precisa ser reconstruído quando o código, as
dependências ou a versão da JVM mudarem. Mensagens `Preload Warning` durante a
criação podem indicar classes dinâmicas que não entraram no cache; elas não
representam falha quando o build termina com sucesso e o contêiner validado
utiliza o arquivo.

Se o erro continuar mesmo com `Tomcat started on port 80`, verifique a data e o
commit da implantação. Contêineres na Vercel ainda são um recurso beta; falhas
intermitentes de cold start devem ser verificadas nos registros antes de
alterar credenciais ou recriar o banco.

### O build excede limites

Verifique no painel os limites atuais de build, memória, duração e tamanho de
imagem do plano. Não reduza validações ou remova o modelo apenas para esconder
um erro de limite; registre o limite e escolha um plano ou uma arquitetura
compatível.

## O que já está bom para portfólio

- fluxo completo do dado até a interface;
- API e serviço de previsão separados por responsabilidade;
- resultados e limitações documentados;
- testes de Python, Java e React;
- contêineres sem usuário root;
- mesma origem para Front-end e API;
- HTTPS e cabeçalhos de segurança fornecidos na publicação;
- preparação reproduzível do banco.

## O que melhorar antes de uso público mais amplo

Esses itens não impedem uma amostra de portfólio, mas limitam um produto real:

- selecionar uma licença para o código;
- automatizar a atualização dos dados oficiais;
- trabalhar com conjunto representativo e reavaliar o modelo;
- adicionar rate limit e proteção contra abuso;
- definir monitoramento, alertas e orçamento;
- automatizar backup e testar restauração;
- criar ambiente de Preview isolado;
- realizar teste formal de acessibilidade e teste de segurança;
- criar política de disponibilidade e suporte.

## O que você precisa compreender agora

- a Vercel executa três serviços, mas não preserva o disco dos contêineres;
- o PostgreSQL externo é obrigatório para manter os dados;
- `/api` e a página compartilham a mesma origem;
- credenciais pertencem às variáveis da plataforma, não ao Git;
- uma página aberta não prova que API, banco e previsão funcionam;
- o smoke test valida o fluxo público mínimo.

## O que poderá ser aprofundado depois

- branches de banco para cada Preview;
- domínio próprio e configuração DNS;
- observabilidade com métricas e alertas;
- proteção contra abuso e autenticação;
- migrações automáticas de esquema;
- estratégias de cache e redução de cold start;
- análise de custo da computação e do banco.

## Referências oficiais

- [Vercel Services](https://vercel.com/docs/services)
- [guia completo de Vercel Services](https://vercel.com/kb/guide/vercel-services)
- [contêineres Docker na Vercel](https://vercel.com/kb/guide/does-vercel-support-docker-deployments)
- [Vite na Vercel](https://vercel.com/docs/frameworks/frontend/vite)
- [variáveis de ambiente](https://vercel.com/docs/environment-variables)
- [PostgreSQL no Marketplace](https://vercel.com/docs/marketplace-storage)
- [integração com monorepositórios](https://vercel.com/docs/monorepos)
