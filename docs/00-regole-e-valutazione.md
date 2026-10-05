# Regole e Valutazione

Fonte: brief del team (chat di kickoff) + documento ufficiale faculty (`hagenthon-temi-sfida-3.html`).

## Vincoli di tempo e team

- **Durata**: 3 ore di sviluppo totali
- **Team**: 3 persone (il documento ufficiale indica team da 2, noi siamo in 3 — nessun impatto sulle regole, solo più capacità)

## Deliverable

1. **Soluzione software e2e funzionante** (prototipo)
2. **Presentazione da 5 minuti** al gruppo, demo della soluzione inclusa
3. **Repo pubblico su GitHub** con tutto il materiale (codice, documentazione, evidenze)

## Parametri di valutazione della soluzione

- **Qualità tecnica**
- **Uso consapevole dell'AI** (token ridotti — evidenziare scelte che riducono consumo/costo, es. prompt mirati, uso di subagent, caching)
- **Verifica umana** — dove e come un umano ha controllato/validato l'output dell'AI
- **Evidenza di validazione tramite pattern** (skill, rules, hooks) — va *documentata* nel repo, non solo praticata
- **Strategia di applicazione AI adottata** — dove/come l'AI contribuisce nella soluzione stessa, e dove no

## Modalità di valutazione

- **Soggettiva**: i faculty valutano la qualità percepita
- **Oggettiva**: la soluzione viene caricata su un portale e **un agente AI la valuta automaticamente** → il pacchetto (repo) va ottimizzato pensando a cosa un valutatore automatico può leggere e capire (README chiaro, struttura pulita, documentazione esplicita dei pattern usati)
- **Classifica** = somma valutazione soggettiva + oggettiva
- **Presentazione**: valutata separatamente

## Cosa tenere a mente per il pacchetto finale

Per massimizzare sia la valutazione umana sia quella automatica, il repo dovrebbe rendere esplicito e facile da trovare:

- Dove e come sono state usate skill / regole (CLAUDE.md) / hooks di Claude Code durante lo sviluppo
- Un breve resoconto della strategia di uso dell'AI (cosa ha fatto l'AI, cosa ha fatto l'umano, perché)
- Evidenza di verifica umana (es. checklist, note di review, test eseguiti)
- Note su uso consapevole dei token (scelte fatte per non sprecare contesto/chiamate)
