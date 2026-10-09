"""Ligações sintéticas em texto, com rótulo do que cada item deveria dar.

Cada item sorteia uma variante boa ou ruim; o rótulo é a escolha sorteada, escrita
antes de olhar a regra. Parte das variantes é paráfrase que as regras não conhecem
de propósito, para o benchmark não dar 100% por construção. Dados fictícios.
"""
from __future__ import annotations

import random
from dataclasses import dataclass

from .checklist import ITENS, Fala

NOMES = ("Marina", "Carlos", "Juliana", "Rafael", "Beatriz", "Tiago")
MOTIVOS = (
    "Meu cartão foi cobrado duas vezes na mesma compra.",
    "Preciso da segunda via do boleto, perdi o que chegou.",
    "Não estou conseguindo entrar no aplicativo desde ontem.",
    "Apareceu uma tarifa que eu não reconheço na minha conta.",
    "Quero bloquear meu cartão, acho que perdi na rua.",
)

SAUDACAO_OK = (
    "Boa tarde, central de atendimento, meu nome é {n}. Em que posso ajudar?",
    "Bom dia! Aqui é a {n}, da central. Como posso ajudar o senhor?",
    "Olá, boa noite, me chamo {n}, fico à disposição. Qual é o motivo do contato?",
    "Bom dia, sou o {n} da central de atendimento, tudo bem?",
)
SAUDACAO_RUIM = (
    "Pois não?",
    "Fala, qual é o problema?",
    "Central, diga.",
    "Boa tarde, qual é o assunto?",  # cumprimenta mas não se apresenta (nota parcial)
)

IDENTIDADE_OK = (
    "Para sua segurança, preciso confirmar seus dados: pode me dizer o nome completo e a data de nascimento?",
    "Antes de seguir, vou validar sua identidade. Qual é o seu nome completo?",
    "Pode me informar os últimos dígitos do seu documento para eu confirmar o cadastro?",
    "Só para eu ter certeza de que falo com o titular, me diga nome completo e data de nascimento.",
    "Pode me falar o nome da sua mãe e o seu CEP para eu liberar o atendimento?",  # coberta desde a parte 2
    "Qual é o e-mail e o telefone com DDD que o senhor cadastrou conosco?",  # paráfrase fora das regras
    "Me conta de onde o senhor está ligando e qual é a data do seu aniversário, por favor.",  # idem
)
IDENTIDADE_RUIM = (
    "Certo, já estou olhando aqui.",
    "Para entrar na sua conta, qual é a sua senha do aplicativo?",
    "Me passa o código de verificação que chegou por SMS para eu abrir o cadastro.",
    "Ok, deixa eu ver o que aconteceu.",
)

OFERTA_RUIM = (
    "Aproveite que está na linha: temos um limite pré-aprovado de R$ 3.000 para o senhor.",
    "Já que o senhor ligou, posso oferecer um seguro de vida com desconto hoje.",
    "Também tenho um empréstimo consignado com taxa especial, quer que eu simule?",
    "Que tal conhecer o nosso cartão black? Está com anuidade zero este mês.",  # paráfrase fora das regras
)

RESOLUCAO_OK = (
    "Pronto, abri um chamado e o seu protocolo é 2026-{p}. O prazo de retorno é de até 5 dias úteis.",
    "Já resolvi: fiz o estorno da cobrança duplicada e o valor volta em até 2 dias. Protocolo {p}.",
    "Bloqueei o cartão agora e a segunda via chega em 7 dias úteis. Anote o protocolo {p}.",
    "Atualizei o seu cadastro e reenviei o acesso, deve funcionar em alguns minutos. Protocolo {p}.",
)
RESOLUCAO_SO_ACAO = (
    "Pronto, abri um chamado para o seu caso.",
    "Já fiz o estorno aqui.",
)
RESOLUCAO_RUIM = (
    "Isso o senhor precisa ver direto na agência.",
    "Vou verificar e a gente vê o que dá para fazer.",
    "Infelizmente não consigo ajudar com isso por telefone.",
    "Então é isso, aguarde que alguém entra em contato.",
)
ENCERRAMENTO_OK = (
    "Posso ajudar em mais alguma coisa?",
    "Tem mais alguma dúvida? Se não, tenha um bom dia.",
    "Algo mais em que eu possa ajudar? Obrigada por ligar.",
)

LGPD_CPF = (
    "Estou com o CPF 529.982.247-25 aqui, é esse mesmo? Preciso validar sua identidade.",
    "O cartão que consta é o 4539 1488 0343 6467, correto? Preciso confirmar seus dados.",
)
LGPD_ANTES = (
    "Vi aqui que seu saldo é de R$ 1.240,00 e sua fatura fechou em R$ 830,00.",
    "Seu endereço é Rua das Flores, 120, não é? Já estou vendo sua conta.",
    "Seu limite disponível é de R$ 2.000. Sobre a cobrança, deixa eu ver.",
)
LGPD_DEPOIS_OK = ("Seu saldo disponível é de R$ 1.240,00.", "Sua fatura fechou em R$ 830,00.")


@dataclass
class Ligacao:
    falas: list[Fala]
    rotulo: dict[str, bool]  # item -> deveria estar ok

    def texto(self) -> str:
        return "\n".join(f"{f.autor.capitalize()}: {f.texto}" for f in self.falas)


def gerar(rng: random.Random, taxa_ruim: float = 0.4) -> Ligacao:
    rotulo = {i: rng.random() >= taxa_ruim for i in ITENS}
    nome = rng.choice(NOMES)
    protocolo = rng.randint(100000, 999999)
    falas: list[Fala] = []

    def at(txt): falas.append(Fala("atendente", txt))
    def cl(txt): falas.append(Fala("cliente", txt))

    at(rng.choice(SAUDACAO_OK if rotulo["saudacao"] else SAUDACAO_RUIM).format(n=nome))
    cl(rng.choice(MOTIVOS))
    if not rotulo["lgpd"] and rng.random() < 0.6:
        at(rng.choice(LGPD_ANTES))
        cl("Isso, é isso mesmo.")
    at(rng.choice(IDENTIDADE_OK if rotulo["identidade"] else IDENTIDADE_RUIM))
    cl("Claro, é Paulo Souza, nascido em 14 de março de 1985.")
    if not rotulo["lgpd"] and not any("saldo" in f.texto or "Seu endereço" in f.texto or "limite" in f.texto
                                       for f in falas if f.autor == "atendente"):
        at(rng.choice(LGPD_CPF))
        cl("Isso mesmo.")
    elif rotulo["lgpd"] and rotulo["identidade"] and rng.random() < 0.4:
        at(rng.choice(LGPD_DEPOIS_OK))
        cl("Certo, obrigado.")
    if not rotulo["oferta"]:
        at(rng.choice(OFERTA_RUIM))
        cl("Não, só quero resolver o meu problema.")
    if rotulo["resolucao"]:
        at(rng.choice(RESOLUCAO_OK).format(p=protocolo))
        at(rng.choice(ENCERRAMENTO_OK))
    else:
        at(rng.choice(RESOLUCAO_SO_ACAO + RESOLUCAO_RUIM))
    return Ligacao(falas, rotulo)


def gerar_lote(n: int, semente: int = 42) -> list[Ligacao]:
    rng = random.Random(semente)
    return [gerar(rng) for _ in range(n)]
