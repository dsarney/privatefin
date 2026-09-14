# CM3070 revision notes

**Closed book from 2026.** No A4 notes, no file upload. You are not meant to recite the mock essays. You are meant to **rebuild** from a small set of facts you already lived.

Tonight: learn the **seven stories** at the bottom. Tomorrow: spend four hours _arguing_ from them. That is still a research exam — the research already happened in the project.

**Paper:** 4 hours, Q1 compulsory (0 marks, skip = whole exam 0), Q2–4 = 20 each, 60 total.

**Time:** Q1 5 min → Q2 70 → Q3 70 → Q4 70 → 15 min skim. ~3.5 min per mark. Short paragraphs, hit every prompt in the question.

---

## Project facts (drop these in)

- **Title:** PrivateFin: A Privacy-First, Explainable Financial Advisory System
- **Template:** CM3020 AI — Financial Advisor Bot
- **Pipeline:** Yahoo Finance → RSI(14) + MACD(12/26/9) in code → OIIR prompt → local Llama 3 / Ollama → Streamlit
- **OIIR:** Observe, Interpret, Infer, Recommend
- **18/18** unit tests
- **Privacy:** 273 endpoint snapshots, 10 inferences, no external Python/Ollama socket; Yahoo still leaves the machine
- **TA-Lib:** 365-day latest values agree to 4 d.p.; 90- and 182-day windows do **not** all match (initialisation)
- **OIIR study:** 20/20 headings; mean **5.95/8** (target 6); MACD sign errors; invented targets / portfolio %
- **Usability:** protocol written; **no participants**
- **Disclaimer:** educational, not professional advice; no trade execution
- **Fallback:** if Ollama down, still show metrics + template

**Walk-backs (proposal → final):**

| Pitch said                     | Final says                                         |
| ------------------------------ | -------------------------------------------------- |
| Zero data egress               | Local LLM inference; Yahoo egress                  |
| AI Act high-risk retail advice | Annex III does **not** list ordinary retail advice |
| Regulatory-grade CoT           | OIIR = user-facing format, not hidden reasoning    |
| Compliance                     | Design _inspired_ by GDPR / AI Act, not certified  |

---

## Question 1 — identity (2 minutes)

**(a)** full title  
**(b)** CM3020 AI, Financial Advisor Bot  
**(c)** four facts: local LLM, Yahoo, RSI/MACD, OIIR + fallback

---

## Question 2

### 2(a) [5] Proposal vs final — written **and** video

**Difference:** proposal/pitch = _intention_. Final report/demo = _evidence_.

**Examples:** walk-back table above. Demo must show Yahoo, fallback, disclaimer (pitch can skip).

**Relation:** same project (template, architecture, RQs: privacy / correctness / explainability). Not a new idea — a more honest version.

Write 3 short paras: difference → examples → relation.

### 2(b) [7] App ethics — **three chunks**

1. **General:** safety/harm, privacy, fairness, transparency, accountability. Finance: fluent wrong advice = harm.
2. **I did:** local LLM, no login/holdings, Yahoo only external, visible RSI/MACD + OIIR, disclaimer, no auto-trade. GDPR minimisation / AI Act transparency as _guides_.
3. **I parked:** output **guards** (knew hallucinations; wanted baseline OIIR scores first); fairness + user study (time). Banner ≠ enough.

### 2(c) [4] Literature survey

**Why:** situate work, avoid fake novelty, justify methods, steal evaluation ideas (Rudin, Bender, TA-Lib).

**Hard:** “financial AI” papers (BloombergGPT, FinGPT, FinBERT) answer _accuracy/scale_, not _privacy/explainability_.

**Fix:** organise by **my RQs**, not model names; say why I rejected RL / backtesting.

### 2(d) [4] Literature ethics — **not** 2(b) again

**One issue:** faithful citation / no stretching sources.

**I did:** walked back AI Act + CoT; BloombergGPT ≠ my Llama; open-source FinGPT ≠ private inference; RSI/MACD = heuristics not edges.

---

## Question 3

### 3(a) [10] Case study — **not PrivateFin** (mention PF only at the end)

**What they are doing:** expert review of input–output pairs. Two jobs mixed. Neither tests “who actually failed.”

**Set 1:** face validity. Hypothetical, leading, mixed “me/teacher/you”. WP = Widening Participation. No baseline. Confounds pretty UI with good model.

**Set 2:** 3 opinions. “Needs support” ≠ “will fail.” Reviewers **see the algorithm output** → anchoring. n=3. No FP/FN, no WP split, no kappa. Ethics: stigma / identifiable students.

**Suggest:** declare the claim first.

- Accuracy → historical outcomes, precision/recall/calibration, WP fairness
- Better teacher decisions → **blind** labels first, then tool vs no-tool tasks
- Actionability → “what would you do next?”
- Error analysis + ethics review

**Closer:** PF scored numbers, OIIR, usability as _separate_ claims. This questionnaire collapses them.

### 3(b) [6] 20-minute talk

