from monitoria_de_atendimento.checklist import monitorar


def test_ola_dentro_de_outra_palavra_nao_e_cumprimento():
    m = monitorar("Atendente: Escola Nova, sou a Ana.")
    assert m.itens["saudacao"].pontos == 7
    assert "sem cumprimento" in m.itens["saudacao"].evidencias


def test_ola_sozinho_continua_sendo_cumprimento():
    m = monitorar("Atendente: Olá, meu nome é Ana.")
    assert m.itens["saudacao"].pontos == 15


def test_tem_ate_nao_vale_como_prazo_de_encerramento():
    m = monitorar("Atendente: O boleto tem até hoje para pagar. Abri o chamado 123.")
    assert m.itens["resolucao"].pontos == 15
    assert "sem encerramento nem prazo" in m.itens["resolucao"].evidencias


def test_prazo_com_em_ate_continua_valendo():
    m = monitorar("Atendente: Abri o chamado 123, retorno em até 2 dias.")
    assert m.itens["resolucao"].pontos == 25
