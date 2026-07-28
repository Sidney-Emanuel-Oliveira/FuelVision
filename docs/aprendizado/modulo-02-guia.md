# Módulo 02 — Ingestão da Camada Raw

## 1. Objetivo

Este módulo construiu o primeiro pipeline do FuelVision. Ele recebe um CSV local, verifica requisitos mínimos, preserva seus bytes na camada raw, evita sobrescritas e registra a execução.

## 2. Problema resolvido

Antes deste módulo, o projeto conseguia explorar apenas uma amostra conhecida. Ainda não existia um fluxo controlado para receber um arquivo e preservar sua versão original.

Copiar manualmente um arquivo pode causar nomes inconsistentes, sobrescrita acidental e ausência de evidências. O pipeline transforma essa tarefa em um processo verificável e repetível.

## 3. Conceitos estudados

**Pipeline de dados** é uma sequência organizada de etapas que recebe dados, realiza operações e produz uma saída. Neste módulo, a entrada é um CSV e a saída é uma cópia raw verificada.

**Camada raw** é a área que preserva dados como recebidos. No FuelVision, nenhuma linha, coluna ou valor é alterado durante a cópia.

**Validação estrutural** verifica se a forma mínima da entrada é aceitável. Aqui, ela confirma caminho, extensão e colunas essenciais, mas não corrige dados.

**SHA-256** é um algoritmo que resume bytes em um identificador. Ele aparece no nome raw e na verificação de integridade.

**Integridade** é a garantia de que os bytes copiados são iguais aos bytes da entrada. O pipeline compara os hashes antes de aceitar a saída.

**Idempotência** significa repetir a mesma entrada sem produzir efeitos adicionais indevidos. Uma segunda ingestão devolve `already_exists`.

**Log** é o registro dos eventos da execução. Ele mostra início, resultado, destino, hash, tamanho e falhas.

**Interface de linha de comando** é uma forma de controlar o programa com argumentos no terminal. No FuelVision, ela recebe o caminho de entrada e opções de saída e log.

## 4. Estrutura criada

```text
fuelvision/
├── data/
│   └── raw/
│       └── <arquivo-gerado-e-ignorado-pelo-git>
├── docs/
│   ├── pipeline/
│   │   └── INGESTAO_RAW.md
│   └── aprendizado/
│       ├── modulo-02-exercicios.md
│       ├── modulo-02-guia.md
│       ├── modulo-02-minha-explicacao.md
│       └── modulo-02-relatorio-tecnico.md
├── logs/
│   └── ingestion.log
├── pipeline/
│   ├── __init__.py
│   └── ingest_raw.py
└── tests/
    └── test_ingest_raw.py
```

Os arquivos de `data/raw/` e `logs/` são gerados durante a execução e ignorados pelo Git.

## 5. Responsabilidade de cada arquivo

- `pipeline/__init__.py`: identifica `pipeline` como pacote Python;
- `pipeline/ingest_raw.py`: contém validação, hash, cópia, log e CLI;
- `tests/test_ingest_raw.py`: verifica cenários de sucesso e falha;
- `docs/pipeline/INGESTAO_RAW.md`: referência operacional e técnica;
- arquivos `modulo-02-*`: guia, exercícios, modelo e relatório;
- `README.md`: mostra os comandos atuais;
- `docs/STATUS_DO_PROJETO.md`: registra a conclusão do módulo;
- `data/raw/*`: saídas locais preservadas;
- `logs/ingestion.log`: histórico local das execuções.

## 6. Fluxo de funcionamento

```text
argumentos
→ configuração do log
→ validação do caminho
→ validação do cabeçalho
→ SHA-256 da entrada
→ nome determinístico
→ cópia exclusiva ou reutilização segura
→ SHA-256 do destino
→ resumo e log
```

## 7. Explicação do código por blocos

### Constantes e erros