| Min | What                                | Why                     |
| --- | ----------------------------------- | ----------------------- |
| 2   | Problem: cloud leak + black box     | Sets the RQ             |
| 5   | Diagram + short demo (AAPL, Medium) | The actual contribution |
| 8   | Evaluation numbers (honest)         | Academic value          |
| 3   | Limits: not a trader, not certified | Trust                   |
| 2   | Questions                           |                         |

**Highlight:** hybrid contract + mixed evidence, not extra features.

**Hard:** live Ollama; MACD in English; 5.95/8 without sounding like a fail. Show a **bad** MACD screenshot.

### 3(c) [4] Further work — **continue 3(b)**, another student

1. **Guards** (MACD sign, no invented targets) + **second** 20-output OIIR study, fixed temperature, **second scorer**, same rubric. Why: format ≠ faithfulness.
2. **Run** the 5-person SUS / clarity protocol. Why: users untested.
3. Optional: packet payloads; RSI/MACD pre-roll.

**Not:** rebuild UI, RL trading, news APIs (wrong RQ).

---

## Question 4

### 4(a) [4] CS vs IT

**IT:** install, glue APIs, pretty screen.  
**CS:** question, method, evaluation, abstraction.

**Where I sit:** CS-ish hybrid contract (deterministic numbers, local LLM, testable privacy). Not a new forecast algo. Cloud chatbot in Streamlit = IT.

**Future:** guards + studies = still CS. More tickers / theme = slides toward IT.

### 4(b) [4] Inclusive design — **theory first**

**Same:** both reject retrofit / “typical user then fix.” Involve excluded people _before_ ship.

**Born-accessible:** artefact + pipeline. Accessibility from day 1 so it _ships_ usable (headings, captions, keyboard). Ex: notes in HTML from week 1, not a scanned PDF in week 12.

**Radical inclusion:** start with people who face the **highest** barriers; may change what the product _is_ (co-design, intersectionality). Ex: bank app whose primary persona is screen-reader + low literacy, not a dashboard with an overlay.

**Optional:** PF did neither; plain English disclaimer ≠ either approach.

### 4(c) [5] ONE construct = **OIIR scaffold**

**Role:** stop free “buy this”; path from evidence → cautious action; scorable.

**Why it mattered:** template wants a bot; Rudin wants no black box. Compromise: black box only in _prose_; numbers outside.

**Not only option:** (1) rules only, (2) FinBERT labels, (3) free-form / hidden CoT, (4) SHAP (wrong tool). Rules safer; OIIR better for _this_ brief.

### 4(d) [3] + 4(e) [4] **Must be the same method = RSI**

**(d)** Wilder RSI-14: gains/losses, α=1/14, 0–100. Chosen because **checkable**; model never computes it. Not “let Llama read the chart.” Not a pile of extra indicators. Not RL.

**(e)** Same CSV + same formula = same number (why we persist files / TA-Lib).  
“Similar” ≠ same: short windows, library seeds, Yahoo revisions, warm-up fill of 50.  
Reproducible **as a function**, not as a live click. LLM temperature was **not** pinned — don’t switch (e) onto the LLM.

---

## Traps

- Skip Q1 → zero for everything.
- 2(b) = app ethics. 2(d) = citing ethics.
- 3(a) is the learning-analytics case. Do not write a PrivateFin essay.
- 3(c) must follow 3(b) (guards + user study), not random features.
- 4(d) and 4(e) stay on **RSI**.
- Don’t claim zero egress, high-risk AI Act, or that OIIR is true CoT.

---

## Seven stories to know cold (closed book)

Say each one out loud. If you can tell it in 30 seconds, you can write the related question.

**1. What I built**  
PrivateFin, CM3020 AI Financial Advisor Bot. Yahoo → RSI+MACD in code → OIIR → local Llama/Ollama → Streamlit. Disclaimer, fallback, no trades.

**2. Pitch vs final**  
Intention → evidence. Written _and_ video. Same architecture. Walked back: zero egress; AI Act high-risk; “regulatory CoT”; certified compliance.

**3. The numbers**  
18/18 tests. 273 snapshots / 10 inferences, no external LLM socket, Yahoo still leaves. TA-Lib 365-day = 4 d.p., short windows don’t. OIIR 20/20 headings, **5.95/8**, MACD flips, invented targets. User study: protocol, zero people.

**4. Ethics split**  
App (2b): SPFTA. Did privacy+transparency. Parked guards + fairness + study.  
Cite (2d): don’t stretch sources. Same walk-backs.

**5. Eval method (3a)**  
I/O questionnaire ≠ “does it detect failure.” Set 1 = looks useful. Set 2 = 3 opinions, already saw the output. Need outcomes, **blind** labels, fairness, ethics. WP = Widening Participation.

**6. Talk + sequel (3b/c)**  
20 min: 2 problem, 5 demo, 8 eval, 3 limits, 2 Qs. Next student: guards + second OIIR + second scorer; run SUS. Not RL.

**7. Theory pair (4)**  
CS = question + method + evidence.  
Born-accessible = ship accessible from day 1. Radical inclusion = design with the most excluded.  
Construct = OIIR. Algorithm = **RSI** (and reproducibility stays on RSI).
