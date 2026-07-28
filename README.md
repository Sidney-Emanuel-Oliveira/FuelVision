# FuelVision

O FuelVision é um projeto educacional e profissional que evoluirá para uma plataforma de análise de preços de combustíveis baseada em dados públicos brasileiros.

O **Módulo 1 — Fonte de Dados e Exploração** adicionou uma amostra pequena e rastreável dos dados oficiais da ANP, um leitor exploratório em Python e documentação sobre estrutura e qualidade. Ainda não existe pipeline, banco de dados, API, interface ou modelo de Machine Learning.

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
- [`docs/aprendizado/modulo-00-guia.md`](docs/aprendizado/modulo-00-guia.md): material educacional do Módulo 0;
- [`docs/dados/FONTE_DADOS_ANP.md`](docs/dados/FONTE_DADOS_ANP.md): origem e processo de amostragem;
- [`docs/dados/DICIONARIO_DADOS.md`](docs/dados/DICIONARIO_DADOS.md): significado dos 16 campos;
- [`docs/dados/RELATORIO_EXPLORACAO.md`](docs/dados/RELATORIO_EXPLORACAO.md): resultados e limitações;
- [`docs/aprendizado/modulo-01-guia.md`](docs/aprendizado/modulo-01-guia.md): material educacional do Módulo 1.

## Pré-requisitos do Módulo 1

Para executar a exploração, basta ter:

- um editor de texto;
- Git para consultar o estado do repositório;
- Python 3.9 ou compatível;
- um terminal para executar os comandos documentados.

O script utiliza somente a biblioteca padrão do Python. Pandas não é necessário neste módulo.

## Como executar a exploração

Na raiz do projeto, execute:

```bash
python3 exploration/explore_sample.py
python3 -m unittest discover -s tests -v
```

O primeiro comando apresenta o perfil da amostra. O segundo executa os testes básicos de leitura e estrutura.

Leia os documentos do Módulo 1 nesta ordem:

1. `docs/dados/FONTE_DADOS_ANP.md`;
2. `docs/dados/DICIONARIO_DADOS.md`;
3. `docs/dados/RELATORIO_EXPLORACAO.md`;
4. `docs/aprendizado/modulo-01-guia.md`;
5. `docs/aprendizado/modulo-01-exercicios.md`.

## Limitações atuais

- somente uma amostra não representativa foi versionada;
- nenhum pipeline de ingestão foi implementado;
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
- não executar commit ou push sem autorização explícita.
