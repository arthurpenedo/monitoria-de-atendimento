from monitoria_de_atendimento.cli import main
from monitoria_de_atendimento.demo import gerar_html


def test_demo_html_mostra_ligacoes_e_nota():
    html = gerar_html(quantas=3, n=100)
    assert html.count("class='lig'") == 3
    assert "/100" in html and "sintéticas" in html


def test_cli_demo_grava_arquivo(tmp_path):
    saida = tmp_path / "site" / "index.html"
    assert main(["demo", "--saida", str(saida)]) == 0
    assert "monitoria-de-atendimento: demo" in saida.read_text(encoding="utf-8")
