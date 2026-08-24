# Validador

**Estágio:** funcionando

## Objetivo

Tornar impossível por construção o erro que a especificação existe para evitar: **explicação que afirma o que o registro não sustenta.** Sem validador, a regra é disciplina; com ele, é rejeição.

## Detalhes

Biblioteca padrão do Python 3.10+, sem dependência — instalar coisa é atrito para quem só quer conferir se o formato serve.

Duas camadas, e a ordem importa: primeiro o JSON Schema 2020-12 valida a forma, depois as sete invariantes validam o **sentido**. Schema pega campo faltando; invariante pega registro bem formado que mente.

A mais importante é a **I3**: com `attribution_method: none`, o campo `contribution` é proibido e a explicação não pode afirmar peso. É a regra que impede inventar "o que mais pesou" quando o modelo não expõe atribuição.

Cada invariante tem um exemplo em `exemplos/` que a viola. Não é ilustração — é o teste: se o validador parar de rejeitar, o exemplo denuncia.

## Métricas

- **7 de 7 invariantes com exemplo que prova a rejeição.** Invariante sem exemplo é afirmação sobre o código, não verificação dele.
- Tempo de execução sobre os 8 exemplos: instantâneo, sem I/O de rede
- Dependências externas: **zero** — é métrica, não detalhe: cada dependência é atrito e superfície de supply chain
- **Não medido:** taxa de falso negativo contra registro de sistema real. Só uso em produção responde, e não há uso em produção.
