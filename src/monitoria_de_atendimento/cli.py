from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .benchmark import rodar
from .checklist import monitorar, relatorio
from .sintetico import gerar_lote


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="monitoria-de-atendimento")
    sub = p.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("avaliar", help="avalia uma transcrição em texto (linhas 'Atendente:' e 'Cliente:')")
    a.add_argument("arquivo")

    g = sub.add_parser("gerar", help="gera ligações sintéticas com o rótulo esperado")
    g.add_argument("--n", type=int, default=3)
    g.add_argument("--semente", type=int, default=42)

    b = sub.add_parser("benchmark", help="mede a checklist contra o rótulo das ligações sintéticas")
    b.add_argument("--n", type=int, default=500)
    b.add_argument("--semente", type=int, default=42)
    b.add_argument("--saida")

    d = sub.add_parser("demo", help="gera a página HTML de demo (ligações sintéticas e o relatório de monitoria)")
    d.add_argument("--saida", default="site/index.html")
    d.add_argument("--quantas", type=int, default=3)

    args = p.parse_args(argv)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")  # consoles Windows em cp1252 quebram com "→" e aspas
    if args.cmd == "avaliar":
        print(relatorio(monitorar(Path(args.arquivo).read_text(encoding="utf-8"))))
    elif args.cmd == "gerar":
        for k, lig in enumerate(gerar_lote(args.n, args.semente), 1):
            falhas = [i for i, ok in lig.rotulo.items() if not ok]
            print(f"--- ligação {k} (falhas esperadas: {', '.join(falhas) or 'nenhuma'}) ---\n{lig.texto()}\n")
    elif args.cmd == "benchmark":
        texto = rodar(args.n, args.semente)
        print(texto)
        if args.saida:
            Path(args.saida).write_text(texto + "\n", encoding="utf-8")
    elif args.cmd == "demo":
        from .demo import gerar_html
        saida = Path(args.saida)
        saida.parent.mkdir(parents=True, exist_ok=True)
        saida.write_text(gerar_html(args.quantas), encoding="utf-8")
        print(f"página gravada em {saida}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
