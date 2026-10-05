# BudgetFacile

Prototipo e2e dell'Hagenthon (Accenture Application Engineering), **Tema 02: Inclusione Finanziaria**.

BudgetFacile trasforma i documenti di una persona (busta paga, bollette, estratto conto) in un budget mensile chiaro e spiega in parole semplici le voci tecniche che contengono. È uno **strumento educativo**: aiuta a capire, non dà consigli finanziari e non dice mai cosa fare con i propri soldi.

## Avvio rapido

Prerequisiti: Python 3.13. Facoltativo: la CLI di Claude Code (`claude`) autenticata sulla macchina, usata per leggere i documenti. Senza CLI l'app resta utilizzabile: le voci si inseriscono a mano e il glossario usa le definizioni riviste dal team.

```bash
python -m venv .venv
.venv/Scripts/pip install -r app/requirements.txt
.venv/Scripts/streamlit run app/main.py
.venv/Scripts/python -m pytest app
```

L'app si apre su `http://localhost:8501`, lo stesso indirizzo del pulsante "Apri app" nella presentazione. Prima di una demo conviene far leggere una volta i documenti, così in diretta il caricamento è immediato (il risultato resta in cache su disco):

```bash
.venv/Scripts/python app/scripts/prewarm_extraction.py "app/demo_assets/*"
```

## Come funziona

1. **Inserisci**: carica i documenti così come sono (PDF o Excel, anche più di uno), oppure inserisci tutto a mano.
2. **Conferma** (obbligatoria, RF-09): ogni voce è modificabile, si può eliminare o aggiungere. Le voci presenti in due documenti (es. lo stipendio in busta paga e il suo accredito sul conto) vengono contate una volta sola e mostrate in giallo. Nessun calcolo parte prima della conferma.
3. **Capisci**: entrate, uscite e risparmio del mese; dove vanno le spese (grafico e tabella); confronto con la regola 50/30/20 come semplice riferimento; glossario dei termini tecnici; in quanti mesi si raggiunge un obiettivo di risparmio, come proiezione matematica.

Requisiti completi: [app/docs/requisiti-funzionali.md](app/docs/requisiti-funzionali.md).

## Dove interviene l'AI, e dove no

| Passo | AI | Come |
|---|---|---|
| Lettura dei documenti | sì | Claude Haiku 4.5 tramite la CLI locale `claude -p`, con output vincolato da uno schema JSON; una chiamata per documento, risultato in cache per hash del file ([extraction.py](app/finsup/extraction.py)) |
| Calcoli e grafici | no | deterministici, coperti da test ([budget.py](app/finsup/budget.py)) |
| Doppioni tra documenti | no | regole deterministiche ([budget.py](app/finsup/budget.py), `remove_duplicates`) |
| Glossario | in parte | termini noti: definizioni riviste a mano, 0 token; termini nuovi: una sola chiamata, solo su richiesta ([glossary.py](app/finsup/glossary.py)) |

Ogni testo generato dall'AI passa dal guardrail anti-consigli [content_guard.py](app/finsup/content_guard.py) **prima** di essere mostrato. Lo stesso guardrail è applicato in sviluppo da un hook di Claude Code ([check_financial_advice.py](agents/hooks/check_financial_advice.py)). I system prompt sono in [agents/prompts/](agents/prompts/).

## Struttura del repository

```
app/                applicazione
  main.py           interfaccia Streamlit (3 passi)
  finsup/           logica: budget, estrazione, glossario, client della CLI, guardrail
  tests/            test pytest (logica, estrazione e glossario con CLI simulata, flusso UI)
  demo_assets/      documenti fittizi dei due scenari demo
  docs/             requisiti funzionali e deliverable del Tema 02
  scripts/          pre-lettura dei documenti per la demo
agents/             struttura agentica: contesto, istruzioni, prompt, skill, subagent, comandi, hook, workflow
presentation/       presentazione HTML
CLAUDE.md, .claude/ file letti da Claude Code (regole, hook e rimandi a skill e subagent in agents/)
```

## Criteri di valutazione: dove trovarli

| Criterio | Dove |
|---|---|
| Qualità tecnica | [app/finsup/](app/finsup/), [app/tests/](app/tests/), [app/requirements.txt](app/requirements.txt) |
| Uso consapevole dell'AI | [agents/workflows/uso-token.md](agents/workflows/uso-token.md), [agents/instructions/uso-ai.md](agents/instructions/uso-ai.md), [ai_client.py](app/finsup/ai_client.py) |
| Verifica umana | [agents/workflows/verifica-umana.md](agents/workflows/verifica-umana.md), conferma obbligatoria RF-09 nell'app |
| Pattern (rules, hook, skill, subagent, comandi) | [CLAUDE.md](CLAUDE.md), [agents/README.md](agents/README.md) |
| Strategia di applicazione dell'AI | [agents/workflows/strategia-ai.md](agents/workflows/strategia-ai.md) |
| Controllo qualità | [agents/workflows/qa-findings.md](agents/workflows/qa-findings.md) |

## Deliverable del Tema 02

- **User Difficulty Statement**: [requisiti-funzionali.md §2](app/docs/requisiti-funzionali.md)
- **Before/After Simplicity Evidence** e **Risk & Clarity Note**: [deliverable-tema02.md](app/docs/deliverable-tema02.md)
- **Presentazione**: [presentation/index.html](presentation/index.html)
