# Verificação de CLA

**Estágio:** funcionando

## Objetivo

Impedir que contribuição externa seja integrada sem aceite registrado. Não é burocracia: **pull request aceito sem CLA torna aquele código impossível de sublicenciar**, e corrigir depois exige localizar a pessoa e obter consentimento.

O `AGENTS.md` do HQ lista publicar repo sem CLA ativo entre os *nunca*. Esta feature é o que destrava qualquer repositório público.

## Detalhes

Fluxo do GitHub Actions próprio, **sem ação de terceiro** — dependência de CI que pode mudar de comportamento ou de dono é risco desproporcional ao que ela economiza aqui.

1. Pull request aberto dispara a conferência do autor contra `.github/cla/assinaturas.json`.
2. Se não assinou, o fluxo comenta com a instrução e **falha a verificação**.
3. A pessoa comenta `Li e aceito o CLA da Acoplum` na própria thread.
4. O fluxo registra o aceite no arquivo, com data e o link do comentário que serviu de prova, e commita.

Usa `pull_request_target` porque o fluxo precisa de permissão de escrita para registrar — e por isso **nunca executa código do pull request**, só lê o login.

## Métricas

- **Falso negativo — contribuição integrada sem aceite: meta zero.** É a única métrica que importa; qualquer ocorrência é incidente, não estatística.
- Aceites registrados: 1 (o titular)
- Falso positivo (bloqueio de quem já assinou): 0
- **Não medido:** tempo entre o bloqueio e o aceite. Só há dado quando houver contribuição externa de verdade.
