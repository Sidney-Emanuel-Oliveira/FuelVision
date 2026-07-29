# Revisão de segurança

## Objetivo e alcance

Esta revisão registra controles existentes e riscos conhecidos. Ela usa o OWASP
ASVS como referência de organização, mas não declara certificação, pentest ou
conformidade completa.

**Superfície de ataque** é o conjunto de entradas que podem receber conteúdo ou
tráfego não confiável. No FuelVision, as principais superfícies são upload
manual de CSV, parâmetros HTTP, corpo de previsão, proxy público e dependências.

## Controles implementados

### Segredos

- `.env` e `deploy/.env` são ignorados;
- modelos versionados contêm somente placeholders;
- a configuração de publicação rejeita domínio ou senhas ausentes;
- o workflow usa apenas credenciais efêmeras de CI;
- erros não devolvem senha, SQL ou stack trace.

### Banco e API

- aplicação usa papel PostgreSQL sem superusuário, criação de banco ou papéis;
- consultas recebem parâmetros em vez de concatenar entrada do usuário;
- filtros, datas, paginação e corpo da previsão são validados;
- API de preços é somente leitura;
- conexão ao serviço Python possui timeout;
- Actuator expõe apenas o endpoint de saúde.

### Contêineres e rede

- Back-end e serviço Python executam como usuários não privilegiados;
- Front-end usa a imagem Nginx não privilegiada e a porta interna 8080;
- serviços de aplicação perdem capabilities no arquivo de produção;
- `no-new-privileges` e sistemas de arquivos somente leitura reduzem impacto de
  comprometimento;
- portas internas do Compose base ficam ligadas a `127.0.0.1`;
- somente o Caddy publica 80 e 443 no servidor;
- não existe montagem do socket Docker nos contêineres.

### Navegador

- Nginx e Caddy enviam CSP, proteção contra MIME sniffing, enquadramento e
  permissões desnecessárias;
- publicação usa HTTPS e HSTS;
- React escapa texto renderizado por padrão;
- a mesma origem atende Front-end e `/api`, sem CORS amplo.

## Dados e privacidade

O projeto não possui contas, cookies de autenticação, formulário pessoal ou
telemetria. O CSV contém campos públicos da ANP relacionados a revendas. Isso
não autoriza enriquecimento, perfilamento ou uso fora da finalidade analítica.

Se futuramente forem coletados dados de pessoas usuárias, será necessária nova
análise de finalidade, retenção, base legal, consentimento quando aplicável e
resposta a incidentes.

## Riscos conhecidos

- não há autenticação ou autorização;
- não há rate limit, WAF ou proteção específica contra negação de serviço;
- PostgreSQL em contêiner único não oferece alta disponibilidade;
- backups e restaurações dependem do operador;
- dependências e imagens precisam de atualizações contínuas;
- não foi realizado pentest;
- CSP permite estilo inline devido à biblioteca de gráficos;
- Swagger e Actuator são acessíveis na porta local do Back-end;
- Docker daemon e sistema operacional estão fora do controle do repositório.

Durante esta revisão, `pip-audit` encontrou vulnerabilidades nas versões
transitivas antigas de Starlette e Click. O runtime mínimo passou de Python 3.9
para 3.11, FastAPI foi atualizado para `0.139.2` e as versões corrigidas
Starlette `1.3.1` e Click `8.3.3` foram fixadas. Uma segunda auditoria encontrou
avisos no `pip` e no `setuptools` da imagem base; ambos foram atualizados para
`26.1.2` e `83.0.0`. A auditoria final encontrou **zero vulnerabilidades
conhecidas** nos ambientes Python da aplicação e da imagem base. O `npm audit`
também encontrou zero vulnerabilidades. Essas verificações representam o banco
de vulnerabilidades consultado em 28/07/2026 e precisam ser repetidas.

## Verificações aplicáveis

```bash
rg -n --hidden --glob '!.git/**' \
  'ghp_|github_pat_|BEGIN.*PRIVATE KEY|AKIA' .

npm audit --prefix frontend
.venv/bin/python -m pip check
docker compose config --quiet
```

Ferramentas especializadas como Trivy, Hadolint, pip-audit e um scanner DAST
devem ser registradas como ausentes quando não estiverem disponíveis; sua falta
não pode ser convertida em resultado aprovado.

## Antes de publicar

- use senhas exclusivas e longas;
- confirme DNS e HTTPS;
- feche portas internas no firewall;
- atualize o host e as imagens;
- defina e teste backup;
- confira os cabeçalhos com `curl --head`;
- execute a suíte completa e o smoke test;
- revise logs e o diff em busca de segredos;
- habilite um canal privado para relatos de vulnerabilidade no GitHub.

## Referências

- [OWASP ASVS](https://owasp.org/www-project-application-security-verification-standard/)
- [Segurança do Docker Engine](https://docs.docker.com/engine/security/)
- [Política de segurança do repositório](../SECURITY.md)
