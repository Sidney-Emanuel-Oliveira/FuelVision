# Publicação do FuelVision em um servidor

> [!NOTE]
> Este guia descreve a estratégia de servidor Linux com Docker Compose. Para
> executar React, Spring Boot e FastAPI na Vercel com PostgreSQL externo,
> consulte o [guia específico da Vercel](DEPLOY_VERCEL.md).

## Resultado esperado

Este guia prepara uma instalação pública em um único servidor Linux com Docker,
domínio e HTTPS. A configuração acrescenta Caddy como **proxy reverso**, o
componente que recebe as conexões da internet e as encaminha ao Front-end.

O repositório não cria servidor, domínio ou conta de nuvem. Essas ações podem
gerar cobrança e exigem decisões do proprietário.

## Escopo desta publicação

A configuração é adequada para demonstração, estudo e portfólio com baixo
tráfego. Ela não afirma alta disponibilidade, conformidade regulatória ou
capacidade de produção empresarial.

O banco é inicializado com a amostra controlada de 60 observações. Publicar a
aplicação não transforma essa amostra em um retrato do mercado brasileiro.

## Pré-requisitos externos

- servidor Linux acessível por SSH;
- Docker Engine e plugin Compose atualizados;
- domínio ou subdomínio controlado pelo proprietário;
- registro DNS `A` e, quando aplicável, `AAAA` apontando para o servidor;
- portas TCP 80 e 443 liberadas; UDP 443 é opcional para HTTP/3;
- política de backup definida antes de inserir dados que precisem ser preservados.

## Arquivos envolvidos

- `compose.yaml`: serviços comuns ao desenvolvimento e à publicação;
- `compose.production.yaml`: segurança, reinício e gateway público;
- `deploy/Caddyfile`: HTTPS, cabeçalhos e encaminhamento;
- `deploy/.env.example`: contrato das variáveis externas;
- `scripts/deploy_smoke.sh`: verificação pós-publicação.

## Preparar os segredos

No servidor:

```bash
cp deploy/.env.example deploy/.env
chmod 600 deploy/.env
```

Edite `deploy/.env` e informe o domínio. Gere duas senhas diferentes, por
exemplo com:

```bash
openssl rand -base64 32
```

O arquivo real é ignorado pelo Git. Nunca cole seus valores em issues, logs,
commits ou capturas de tela.

## Validar antes de subir

```bash
docker compose \
  --env-file deploy/.env \
  -f compose.yaml \
  -f compose.production.yaml \
  config --quiet
```

O Compose rejeita a configuração se domínio ou senhas obrigatórias estiverem
ausentes.

## Publicar

```bash
docker compose \
  --env-file deploy/.env \
  -f compose.yaml \
  -f compose.production.yaml \
  up --detach --build --wait
```

Quando o DNS estiver correto, o Caddy solicita e renova o certificado HTTPS
automaticamente. Os volumes `fuelvision_caddy_data` e
`fuelvision_caddy_config` preservam certificados e estado do gateway.

## Verificar

```bash
docker compose \
  --env-file deploy/.env \
  -f compose.yaml \
  -f compose.production.yaml \
  ps
```

Depois:

```bash
scripts/deploy_smoke.sh https://seu-dominio.example
curl --head https://seu-dominio.example
```

Verifique também no navegador os filtros, tabelas alternativas aos gráficos,
estimativa e alertas estatísticos.

## Atualizar uma publicação

Antes da atualização, revise as mudanças e preserve um ponto de retorno:

```bash
git fetch --tags origin
git pull --ff-only origin main
docker compose \
  --env-file deploy/.env \
  -f compose.yaml \
  -f compose.production.yaml \
  up --detach --build --wait
```

Não use `git reset --hard` para atualizar o servidor. Uma atualização que
modifique dados ou esquema precisa de backup e plano próprio de migração.

## Backup mínimo do banco

Exemplo de exportação lógica antes de uma mudança:

```bash
docker compose \
  --env-file deploy/.env \
  -f compose.yaml \
  -f compose.production.yaml \
  exec -T postgres \
  pg_dump --username=postgres --dbname=fuelvision --format=custom \
  > fuelvision-backup.dump
```

Confirme que o arquivo existe, tem tamanho plausível e pode ser armazenado em
local protegido. Um backup não testado ainda possui risco de não ser restaurável.

## Segurança operacional

- permita SSH somente a pessoas autorizadas e prefira chaves;
- mantenha sistema operacional, Docker e imagens atualizados;
- não publique as portas locais 5433, 8000, 8080 ou 5173 no firewall;
- exponha somente 80 e 443 por meio do Caddy;
- revise logs sem registrar senhas ou corpos sensíveis;
- aplique limite de tráfego em uma camada externa se o uso crescer;
- não trate `restart: unless-stopped` como alta disponibilidade.

## O que ainda exige decisão humana

- provedor e custo do servidor;
- nome e registro do domínio;
- política de privacidade, se futuramente houver coleta de dados pessoais;
- frequência, retenção e teste de restauração dos backups;
- monitoramento e alertas;
- licença do código-fonte;
- estratégia de atualização de dados e do modelo.

## Referências oficiais

- [Docker: Compose em produção](https://docs.docker.com/compose/how-tos/production/)
- [Docker: combinação de arquivos Compose](https://docs.docker.com/compose/how-tos/multiple-compose-files/)
- [Caddy: HTTPS automático](https://caddyserver.com/docs/automatic-https)
- [Caddy: proxy reverso](https://caddyserver.com/docs/caddyfile/directives/reverse_proxy)
