# CM3070 mock test — answers

There are FOUR questions.

- Question 1 is COMPULSORY (no marks). If you skip it, the whole exam is marked zero.
- Answer ALL of Questions 2–4. Each carries 20 marks.
- Total: 60 marks.

---

## Question 1

This question is COMPULSORY, though it carries no marks. If you do not answer this question, you will get a mark of zero for your entire exam.

### (a)

What was the title of your project?

**Answer:** PrivateFin: A Privacy-First, Explainable Financial Advisory System

### (b)

Which template was your project based on?

**Answer:** CM3020 Artificial Intelligence — Financial Advisor Bot

### (c)

Briefly describe what your project was about.

**Answer:** PrivateFin is a local-first financial advisory prototype. It downloads public stock data from Yahoo Finance, computes RSI and MACD, and uses a local LLM to explain a recommendation in an Observe–Interpret–Infer–Recommend (OIIR) format. User prompts stay on the machine; the only external call is Yahoo Finance. If the local model is offline, the app still shows the structured analysis.

---

## Question 2

### (a) [5 marks]

What is the main difference between the proposal for a project (whether as a video pitch or a written document) and the final report (again, whether considering the written document or the video aspect of this). Using your own project, give examples to illustrate this difference. Also comment on how your proposal related to your final report.

**Answer:** The proposal is a plan: it says what you intend to build, why it matters, and how you will evaluate it. The final report is an account of what actually happened: what was implemented, what evidence you have, and what you can no longer claim. That holds for both media. A pitch video sells a future system; a final demo has to show the running pipeline and cannot honestly over-claim. A written proposal does the same job on paper; a final report has to survive contact with implementation and evaluation.

In PrivateFin this gap was large. The preliminary report and proposal video described “zero data egress”, treated the EU AI Act as if retail investment advice were automatically high-risk, and talked about regulatory-grade chain-of-thought. The final report and demo kept the same core idea — local Llama 3, Yahoo Finance, RSI/MACD, OIIR, Streamlit — but narrowed the claims: local LLM inference, not a fully offline app; OIIR as a user-facing format, not hidden model reasoning; an educational disclaimer rather than legal compliance. Evaluation also changed the story: tests passed, the 365-day TA-Lib values agreed, but OIIR quality missed the 6/8 target and the user study was never run. The final demo therefore had to show Yahoo as an external call, the fallback when Ollama is down, and the disclaimer — things a pitch can skip.

The proposal still related closely to the final report: it fixed the template, the architecture, and the research questions (privacy, correctness, explainability). The final work did not become a different project; it became a more honest version of the same one. That relationship — same aim, tighter claims, evidence instead of intention — is the main difference I would illustrate.

### (b) [7 marks]

The consideration of ethics is an important part of a design and development project. What are the most important ethical aspects to consider in software design and development? Which specific ethical considerations did you take into account in your project? Are there other ethical considerations you could or should have taken into account that you decided not to? Explain why.

**Answer:** The main ethical issues in software are harm/safety, privacy and data minimisation, fairness, transparency, and accountability (who is responsible when the system is wrong). In finance, a fluent but wrong recommendation can cost someone money, so overconfident automation is a safety issue, not just a UX issue.

In PrivateFin I focused on privacy by design and transparency. Prompts go to a local LLM; there is no login and no request for holdings. Market data is the only intended external call, and users see RSI/MACD plus an OIIR explanation and an educational disclaimer. I used GDPR-style minimisation and AI-Act-style transparency as design guides, not as a claim that the app is certified. I also kept the model from executing trades, so a human still has to act.

What I deprioritised was output safety beyond a banner, and fairness. Evaluation showed fluent OIIR can still reverse MACD or invent price targets. I deferred hard post-generation checks so I could score the baseline prompt. For a real user-facing advisor that order is wrong: filters should sit in the pipeline, not only in a disclaimer. Fairness and a consented user study were also out of scope for time: the UI is English-only Streamlit, and I never tested whether novices actually calibrate trust. Those were conscious scope choices, not because they do not matter.

### (c) [4 marks]

Explain the importance of doing background reading and a literature survey in a Computer Science project. Describe the most challenging aspect you faced when writing your literature survey, and how you overcame this.

**Answer:** Background reading stops a project being “I built a thing.” It shows where the idea sits, what has already been tried, and why your design choices are justified. Without it you can pick a fashionable method that answers the wrong question, or claim novelty that does not exist. The survey also gives you vocabulary and evaluation ideas (for me: Rudin on interpretability, Bender on fluent-but-ungrounded text, TA-Lib as an independent numerical check).

