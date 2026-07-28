# Fonte de dados da ANP

## 1. Conjunto escolhido

O Módulo 1 utiliza a **Série Histórica de Preços de Combustíveis e de GLP**, publicada pela Agência Nacional do Petróleo, Gás Natural e Biocombustíveis (ANP).

Uma **fonte oficial** é um dado publicado pelo órgão responsável por produzi-lo ou mantê-lo. Neste caso, a própria ANP informa que acompanha preços de revendedores por meio do Levantamento de Preços de Combustíveis (LPC), realizado semanalmente por empresa contratada.

Links oficiais, consultados em 28/07/2026:

- [página da Série Histórica de Preços de Combustíveis e de GLP](https://www.gov.br/anp/pt-br/centrais-de-conteudo/dados-abertos/serie-historica-de-precos-de-combustiveis);
- [metadados da série histórica](https://www.gov.br/anp/pt-br/centrais-de-conteudo/dados-abertos/arquivos/shpc/metadados-serie-historica-precos-combustiveis-1.pdf);
- [arquivo de combustíveis automotivos do 1º semestre de 2026](https://www.gov.br/anp/pt-br/centrais-de-conteudo/dados-abertos/arquivos/shpc/dsas/ca/ca-2026-01.zip).

## 2. O que a fonte representa

Segundo a ANP, a pesquisa abrange gasolina C, etanol hidratado, óleo diesel B, GNV e GLP P13. O recurso escolhido para a amostra é o arquivo de **combustíveis automotivos** do primeiro semestre de 2026; o arquivo separado de GLP P13 não foi utilizado.

Cada registro do CSV representa a observação de um produto, em uma revenda, numa data de coleta, acompanhada do valor de venda e de dados de localização e identificação.

## 3. Formato e atualização

Os metadados oficiais informam:

- formato: CSV;
- periodicidade: semanal, mensal e semestral;
- origem: ANP/SDC — Superintendência de Defesa da Concorrência;
- contato publicado: `sdc@anp.gov.br`.

Na inspeção do arquivo de 2026, foram observados:

- arquivo compactado em ZIP;
- CSV separado por ponto e vírgula;
- texto UTF-8 com BOM;
- datas no formato `dd/mm/aaaa`;
- valores decimais com vírgula;
- 16 colunas.

## 4. Identificação do arquivo utilizado

- recurso: combustíveis automotivos, 1º semestre de 2026;
- tamanho do ZIP: `8.488.624` bytes;
- tamanho do CSV descompactado: `72.117.162` bytes;
- registros do CSV completo: `422.418`, sem contar o cabeçalho;
- SHA-256 do ZIP baixado em 28/07/2026: `a2c95e5dfa324a9d7253d4e8d53022e0c08dcc5eb6f18551527ee9f29305c54c`.

**SHA-256** é um resumo matemático usado para identificar o conteúdo de um arquivo. Se um byte mudar, o resumo tende a mudar. Ele ajuda na rastreabilidade, mas não substitui a validação da origem oficial.

## 5. Como a amostra foi criada

O arquivo completo foi baixado somente para `/tmp`, fora do repositório. Em seguida, um comando temporário baseado na biblioteca `csv` do Python percorreu o conteúdo na ordem publicada e selecionou os dois primeiros registros de cada combinação entre:

- região: `CO`, `N`, `NE`, `S` e `SE`;
- produto: `DIESEL`, `DIESEL S10`, `ETANOL`, `GASOLINA`, `GASOLINA ADITIVADA` e `GNV`.

Resultado: 30 combinações × 2 registros = 60 registros.

A seleção é determinística para a versão identificada do arquivo: repetir a regra sobre o mesmo conteúdo gera a mesma amostra. O CSV foi regravado em UTF-8, sem o BOM inicial, mantendo cabeçalho, separador e valores dos campos.

## 6. O que a amostra não representa

A amostra foi construída para estudar estrutura e qualidade, não para realizar inferência estatística. Ela:

- não é aleatória;
- não preserva a proporção real de registros por região ou produto;
- contém apenas os primeiros registros encontrados em cada grupo;
- não permite generalizar médias, mínimos ou máximos para municípios, estados, regiões ou para o Brasil;
- não substitui o conjunto completo em análises futuras.

## 7. Cuidados de uso

- o CNPJ e o endereço identificam estabelecimentos e devem ser tratados como textos públicos da fonte, sem enriquecimentos indevidos;
- o arquivo completo não deve ser versionado;
- atualizações da ANP podem alterar conteúdo, período, links ou estrutura;
- a ausência de `Valor de Compra` é esperada em períodos recentes: os metadados informam que essa série está disponível somente até agosto de 2020;
- resultados devem sempre registrar versão da fonte, regra de seleção e limitações.
