# FuelVision

O FuelVision é um projeto educacional e profissional que evoluirá para uma plataforma de análise de preços de combustíveis baseada em dados públicos brasileiros.

O **Módulo 3 — Limpeza, Transformação e Validação** adicionou a conversão dos dados brutos em registros processados, com padronização, regras de qualidade, separação de rejeitados e manifesto reproduzível. Ainda não existe banco de dados, API, interface ou modelo de Machine Learning.

## Propósito

O projeto pretende reunir, de forma gradual:

- Engenharia de Dados para obtenção, validação e preparação dos dados;
- Analytics para produzir consultas e indicadores;
- uma API para disponibilizar informações;
- uma interface para apresentar resultados;
- Machine Learning para experimentos de previsão e detecção de comportamentos atípicos.

Cada capacidade será construída somente no módulo correspondente. A ordem oficial está em [`docs/PLANO_FUELVISION.md`](docs/PLANO_FUELVISION.md).

## Estado atual

Consulte:

- [`docs/PROPOSTA_DO_PROJETO.md`](docs/PROPOSTA_DO_PROJETO.md): problema, objetivos e limites;
- [`docs/arquitetura/ARQUITETURA_PLANEJADA.md`](docs/arquitetura/ARQUITETURA_PLANEJADA.md): evolução planejada;
- [`docs/STATUS_DO_PROJETO.md`](docs/STATUS_DO_PROJETO.md): progresso dos módulos;
- [`docs/dados/FONTE_DADOS_ANP.md`](docs/dados/FONTE_DADOS_ANP.md): origem e processo de amostragem;
- [`docs/dados/DICIONARIO_DADOS.md`](docs/dados/DICIONARIO_DADOS.md): significado dos 16 campos;
- [`docs/dados/RELATORIO_EXPLORACAO.md`](docs/dados/RELATORIO_EXPLORACAO.md): resultados e limitações;
- [`docs/pipeline/INGESTAO_RAW.md`](docs/pipeline/INGESTAO_RAW.md): operação e regras da ingestão raw;
- [`docs/pipeline/TRANSFORMACAO_VALIDACAO.md`](docs/pipeline/TRANSFORMACAO_VALIDACAO.md): limpeza, validações e rejeições;
- [`docs/dados/DICIONARIO_DADOS_PROCESSADOS.md`](docs/dados/DICIONARIO_DADOS_PROCESSADOS.md): esquema da saída processada.

## Pré-requisitos atuais

Para executar as ferramentas atuais, basta ter:

- um editor de texto;
- Git para consultar o estado do repositório;
- Python 3.9 ou compatível;
- um terminal para executar os comandos documentados.

O script utiliza somente a biblioteca padrão do Python. Pandas não é necessário neste módulo.

## Como executar

Na raiz do projeto, execute:

```bash
python3 exploration/explore_sample.py
python3 -m pipeline.ingest_raw data/samples/precos-combustiveis-amostra.csv
python3 -m pipeline.transform_data data/raw/precos-combustiveis-amostra__d5dd2159be5b.csv
python3 -m unittest discover -s tests -v
```

O primeiro comando apresenta o perfil da amostra. O segundo preserva a entrada raw. O terceiro gera dados processados, rejeitados e manifesto. O quarto executa todos os testes.

Leia os documentos técnicos do Módulo 3 nesta ordem:

1. `docs/pipeline/INGESTAO_RAW.md`;
2. `docs/pipeline/TRANSFORMACAO_VALIDACAO.md`;
3. `docs/dados/DICIONARIO_DADOS_PROCESSADOS.md`.

## Limitações atuais

- somente uma amostra não representativa foi versionada;
- o processamento foi validado somente sobre uma amostra pequena;
- as regras de padronização ainda não usam banco ou catálogo externo;
- nenhum banco foi configurado;
- nenhuma API ou interface foi criada;
- nenhum modelo de Machine Learning foi desenvolvido;
- não existem conclusões estatísticas ou métricas de negócio.

Essas limitações são intencionais e preservam a progressão definida no plano.

## Regras de contribuição

- trabalhar em apenas um módulo por vez;
- não versionar `.env`, credenciais, datasets grandes ou artefatos gerados;
- executar e registrar as verificações aplicáveis;
- documentar decisões e limitações;
- executar commit e push somente após a conclusão e aprovação das verificações do módulo.
