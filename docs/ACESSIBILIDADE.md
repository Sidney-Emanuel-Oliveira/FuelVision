# Revisão de acessibilidade

## Objetivo

O dashboard foi revisado com base em critérios selecionados da WCAG 2.2. A
revisão melhora o acesso, mas não equivale a uma auditoria de conformidade nem a
testes completos com pessoas usuárias.

**Acessibilidade digital** é a prática de construir interfaces que possam ser
percebidas, compreendidas e operadas por pessoas com diferentes necessidades e
tecnologias assistivas.

## Controles existentes e revisados

| Área | Implementação |
| --- | --- |
| idioma | documento declara `lang="pt-BR"` |
| estrutura | `header`, `main`, `footer`, títulos e seções semânticas |
| teclado | link “Pular para o conteúdo principal” e foco visível |
| formulários | rótulos associados por envolvimento de cada controle |
| estados | carregamentos usam `role="status"`; erros usam `role="alert"` |
| gráficos | descrição acessível e dados equivalentes em tabelas expansíveis |
| tabelas | cabeçalhos identificados com `scope="col"` |
| movimento | interface não depende de animação para transmitir informação |
| responsividade | layout parte de largura mínima de 320 pixels |
| linguagem | previsão e anomalia recebem contexto e aviso compreensíveis |

## Fluxo por teclado a verificar

1. pressione `Tab` ao abrir a página;
2. confirme que o atalho para o conteúdo aparece;
3. percorra filtros, botões, estimativa e tabelas;
4. confirme que o foco sempre está visível;
5. aplique um período inválido e confirme o anúncio do erro;
6. abra os elementos `details` para consultar os dados dos gráficos.

## Contraste

As combinações principais usam texto escuro sobre fundo claro ou texto claro
sobre fundo escuro. Cores de destaque não são a única forma de identificar
média, mínimo, máximo, estado ou erro; rótulos textuais permanecem presentes.

Uma ferramenta automática pode encontrar violações comuns, mas a validação de
contraste deve considerar o par real de cores, tamanho e peso do texto.

Em 28/07/2026, o Lighthouse `13.4.1` foi executado com Chrome headless sobre a
composição de produção local. A primeira auditoria obteve 96/100 e identificou
contraste insuficiente em textos secundários e divergência no nome acessível da
marca. Depois do ajuste das cores e da semântica do link, a repetição obteve
**100/100 na categoria de acessibilidade**, sem auditorias automáticas
reprovadas. Esse resultado não é uma declaração formal de conformidade.

## Limitações da revisão

- não houve teste com leitor de tela real;
- não houve teste com pessoas com deficiência;
- gráficos de terceiros podem produzir uma árvore de acessibilidade complexa;
- não foi emitida declaração formal de conformidade WCAG;
- zoom elevado, alto contraste do sistema e diferentes navegadores precisam de
  validação manual mais ampla;
- critérios cognitivos e clareza de conteúdo exigem avaliação humana contínua.

## Próximas verificações recomendadas

- testar VoiceOver no macOS e NVDA no Windows;
- repetir Lighthouse e executar axe na página publicada;
- validar contraste com ferramenta dedicada;
- navegar a 200% e 400% de zoom;
- testar somente com teclado em Chrome, Firefox e Safari;
- incluir pessoas reais em testes de usabilidade.

## Referência

- [Web Content Accessibility Guidelines 2.2](https://www.w3.org/TR/WCAG22/)
