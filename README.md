# Registro de Decisão

Formato aberto para registrar decisão automatizada: **o que entrou, o que saiu, e a explicação amarrada ao que foi realmente usado.**

A ideia inteira cabe numa regra: *a explicação só pode citar o que está no registro.* Um texto convincente que não corresponde ao que o modelo fez é pior que nenhuma explicação — cria passivo em vez de reduzir. Esta especificação existe para tornar esse erro **impossível por construção**, não improvável por disciplina.

## Em dois minutos

```bash
git clone https://github.com/acoplum/spec-registro-decisao
cd spec-registro-decisao
python3 validar.py exemplos/*.json
```

Sem instalar nada: o validador é biblioteca padrão do Python 3.10+.

Você vai ver sete registros serem **rejeitados**, um por invariante, e um ser aceito. Os rejeitados existem de propósito — provam que a regra pega o caso, em vez de a documentação afirmar que pegaria.

O comando **sai com código 1**, e está certo: um validador que rejeitou algo não pode dizer que deu tudo bem. Para ver o código 0, rode só o exemplo válido — `python3 validar.py exemplos/valido.json`.

```
REJEITADO i5-cpf-em-claro.json
          I5: subject.ref parece conter CPF em claro
REJEITADO i7-cadeia-rompida.json
          I7: hash não corresponde ao conteúdo
aceito    valido.json
```

## As sete invariantes

O validador rejeita o registro que violar qualquer uma. Elas estão descritas com o racional completo em [`ESPECIFICACAO.md`](ESPECIFICACAO.md).

A que mais importa é a **I3**: se `attribution_method` é `none`, o campo `contribution` é proibido em qualquer feature, e a explicação não pode afirmar peso. É a regra que impede o produto de inventar "o que mais pesou" quando o modelo não expõe atribuição.

## O que há aqui

| Arquivo | O que é |
|---|---|
| [`ESPECIFICACAO.md`](ESPECIFICACAO.md) | o contrato: campos, invariantes, base legal por campo, e o que ficou fora da 0.1 |
| `registro-decisao.schema.json` | JSON Schema 2020-12 |
| `validar.py` | validador de referência, stdlib, com as sete invariantes |
| `exemplos/` | um exemplo por invariante provando que rejeita, mais um válido |
| `vocabulario.json` | termos controlados |
| `registro-versoes.json` | resolução de versão de modelo e de política |

## Por que isto existe

O art. 20 da LGPD garante ao titular revisão por pessoa natural, hoje. O PL 2338/2023 acrescenta direito à explicação e à contestação. Quem decide crédito, preço, triagem ou risco por algoritmo vai precisar mostrar como — e a maior parte dos sistemas não guarda o registro para isso.

Este formato é o substrato compartilhado de três ferramentas de governança em construção. Publicado separado porque **formato só serve se for implementável por quem não escreveu o produto**.

## Estágio

**Versão 0.1, de trabalho.** Nenhuma implementação em produção ainda, e o formato pode mudar em pontos que o uso real revelar. Mudança quebra-compatibilidade sobe a versão e entra no histórico da especificação.

Limite declarado: o escopo é **registrar e explicar**, não auditar modelo. Nada aqui avalia se o modelo é justo ou tem viés.

## Contribuir

Pull request é bem-vindo. Antes de integrar, é preciso aceitar o [CLA](CLA.md) — comentando `Li e aceito o CLA da Acoplum` no pull request. A verificação é automática e o aceite fica registrado em `.github/cla/assinaturas.json`.

O CLA existe por um motivo prático, não burocrático: sem ele este código não pode ser sublicenciado depois, e corrigir isso exigiria localizar cada pessoa que contribuiu.

## Licença

[Apache-2.0](LICENSE). Escolhida de propósito para especificação e SDK: entra na sua aplicação sem contaminar o seu código.
