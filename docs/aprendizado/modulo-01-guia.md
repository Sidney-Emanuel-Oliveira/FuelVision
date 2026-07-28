# Módulo 01 — Fonte de Dados e Exploração

## 1. Objetivo

Este módulo identificou uma fonte oficial da ANP, criou uma amostra pequena e rastreável, documentou seus campos e implementou uma exploração inicial com testes básicos.

Ele existe para substituir suposições por evidências antes da criação do pipeline do Módulo 2.

## 2. Problema resolvido

O FuelVision ainda não conhecia o formato real dos dados que utilizará. Sem essa análise, poderíamos escolher separador, codificação, nomes de colunas ou tipos incorretos.

O módulo resolveu esse problema ao registrar a origem e verificar uma amostra real, sem colocar o arquivo completo de 72 MB no repositório.

## 3. Conceitos estudados

**Fonte oficial** é um dado publicado pelo órgão responsável. No FuelVision, a ANP publica a Série Histórica de Preços de Combustíveis. Usar a fonte oficial reduz a dependência de cópias de origem desconhecida.

**CSV** é um formato textual de tabela. Cada linha representa um registro e um caractere separa as colunas. O arquivo da ANP usa ponto e vírgula, não vírgula.

**Esquema** é a estrutura esperada dos dados. Aqui, ele é formado por 16 nomes de colunas e seus significados. Conhecer o esquema permite detectar uma mudança de cabeçalho.

**Amostra** é uma parte do conjunto completo. Esta amostra possui 60 registros escolhidos para cobrir regiões e produtos. Ela ajuda a estudar formato, mas não representa proporcionalmente o Brasil.

**Análise exploratória** é uma investigação inicial da estrutura e da qualidade. O script conta ausências e duplicidades e verifica formatos sem corrigir os dados.

**Valor ausente** é um campo sem conteúdo. `Valor de Compra` está vazio em toda a amostra, de acordo com a limitação temporal informada pelos metadados.

**Duplicidade exata** ocorre quando duas linhas são iguais em todos os campos. A amostra não possui duplicidades exatas, mas isso não descarta duplicidades de negócio.

**Tipo semântico** descreve o significado do valor. Um CNPJ contém dígitos, porém é identificador e deve ser tratado como texto.

## 4. Estrutura criada

```text
fuelvision/
├── data/
│   └── samples/
│       └── precos-combustiveis-amostra.csv
├── docs/
│   ├── dados/
│   │   ├── DICIONARIO_DADOS.md
│   │   ├── FONTE_DADOS_ANP.md
│   │   └── RELATORIO_EXPLORACAO.md
│   ├── aprendizado/
│   │   ├── modulo-01-exercicios.md
│   │   ├── modulo-01-guia.md
│   │   ├── modulo-01-minha-explicacao.md
│   │   └── modulo-01-relatorio-tecnico.md
│   └── STATUS_DO_PROJETO.md
├── exploration/
│   └── explore_sample.py
├── tests/
│   └── test_explore_sample.py
└── README.md
```

## 5. Responsabilidade de cada arquivo

- `data/samples/precos-combustiveis-amostra.csv`: 60 registros reais usados no estudo;
- `exploration/explore_sample.py`: lê e resume somente a amostra versionada;
- `tests/test_explore_sample.py`: confirma leitura, formato, grupos e rejeição de cabeçalho inesperado;
- `docs/dados/FONTE_DADOS_ANP.md`: documenta origem e seleção;
- `docs/dados/DICIONARIO_DADOS.md`: define significado e tipo dos campos;
- `docs/dados/RELATORIO_EXPLORACAO.md`: registra resultados e limites;
- arquivos `modulo-01-*`: apoiam estudo, exercícios, explicação e auditoria técnica;
- `README.md`: apresenta como executar o estado atual;
- `docs/STATUS_DO_PROJETO.md`: registra o progresso oficial.

## 6. Fluxo de funcionamento

```text
amostra CSV → leitura com separador ; → conferência do cabeçalho → perfil de qualidade → resumo no terminal
```

O arquivo completo da ANP participou apenas da criação controlada da amostra e permaneceu fora do repositório.

## 7. Explicação do código por blocos

### Caminho e esquema esperado

- responsabilidade: localizar a amostra e declarar as 16 colunas;
- entrada: estrutura do projeto e metadados da fonte;
- processamento: cria um caminho independente da pasta atual do terminal;
- saída: `SAMPLE_PATH` e `EXPECTED_COLUMNS`;
- comunicação: usados pelo leitor e pelos testes;
- possível erro: arquivo movido ou cabeçalho alterado.

### Leitura

- responsabilidade: abrir o CSV e devolver registros;
- entrada: arquivo UTF-8 separado por `;`;
- processamento: `csv.DictReader` associa cada valor ao nome da coluna;
- saída: lista de dicionários de texto;
- comunicação: envia os registros para `analyze_records`;
- possíveis erros: arquivo inexistente, codificação inválida ou esquema diferente.

O leitor aceita `utf-8-sig` porque essa codificação também remove o BOM quando ele existe. A amostra não possui BOM, mas o comportamento continua seguro.

### Interpretação de data e preço

- responsabilidade: verificar se textos possuem formatos utilizáveis;
- entrada: data `dd/mm/aaaa` ou preço com vírgula;
- processamento: usa `datetime.strptime` e `Decimal`;
- saída: objetos de data e decimal;
- possíveis erros: calendário impossível ou caracteres não numéricos.