The hard part was that “financial AI” is a huge, uneven literature. BloombergGPT, FinGPT and FinBERT look like the obvious papers, but they optimise domain accuracy and scale, whereas my questions were local inference, inspectable indicators, and explanation faithfulness. Early drafts treated every finance LLM as a competitor I had to beat. I overcame this by organising the review around my research questions instead of around model names, and by including alternatives from the template (RL, backtesting) in order to say explicitly why I did not use them. That turned the survey into a justification of scope, not a catalogue of papers.

### (d) [4 marks]

Discuss ONE ethical consideration in selecting and reporting background material, and explain your approach to addressing this consideration in your own project.

**Answer:** One ethical issue is faithful reporting: not stretching a source so it appears to prove your project. Confirmation bias is easy in a literature review — you quote the bits that make cloud systems look unethical and skip limits, caveats, or the actual scope of a law.

I had to correct this in PrivateFin. Early writing treated the EU AI Act as if retail investment advice were listed as high-risk, and described OIIR as regulatory-grade chain-of-thought. The Act’s Annex III does not actually list ordinary retail advice that way, and Wei et al.’s chain-of-thought paper is not evidence that my four headings reveal hidden model reasoning. In the final review I reported what the sources support and what they do not: BloombergGPT shows domain data helps, not that local Llama 3 is equivalent; FinGPT being open-source does not mean inference is private; RSI/MACD papers describe heuristics, not proven trading edges. The ethical approach was to cite to justify a bounded design, not to inflate the contribution.

---

## Question 3

### (a) [10 marks]

Consider the following case study:

Imagine that your project is the development of a learning analytics algorithm to detect students at risk of failure.

Your evaluation consists of asking reviewers to take a set of inputs to the algorithm and their corresponding outputs, and answering the following sets of questions.

**Set 1**

- Does the output help me understand which students are at risk?
- Would this output help a teacher support students better?
- Would this output help you improve your WP student retention?

**Set 2**

- Do you think student A is in need of additional support?
- Do you think student B is in need of additional support?
- Do you think student C is in need of additional support?

Critically discuss the tasks presented, and the questions asked, in the context of the evaluation approach that is being taken. Include suggestions for additional or different approaches to the evaluation.

**Answer:** This evaluation is a form of expert review of input–output pairs. It is trying to do two different jobs at once: Set 1 asks whether the _presentation_ looks useful, and Set 2 asks reviewers to judge _individual students_. Neither set actually tests whether the algorithm detects students who later fail. For a high-stakes classifier, that is a weak evaluation approach.

Set 1 measures face validity and perceived usefulness, not correctness. The questions are hypothetical (“would this help”), leading, and aimed at mixed audiences (“me”, “a teacher”, “you” / WP retention). Reviewers may not be teachers, may not know what Widening Participation retention means, and can praise a fluent dashboard that is still biased or inaccurate. There is no baseline (current tutor judgement, a simple attendance rule, or a random list), so you cannot tell whether the algorithm adds value. Usefulness of the _display_ is also confounded with quality of the _model_.

Set 2 looks more concrete, but it is still opinion on three unnamed cases. “Needs additional support” is not the same construct as “at risk of failure.” Reviewers see the algorithm’s outputs as well as the inputs, so they are likely to anchor on the system’s label rather than judging independently. Three students is not a sample: no sampling frame, no false-positive/false-negative split, no WP vs non-WP breakdown, no inter-rater agreement. There is also an ethical problem: labelling students as at-risk from identifiable records without a protocol for consent, stigma, or how a wrong flag would be used.

What is missing is a declared claim and a matching method. If the claim is predictive accuracy, you need historical outcomes (who actually failed or withdrew), a frozen test set, and metrics such as precision, recall, calibration, and subgroup fairness for WP students. If the claim is that teachers make better decisions, reviewers should first label cases _blind_ (inputs only), then you compare human–human and human–algorithm agreement; separately, teachers should complete realistic tasks with and without the tool. If the claim is actionability, ask what intervention they would take and whether the explanation is understandable, not only “would this help.”

I would add: a small error analysis of misses and false alarms; a fairness/bias check so WP status is not used as a proxy that simply flags disadvantaged students; and an ethics review before any live deployment. The lesson from PrivateFin is the same: we scored OIIR structure and indicator numbers separately from usability, and we did not treat a working demo as evidence that users were helped. This case study collapses those layers into a short questionnaire, so it cannot support a claim that at-risk students are actually detected or better supported.

### (b) [6 marks]

