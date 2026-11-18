from monitoria_de_atendimento.checklist import monitorar


def test_protocolo_de_11_digitos_nao_e_cpf():
    m = monitorar("Atendente: Anotei o protocolo 12345678902 para o senhor.")
    assert m.ok("lgpd")


def test_cpf_com_digito_verificador_certo_continua_violando():
    m = monitorar("Atendente: O CPF 52998224725 é seu?")
    assert not m.ok("lgpd")


def test_cpf_de_numeros_repetidos_nao_conta():
    assert monitorar("Atendente: Digite 11111111111 no painel.").ok("lgpd")
