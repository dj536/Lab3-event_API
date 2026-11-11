# Lab 3 — From spec to working API (50 min, pairs)

Build the API described in `SPEC.md` with **Copilot Agent mode**, step by step.

1. **Instructions (5 min)** — create `.github/copilot-instructions.md` (stack, style, "run pytest after every change", "never add a dependency without asking").
2. **Plan (5 min)** — Plan mode: "Read SPEC.md and propose a step-by-step plan. Do not write code yet." Review and correct the plan.
3. **Build (25 min)** — Agent mode, one step at a time. After each green step: review the diff, `git commit`.
4. **Verify (10 min)** — `pytest tests -q` (acceptance tests, do not modify them) + write 5 tests of your own in `tests/test_mine.py`.
5. **Ship (5 min)** — push, post your score (passed / 18) on the board.

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload     # http://127.0.0.1:8000/docs
pytest tests -q
```

---

# TP 3 — De la spec à l'API (50 min, en binôme)

Construisez l'API décrite dans `SPEC.md` avec le **mode Agent de Copilot**, étape par étape.

1. **Instructions (5 min)** — créez `.github/copilot-instructions.md` (stack, style, « lance pytest après chaque modification », « n'ajoute jamais de dépendance sans demander »).
2. **Plan (5 min)** — mode Plan : « Lis SPEC.md et propose un plan étape par étape. N'écris pas encore de code. » Relisez et corrigez le plan.
3. **Construction (25 min)** — mode Agent, une étape à la fois. Après chaque étape verte : relire le diff, `git commit`.
4. **Vérification (10 min)** — `pytest tests -q` (tests d'acceptation, ne pas les modifier) + 5 tests à vous dans `tests/test_mine.py`.
5. **Livraison (5 min)** — push, score (réussis / 18) au tableau.
