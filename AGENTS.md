# Instruções permanentes do projeto FuelVision

## 1. Perfil do estudante

Este projeto está sendo desenvolvido por um estudante que atualmente cursa:

- 4º período de Engenharia de Software;
- 2º período de Big Data e Inteligência Artificial.

As explicações devem ser compatíveis com esse momento acadêmico.

O objetivo não é reduzir o rigor técnico, eliminar conceitos importantes ou alterar a lógica correta da solução. O objetivo é apresentar a mesma lógica e o mesmo raciocínio técnico em uma linguagem progressiva, clara e adequada ao nível atual do estudante.

## 2. Estilo das explicações

Toda documentação educacional deve ser escrita em português do Brasil.

As explicações devem:

- utilizar linguagem clara e direta;
- evitar frases excessivamente acadêmicas;
- evitar termos técnicos não explicados;
- apresentar primeiro o propósito e depois a implementação;
- explicar por que algo existe antes de explicar como funciona;
- dividir assuntos complexos em blocos menores;
- relacionar novos conceitos ao que já foi implementado;
- manter a precisão técnica;
- informar quando uma explicação está sendo simplificada;
- diferenciar claramente uma simplificação de uma definição técnica completa.

Não transformar a explicação em conteúdo infantil ou superficial.

Não omitir decisões, riscos ou limitações importantes apenas porque o estudante ainda é iniciante.

## 3. Destaque dos conceitos

Ao apresentar um conceito importante pela primeira vez:

1. Escreva o termo em **negrito**.
2. Apresente uma definição simples.
3. Explique onde ele aparece no módulo.
4. Dê um exemplo relacionado ao FuelVision.
5. Informe por que o conceito é importante.

Exemplo:

**Pipeline de dados** é uma sequência organizada de etapas que recebe dados, realiza operações sobre eles e gera uma saída. No FuelVision, o pipeline receberá os arquivos de preços da ANP, validará seu formato e produzirá dados preparados para análise.

Não destacar palavras aleatórias. O negrito deve ser reservado para conceitos, responsabilidades, entradas, saídas, comandos e avisos relevantes.

## 4. Estrutura pedagógica

Sempre que explicar uma funcionalidade, utilizar esta ordem:

### O que será construído

Explique o resultado esperado.

### Por que isso é necessário

Explique o problema técnico ou de negócio resolvido.

### Conceitos utilizados

Defina os conceitos importantes em linguagem acessível.

### Como o fluxo funciona

Mostre a sequência da execução.

Exemplo:

arquivo CSV → leitura → validação → transformação → armazenamento

### Arquivos envolvidos

Explique a responsabilidade de cada arquivo.

### Código por blocos

Divida o código em partes lógicas.

Para cada bloco, explique:

- responsabilidade;
- entrada;
- processamento;
- saída;
- comunicação com outras partes;
- possíveis erros;
- como verificar se está funcionando.

### Como executar e testar

Apresente comandos e resultados esperados.

### O que o estudante precisa compreender agora

Liste os conhecimentos essenciais para avançar.

### O que poderá ser aprofundado depois

Liste assuntos mais avançados que não precisam ser dominados imediatamente.

## 5. Nível de profundidade

Não é necessário explicar literalmente todas as linhas de código.

Priorizar:

- fluxo da aplicação;
- responsabilidade das funções;
- responsabilidade das classes;
- entrada e saída;
- regras de negócio;
- transformações de dados;
- chamadas entre arquivos;
- tratamento de erros;
- testes;
- decisões de arquitetura.

Explicar uma linha individualmente apenas quando ela:

- possuir sintaxe nova e importante;
- modificar o fluxo da aplicação;
- representar uma regra relevante;
- puder causar um erro difícil de entender;
- utilizar um conceito essencial do módulo.

Não gastar longas explicações com imports triviais, chaves, parênteses ou estruturas repetitivas.

## 6. Progressão do aprendizado

A dificuldade deve aumentar gradualmente.

Antes de utilizar um conceito mais avançado:

1. Verifique se ele já foi apresentado.
2. Caso não tenha sido, forneça uma introdução.
3. Mostre um exemplo simples.
4. Aplique o conceito ao projeto.
5. Registre-o no glossário do módulo.

Não assumir que o estudante já domina:

- ambientes virtuais;
- dependências;
- orientação a objetos avançada;
- injeção de dependência;
- ORM;
- serialização;
- arquitetura em camadas;
- processamento vetorizado;
- estatística;
- Machine Learning;
- métricas de avaliação;
- containers;
- integração contínua.

Esses assuntos devem ser ensinados no módulo em que aparecerem.

## 7. Rigor técnico

A linguagem deve ser acessível, mas a implementação deve seguir boas práticas reais.

Não:

- escolher uma solução tecnicamente incorreta apenas por ser mais simples;
- ocultar erros;
- retirar validações necessárias;
- criar resultados falsos;
- inventar métricas;
- chamar um conjunto pequeno de dados de Big Data sem justificativa;
- chamar uma regra comum de Inteligência Artificial;
- declarar um modelo como bom sem avaliação;
- adicionar tecnologias apenas para aumentar a lista do projeto.

Quando existirem duas opções, explicar:

- opção escolhida;
- alternativa;
- vantagem;
- desvantagem;
- motivo da decisão.

## 8. Desenvolvimento por módulos

Ler antes de qualquer trabalho:

- `docs/PLANO_FUELVISION.md`;
- `docs/STATUS_DO_PROJETO.md`;
- documentação do módulo atual.

Executar somente um módulo por vez.

Não criar antecipadamente funcionalidades de módulos futuros.

Não iniciar o próximo módulo automaticamente.

## 9. Regra de autorização

Somente iniciar o módulo seguinte quando a mensagem do usuário, removendo espaços e ignorando maiúsculas ou minúsculas, for exatamente:

`sim`

Exemplos que autorizam:

- `sim`
- `Sim`
- ` SIM `

Exemplos que não autorizam:

- `acho que sim`
- `sim, mas tenho uma dúvida`
- `posso dizer sim?`
- qualquer explicação que contenha a palavra “sim”

Caso a resposta não seja exatamente `sim`, permanecer no módulo atual.

## 10. Encerramento obrigatório do módulo

Ao concluir cada módulo:

1. Executar os testes aplicáveis.
2. Revisar as alterações.
3. Criar o guia do módulo.
4. Criar os exercícios.
5. Criar o modelo para a explicação do estudante.
6. Criar o relatório técnico.
7. Atualizar o status do projeto.
8. Informar as limitações atuais.
9. Propor uma pequena alteração que o estudante deverá realizar.
10. Parar completamente.

Finalizar exatamente com:

“O módulo foi concluído. Revise a documentação, explique com suas palavras o que entendeu e realize os exercícios propostos. Digite apenas ‘sim’ quando estiver pronto para iniciar o próximo módulo.”

## 11. Exercícios

Não responder os exercícios pelo estudante.

Cada módulo deve conter:

- perguntas conceituais;
- exercícios práticos;
- uma pequena alteração manual;
- um exercício de depuração;
- uma pergunta sobre limitações;
- uma pergunta sobre decisões técnicas.

Os exercícios devem utilizar apenas conteúdos que já tenham sido ensinados.

## 12. Testes e revisão

Antes de considerar um módulo concluído:

- executar os testes;
- executar lint e formatação quando existirem;
- revisar o diff;
- procurar imports não utilizados;
- procurar código duplicado;
- procurar segredos;
- confirmar que `.env` não será versionado;
- confirmar que o módulo pode ser executado seguindo a documentação;
- registrar erros e correções no relatório técnico.

Não executar commit ou push sem autorização explícita.