Imagine you are required to give an in-person presentation, of 20 minutes, to discuss the most significant aspects of your project. Outline, with concrete detail, what this presentation would consist of, and which parts of the project you would highlight. Justify your choices of what you would include. Also comment on what aspects would be most challenging to present.

**Answer:** I would not try to retell the whole report. The significant story is the _hybrid architecture_ and whether the evidence supports the claims. Rough timing:

1. Problem (2 min). Cloud financial LLMs leak query intent; black-box buy/hold/sell is hard to inspect. PrivateFin’s question: can a consumer machine combine deterministic indicators with a local LLM explanation?

2. Design (5 min). One diagram: Yahoo Finance → RSI/MACD in code → OIIR prompt → Ollama on localhost → Streamlit. Highlight three boundaries: numbers are not computed by the model; prompts are not sent to a cloud LLM; the UI shows an educational disclaimer and a fallback if Ollama is down. Short live or recorded demo: pick Apple, Medium risk, show metrics then OIIR.

3. Evaluation (8 min). This is the core. Tests: 18/18 passed. Privacy: 273 endpoint snapshots, no external Python/Ollama socket, but Yahoo still leaves the machine. Indicators: 365-day TA-Lib agreement to four decimals; shorter windows disagree because of initialisation. Explainability: 20/20 OIIR headings, mean 5.95/8, missed target; MACD sign errors and invented targets. Usability: protocol written, no participants.

4. Honest close (3 min). Contribution is synthesis and evaluation discipline, not a new trading algorithm and not a regulated adviser. Remaining 2 minutes for questions.

I would highlight evaluation over extra features because the project’s academic value is showing where claims hold and where they fail. The hardest parts to present: a live Ollama demo that can stall; explaining MACD without a finance lecture; and saying the explanation study failed its mean without sounding like the whole project failed. I would screenshot a known-bad output (reversed MACD) so the limitation is visible, not hidden.

### (c) [4 marks]

Based on the significant aspects of your project identified in part (b) of this question, suggest further work – with justification of why – that another student might do, to continue or further advance the outcome in some way. Be as explicit as possible.

**Answer:** Another student should not rebuild the Streamlit shell. They should take the unfinished evidence and the known failure modes.

First, add deterministic output guards, then repeat the 20-sample OIIR study with a _different_ frozen ticker set, fixed temperature, and an independent second scorer using the existing 0–2 rubric (accuracy, coherence, completeness, transparency). Guards should reject invented price targets/portfolio percentages and check that MACD-versus-signal language matches the numeric sign. Justification: part (b)’s main finding was that format compliance is not faithfulness; a follow-on project can test whether those checks raise the mean above 6/8.

Second, run the prepared five-participant usability protocol (Apple + Medium risk task, SUS, clarity ratings, interview) and report whether novices can find RSI and say whether they would trust the recommendation. Justification: architecture and indicator tests are already evidenced; user understanding is not.

Optional third: payload-level packet capture during inference to complement the loopback socket audit, and a declared RSI/MACD pre-roll so short-window TA-Lib disagreement is designed out. I would not start with RL trading or extra news APIs: those change the research question away from local, inspectable explanation.

---

## Question 4

### (a) [4 marks]

Explain what makes a project a Computer Science project rather than an IT deployment. Discuss, with justification, where your project fits within this range, and what implications this has for future work on the same project.

**Answer:** An IT deployment mainly configures existing products: install, connect APIs, make a usable screen. A Computer Science project poses a research question, chooses or designs methods, and evaluates whether claims hold. It needs abstraction (what is the system actually doing?), algorithms or models with defined behaviour, and evidence, not only a working demo.

PrivateFin sits on the CS side of that range, but it is not a new forecasting algorithm. The CS content is the *hybrid contract*: RSI/MACD are computed deterministically in code; the LLM is only allowed to explain supplied values; privacy is treated as a testable boundary (loopback Ollama vs Yahoo egress); and each claim has a method (unit tests, TA-Lib comparison, endpoint audit, OIIR rubric). If I had only wrapped yfinance and a cloud chatbot in Streamlit, that would have been IT.

Implication for future work: keep going in the CS direction — output guards, a second scored study, payload capture — rather than “more tickers and a nicer theme.” Extra UI without a new question and evaluation would slide the project toward deployment.

### (b) [4 marks]

In terms of inclusive design, explain the core similarities and differences between the radical inclusion approach and the born-accessible approach to inclusive software design. Include examples to illustrate the distinctions.