- responsabilidade: declarar caminhos padrão, colunas mínimas e falhas conhecidas;
- entrada: decisões do módulo e esquema estudado no Módulo 1;
- processamento: não realiza processamento em tempo de importação;
- saída: valores reutilizados pelas funções;
- comunicação: validação, CLI e testes importam essas definições;
- possíveis erros: uma coluna necessária ser adicionada sem justificativa.

As exceções específicas permitem diferenciar arquivo ausente, extensão inválida, esquema incompleto e conflito de destino.

### Validação do caminho

- responsabilidade: confirmar existência, arquivo regular e extensão `.csv`;
- entrada: `Path` fornecido pelo usuário;
- processamento: usa `exists`, `is_file` e `suffix`;
- saída: nenhuma quando válido; exceção quando inválido;
- comunicação: executada antes de abrir o arquivo;
- possíveis erros: caminho digitado incorretamente ou apontando para pasta.

### Validação do cabeçalho

- responsabilidade: ler somente a primeira linha e procurar colunas mínimas;
- entrada: CSV UTF-8 com separador `;`;
- processamento: `csv.reader` e comparação de nomes;
- saída: cabeçalho completo;
- comunicação: o cabeçalho aparece no resultado interno;
- possíveis erros: codificação incompatível, arquivo vazio ou coluna ausente.

Colunas adicionais são preservadas. Essa decisão evita transformar uma validação mínima em uma regra rígida sobre todas as versões futuras.

### Cálculo do hash

- responsabilidade: identificar o conteúdo;
- entrada: arquivo em modo binário;
- processamento: lê blocos de 1 MiB e atualiza SHA-256;
- saída: texto hexadecimal com 64 caracteres;
- comunicação: nome do destino, integridade e log;
- possíveis erros: falta de permissão ou alteração da fonte durante a cópia.

Ler em blocos evita carregar arquivos grandes inteiros na memória.

### Cópia sem sobrescrita

- responsabilidade: preservar bytes sem substituir um destino existente;
- entrada: origem, destino e hash esperado;
- processamento: cria diretório, usa modo exclusivo, copia em blocos e confere o hash;
- saída: `created` ou `already_exists`;
- comunicação: envia status para `ingest_file`;
- possíveis erros: permissão, espaço em disco, conflito ou falha de integridade.

Se a execução criou um arquivo parcial e depois falhou, o bloco remove somente esse arquivo parcial.

### Orquestração

- responsabilidade: executar as etapas na ordem correta;
- entrada: origem e diretório raw;
- processamento: valida, calcula, copia e reúne metadados;
- saída: dicionário com status, caminhos, hash, bytes e colunas;
- comunicação: CLI e testes chamam `ingest_file`;
- possíveis erros: qualquer exceção esperada das etapas internas.

**Orquestração** é a coordenação de funções menores. Ela não significa uma ferramenta externa; neste módulo é apenas a função que organiza o fluxo.

### CLI e logs

- responsabilidade: receber argumentos e comunicar o resultado;
- entrada: terminal;
- processamento: `argparse`, configuração do log e chamada da ingestão;
- saída: texto no terminal, código de saída e arquivo de log;
- comunicação: traduz exceções esperadas em código `1`;
- possíveis erros: argumentos inválidos ou diretório de log sem permissão.

## 8. Como executar

Na raiz do projeto:

```bash
python3 pipeline/ingest_raw.py data/samples/precos-combustiveis-amostra.csv
```

Primeira execução:

```text
status=created
```

Execuções seguintes com o mesmo conteúdo:

```text
status=already_exists
```

## 9. Como testar

```bash
python3 -m unittest discover -s tests -v
PYTHONPYCACHEPREFIX=/tmp/fuelvision-module-02-pycache \
  python3 -m py_compile exploration/explore_sample.py pipeline/__init__.py pipeline/ingest_raw.py tests/test_explore_sample.py tests/test_ingest_raw.py
```

Os testes do módulo cobrem:

