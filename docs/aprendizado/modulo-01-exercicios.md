# Exercícios do Módulo 01 — Fonte de Dados e Exploração

Não há respostas neste arquivo. Registre suas respostas em `modulo-01-minha-explicacao.md`.

## 1. Perguntas teóricas

1. Por que a página da ANP é considerada uma fonte oficial para este projeto?
2. Qual é a diferença entre o arquivo completo, uma amostra e a população que desejamos estudar?
3. Por que CNPJ e CEP devem ser tratados como texto mesmo sendo formados principalmente por dígitos?
4. O que significa encontrar zero duplicidades exatas e o que esse resultado não garante?
5. Por que `Valor de Compra` vazio não deve ser preenchido automaticamente com zero?

## 2. Exercícios práticos

1. Execute o script e relacione cada linha do resumo à seção correspondente do relatório de exploração.
2. Abra a amostra em um editor de texto e identifique cabeçalho, delimitador, um valor ausente e as duas unidades de medida.
3. Execute os testes individualmente com `python3 -m unittest tests.test_explore_sample -v` e descreva o propósito de cada caso.

## 3. Exercício de depuração

Em uma cópia temporária da amostra, troque o cabeçalho `Municipio` por `Cidade` e tente carregá-la com `load_records`. Explique o erro e por que rejeitar silenciosamente a mudança seria perigoso. Não altere a amostra oficial do módulo.

## 4. Exercício de modificação do código

Adicione ao resumo a quantidade de estados distintos da amostra. Crie primeiro um teste que espera esse valor e depois modifique `analyze_records` e `print_summary`. Não calcule nem implemente médias de preço.

## 5. Pergunta sobre limitações

Por que o menor e o maior preço da amostra não podem ser apresentados como o menor e o maior preço do Brasil no primeiro semestre de 2026?

## 6. Pergunta sobre decisões técnicas

Quais são a vantagem e a desvantagem de usar a biblioteca padrão do Python em vez de instalar Pandas neste módulo?
