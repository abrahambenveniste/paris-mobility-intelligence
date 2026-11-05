# Working and learning with an assistant

## Our working agreement

Keep each increment small enough to explain. Before adding a feature, state its user question, necessary data and expected result. Afterwards show a short code excerpt, labelled input/output, checks performed, limitations and one understanding question. Link the full source rather than filling the conversation with entire files.

Use three explicit sample labels: **observed** (inspected source data or measured counts), **derived** (computed from specified inputs), and **synthetic** (fabricated to teach or test). Never present an example as measured evidence. Private raw samples can be inspected locally; publishing source records needs a terms review.

The owner sets direction and approves choices. Codex has assisted implementation, checks and documentation. Do not claim the owner independently wrote assistant-produced code or completed an exercise without evidence. Personal understanding is demonstrated by explaining decisions, running checks, making changes and recognising limits. Record these contributions as they occur.

## Useful prompts

- “Before coding, explain the problem in ordinary language. What is the smallest useful result?”
- “Show one input record, the exact transformation, and its output. Label real and synthetic data.”
- “Explain this function line by line. Define unfamiliar terms and ask me one question afterwards.”
- “Why did we choose this approach? Give one simpler alternative and the tradeoff. Separate assumptions from evidence.”
- “What does this test prove, and what does it not prove? Show an input that should fail.”
- “Give me a small exercise using existing local data. Wait for my attempt before showing the answer.”
- “Review my explanation as if you were interviewing me. Correct factual errors without making the project sound more advanced than it is.”
- “Document what changed, why, the evidence, the limitation and the next action. Avoid unexplained jargon.”

A reusable request:

> Help me implement [small feature] to answer [user question]. First explain the data and simplest approach. Show a short code example and labelled input/output. Make only the agreed change, run proportionate checks, and update GitHub. Then ask one question to check my understanding. Do not add infrastructure without a concrete need.

## Learning checkpoints — not yet recorded as completed

| Exercise | Evidence of understanding |
| --- | --- |
| Run the synthetic example | Explain expected time versus actual arrival, and why UTC is used |
| Inspect one local stop | Explain its identifier, coordinates and coverage flag |
| Trace a map marker | Find its Python output and JavaScript drawing operation |
| Change the synthetic line ID | Predict why selecting another line produces no matching departures |
| Run an existing test | Explain its input, assertion and remaining limitation |
| Explain the unmatched point | Say why we omit its location instead of guessing |
| Demonstrate the app | Explain snapshot age, source-record age and cached response age |

Record completed work in the journal only after it happens, with the owner's explanation or observed result. No new feature is required to demonstrate these skills.

## Presenting the project

An accurate starting description:

> “This is my AI-assisted Paris transport data project. I chose a small two-line pilot and prioritised data quality. The current app combines official route geometry and boarding points with on-demand predictions. The repository explains its transformations and limitations. I am working through the implementation so I can reproduce and explain each step.”

Update that description as your own contributions and understanding grow. Be prepared to distinguish a map from a simulation, a prediction from an observation, and passing tests from verified source accuracy.
