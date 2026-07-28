# Relatório técnico do Módulo 01 — Fonte de Dados e Exploração

## Data

28/07/2026

## Objetivo

Identificar e documentar uma fonte oficial da ANP, criar uma amostra pequena, explorar estrutura e qualidade e testar sua leitura, sem implementar pipeline ou funcionalidades posteriores.

## Arquivos criados

- `data/samples/precos-combustiveis-amostra.csv`;
- `exploration/explore_sample.py`;
- `tests/test_explore_sample.py`;
- `docs/dados/FONTE_DADOS_ANP.md`;
- `docs/dados/DICIONARIO_DADOS.md`;
- `docs/dados/RELATORIO_EXPLORACAO.md`;
- `docs/aprendizado/modulo-01-guia.md`;
- `docs/aprendizado/modulo-01-exercicios.md`;
- `docs/aprendizado/modulo-01-minha-explicacao.md`;
- `docs/aprendizado/modulo-01-relatorio-tecnico.md`.

## Arquivos alterados

- `README.md`;
- `docs/STATUS_DO_PROJETO.md`.

## Fonte e amostra

A fonte escolhida foi a Série Histórica de Preços de Combustíveis e de GLP da ANP. O ZIP de combustíveis automotivos do primeiro semestre de 2026 foi baixado temporariamente, fora do repositório.

- ZIP: `8.488.624` bytes;
- CSV descompactado: `72.117.162` bytes e `422.418` registros;
- SHA-256: `a2c95e5dfa324a9d7253d4e8d53022e0c08dcc5eb6f18551527ee9f29305c54c`;
- amostra versionada: 60 registros, dois por combinação entre cinco regiões e seis produtos;
- tamanho da amostra: `9.937` bytes antes de qualquer possível alteração futura.

## Comandos executados

### Leitura e estado inicial

```bash
sed -n '<intervalo>p' docs/PLANO_FUELVISION.md
sed -n '1,240p' docs/STATUS_DO_PROJETO.md
find docs -maxdepth 3 -type f -iname '*modulo-01*'
git status --short --branch
rg --files -g '!**/.git/**'
```

### Pesquisa e inspeção da fonte

Foram consultadas páginas oficiais da ANP pela ferramenta de navegação. No terminal:

```bash
curl --head --location <url-oficial>
curl --location --range 0-0 --max-filesize 1000000 <url-oficial>
curl --location --max-filesize 9000000 <url-oficial>
wc -c <arquivo>
shasum -a 256 <arquivo>
unzip -l <arquivo.zip>
unzip -p <arquivo.zip> | dd of=<arquivo-temporário>
file <arquivo-temporário>
wc -c -l <arquivo-temporário>
head -n 3 <arquivo-temporário>
```

Os endereços completos e a identificação do recurso estão em `docs/dados/FONTE_DADOS_ANP.md`.

### Execução e testes

```bash
python3 exploration/explore_sample.py
python3 -m unittest discover -s tests -v
python3 -m unittest tests.test_explore_sample -v
PYTHONPYCACHEPREFIX=/tmp/fuelvision-pycache python3 -m py_compile exploration/explore_sample.py tests/test_explore_sample.py
```

### Qualidade

```bash
prettier --write README.md docs/STATUS_DO_PROJETO.md "docs/dados/*.md" "docs/aprendizado/modulo-01-*.md"
prettier --check README.md docs/STATUS_DO_PROJETO.md "docs/dados/*.md" "docs/aprendizado/modulo-01-*.md"
find . -type f -size +1M
find . -type f <padrões-temporários>
find . -type d -name '__pycache__'
rg <padrões-de-segredos>
rg -n '^(from|import) ' -g '*.py' .
awk 'length($0) > 100 ...' exploration/explore_sample.py tests/test_explore_sample.py
```

## Testes executados

Cinco testes com `unittest` verificaram:

1. quantidade de linhas, colunas, regiões e produtos;
2. datas, preços e unidades interpretáveis;
3. perfil documentado de ausências, espaços e duplicidades;
4. rejeição de cabeçalho inesperado;
5. ausência de nomes repetidos no esquema esperado.

