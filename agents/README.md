# agents/: struttura agentica di BudgetFacile

BudgetFacile è il nome del prodotto; FinSup (`app/finsup/`, `finsup-copy-check`, `finsup-copy-reviewer`) è il nome interno del progetto.

Tutto ciò che guida gli agenti, in sviluppo (Claude Code) e a runtime (le chiamate dell'app a Claude), sta qui. È la fonte unica: `.claude/` contiene solo i collegamenti che Claude Code richiede per scoprire i componenti (vedi [sotto](#perché-claude-contiene-solo-rimandi)).

| Cartella | Contenuto | Tipo | Criterio di valutazione |
|---|---|---|---|
| [instructions/](instructions/) | Regole modulari importate da [`CLAUDE.md`](../CLAUDE.md): [dominio](instructions/dominio.md), [uso dell'AI](instructions/uso-ai.md), [processo](instructions/processo.md) | **Rules** | pattern, uso consapevole dell'AI |
| [hooks/](hooks/) | [`check_financial_advice.py`](hooks/check_financial_advice.py): hook **PreToolUse** su Write/Edit/MultiEdit che blocca la scrittura di file con linguaggio da consulente (exit 2). Configurato in [`.claude/settings.json`](../.claude/settings.json), testato in [`app/tests/test_hook.py`](../app/tests/test_hook.py) | **Hook** | pattern, qualità tecnica |
| [skills/](skills/) | [`finsup-copy-check`](skills/finsup-copy-check/SKILL.md): checklist su consigli, significato e accessibilità, con [eval](skills/finsup-copy-check/evals.md). [`accenture-html-deck`](skills/accenture-html-deck/SKILL.md): brand e struttura della presentazione | **Skill** | pattern, verifica umana |
| [subagents/](subagents/) | [`finsup-copy-reviewer`](subagents/finsup-copy-reviewer.md): revisore dei testi in sola lettura (Haiku). **Profili QA**, uno per punto di vista, ciascuno col modello adatto al compito: [`qa-faculty`](subagents/qa-faculty.md) (giuria, Sonnet), [`qa-check-agent`](subagents/qa-check-agent.md) (agente valutatore del portale, Sonnet), [`qa-graphic-designer`](subagents/qa-graphic-designer.md) (brand e UI, Opus per la visione), [`qa-utente-target`](subagents/qa-utente-target.md) (persona del Tema 02, Sonnet: su Haiku inventava numeri) | **Subagent** | uso consapevole dell'AI, verifica |
| [commands/](commands/) | [`/qa-review`](commands/qa-review.md): lancia i profili QA in parallelo e unisce i findings in [qa-findings.md](workflows/qa-findings.md). [`/demo-ready`](commands/demo-ready.md): checklist pre-freeze (test, struttura, guardrail, review, verifica umana) | **Comando slash** | verifica umana, qualità tecnica |
| [prompts/](prompts/) | System prompt usati **dall'app a runtime**, caricati con `finsup.prompts.load_prompt` | **Prompt** | strategia AI, token |
| [workflows/](workflows/) | [Workflow SDD](workflows/sdd-workflow.md) · [Strategia AI](workflows/strategia-ai.md) · [Uso dei token](workflows/uso-token.md) · [Verifica umana (log)](workflows/verifica-umana.md) | **Workflow** | strategia AI, verifica umana, token |
| [context/](context/) | Brief e regole del workshop: [regole e valutazione](context/regole-e-valutazione.md), [temi](context/temi-della-sfida.md), [progetto](context/progetto.md). Letti on demand, mai incollati nei prompt | **Contesto** | context engineering |

## Doppia rete sul vincolo "niente consigli finanziari"

```
sviluppo:  Claude Code ──Write/Edit──▶ hook PreToolUse ──violazione──▶ blocco (exit 2), Claude riformula
runtime:   Claude (CLI) ──testo──▶ content_guard.find_violations ──violazione──▶ testo non mostrato
review:    skill / subagent (pre-filtro AI) ──▶ persona del team ──▶ verifica-umana.md
```

Lo stesso modulo `app/finsup/content_guard.py` è usato sia dall'hook sia dall'app: una sola definizione del vincolo, testata una volta.

## Perché `.claude/` contiene solo rimandi

La consegna chiede la struttura agentica in `agents/`, ma Claude Code scopre skill, subagent e comandi solo in `.claude/skills/`, `.claude/agents/`, `.claude/commands/`. Lì teniamo quindi un file minimo con nome, descrizione, strumenti e modello, che rimanda al file completo in `agents/`: disclosure progressiva, nessuna logica duplicata. L'hook è referenziato direttamente da `.claude/settings.json`.