- igualdade byte a byte;
- repetição sem sobrescrita;
- arquivo inexistente;
- diretório usado como entrada;
- extensão diferente de CSV;
- extensão `.CSV` em letras maiúsculas;
- arquivo vazio;
- colunas obrigatórias ausentes;
- conflito de conteúdo no destino;
- execução completa da CLI com log;
- falha da CLI com código de saída e log.

## 10. Resultados esperados

- todos os 16 testes do projeto terminam com `OK`;
- o arquivo raw possui `9.937` bytes para a amostra atual;
- origem e destino possuem SHA-256 `d5dd2159be5bd72228393f18b60a0c6eeccd061b9870fe3f0542b1a7a1620b23`;
- a segunda execução não altera o arquivo;
- `data/raw/` e `logs/` permanecem ignorados pelo Git.

## 11. Erros comuns

- `Input file does not exist`: caminho incorreto;
- `Input path is not a regular file`: uma pasta foi informada;
- `Input file must use the .csv extension`: extensão diferente;
- `Missing required columns`: cabeçalho incompatível;
- `Destination already exists with different content`: conflito que exige investigação;
- `Permission denied`: diretório sem permissão de leitura ou escrita;
- código `2`: argumento obrigatório ausente ou opção escrita incorretamente.

## 12. Limitações atuais

- entrada somente local e CSV;
- separador fixo em `;` e codificação UTF-8;
- sem download automático;
- sem validação de todas as linhas;
- sem limpeza, transformação ou dados processados;
- sem catálogo central de execuções;
- sem banco, API, Front-end ou Machine Learning.

## 13. Decisões técnicas

### Nome por conteúdo

- escolha: nome original mais 12 caracteres do SHA-256;
- alternativa: adicionar data e hora;
- vantagem: mesma entrada gera o mesmo destino;
- desvantagem: o nome não mostra quando a execução ocorreu;
- motivo: horários pertencem ao log, enquanto o nome identifica conteúdo.

### Repetição segura

- escolha: reutilizar destino quando o hash completo é igual;
- alternativa: falhar sempre que o destino existir;
- vantagem: facilita reexecução sem cópias duplicadas;
- desvantagem: exige uma leitura adicional do destino;
- motivo: idempotência é importante em pipelines reproduzíveis.

### Biblioteca padrão

- escolha: `csv`, `hashlib`, `shutil`, `logging` e `argparse`;
- alternativa: adicionar bibliotecas externas;
- vantagem: zero dependências novas;
- desvantagem: menos recursos prontos para pipelines maiores;
- motivo: o escopo atual é pequeno e totalmente atendido pelo Python.

## 14. Alterações que eu devo conseguir fazer

1. adicionar uma coluna mínima justificada e atualizar os testes;
2. alterar o tamanho dos blocos usados no hash e explicar o efeito;
3. criar um teste para extensão `.CSV` em letras maiúsculas;
4. melhorar uma mensagem de erro sem ocultar sua causa.

## 15. Glossário

- **argumento posicional**: valor obrigatório informado sem nome de opção;
- **byte**: unidade básica do conteúdo binário de um arquivo;
- **CLI**: interface de linha de comando;
- **código de saída**: número que informa sucesso ou falha ao sistema;
- **colisão**: dois conteúdos produzirem o mesmo nome resumido;
- **exceção**: objeto que representa uma falha durante a execução;
- **hash**: resumo calculado a partir do conteúdo;
- **pacote Python**: diretório organizado para conter módulos importáveis;
- **sobrescrita**: substituição do conteúdo de um arquivo existente;
- **status**: resultado categórico de uma operação.

## O que você precisa compreender agora

- raw significa preservar a entrada, não corrigi-la;
- validação mínima protege o fluxo sem antecipar transformações;
- hash identifica conteúdo e verifica integridade;
- idempotência permite reexecuções seguras;
- logs registram eventos, mas não substituem testes.

## O que poderá ser aprofundado depois

- cópias transacionais e sistemas de arquivos distribuídos;
- manifestos e catálogos de dados;
- armazenamento em nuvem;
- observabilidade centralizada;
- ingestões paralelas e agendadas.
