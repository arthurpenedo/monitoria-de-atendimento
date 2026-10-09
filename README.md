# monitoria-de-atendimento

Monitoria de ligação de atendimento ainda é feita por amostragem humana: se ouve uma fração pequena das chamadas. Este projeto aplica uma **checklist de monitoria** sobre a transcrição de uma ligação e devolve nota de 0 a 100, os trechos que justificam cada ponto perdido e um feedback curto para o atendente. Sem API paga, sem modelo, zero dependências.

> Parte 1 (texto). A transcrição por áudio (faster-whisper) e as vozes sintéticas (Piper) ficam para a parte 2.

## Checklist

| Item | Pontos | Passa quando |
|---|---|---|
| saudação | 15 | cumprimenta (8) e se apresenta (7) |
| identidade | 20 | valida a identidade (nome completo, nascimento...) e **nunca** pede senha, token ou CVV (negação como "nunca peço sua senha" é aceita) |
| resolução | 25 | informa a ação ou o protocolo (15) e encerra com prazo ou "mais alguma coisa?" (10) |
| oferta indevida | 20 | não oferece produto que o cliente não pediu |
| LGPD | 20 | não fala saldo, fatura ou endereço antes de validar a identidade e não lê CPF ou cartão inteiro |

## Como rodar

```bash
pip install -e .[dev]
monitoria-de-atendimento gerar --n 2            # ligações sintéticas com o rótulo esperado
monitoria-de-atendimento avaliar ligacao.txt    # linhas "Atendente: ..." e "Cliente: ..."
monitoria-de-atendimento benchmark --saida BENCHMARK.md
pytest
```

Exemplo de saída:

```
| Item | Pontos | Evidência |
| identidade | 0/20 | pede dado sensível ("senha"): "Qual é a sua senha?" |
Nota: 55/100
Feedback:
- Confirme a identidade (nome completo, data de nascimento) e nunca peça senha, token ou CVV.
```

## Números medidos (`BENCHMARK.md`, 500 ligações sintéticas, semente 42)

- Acerto médio da checklist contra o rótulo: **97,1%** (baseline "tudo ok": 62,4%).
- Por item: saudação 100%, resolução 100%, oferta 100%, LGPD 97,6%, identidade 87,8%.
- Nota média: 96,6 nas ligações sem falha rotulada; 60,5 nas que têm ao menos uma.
- Casos escritos à mão: 10/10. 15 testes.

## Limites honestos

- As ligações sintéticas e as regras têm o mesmo autor: o número mede a mecânica, não o desempenho em ligações reais. Incluí paráfrases que as regras não conhecem de propósito; a maior perda é "nome da sua mãe e CEP" como validação de identidade (identidade 87,8%).
- Regras por palavras não pegam ironia, contexto longo nem itens subjetivos (tom, clareza). Para esses a ideia é um modelo aberto via Ollama, ainda não feito.
- Sem áudio ainda e sem separação automática de quem fala: a transcrição precisa vir rotulada.
- Nenhum dado real de ligação foi usado; todos os nomes, CPFs e cartões são fictícios.

## Licença

MIT
