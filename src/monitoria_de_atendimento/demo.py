"""Página de demo estática: ligações sintéticas ao lado do relatório de monitoria (nota e trechos que justificam)."""
from __future__ import annotations

from html import escape

from .checklist import ITENS, PESOS, monitorar
from .sintetico import Ligacao, gerar_lote

CSS = (
    "body{font-family:system-ui,sans-serif;max-width:1000px;margin:2rem auto;padding:0 1rem}"
    ".lig{display:grid;grid-template-columns:1fr 1fr;gap:1rem;border:1px solid #ddd;border-radius:6px;"
    "padding:.8rem;margin-bottom:1rem}pre{background:#f6f6f6;padding:.6rem;white-space:pre-wrap;margin:0;font-size:.8rem}"
    "table{border-collapse:collapse;width:100%;font-size:.85rem}td,th{border-bottom:1px solid #eee;padding:.25rem;text-align:left}"
    ".ok{color:#0a6b2d}.falha{color:#b00020;font-weight:600}h3{margin:.2rem 0 .6rem}"
)


def _escolher(lote: list[Ligacao], quantas: int) -> list[Ligacao]:
    """Uma ligação sem falha e as primeiras com mais falhas rotuladas, para a página mostrar contraste."""
    perfeitas = [lig for lig in lote if all(lig.rotulo.values())]
    ruins = sorted((lig for lig in lote if not all(lig.rotulo.values())),
                   key=lambda lig: -sum(not ok for ok in lig.rotulo.values()))
    return (perfeitas[:1] + ruins)[:quantas]


def _bloco(lig: Ligacao) -> str:
    m = monitorar(lig.falas)
    linhas = "".join(
        "<tr><td>{}</td><td class='{}'>{}/{}</td><td>{}</td></tr>".format(
            item, "ok" if m.ok(item) else "falha", m.itens[item].pontos, PESOS[item],
            escape("; ".join(m.itens[item].evidencias) or "-"))
        for item in ITENS
    )
    feedback = "".join(f"<li>{escape(f)}</li>" for f in m.feedback())
    return (
        f"<div class='lig'><div><h3>Ligação sintética</h3><pre>{escape(lig.texto())}</pre></div>"
        f"<div><h3>Nota {m.nota}/100</h3><table><tr><th>Item</th><th>Pontos</th><th>Evidência</th></tr>"
        f"{linhas}</table>{'<p>Feedback:</p><ul>' + feedback + '</ul>' if feedback else ''}</div></div>"
    )


def gerar_html(quantas: int = 3, n: int = 500, semente: int = 42) -> str:
    """Mostra `quantas` ligações do lote de `n` e o acerto médio da checklist contra o rótulo."""
    lote = gerar_lote(n, semente)
    acertos = sum(monitorar(lig.falas).ok(i) == lig.rotulo[i] for lig in lote for i in ITENS)
    media = acertos / (n * len(ITENS))
    blocos = "".join(_bloco(lig) for lig in _escolher(lote, quantas))
    return (
        "<!doctype html><html lang='pt-BR'><head><meta charset='utf-8'>"
        f"<title>monitoria-de-atendimento: demo</title><style>{CSS}</style></head><body>"
        "<h1>monitoria-de-atendimento: demo</h1>"
        "<p>Ligações <b>sintéticas</b> (nenhum dado real) e o relatório da checklist: saudação, identidade sem senha, "
        "resolução, oferta indevida e dado pessoal (LGPD), com o trecho que justifica cada ponto. "
        f"Acerto médio contra o rótulo em {n} ligações (semente {semente}): {media:.1%}. "
        "<a href='https://github.com/arthurpenedo/monitoria-de-atendimento'>Código no GitHub</a>.</p>"
        f"{blocos}"
        "<p><small>As ligações e as regras têm o mesmo autor: o número mede a mecânica da checklist, "
        "não o desempenho em ligações reais.</small></p></body></html>"
    )
