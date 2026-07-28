# Relatório técnico do Módulo 02 — Ingestão da Camada Raw

## Data

28/07/2026

## Objetivo

Criar o primeiro pipeline Python para validar uma entrada CSV, preservar seus bytes na camada raw, evitar sobrescrita, registrar logs e produzir uma saída reproduzível.

## Arquivos criados

- `pipeline/__init__.py`;
- `pipeline/ingest_raw.py`;
- `tests/test_ingest_raw.py`;
- `docs/pipeline/INGESTAO_RAW.md`;
- `docs/aprendizado/modulo-02-guia.md`;
- `docs/aprendizado/modulo-02-exercicios.md`;
- `docs/aprendizado/modulo-02-minha-explicacao.md`;
- `docs/aprendizado/modulo-02-relatorio-tecnico.md`.

Arquivos locais gerados e ignorados pelo Git:

- `data/raw/precos-combustiveis-amostra__d5dd2159be5b.csv`;
- `logs/ingestion.log`.

## Arquivos alterados

- `README.md`;
- `docs/STATUS_DO_PROJETO.md`.

## Comandos executados

### Preparação do histórico

Antes da implementação, os Módulos 0 e 1 foram consolidados no commit-base `63920f7` e enviados para `origin/main`. Isso separou o histórico anterior das mudanças do Módulo 2.

### Execução

```bash
python3 pipeline/ingest_raw.py data/samples/precos-combustiveis-amostra.csv
python3 pipeline/ingest_raw.py data/samples/precos-combustiveis-amostra.csv
find data/raw -maxdepth 1 -type f -print
wc -c data/raw/*.csv
tail -n 5 logs/ingestion.log
```

### Testes e compilação

```bash
python3 -m unittest discover -s tests -v
PYTHONPYCACHEPREFIX=/tmp/fuelvision-module-02-pycache \
  python3 -m py_compile exploration/explore_sample.py pipeline/__init__.py pipeline/ingest_raw.py tests/test_explore_sample.py tests/test_ingest_raw.py
```

### Qualidade

```bash
prettier --write README.md docs/STATUS_DO_PROJETO.md docs/pipeline/INGESTAO_RAW.md "docs/aprendizado/modulo-02-*.md"
prettier --check README.md docs/STATUS_DO_PROJETO.md docs/pipeline/INGESTAO_RAW.md "docs/aprendizado/modulo-02-*.md"
git status --short --branch
git diff --check
git diff --stat
rg -n '^(from|import) ' -g '*.py' .
awk 'length($0) > 100 ...' exploration/*.py pipeline/*.py tests/*.py
rg <padrões-de-segredos>
find . <padrões-de-arquivos-grandes-e-temporários>
git check-ignore -v <arquivo-raw> <arquivo-de-log>
shasum -a 256 <origem> <destino>
```

## Testes executados

O projeto possui 16 testes aprovados, sendo 11 relacionados diretamente à ingestão raw:

1. cópia exatamente igual à entrada;
2. repetição sem sobrescrita;
3. rejeição de entrada inexistente;
4. rejeição de diretório como entrada;
5. rejeição de extensão diferente de CSV;
6. aceitação da extensão `.CSV`;
7. rejeição de CSV vazio;
8. relatório de colunas mínimas ausentes;
9. rejeição de conflito no destino;
10. execução completa da CLI com saída e log;
11. falha da CLI com código `1`, mensagem e log.

Os cinco testes do Módulo 1 também foram executados para evitar regressões.

## Resultado dos testes

- testes: 16 aprovados;
- compilação: aprovada;
- formatação Markdown: aprovada antes deste relatório e repetida na revisão final;
- `git diff --check`: aprovado antes deste relatório e repetido na revisão final;
- primeira execução real: `created`;
- segunda execução real: `already_exists`;
- tamanho da origem: `9.937` bytes;
- tamanho do destino: `9.937` bytes;
- SHA-256 de ambos: `d5dd2159be5bd72228393f18b60a0c6eeccd061b9870fe3f0542b1a7a1620b23`;
- raw e log: corretamente ignorados pelo Git;
- arquivos versionáveis maiores que 1 MB: nenhum;
- padrões de segredos: nenhum encontrado;
- caches ou temporários indevidos no projeto: nenhum encontrado.

## Erros encontrados

1. A revisão de imports encontrou `List` sem uso em `pipeline/ingest_raw.py`.
2. A primeira versão tratava a criação do diretório de log, mas uma falha ao abrir o próprio arquivo de log ainda poderia escapar como `OSError`.
3. Durante a preparação do commit-base anterior ao módulo, o Prettier encontrou um modelo do Módulo 0 fora do estilo e `git diff --cached --check` encontrou uma linha em branco extra no fim de `.gitignore`.
4. A revisão staged do Módulo 2 encontrou uma linha em branco adicional no fim de `pipeline/__init__.py`.

Nenhum teste do Módulo 2 falhou durante a implementação.

## Correções realizadas

1. O import sem uso foi removido e todos os testes foram repetidos.
2. A criação do `FileHandler` foi incluída no tratamento que converte falhas em `IngestionError`.
3. Foram adicionados testes para CSV vazio, extensão maiúscula e falha completa da CLI.
4. Os dois problemas de formatação do commit-base foram corrigidos antes de seu commit e push.
5. A linha adicional de `pipeline/__init__.py` foi removida antes do commit do Módulo 2.

## Dependências adicionadas

Nenhuma. O pipeline utiliza somente a biblioteca padrão do Python 3.9:

- `argparse`;
- `csv`;
- `hashlib`;
- `logging`;
- `pathlib`;
- `shutil`;
- `unittest` nos testes.

## Decisões tomadas

- validar somente caminho, extensão e colunas mínimas;
- preservar bytes sem limpar o conteúdo;
- usar SHA-256 para nome e verificação de integridade;
- usar os 12 primeiros caracteres no nome e o hash completo na conferência;
- abrir o destino em modo exclusivo para impedir sobrescrita;
- considerar a repetição com conteúdo igual um sucesso `already_exists`;
- remover somente arquivos parciais criados pela execução que falhou;
- manter raw e logs fora do Git;
- usar códigos de saída `0`, `1` e `2` para automação futura.

## Pendências

- o estudante pode revisar o material e realizar os exercícios posteriormente;
- nenhuma pendência educacional bloqueia a progressão funcional;
- nenhuma pendência técnica bloqueia o Módulo 2;
- o commit e o push do módulo serão executados após a revisão final deste relatório.

## Limitações atuais

- somente arquivos CSV locais;
- codificação UTF-8 e separador `;`;
- sem download automático;
- sem validação completa das linhas;
- sem limpeza, transformação, dados processados ou registros rejeitados;
- sem banco, API, Front-end ou Machine Learning.

## Status final do módulo

**Concluído.** Código, testes, documentação e verificações aplicáveis foram realizados. A entrega Git será feita somente se a última revisão permanecer aprovada.
