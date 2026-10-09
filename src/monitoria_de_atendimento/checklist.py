"""Checklist de monitoria sobre transcrição de ligação (texto).

Regras explícitas, sem modelo: cada ponto perdido vem com o trecho que o causou.
Itens e pesos (soma 100): saudação 15, identidade 20, resolução 25, oferta indevida 20, LGPD 20.
Os termos ficam sem acento porque o texto é normalizado antes da busca.
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field

ITENS = ("saudacao", "identidade", "resolucao", "oferta", "lgpd")
PESOS = {"saudacao": 15, "identidade": 20, "resolucao": 25, "oferta": 20, "lgpd": 20}

CUMPRIMENTO = ("bom dia", "boa tarde", "boa noite", "ola")
SE_APRESENTA = ("meu nome e", "me chamo", "sou o ", "sou a ", "aqui e o ", "aqui e a ", "falando com")

VERIFICA = (
    "nome completo", "data de nascimento", "ultimos digitos", "confirmar seus dados",
    "validar sua identidade", "confirmar sua identidade", "confirmar o cpf", "me informar o cpf",
    "me confirmar o cpf", "dados cadastrais", "confirmar o cadastro",
    "nome da sua mae", "nome da mae", "seu cep", "o cep", "falo com o titular", "falando com o titular",
    "ultimos digitos do seu documento", "endereco cadastrado", "confirmar quem esta falando",
)
SENSIVEL = (
    r"senha", r"token", r"cvv", r"codigo de seguranca", r"codigo de verificacao",
    r"codigo (que )?(chegou|enviado) por sms", r"numero completo do cartao",
)
NEGACAO = re.compile(r"(nunca|jamais|nao|sem|evite)\b[^.?!]{0,40}$")

ACAO = (
    "protocolo", "abri um chamado", "abri o chamado", "ja resolvi", "foi resolvido", "resolvido",
    "vou encaminhar", "encaminhei", "estorno", "bloqueei", "desbloqueei", "segunda via",
    "ajustei", "cancelei", "regularizei", "atualizei", "reenviei",
)
ENCERRA = (
    "mais alguma", "algo mais", "posso ajudar em mais", "tenha um bom", "tenha um otimo",
    "obrigado por ligar", "obrigada por ligar", "prazo de", "em ate",
)

OFERTAS = (
    r"limite pre.?aprovado", r"pre.?aprovad", r"seguro (de|prestamista|residencial|de vida)",
    r"contratar um seguro", r"oferecer um seguro", r"emprestimo", r"consignado", r"upgrade",
    r"cartao (premium|black|gold|platinum)", r"investimento", r"aproveite", r"oferta especial",
    r"promocao exclusiva",
)

DADO_ANTES_DE_VALIDAR = (r"seu saldo", r"sua fatura (e|esta|fechou)", r"seu limite (e|disponivel)",
                         r"seu endereco (e|cadastrado)", r"voce mora")
CPF = re.compile(r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b")
CARTAO = re.compile(r"\b(?:\d[ -]?){13,16}\b")

DICAS = {
    "saudacao": "Comece com cumprimento e apresente-se (nome e empresa).",
    "identidade": "Confirme a identidade (nome completo, data de nascimento) e nunca peça senha, token ou CVV.",
    "resolucao": "Diga o que foi feito, passe protocolo ou prazo e pergunte se há algo mais.",
    "oferta": "Não ofereça produto que o cliente não pediu, principalmente em reclamação.",
    "lgpd": "Não fale saldo, fatura ou endereço antes de validar a identidade, nem leia CPF ou cartão inteiro em voz alta.",
}


def normalizar(texto: str) -> str:
    base = unicodedata.normalize("NFD", texto.lower())
    return "".join(c for c in base if unicodedata.category(c) != "Mn")


@dataclass
class Fala:
    autor: str  # "atendente" ou "cliente"
    texto: str


def ler_transcricao(texto: str) -> list[Fala]:
    """Linhas `Atendente: ...` e `Cliente: ...`; linha sem prefixo continua a fala anterior."""
    falas: list[Fala] = []
    for linha in texto.splitlines():
        linha = linha.strip()
        if not linha:
            continue
        m = re.match(r"(?i)^(atendente|cliente)\s*:\s*(.*)$", linha)
        if m:
            falas.append(Fala(m.group(1).lower(), m.group(2)))
        elif falas:
            falas[-1].texto += " " + linha
        else:
            raise ValueError("a transcrição deve começar com 'Atendente:' ou 'Cliente:'")
    return falas


@dataclass
class ResultadoItem:
    pontos: int
    evidencias: list[str] = field(default_factory=list)


@dataclass
class Monitoria:
    itens: dict[str, ResultadoItem]

    @property
    def nota(self) -> int:
        return sum(i.pontos for i in self.itens.values())

    def ok(self, item: str) -> bool:
        return self.itens[item].pontos == PESOS[item]

    def feedback(self) -> list[str]:
        return [DICAS[i] for i in ITENS if not self.ok(i)]


def _trecho(texto: str, n: int = 90) -> str:
    return texto if len(texto) <= n else texto[: n - 1] + "…"


def _sensivel_pedido(t: str) -> str | None:
    """Primeiro termo sensível sem negação logo antes (\"nunca peço sua senha\" é ok)."""
    for padrao in SENSIVEL:
        for m in re.finditer(padrao, t):
            trecho = re.split(r"[.?!]", t[max(0, m.start() - 45): m.start()])[-1]
            if not NEGACAO.search(trecho + " "):
                return m.group(0)
    return None


def _saudacao(at: list[tuple[int, str, str]]) -> ResultadoItem:
    if not at:
        return ResultadoItem(0, ["sem fala do atendente"])
    _, bruto, t = at[0]
    cumprimenta = any(c in t for c in CUMPRIMENTO)
    apresenta = any(a in t for a in SE_APRESENTA)
    pontos = (8 if cumprimenta else 0) + (7 if apresenta else 0)
    ev = [f"primeira fala: \"{_trecho(bruto)}\""]
    if not cumprimenta:
        ev.append("sem cumprimento")
    if not apresenta:
        ev.append("não se apresentou")
    return ResultadoItem(pontos, ev)


def _identidade(at: list[tuple[int, str, str]]) -> tuple[ResultadoItem, int | None]:
    """Devolve também o índice da primeira fala que valida identidade (para a ordem do LGPD)."""
    for i, bruto, t in at:
        pedido = _sensivel_pedido(t)
        if pedido:
            return ResultadoItem(0, [f"pede dado sensível (\"{pedido}\"): \"{_trecho(bruto)}\""]), None
    for i, bruto, t in at:
        if any(v in t for v in VERIFICA):
            return ResultadoItem(20, [f"valida identidade: \"{_trecho(bruto)}\""]), i
    return ResultadoItem(0, ["não validou a identidade"]), None


def _resolucao(at: list[tuple[int, str, str]]) -> ResultadoItem:
    acao = next(((b, a) for _, b, t in at for a in ACAO if a in t), None)
    encerra = next(((b, e) for _, b, t in reversed(at) for e in ENCERRA if e in t), None)
    pontos = (15 if acao else 0) + (10 if encerra else 0)
    ev = []
    ev.append(f"ação/protocolo (\"{acao[1]}\"): \"{_trecho(acao[0])}\"" if acao else "nenhuma ação ou protocolo informado")
    ev.append(f"encerramento (\"{encerra[1]}\")" if encerra else "sem encerramento nem prazo")
    return ResultadoItem(pontos, ev)


def _oferta(at: list[tuple[int, str, str]], cliente: str) -> ResultadoItem:
    for _, bruto, t in at:
        for padrao in OFERTAS:
            m = re.search(padrao, t)
            if m and not re.search(padrao, cliente):
                return ResultadoItem(0, [f"oferta que o cliente não pediu (\"{m.group(0)}\"): \"{_trecho(bruto)}\""])
    return ResultadoItem(20, ["sem oferta indevida"])


def _lgpd(at: list[tuple[int, str, str]], idx_valida: int | None) -> ResultadoItem:
    ev = []
    for i, bruto, t in at:
        if CPF.search(t) or CARTAO.search(t):
            ev.append(f"lê CPF ou cartão inteiro: \"{_trecho(bruto)}\"")
        if idx_valida is None or i < idx_valida:
            for padrao in DADO_ANTES_DE_VALIDAR:
                if re.search(padrao, t):
                    ev.append(f"fala dado pessoal antes de validar a identidade: \"{_trecho(bruto)}\"")
                    break
    return ResultadoItem(0, ev) if ev else ResultadoItem(20, ["sem exposição de dado pessoal"])


def monitorar(transcricao: str | list[Fala]) -> Monitoria:
    falas = ler_transcricao(transcricao) if isinstance(transcricao, str) else transcricao
    at = [(i, f.texto, normalizar(f.texto)) for i, f in enumerate(falas) if f.autor == "atendente"]
    cliente = normalizar(" ".join(f.texto for f in falas if f.autor == "cliente"))
    identidade, idx_valida = _identidade(at)
    return Monitoria({
        "saudacao": _saudacao(at),
        "identidade": identidade,
        "resolucao": _resolucao(at),
        "oferta": _oferta(at, cliente),
        "lgpd": _lgpd(at, idx_valida),
    })


def relatorio(m: Monitoria) -> str:
    linhas = ["| Item | Pontos | Evidência |", "|---|---|---|"]
    for i in ITENS:
        r = m.itens[i]
        linhas.append(f"| {i} | {r.pontos}/{PESOS[i]} | {'; '.join(r.evidencias)} |")
    linhas.append(f"\nNota: {m.nota}/100")
    fb = m.feedback()
    if fb:
        linhas.append("\nFeedback:")
        linhas += [f"- {f}" for f in fb]
    return "\n".join(linhas)