A compilação sintática também foi executada com `py_compile`.

## Resultado dos testes

- testes: 5 aprovados;
- compilação: aprovada;
- execução do script: aprovada;
- formatação Markdown: aprovada antes da criação deste relatório e repetida na revisão final;
- arquivos maiores que 1 MB no projeto: nenhum;
- padrões de segredos: nenhum encontrado;
- arquivos temporários ou `__pycache__`: nenhum encontrado;
- arquivo completo da ANP no projeto: ausente;
- commit e push: não executados.

Resultados da exploração:

- 60 registros e 16 colunas;
- 5 regiões e 6 produtos;
- período de 01/01/2026 a 07/01/2026;
- intervalo observado de venda: `3,99` a `8,17`;
- 43 ausências em `Complemento`;
- 60 ausências em `Valor de Compra`;
- 0 duplicidades exatas;
- 0 datas, preços ou combinações produto–unidade inválidas;
- 60 CNPJs e 3 nomes de rua com espaços externos.

## Erros encontrados

1. Pandas não estava instalado e a importação retornou `ModuleNotFoundError`.
2. Uma consulta de rede no ambiente restrito não resolveu o domínio da ANP.
3. A consulta HTTP `HEAD`, mesmo autorizada, recebeu `403 Forbidden`.
4. A extração comum do ZIP falhou com `Illegal byte sequence` devido ao nome interno do CSV.
5. A primeira compilação tentou gravar cache fora do espaço permitido e retornou `PermissionError`.
6. A revisão encontrou o import `Counter` e uma alteração de `sys.path` sem necessidade.
7. A primeira tentativa de remover esses itens foi rejeitada por sintaxe inválida do patch e não alterou os arquivos.

## Correções realizadas

1. Foi escolhida a biblioteca padrão do Python, suficiente para o escopo; nenhuma instalação foi necessária.
2. As requisições necessárias foram repetidas com a autorização de rede adequada.
3. Um `GET` parcial limitado confirmou o recurso e seu tamanho antes do download.
4. O único conteúdo do ZIP foi extraído como fluxo para um nome temporário seguro, sem mudar seus bytes.
5. `PYTHONPYCACHEPREFIX` direcionou o cache de compilação para `/tmp`.
6. Os imports e o ajuste desnecessários foram removidos e os testes foram repetidos.
7. As duas remoções foram reaplicadas em um patch válido.

## Ferramentas indisponíveis

- Pandas: não instalado;
- `ruff`: não instalado;
- `black`: não instalado;
- `flake8`: não instalado;
- `pylint`: não instalado;
- `markdownlint`: não instalado.

Nenhuma dessas ausências bloqueia o módulo. A biblioteca padrão, `unittest`, `py_compile` e o Prettier disponível cobriram as necessidades atuais.

## Dependências adicionadas

Nenhuma. O código utiliza apenas a biblioteca padrão do Python 3.9.

## Decisões tomadas

- escolher a fonte oficial da ANP e registrar links, versão e hash;
- manter o arquivo completo somente em `/tmp`;
- selecionar dois registros por combinação região–produto;
- usar a biblioteca padrão em vez de instalar Pandas;
- tratar CNPJ, CEP e número de endereço como identificadores textuais;
- preservar ausências e espaços para não antecipar a limpeza do Módulo 3;
- não calcular indicadores que possam ser confundidos com conclusões nacionais.

## Pendências

- o estudante deve revisar o material, preencher sua explicação e realizar os exercícios;
- a alteração manual proposta ainda deve ser feita pelo estudante;
- nenhuma pendência técnica bloqueia o Módulo 1.

## Limitações atuais

A amostra não é representativa, cobre somente poucos dias e não autoriza generalizações. Não há download automatizado, pipeline, camada raw, limpeza, banco, API, Front-end ou Machine Learning.

## Status final do módulo

**Concluído.** As entregas e verificações aplicáveis ao Módulo 1 foram realizadas. O projeto deve permanecer parado até a autorização exata prevista nas instruções permanentes.
