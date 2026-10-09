from __future__ import annotations

from .checklist import ITENS, monitorar
from .sintetico import gerar_lote

# Casos escritos à mão: (transcrição, item, esperado ok?)
CURADOS = (
    ("Atendente: Bom dia, meu nome é Ana.", "saudacao", True),
    ("Atendente: Fala, o que houve?", "saudacao", False),
    ("Atendente: Qual é a sua senha?", "identidade", False),
    ("Atendente: Nunca peço sua senha. Pode confirmar seu nome completo?", "identidade", True),
    ("Atendente: Aproveite o limite pré-aprovado!", "oferta", False),
    ("Cliente: Queria um empréstimo.\nAtendente: Posso simular o empréstimo para o senhor.", "oferta", True),
    ("Atendente: Seu saldo é R$ 50.\nCliente: Ok.\nAtendente: Agora preciso validar sua identidade.", "lgpd", False),
    ("Atendente: Vou validar sua identidade. Pode dizer o nome completo?\nCliente: João.\nAtendente: Seu saldo é R$ 50.", "lgpd", True),
    ("Atendente: Anotei o protocolo 123. Posso ajudar em mais alguma coisa?", "resolucao", True),
    ("Atendente: Vou ver o que dá.", "resolucao", False),
)


def acerto_curados() -> tuple[int, int, list[str]]:
    certos, falhas = 0, []
    for texto, item, esperado in CURADOS:
        obtido = monitorar(texto).ok(item)
        if obtido == esperado:
            certos += 1
        else:
            falhas.append(f"{item}: esperado {'ok' if esperado else 'falha'} → \"{texto[:60]}\"")
    return certos, len(CURADOS), falhas


def rodar(n: int = 500, semente: int = 42) -> str:
    lote = gerar_lote(n, semente)
    certos = {i: 0 for i in ITENS}
    base = {i: 0 for i in ITENS}
    notas_boas, notas_ruins = [], []
    erros: list[str] = []
    for lig in lote:
        m = monitorar(lig.falas)
        for i in ITENS:
            certos[i] += m.ok(i) == lig.rotulo[i]
            base[i] += lig.rotulo[i]  # baseline: sempre "ok"
            if m.ok(i) != lig.rotulo[i] and len(erros) < 5:
                erros.append(f"{i}: rótulo {'ok' if lig.rotulo[i] else 'falha'}, regra {'ok' if m.ok(i) else 'falha'}")
        (notas_boas if all(lig.rotulo.values()) else notas_ruins).append(m.nota)
    media = sum(certos.values()) / (n * len(ITENS))
    media_base = sum(base.values()) / (n * len(ITENS))
    c, t, falhas = acerto_curados()
    out = [f"## Checklist vs. rótulo (ligações sintéticas, n={n}, semente {semente})\n",
           "| Item | Acerto | Baseline (sempre ok) |", "|---|---|---|"]
    out += [f"| {i} | {certos[i] / n:.1%} | {base[i] / n:.1%} |" for i in ITENS]
    out += [f"| **média** | **{media:.1%}** | {media_base:.1%} |", ""]
    out += ["## Nota média (0-100)\n",
            f"- ligações sem nenhuma falha rotulada (n={len(notas_boas)}): {sum(notas_boas) / max(1, len(notas_boas)):.1f}",
            f"- ligações com pelo menos uma falha rotulada (n={len(notas_ruins)}): {sum(notas_ruins) / max(1, len(notas_ruins)):.1f}",
            "", f"## Casos escritos à mão: {c}/{t}\n"]
    out += [f"- {f}" for f in falhas] or ["- sem falhas"]
    out += ["", "## Primeiros desacordos com o rótulo\n"] + ([f"- {e}" for e in erros] or ["- nenhum"])
    out.append("\nAs ligações e a checklist têm o mesmo autor: o número mede a mecânica das regras, "
               "não o desempenho em ligações reais.")
    return "\n".join(out)
