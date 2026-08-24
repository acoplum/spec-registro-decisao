#!/usr/bin/env python3
"""Validador de referência do Registro de Decisão 0.1.

Implementa as sete invariantes da especificação. Estrutura é conferida pelo
JSON Schema (registro-decisao.schema.json); as invariantes exigem lógica que
o Schema não expressa — referência cruzada, vocabulário externo e hash.

Uso:
    validar.py <registro.json> [...]        valida
    validar.py --assinar <registro.json>    calcula integrity.hash e grava
"""

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

BASE = Path(__file__).parent
VOCABULARIO = BASE / "vocabulario.json"
REGISTRO_VERSOES = BASE / "registro-versoes.json"

# I5 — padrões de dado pessoal bruto que jamais devem aparecer em subject.ref
PII = [
    (re.compile(r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b"), "CPF"),
    (re.compile(r"\b\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}\b"), "CNPJ"),
    (re.compile(r"[^@\s]+@[^@\s]+\.[a-z]{2,}"), "e-mail"),
    (re.compile(r"\+?\d{2}\s?\(?\d{2}\)?\s?9?\d{4}-?\d{4}\b"), "telefone"),
]


def hash_canonico(registro):
    """sha256 do registro sem integrity.hash, chaves ordenadas, UTF-8 compacto.

    Determinístico e reprodutível por qualquer implementação — é o que permite
    a um auditor recalcular o hash anos depois.
    """
    copia = json.loads(json.dumps(registro))
    copia.get("integrity", {}).pop("hash", None)
    serial = json.dumps(copia, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return "sha256:" + hashlib.sha256(serial.encode("utf-8")).hexdigest()


def _carrega(caminho, chave_tenant):
    if not caminho.exists():
        return None
    dados = json.loads(caminho.read_text(encoding="utf-8"))
    return dados.get(chave_tenant, dados.get("_default"))


def valida(registro, prev_hash_esperado=None):
    """Retorna lista de violações. Lista vazia significa registro aceito."""
    erros = []
    tenant = registro.get("tenant_id", "")
    inputs = registro.get("inputs", {})
    features = inputs.get("features", [])
    ids = {f.get("id") for f in features}
    metodo = inputs.get("attribution_method")

    # I1 — a explicação não pode citar o que não está no registro
    for ref in registro.get("explanation", {}).get("derived_from", []):
        if ref not in ids:
            erros.append(f"I1: explanation.derived_from cita '{ref}', ausente de inputs.features")

    # I2 — atribuição declarada e coerente
    com_peso = [f["id"] for f in features if "contribution" in f]
    if metodo == "none":
        if com_peso:
            erros.append(
                "I2: attribution_method='none' proíbe contribution; presente em "
                + ", ".join(com_peso)
            )
    elif metodo in ("exact", "approximate"):
        sem_peso = [f.get("id") for f in features if "contribution" not in f]
        if sem_peso:
            erros.append(
                f"I2: attribution_method='{metodo}' exige contribution; ausente em "
                + ", ".join(str(i) for i in sem_peso)
            )
        if metodo == "approximate" and not inputs.get("attribution_note"):
            erros.append("I2: attribution_method='approximate' exige attribution_note nomeando o método")
    else:
        erros.append(f"I2: attribution_method inválido ou ausente: {metodo!r}")

    # I3 — códigos de razão vêm de vocabulário registrado
    vocab = _carrega(VOCABULARIO, tenant)
    if vocab is None:
        erros.append(f"I3: sem vocabulário registrado para o tenant '{tenant}'")
    else:
        for codigo in registro.get("reason_codes", []):
            if codigo not in vocab:
                erros.append(f"I3: reason_code '{codigo}' fora do vocabulário do tenant")

    # I4 — o resultado está no espaço de resultados
    decisao = registro.get("decision", {})
    if decisao.get("outcome") not in decisao.get("outcome_space", []):
        erros.append(
            f"I4: outcome '{decisao.get('outcome')}' não consta de outcome_space"
        )

    # I5 — nada de dado pessoal bruto
    ref = registro.get("subject", {}).get("ref", "")
    for padrao, nome in PII:
        if padrao.search(ref):
            erros.append(f"I5: subject.ref parece conter {nome} em claro")

    # I6 — versão de modelo e de política resolvíveis
    registro_versoes = _carrega(REGISTRO_VERSOES, tenant)
    if registro_versoes is None:
        erros.append(f"I6: sem registro de versões para o tenant '{tenant}'")
    else:
        sistema = registro.get("system", {})
        modelo = sistema.get("model", {})
        chave = f"{modelo.get('name')}@{modelo.get('version')}"
        if chave not in registro_versoes.get("models", []):
            erros.append(f"I6: modelo '{chave}' não resolve no registro de versões")
        if sistema.get("policy_version") not in registro_versoes.get("policies", []):
            erros.append(
                f"I6: policy_version '{sistema.get('policy_version')}' não resolve no registro"
            )

    # I7 — cadeia íntegra
    integridade = registro.get("integrity", {})
    calculado = hash_canonico(registro)
    if integridade.get("hash") != calculado:
        erros.append(f"I7: hash não corresponde ao conteúdo (esperado {calculado})")
    if prev_hash_esperado is not None and integridade.get("prev_hash") != prev_hash_esperado:
        erros.append("I7: prev_hash não encadeia com o registro anterior")

    return erros


def main():
    ap = argparse.ArgumentParser(description="Valida registros de decisão 0.1")
    ap.add_argument("arquivos", nargs="+", type=Path)
    ap.add_argument("--assinar", action="store_true", help="calcula integrity.hash e grava no arquivo")
    args = ap.parse_args()

    falhou = False
    for caminho in args.arquivos:
        registro = json.loads(caminho.read_text(encoding="utf-8"))

        if args.assinar:
            registro.setdefault("integrity", {})["hash"] = hash_canonico(registro)
            caminho.write_text(
                json.dumps(registro, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
            )
            print(f"assinado  {caminho.name}  {registro['integrity']['hash'][:23]}...")
            continue

        erros = valida(registro)
        if erros:
            falhou = True
            print(f"REJEITADO {caminho.name}")
            for e in erros:
                print(f"          {e}")
        else:
            print(f"aceito    {caminho.name}")

    return 1 if falhou else 0


if __name__ == "__main__":
    sys.exit(main())
