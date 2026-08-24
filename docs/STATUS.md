# Status — Registro de Decisão

**Atualizado:** 2026-08-24 · **Estágio:** especificação 0.1 publicada, sem implementação em produção

## O que é

Formato aberto para registrar decisão automatizada, com a explicação amarrada ao que foi realmente usado. Substrato compartilhado de três ferramentas de governança em construção.

**Primeiro repositório público da Acoplum.**

## O que já funciona

- Especificação 0.1 completa: campos, sete invariantes, base legal por campo, escopo excluído
- JSON Schema 2020-12
- Validador de referência em stdlib, sem dependência
- Um exemplo por invariante provando que a regra rejeita, mais um válido
- Verificação de CLA automática nos pull requests

## O que não funciona ainda

- **Nenhuma implementação em produção.** O formato nunca foi exercitado por um sistema real, e é isso que revela o que falta.
- Sem SDK. Quem quiser usar escreve o registro à mão ou gera do schema.
- Sem versão em inglês, o que limita contribuição de fora do Brasil.

## Como rodar agora

```bash
python3 validar.py exemplos/*.json
```

Python 3.10 ou mais novo. Nada a instalar.

## Onde está publicado

`github.com/acoplum/spec-registro-decisao`
