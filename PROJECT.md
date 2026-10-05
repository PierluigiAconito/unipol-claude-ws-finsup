# Progetto: unipol-claude-ws-finsup

Prototipo e2e sviluppato durante l'**Hagenthon** (Accenture Application Engineering) — Tema 02: **Inclusione Finanziaria**.

Documento unico di riferimento per il team: consolida regole del workshop, tema ufficiale scelto e stato dei requisiti funzionali. Per il dettaglio completo dei 3 temi (incluso ciò che non abbiamo scelto) vedi [docs/01-temi-della-sfida.md](docs/01-temi-della-sfida.md).

## Team e vincoli di tempo

- **Team**: 2 persone
- **Durata**: 3 ore di sviluppo totali
- **Deliverable**: prototipo software e2e funzionante + presentazione di 5 minuti (demo inclusa) + repo pubblico GitHub

## Tema scelto: Inclusione Finanziaria

**Obiettivo**: usare strumenti di agentic coding per supportare l'educazione alla finanza personale di base, aiutando le persone con bassa alfabetizzazione finanziaria a comprendere concetti e gestire meglio le proprie finanze quotidiane.

**Focus**: non creare un consulente finanziario AI. Aiutare a *comprendere*, non a *decidere al posto di*.

### Vincoli specifici (vanno rispettati dall'applicazione)

- Scenario educativo preciso, uno tra: comprensione di un concetto finanziario di base, gestione del budget personale, lettura di un estratto conto/bolletta, comprensione di costi e commissioni, simulazione di una scelta quotidiana di risparmio.
- Deve dimostrare un miglioramento tangibile nella comprensione/capacità dell'utente (evidenza before/after).
- **Vietato**: raccomandazioni di investimento, consulenza finanziaria personalizzata, indicazioni su cosa comprare/vendere/scegliere.
- Deve includere una capability software concreta — non solo testo riscritto da un LLM.

### Cosa evitare (criteri di esclusione espliciti dei faculty)

- chatbot generici
- pura riscrittura di testi senza logica applicativa
- soluzioni che danno consigli finanziari
- semplificazioni che alterano il significato originale
- demo non collegate a un processo reale

### Deliverable specifici richiesti in demo/presentazione

1. **User Difficulty Statement** — quale difficoltà ha l'utente, in quale processo, perché è rilevante.
2. **Before / After Simplicity Evidence** — un esempio concreto di testo/flusso/schermata reso più chiaro.
3. **Risk & Clarity Note** — cosa è stato semplificato, cosa non è stato alterato, come è stata evitata ambiguità.

## Requisiti funzionali

🚧 In definizione (in carico alla collega) — vedi [docs/02-requisiti-funzionali.md](docs/02-requisiti-funzionali.md), da aggiornare appena pronti: persona target, scenario educativo preciso, funzionalità core, criterio di misurazione del miglioramento.

## Criteri di valutazione da soddisfare nel pacchetto finale

| Criterio | Dove viene mostrato nel repo |
|---|---|
| Qualità tecnica | struttura del codice, test, README |
| Uso consapevole dell'AI (token ridotti) | `CLAUDE.md` snello + nota strategia AI (da aggiungere) |
| Verifica umana | checklist/log di review (da aggiungere) |
| Evidenza pattern (skill, rules, hooks) | `.claude/` — CLAUDE.md, skill dedicate, hook di guardrail sui contenuti finanziari |
| Strategia di applicazione AI | nota dedicata su dove l'AI contribuisce nella soluzione e dove serve l'umano |

**Valutazione**: soggettiva (faculty) + oggettiva (agente AI su portale, legge il repo) → la somma determina la classifica. Il repo va quindi ottimizzato per essere leggibile sia da umani che da un agente valutatore automatico.

## Note di provenienza

- Regole di workshop e criteri di valutazione: kickoff chat con il team + brief ufficiale faculty (`hagenthon-temi-sfida-3.html`)
- Dettaglio completo dei 3 temi (anche quelli non scelti): [docs/01-temi-della-sfida.md](docs/01-temi-della-sfida.md)
