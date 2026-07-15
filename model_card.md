# DocuBot Model Card

This model card is a short reflection on your DocuBot system. Fill it out after you have implemented retrieval and experimented with all three modes:

1. Naive LLM over full docs  
2. Retrieval only  
3. RAG (retrieval plus LLM)

Use clear, honest descriptions. It is fine if your system is imperfect.

---

## 1. System Overview

**What is DocuBot trying to do?**  
Describe the overall goal in 2 to 3 sentences.

> _Your answer here._

**What inputs does DocuBot take?**  
For example: user question, docs in folder, environment variables.

> _Your answer here._

**What outputs does DocuBot produce?**

> _Your answer here._

---

## 2. Retrieval Design

**How does your retrieval system work?**  
Describe your choices for indexing and scoring.

- How do you turn documents into an index?
- How do you score relevance for a query?
- How do you choose top snippets?

> _Your answer here._

**What tradeoffs did you make?**  
For example: speed vs precision, simplicity vs accuracy.

> _Your answer here._

---

## 3. Use of the LLM (Gemini)

**When does DocuBot call the LLM and when does it not?**  
Briefly describe how each mode behaves.

- Naive LLM mode:
- Retrieval only mode:
- RAG mode:

> _Your answer here._

**What instructions do you give the LLM to keep it grounded?**  
Summarize the rules from your prompt. For example: only use snippets, say "I do not know" when needed, cite files.

> _Your answer here._

---

## 4. Experiments and Comparisons

Run the **same set of queries** in all three modes. Fill in the table with short notes.

You can reuse or adapt the queries from `dataset.py`.

| Query | Naive LLM: helpful or harmful? | Retrieval only: helpful or harmful? | RAG: helpful or harmful? | Notes |
|------|---------------------------------|--------------------------------------|---------------------------|-------|
| Example: Where is the auth token generated? | | | | |
| Example: How do I connect to the database? | | | | |
| Example: Which endpoint lists all users? | | | | |
| Example: How does a client refresh an access token? | | | | |

**What patterns did you notice?**  

- When does naive LLM look impressive but untrustworthy?  
- When is retrieval only clearly better?  
- When is RAG clearly better than both?

> _Your answer here._

---

## 5. Failure Cases and Guardrails

**Describe at least two concrete failure cases you observed.**  
For each one, say:

- What was the question?  
- What did the system do?  
- What should have happened instead?

> _Failure case 1 here._

> _Failure case 2 here._

**When should DocuBot say “I do not know based on the docs I have”?**  
Give at least two specific situations.

> _Your answer here._

**What guardrails did you implement?**  
Examples: refusal rules, thresholds, limits on snippets, safe defaults.

> _Your answer here._

---

## 6. Limitations and Future Improvements

**Current limitations**  
List at least three limitations of your DocuBot system.

1. _Limitation 1_
2. _Limitation 2_
3. _Limitation 3_

**Future improvements**  
List two or three changes that would most improve reliability or usefulness.

1. _Improvement 1_
2. _Improvement 2_
3. _Improvement 3_

---

## 7. Responsible Use

**Where could this system cause real world harm if used carelessly?**  
Think about wrong answers, missing information, or over trusting the LLM.

> _Your answer here._

**What instructions would you give real developers who want to use DocuBot safely?**  
Write 2 to 4 short bullet points.

- _Guideline 1_
- _Guideline 2_
- _Guideline 3 (optional)_

---


# DocuBot Model Card

## Model/System Name

DocuBot

## Goal

DocuBot is a lightweight documentation assistant that helps developers answer questions about a local project documentation folder.

The goal is to compare three approaches:

1. Naive LLM generation
2. Retrieval only
3. Retrieval-Augmented Generation, also called RAG

## Data Used

DocuBot uses local documentation files from the `docs/` folder.

The main documentation files include information about authentication, API endpoints, setup instructions, and database configuration.

## System Overview

DocuBot loads `.md` and `.txt` files from the `docs/` folder. It builds a small retrieval index by mapping words to the documents where they appear.

When a user asks a question, DocuBot can search the documentation and return the most relevant snippets.

In RAG mode, DocuBot retrieves snippets first, then asks the LLM to answer using only those snippets.

## Mode 1: Naive LLM Generation

Naive LLM mode sends the documentation to the language model without using a retrieval step.

This mode can produce clear and fluent answers, but it is less reliable because the model may blend details together or answer without showing clear evidence.

For example, when asked where the auth token is generated, a good answer should mention `generate_access_token` in `auth_utils.py`.

Naive generation is useful for comparison, but I would not trust it by itself for developer documentation questions.

## Mode 2: Retrieval Only

Retrieval Only mode does not use the LLM. It searches the documentation and returns matching snippets.

This mode is more grounded because the answer comes directly from the documentation files.

For example, when asked which endpoint returns all users, Retrieval Only found `GET /api/users` in `API_REFERENCE.md`.

The downside is that Retrieval Only can be harder to read because it returns raw snippets instead of a polished explanation.

## Mode 3: RAG

RAG mode combines retrieval with generation.

First, DocuBot retrieves the most relevant snippets. Then the LLM uses only those snippets to write a clear answer.

This produced the best balance because the answers were easier to understand than raw retrieval, but still grounded in documentation evidence.

For example, RAG can answer that auth tokens are generated by `generate_access_token` in `auth_utils.py`, while relying on the retrieved `AUTH.md` snippet.

## Guardrail Behavior

DocuBot includes a guardrail for questions that are not supported by the documentation.

When asked, “How do I cook pasta?”, DocuBot answered:

“I do not know based on these docs.”

This is good behavior because the documentation does not contain cooking instructions. A refusal is safer than a confident but unsupported answer.

## Observed Strengths

DocuBot successfully retrieves relevant documentation snippets.

It can identify important details such as:

* `generate_access_token` in `auth_utils.py`
* `GET /api/users`
* `DATABASE_URL`
* The local SQLite default behavior

RAG mode gives clearer answers than Retrieval Only while staying more grounded than Naive LLM mode.

## Observed Limitations

The retrieval system is simple and based on word matching.

It may still return extra snippets if different documents share similar words.

It does not understand meaning deeply like a full semantic search system.

The quality of RAG answers depends on whether retrieval finds the right snippets first.

## Reliability and Safety

The most important safety feature is the refusal guardrail.

If DocuBot cannot find useful documentation evidence, it should say it does not know instead of guessing.

This makes the system more reliable for private or unfamiliar documentation.

## What I Learned

This project showed me why retrieval matters in AI systems.

A language model alone can sound confident even when it is not clearly grounded. Retrieval gives the model evidence before it answers.

I also learned that RAG is not just about using a smarter model. The retrieval design, snippet size, scoring logic, and guardrails all affect the quality of the final answer.

As an AI engineer, this project shows that I can build a small but practical RAG pipeline, test its behavior, and think critically about reliability.