`Decimal` foi escolhido para valores monetários. `float` é mais comum em cálculos gerais, mas representa muitos decimais apenas de forma aproximada.

### Perfil de qualidade

- responsabilidade: produzir indicadores da amostra;
- entrada: lista de registros;
- processamento: conta vazios, espaços, duplicidades e formatos inválidos;
- saída: dicionário `summary`;
- comunicação: o apresentador e os testes leem esse resumo;
- possível erro: regra simplificada ser interpretada como validação completa.

A unidade é conferida com uma regra simples: GNV usa `R$ / m³` e os outros produtos da amostra usam `R$ / litro`. Isso vale para o escopo observado, não é uma regra universal para qualquer dataset.

### Apresentação

- responsabilidade: tornar o resultado legível no terminal;
- entrada: resumo calculado;
- processamento: formata listas e contagens;
- saída: texto impresso;
- comunicação: não grava arquivos nem modifica a amostra;
- possível erro: usar os números sem ler as limitações.

## 8. Como executar

Na raiz do projeto:

```bash
python3 exploration/explore_sample.py
```

Não é necessário instalar Pandas ou outra dependência.

## 9. Como testar

Execute:

```bash
python3 -m unittest discover -s tests -v
PYTHONPYCACHEPREFIX=/tmp/fuelvision-pycache python3 -m py_compile exploration/explore_sample.py tests/test_explore_sample.py
```

Os testes verificam:

- 60 linhas, 16 colunas, cinco regiões e seis produtos;
- formatos válidos de datas, preços e unidades na amostra;
- rejeição de cabeçalho inesperado;
- ausência de nomes repetidos no esquema esperado.

## 10. Resultados esperados

O script deve informar, entre outros resultados:

```text
Rows: 60
Columns: 16
Exact duplicate rows: 0
Invalid dates: 0
Invalid sale prices: 0
```

Os testes devem terminar com `OK`.

## 11. Erros comuns

- `FileNotFoundError`: amostra ausente ou movida;
- erro sobre `documented ANP schema`: cabeçalho diferente do esperado;
- `ModuleNotFoundError: pandas`: Pandas não é usado nem necessário neste módulo;
- `PermissionError` na compilação: direcionar `PYTHONPYCACHEPREFIX` para `/tmp`;
- interpretar preço com `float` sem compreender aproximações;
- comparar GNV e combustíveis líquidos sem considerar unidades diferentes.

## 12. Limitações atuais

- apenas 60 registros não aleatórios;
- período limitado aos primeiros dias de 2026;
- sem limpeza, transformação ou rejeição de registros;
- sem pipeline, camada raw ou download automatizado;
- sem banco, API, Front-end ou Machine Learning;
- nenhuma conclusão estatística sobre preços do Brasil.

## 13. Decisões técnicas

### Biblioteca padrão em vez de Pandas

- escolha: usar `csv`, `datetime` e `Decimal`;
- alternativa: instalar Pandas;
- vantagem escolhida: nenhuma dependência para uma leitura pequena e direta;
- desvantagem: análises tabulares complexas exigiriam mais código;
- motivo: o objetivo atual cabe com clareza na biblioteca padrão.

### Amostragem por região e produto

- escolha: dois primeiros registros de cada combinação;
- alternativa: primeiras 60 linhas do arquivo;
- vantagem escolhida: garante presença de todos os grupos observados;
- desvantagem: não preserva proporções e favorece registros iniciais;
- motivo: estudar diversidade de esquema e unidades, não estimar o mercado.

### Preservar problemas observados

- escolha: registrar espaços e ausências sem corrigi-los;
- alternativa: limpar a amostra;
- vantagem escolhida: mantém evidências da qualidade real;
- desvantagem: os dados ainda não estão prontos para análises finais;
- motivo: limpeza pertence ao Módulo 3.

## 14. Alterações que eu devo conseguir fazer

1. acrescentar ao resumo a quantidade de estados distintos;
2. criar um teste para o período esperado da amostra;
3. melhorar uma descrição do dicionário sem mudar o significado oficial;
4. explicar por que o intervalo de preços não representa o Brasil.

## 15. Glossário

- **BOM**: marca opcional no início de um texto Unicode;
- **cabeçalho**: primeira linha que nomeia as colunas;
- **codificação**: regra que converte bytes em caracteres;
- **dado categórico**: valor pertencente a um conjunto de categorias;
- **delimitador**: caractere que separa campos no CSV;
- **metadado**: informação que descreve origem, formato ou campos de outro dado;
- **população**: conjunto completo sobre o qual se deseja estudar;
- **rastreabilidade**: capacidade de identificar origem e processo de produção;
- **registro**: uma linha de dados;
- **viés de seleção**: distorção causada pela forma de escolher uma amostra.

## O que você precisa compreender agora

- a origem e a versão dos dados precisam ser registradas;
- uma amostra ajuda a estudar estrutura, mas não autoriza generalizações;
- CSV armazena textos e o programa interpreta tipos;
- ausência e inconsistência devem ser entendidas antes de serem corrigidas;
- testes confirmam comportamentos definidos, não a qualidade de todo o arquivo.

## O que poderá ser aprofundado depois

- amostragem aleatória e representatividade estatística;
- inferência automática de tipos;
- processamento tabular com Pandas;
- validação de CNPJ e regras de domínio;
- perfil de qualidade sobre o conjunto completo.
