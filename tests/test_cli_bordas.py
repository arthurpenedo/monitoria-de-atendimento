from monitoria_de_atendimento.cli import main


def test_avaliar_arquivo_inexistente_devolve_2(tmp_path, capsys):
    assert main(["avaliar", str(tmp_path / "nao.txt")]) == 2
    assert "não encontrado" in capsys.readouterr().err


def test_benchmark_n_zero_devolve_2(capsys):
    assert main(["benchmark", "--n", "0"]) == 2
    assert "1 ou mais" in capsys.readouterr().err


def test_benchmark_saida_cria_a_pasta(tmp_path):
    saida = tmp_path / "novo" / "bench.txt"
    assert main(["benchmark", "--n", "5", "--saida", str(saida)]) == 0
    assert saida.read_text(encoding="utf-8").strip()
