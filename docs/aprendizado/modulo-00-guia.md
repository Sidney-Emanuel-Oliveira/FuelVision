# Módulo 00 — Fundação e Planejamento

## 1. Objetivo

Este módulo preparou a base documental e o controle de versão local do FuelVision. Seu objetivo é permitir que o projeto cresça com propósito, limites e progresso verificáveis.

## 2. Problema resolvido

Antes deste módulo, havia instruções e um plano, mas o status estava vazio, não existia README, a arquitetura inicial não estava registrada e a pasta não era um repositório Git. Isso dificultava entender rapidamente o projeto e revisar sua evolução.

## 3. Conceitos estudados

**README** é o documento de entrada de um repositório. No FuelVision, ele apresenta o propósito, o estado atual, os documentos centrais e as verificações iniciais. É importante para que outra pessoa saiba por onde começar.

**Controle de versão** é o acompanhamento histórico de alterações. O Git foi iniciado localmente para preparar revisões futuras. Neste módulo não houve commit nem comunicação com repositórios remotos.

**`.gitignore`** é um arquivo de regras que impede o Git de incluir certos caminhos por padrão. No FuelVision, ele protege configurações locais como `.env`, artefatos de ferramentas e futuros dados gerados.

**Arquitetura de software** é a divisão do sistema em partes com responsabilidades claras. Neste módulo, a arquitetura é apenas planejada: ela ajuda a entender a ordem futura sem criar essas partes antes da hora.

**Escopo** define o que pertence e o que não pertence a uma entrega. O escopo do Módulo 0 inclui documentação e preparação, mas exclui toda funcionalidade de dados e aplicação.

## 4. Estrutura criada

```text
fuelvision/
├── .gitignore
├── AGENTS.md
├── README.md
└── docs/
    ├── PLANO_FUELVISION.md
    ├── PROPOSTA_DO_PROJETO.md
    ├── STATUS_DO_PROJETO.md
    ├── arquitetura/
    │   └── ARQUITETURA_PLANEJADA.md
    └── aprendizado/
        ├── modulo-00-exercicios.md
        ├── modulo-00-guia.md
        ├── modulo-00-minha-explicacao.md
        └── modulo-00-relatorio-tecnico.md
```

A pasta interna `.git/` também foi criada pelo Git, mas não aparece na árvore por ser metadado da ferramenta e não documentação do projeto.

## 5. Responsabilidade de cada arquivo

- `AGENTS.md`: instruções permanentes de trabalho e ensino;
- `README.md`: apresentação e navegação inicial;
- `.gitignore`: exclusões do controle de versão;
- `docs/PLANO_FUELVISION.md`: fonte oficial dos módulos e da progressão;
- `docs/PROPOSTA_DO_PROJETO.md`: problema, objetivos, público e limites;
- `docs/arquitetura/ARQUITETURA_PLANEJADA.md`: componentes e dependências previstos;
- `docs/STATUS_DO_PROJETO.md`: situação oficial de cada módulo;
- arquivos `modulo-00-*`: guia, atividades, modelo do estudante e evidências técnicas.

## 6. Fluxo de funcionamento

Como não existe aplicação executável, o fluxo deste módulo é documental:

```text
instruções permanentes → plano oficial → proposta → arquitetura planejada → status → revisão e aprendizado
```

## 7. Explicação do código por blocos

Este módulo não possui código da aplicação. Os arquivos podem ser entendidos em três blocos.

### Entrada e orientação

- faz: apresenta o projeto e aponta as regras;
- existe para: evitar que uma pessoa comece por um módulo incorreto;
- recebe: leitura do `README.md`, `AGENTS.md` e plano;
- devolve: propósito, ordem e limites;
- comunica-se com: todos os documentos;
- pode dar errado: links ou informações podem ficar inconsistentes.

### Planejamento técnico

- faz: registra proposta e arquitetura progressiva;
- existe para: separar responsabilidades futuras;
- recebe: objetivos do plano oficial;
- devolve: visão organizada, sem implementação;
- comunica-se com: status e módulos posteriores;
- pode dar errado: uma descrição futura pode ser confundida com algo já pronto. Por isso o estado real está explícito.

### Controle e aprendizagem

