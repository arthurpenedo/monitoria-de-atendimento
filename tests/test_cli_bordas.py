from monitoria_de_atendimento.cli import main


def test_avaliar_arquivo_inexistente_devolve_2(tmp_path, capsys):
    assert main(["avaliar", str(tmp_path / "nao.txt")]) == 2
    assert "não encontrado" in capsys.readouterr().err


def test_avaliar_aceita_transcricao_com_bom(tmp_path, capsys):
    arq = tmp_path / "t.txt"
    arq.write_bytes("﻿Atendente: bom dia\nCliente: oi\n".encode())
    assert main(["avaliar", str(arq)]) == 0
    assert capsys.readouterr().out.strip()


def test_avaliar_arquivo_fora_de_utf8_ou_sem_falantes_devolve_2(tmp_path, capsys):
    latin = tmp_path / "latin.txt"
    latin.write_bytes("Atendente: olá, não\n".encode("latin-1"))
    sem_falante = tmp_path / "sem.txt"
    sem_falante.write_text("bom dia\n", encoding="utf-8")
    assert main(["avaliar", str(latin)]) == 2
    assert main(["avaliar", str(sem_falante)]) == 2
    assert "Não consegui avaliar" in capsys.readouterr().err


def test_saida_apontando_para_pasta_devolve_2(tmp_path, capsys):
    assert main(["benchmark", "--n", "1", "--saida", str(tmp_path)]) == 2
    assert main(["demo", "--saida", str(tmp_path)]) == 2
    assert "pasta" in capsys.readouterr().err


def test_benchmark_n_zero_devolve_2(capsys):
    assert main(["benchmark", "--n", "0"]) == 2
    assert "1 ou mais" in capsys.readouterr().err


def test_benchmark_saida_cria_a_pasta(tmp_path):
    saida = tmp_path / "novo" / "bench.txt"
    assert main(["benchmark", "--n", "5", "--saida", str(saida)]) == 0
    assert saida.read_text(encoding="utf-8").strip()


def test_gerar_n_zero_devolve_2(capsys):
    assert main(["gerar", "--n", "0"]) == 2
    assert "1 ou mais" in capsys.readouterr().err


def test_demo_quantas_zero_nao_grava_pagina(tmp_path, capsys):
    saida = tmp_path / "p.html"
    assert main(["demo", "--quantas", "0", "--saida", str(saida)]) == 2
    assert not saida.exists()
