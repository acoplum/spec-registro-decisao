# Especificação — Registro de Decisão

Fecha o passo 7 do `ROADMAP.md` (HQ: `ROADMAP.md`) e a pendência P5. Versão de trabalho **0.1**.

Este é o contrato técnico que separa produto honesto de gerador de prosa convincente. O risco registrado em `projetos/2-glassbox.md` do HQ é literal: *"um texto convincente que não corresponde ao que o modelo fez é pior que nenhuma explicação — cria passivo em vez de reduzir"*. A especificação existe para tornar esse erro **impossível por construção**, não improvável por disciplina.

## É o substrato dos três produtos

O registro de decisão é o evento compartilhado que justifica AgentLedger, GlassBox e TokenMeter serem um repositório com três módulos, e não três empresas:

| Módulo | O que acrescenta ao registro | O que lê dele |
|---|---|---|
| **GlassBox** | `explanation`, `human_review`, `appeal` | explica ao titular da decisão |
| **AgentLedger** | `agent` — identidade, autoridade, limite | prova de controle para auditor |
| **TokenMeter** | `cost` | custo por tarefa, agente e resultado |

Um evento, três leituras. É por isso que a licença da especificação é a mais permissiva do portfólio (Apache-2.0, ou CC0 se o objetivo for virar padrão de fato): quanto mais gente escrever nesse formato, mais valem os três módulos.

## Registro completo

```json
{
  "spec_version": "0.1",
  "decision_id": "01K3XQZJ8YB4N7V2M9RTFA6PCE",
  "occurred_at": "2026-08-23T14:02:11.482Z",
  "tenant_id": "banco-exemplo",

  "subject": {
    "ref": "sha256:9f2b7c1e4a08d5f3b6c9e2a7d4f1b8c5e3a6d9f2b7c1e4a08d5f3b6c9e2a7d4f1",
    "ref_scheme": "sha256(cpf + tenant_salt)"
  },

  "decision": {
    "domain": "credito.limite",
    "outcome": "recusado",
    "outcome_space": ["aprovado", "aprovado_com_limite", "recusado"],
    "automated": true
  },

  "system": {
    "model": { "name": "risco-pf", "version": "4.2.0" },
    "policy_version": "2026.08.1",
    "code_version": "glassbox-server 0.1.0"
  },

  "inputs": {
    "attribution_method": "exact",
    "attribution_note": "coeficientes do modelo linear",
    "features": [
      { "id": "f1", "name": "renda_declarada_faixa", "value": "3-5sm", "contribution": -0.31 },
      { "id": "f2", "name": "tempo_relacionamento_meses", "value": 4, "contribution": -0.22 },
      { "id": "f3", "name": "restricao_externa", "value": true, "contribution": -0.47 }
    ]
  },

  "reason_codes": ["RESTRICAO_EXTERNA_ATIVA", "RELACIONAMENTO_RECENTE"],

  "explanation": {
    "language": "pt-BR",
    "text": "O pedido foi recusado porque existe restrição ativa em consulta externa e porque o relacionamento tem 4 meses.",
    "derived_from": ["f3", "f2"]
  },

  "human_review": {
    "required": true,
    "state": "pendente",
    "reviewer_ref": null,
    "overrode_outcome": null
  },

  "appeal": {
    "available": true,
    "channel": "https://banco-exemplo.com.br/contestar/01K3XQZJ8YB4N7V2M9RTFA6PCE",
    "state": "nao_solicitada"
  },

  "cost": { "tokens_input": 0, "tokens_output": 0, "currency": "BRL", "amount": 0 },
  "agent": null,

  "integrity": {
    "prev_hash": "sha256:0000000000000000000000000000000000000000000000000000000000000000",
    "hash": "sha256:4c8e1f6a2b9d3e7c5a0f8b4d1e6c9a3f7b2d5e8c1a4f7b0d3e6c9a2f5b8d1e4c"
  }
}
```

## As sete invariantes

O que transforma isto de formato em contrato. O validador **rejeita** o registro que violar qualquer uma — não avisa, rejeita.

**I1 · A explicação não pode citar o que não está no registro.**
Todo id em `explanation.derived_from` precisa existir em `inputs.features[].id`. É a invariante central: impede que a explicação invente variável que o modelo não usou.

**I2 · Atribuição declarada, e coerente.**
`attribution_method` é obrigatório e assume um de três valores:

| Valor | Significa | `contribution` |
|---|---|---|
| `exact` | o modelo expõe peso por variável (coeficiente linear, árvore) | obrigatório |
| `approximate` | peso estimado por método externo (SHAP, LIME) | obrigatório, com `attribution_note` nomeando o método |
| `none` | o modelo não expõe atribuição | **proibido** |

Com `none`, o registro só pode afirmar **quais dados entraram**, nunca quanto cada um pesou — e o widget renderiza um texto diferente. É a degradação honesta, e é o coração do produto: quase todo concorrente fabrica atribuição confiante para modelo que não a suporta.

**I3 · Códigos de razão vêm de vocabulário registrado.**
`reason_codes` só aceita códigos do vocabulário do tenant. Texto livre em campo de razão vira deriva: dois analistas escrevem a mesma razão de três formas, e a auditoria perde comparabilidade.

**I4 · O resultado está no espaço de resultados.**
`outcome` precisa constar de `outcome_space`. Sem isso o titular não sabe o que era possível, e "recusado" não informa nada.

**I5 · Nada de PII bruto.**
`subject.ref` é rejeitado se casar com padrão de CPF, CNPJ, e-mail ou telefone. Guarda-se referência pseudonimizada e o esquema usado, nunca o dado. Vale a lição do AgeProof: não persistir o que não é necessário é arquitetura, não zelo.

**I6 · Versão resolvível.**
`system.model.version` e `system.policy_version` precisam resolver num registro no momento da escrita. O auditor vai reconstruir uma decisão de dois anos atrás; se a versão do modelo não é resolvível, o registro é papel.

**I7 · Cadeia íntegra.**
`integrity.prev_hash` encadeia com o registro anterior do mesmo tenant, e `hash` cobre o registro inteiro. Append-only: adulteração é detectável, não impedida.

## Como o widget muda com a atribuição

O mesmo caso, com métodos diferentes de atribuição:

**`exact` ou `approximate`**

> Seu pedido foi recusado. O que mais pesou: restrição ativa em consulta externa, e relacionamento de 4 meses. Você pode pedir revisão por uma pessoa.

**`none`**

> Seu pedido foi recusado. Os dados usados nesta análise foram: consulta de restrição externa, tempo de relacionamento e faixa de renda declarada. Não podemos informar o peso de cada um. Você pode pedir revisão por uma pessoa.

A segunda versão é pior de ler e melhor de defender. Vender a primeira quando o modelo só sustenta a segunda é exatamente o passivo que a especificação existe para impedir.

## Base legal dos campos

Não são campos de conveniência:

| Campo | Origem |
|---|---|
| `explanation` | PL 2338/2023 — direito à explicação |
| `human_review` | **art. 20 da LGPD** — direito à revisão por pessoa natural, já em vigor |
| `appeal` | PL 2338/2023 — direito à contestação |
| `integrity` | evidência de auditoria; o que Groovia atende no caso citado na run `token-strategy` |
| `agent` | Res. CNJ 615/2025 e o padrão ACAP — identidade e autoridade do agente |

O `human_review` é o mais mal implementado do mercado e o único cuja obrigação já existe hoje, não em 2026.

## Fora do escopo da 0.1

Deliberadamente ausentes, para a versão 0.1 ficar implementável:

- **Auditoria do modelo.** A especificação registra o que o modelo usou e devolveu. Não avalia se o modelo é justo, nem se tem viés. Dizer isso em voz alta é requisito de tom de voz.
- **Explicação contrafactual** ("o que eu precisaria mudar para ser aprovado"). É o que o titular mais quer e o que dá mais trabalho para fazer certo. Fica para depois, e não deve ser prometido antes.
- **Assinatura criptográfica por terceiro.** O encadeamento de hash detecta adulteração interna; carimbo de tempo confiável entra quando um cliente exigir.
- **Decisão distribuída** entre múltiplos agentes com handoff. É o gap de governança agente-agente que as runs apontaram como aberto; exige modelar cadeia, não evento.

## Implementação de referência — ✅ feita em 2026-08-23

JSON Schema, validador e exemplos em este repositório. As sete invariantes estão implementadas e cada uma tem um exemplo que a viola, provando que rejeita.

I2 é barrada em duas camadas — o Schema também a expressa, via `if`/`then` — porque é a invariante que sustenta a honestidade do produto.

Em incubação no HQ; ganha repo próprio quando alguém de fora precisar implementar o formato.

O gate do passo 8 do roadmap (publicar o GlassBox) inclui: um dev de fora instala, aponta para uma decisão e vê a explicação em menos de dez minutos, seguindo só o README.