**Answer:** Both approaches reject the old model of building for a “typical” user and bolting on access later (for example scanning a PDF and adding alt text after a complaint). Both want disabled and other excluded people considered *before* release, and both argue that this is cheaper and fairer than retrofit.

They differ in what they treat as the centre of the problem. **Born-accessible** is about the artefact and the pipeline: accessibility is a first-class requirement from conception, so the product ships already usable with assistive tech and meets standards (semantic structure, captions, keyboard access). Example: writing course notes in properly headed HTML from week 1, rather than remediating a slide deck in week 12. **Radical inclusion** is broader and more political: you design *with* the people who currently face the highest barriers, including intersectional exclusion (disability plus language, literacy, income), and you may change what the product *is*, not only how it complies. Example: a bank app whose primary persona is a screen-reader user with low financial literacy, so voice, plain language and trust cues drive the architecture, instead of a visual dashboard with an accessibility overlay.

PrivateFin did neither well. A born-accessible version would have treated Streamlit keyboard/screen-reader support as a requirement, not a later nice-to-have. A radical-inclusion version would have co-designed the OIIR explanation with novices and disabled investors first. I used plain English and a disclaimer, which is closer to a weak inclusive intention than to either approach.

### (c) [5 marks]

Identify ONE significant theoretical construct used in your project and explain its role in the project. Discuss why the construct was significant, and whether it was the best or the only option you could have chosen. If it was the best or only option, describe why this was the case; and if it wasn’t, then discuss what other options were available and why you did not choose them.

**Answer:** The construct I would name is a **constrained, user-facing explanation scaffold** — OIIR (Observe, Interpret, Infer, Recommend) — related to chain-of-thought prompting but not treated as a window into the model’s hidden reasoning.

Its role was to stop the LLM producing an unstructured “buy this” paragraph. The four stages force a path from evidence to a cautious action, give the UI a stable shape, and let me score completeness, faithfulness and proportionality. That mattered because the template asked for advisory language, while Rudin-style advice would say: do not use a black box for high-stakes decisions. OIIR was the compromise: keep the black box in the *communication* layer, and keep the numbers outside it.

It was not the only option. I could have: (1) a purely rule-based advisor (if RSI ≥ 70 then “overbought / caution”) with no LLM; (2) FinBERT-style classification labels only; (3) free-form prompting or hidden CoT; (4) post-hoc explainers such as SHAP, which do not fit a generative chatbot. The rule-based option is more interpretable in Rudin’s sense and might have been *better* for safety, but it would have failed the generative “advisor bot” brief and helped novices less with prose. Free-form prompting was worse for evaluation. So OIIR was the best fit for *this* research question — structured, checkable explanation on consumer hardware — not the only theoretically respectable design.

### (d) [3 marks]

Describe ONE algorithm or method you used in the app, program, or system that you designed and developed, and explain your choice process, justifying the decisions you made about using that algorithm or method.

**Answer:** I used **Wilder-style RSI over 14 periods** on closing prices: split up/down moves, exponentially smooth gains and losses with α = 1/14, then map relative strength onto 0–100, with explicit handling of zero-loss/zero-gain and a warm-up fill.

I chose it because it is closed-form, standard in technical analysis, and *checkable* against the LLM’s prose. The model never computes RSI; the engine does, and the prompt quotes the value. I preferred that over asking Llama 3 to “look at the chart,” and over adding a pile of extra indicators that would have looked more impressive but made faithfulness harder to test. MACD was added as a second inspectable signal, but RSI was the primary simple momentum method. I rejected RL/backtested trading rules because they would have answered a profitability question I was not asking.

### (e) [4 marks]

Reproducibility refers to the extent to which an algorithm, method, or tool can produce the same result when used again under the same, or similar, conditions. Discuss how this concept applies to the algorithm or method you described in Part (d) above.

**Answer:** For a *fixed* close series and the same RSI parameters and pandas `ewm` convention, the algorithm is deterministic: another run on the same CSV should match to machine precision. That is why I persist downloads and compare against TA-Lib.

Reproducibility weakens as soon as the conditions are only “similar.” Short windows disagree with TA-Lib because libraries seed the Wilder average differently; my 365-day latest values agreed to four decimals, but 90- and 182-day comparisons did not all match. Yahoo Finance can also revise history, so repeating the same ticker and dates later is not the same input. The warm-up fill of 50 during the first periods is a declared convention; a different convention would change early values.

So RSI is reproducible as a function, not as a live market feature. That is the opposite of the LLM path, where temperature was not even pinned. I would not claim bit-for-bit reproducibility of a live “Generate analysis” click — only of the indicator function on a preserved file.
