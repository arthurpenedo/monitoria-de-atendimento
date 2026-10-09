import re

import pytest

from monitoria_de_atendimento.benchmark import acerto_curados, rodar
from monitoria_de_atendimento.checklist import PESOS, ler_transcricao, monitorar, relatorio
from monitoria_de_atendimento.cli import main
from monitoria_de_atendimento.sintetico import gerar_lote

BOA = """Atendente: Bom dia, meu nome é Ana, da central. Em que posso ajudar?
Cliente: Meu cartão foi cobrado duas vezes.
Atendente: Para sua segurança, preciso confirmar seus dados: nome completo e data de nascimento?
Cliente: Paulo Souza, 14/03/1985.
Atendente: Já resolvi: fiz o estorno e o valor volta em até 2 dias. Protocolo 123456. Posso ajudar em mais alguma coisa?
"""


def test_pesos_somam_100():
    assert sum(PESOS.values()) == 100


def test_ligacao_boa_tira_100():
    m = monitorar(BOA)
    assert m.nota == 100 and m.feedback() == []


def test_leitura_junta_linhas_de_continuacao():
    falas = ler_transcricao("Atendente: Olá\ncontinua aqui\nCliente: oi")
    assert falas[0].texto == "Olá continua aqui" and falas[1].autor == "cliente"


def test_transcricao_sem_prefixo_da_erro():
    with pytest.raises(ValueError):
        ler_transcricao("texto solto")


def test_pedir_senha_zera_identidade_e_cita_trecho():
    m = monitorar("Atendente: Bom dia, sou a Ana. Qual é a sua senha?")
    assert m.itens["identidade"].pontos == 0
    assert "senha" in m.itens["identidade"].evidencias[0]


def test_negacao_de_senha_nao_penaliza():
    m = monitorar("Atendente: Nunca peço sua senha. Pode confirmar seu nome completo?")
    assert m.ok("identidade")


def test_identidade_por_parafrase_conhecida():
    m = monitorar("Atendente: Pode me falar o nome da sua mãe e o seu CEP para eu liberar o atendimento?")
    assert m.ok("identidade")


def test_oferta_so_vale_se_cliente_nao_pediu():
    assert not monitorar("Atendente: Aproveite o limite pré-aprovado.").ok("oferta")
    assert monitorar("Cliente: Quero um empréstimo.\nAtendente: Simulo o empréstimo.").ok("oferta")


def test_saldo_antes_de_validar_viola_lgpd_e_depois_nao():
    antes = monitorar("Atendente: Seu saldo é R$ 10.\nAtendente: Preciso validar sua identidade.")
    depois = monitorar("Atendente: Preciso validar sua identidade.\nAtendente: Seu saldo é R$ 10.")
    assert not antes.ok("lgpd") and depois.ok("lgpd")


def test_ler_cpf_inteiro_viola_lgpd():
    assert not monitorar("Atendente: O CPF 529.982.247-25 é seu?").ok("lgpd")


def test_saudacao_parcial():
    m = monitorar("Atendente: Boa tarde, qual é o assunto?")
    assert m.itens["saudacao"].pontos == 8


def test_gerador_e_deterministico_e_rotulado():
    a, b = gerar_lote(20, 7), gerar_lote(20, 7)
    assert [x.texto() for x in a] == [x.texto() for x in b]
    assert all(set(x.rotulo) == set(PESOS) for x in a)


def test_casos_curados():
    certos, total, falhas = acerto_curados()
    assert certos == total, falhas


def test_benchmark_bate_o_baseline():
    texto = rodar(200, 1)
    m = re.search(r"\| \*\*média\*\* \| \*\*([\d.]+)%\*\* \| ([\d.]+)%", texto)
    assert float(m.group(1)) > float(m.group(2)) + 20


def test_cli_avaliar(tmp_path, capsys):
    f = tmp_path / "lig.txt"
    f.write_text(BOA, encoding="utf-8")
    assert main(["avaliar", str(f)]) == 0
    assert "Nota: 100/100" in capsys.readouterr().out


def test_relatorio_lista_feedback():
    assert "Feedback:" in relatorio(monitorar("Atendente: Pois não?"))