- faz: registra estado, verificações, exercícios e reflexão;
- existe para: demonstrar conclusão e apoiar o estudo;
- recebe: arquivos criados e resultados reais dos comandos;
- devolve: evidências e tarefas para o estudante;
- comunica-se com: guia, relatório e status;
- pode dar errado: registrar um teste não executado. O relatório deve conter apenas comandos realmente usados.

## 8. Como executar

Não há aplicação para iniciar. Para consultar o ambiente e o repositório:

```bash
python3 --version
java -version
node --version
npm --version
git status --short --branch
```

## 9. Como testar

As verificações deste módulo são estruturais e documentais:

```bash
git status --short --branch
git diff --check
prettier --check README.md docs/PROPOSTA_DO_PROJETO.md docs/STATUS_DO_PROJETO.md docs/arquitetura/ARQUITETURA_PLANEJADA.md "docs/aprendizado/*.md"
```

Também é necessário revisar arquivos ignorados, temporários, possíveis segredos e o diff. Um formatador verifica estilo; ele não confirma se uma decisão técnica está correta.

## 10. Resultados esperados

- o Git reconhece a pasta como repositório;
- o status lista os arquivos ainda sem commit;
- a documentação possui as seções obrigatórias;
- `.env` é ignorado;
- não existem implementações de módulos posteriores;
- as verificações terminam sem erro ou têm seus problemas registrados no relatório.

## 11. Erros comuns

- `not a git repository`: o Git ainda não foi iniciado ou o comando foi executado fora da pasta;
- `command not found`: a ferramenta consultada não está instalada ou não está no `PATH`, a lista de locais pesquisados pelo terminal;
- arquivo sensível aparecendo no status: revisar `.gitignore` antes de qualquer commit;
- link quebrado: conferir nome, letras maiúsculas e caminho relativo;
- confundir arquitetura planejada com implementada: consultar a seção “Estado real” e o status.

## 12. Limitações atuais

Não existem fonte de dados analisada, dataset, pipeline, banco, consultas, API, Front-end, Machine Learning, testes de código, container ou deploy. Python, Java, Node.js e npm foram verificados, mas não são dependências deste módulo.

## 13. Decisões técnicas

Foi escolhida documentação Markdown porque é legível como texto, funciona bem com Git e não exige ferramenta especial. A alternativa seria usar uma plataforma externa de documentação, que teria edição visual mais rica, mas criaria uma dependência desnecessária neste começo.

O `.gitignore` inclui categorias de tecnologias futuras apenas como proteção de versionamento. Isso não instala nem implementa essas tecnologias. A vantagem é reduzir o risco de versionar segredos ou artefatos; a desvantagem é exigir revisão quando a estrutura real surgir.

## 14. Alterações que eu devo conseguir fazer

Depois de compreender o módulo, você deve conseguir:

1. melhorar uma frase do propósito sem alterar o escopo;
2. acrescentar um erro documental comum ao guia;
3. explicar por que uma pasta futura não deve ser criada vazia;
4. adicionar uma regra segura e justificada ao `.gitignore`.

## 15. Glossário

- **branch**: linha de desenvolvimento mantida pelo Git;
- **dependência**: ferramenta ou biblioteca necessária para executar uma parte do projeto;
- **documentação**: registro que explica propósito, uso, decisões e limites;
- **Git**: sistema distribuído de controle de versão;
- **Markdown**: formato textual simples usado nos arquivos `.md`;
- **módulo**: etapa delimitada do plano com objetivos e entregas próprios;
- **repositório**: pasta acompanhada por um sistema de controle de versão;
- **segredo**: informação sensível, como senha, token ou chave privada;
- **verificação reproduzível**: comando ou procedimento que outra pessoa pode repetir.

## O que você precisa compreender agora

- o plano oficial controla a ordem do desenvolvimento;
- arquitetura planejada não significa funcionalidade implementada;
- Git acompanha mudanças, enquanto `.gitignore` reduz inclusões indevidas;
- documentação e verificações são entregas técnicas, não enfeites.

## O que poderá ser aprofundado depois

- estratégias de branches e revisão de código;
- automação de lint e integração contínua;
- diagramas formais de arquitetura;
- organização detalhada de cada componente executável.
