<!-- <AI-Generated START> -->

# The LPN-Engine: Local, Trustworthy AI Code Assistance

## What is the LPN-Engine?

The **LPN-Engine** (Local Polyglot Neurosymbolic Engine) is an AI coding assistant that runs entirely on our own hardware and checks its own work before anyone sees it.

The name describes the design:

- **Local** — it runs on a Mac mini in our building. No cloud service, no subscription, and our code and documentation never leave our network.
- **Polyglot** — "many languages." It generates and verifies code in the five languages our teams use: PHP, Python, Rust, JavaScript, and C# — checked by each language's own real toolchain.
- **Neurosymbolic** — the technical term, but the idea is simple. "Neuro" is the AI language model: creative, fast, but unreliable. "Symbolic" is a set of rule-based checkers — the same compilers our build systems use — which apply hard, unambiguous logic. The LPN-Engine makes them work as a pair: **the AI writes, the rules decide.** Whenever the two disagree, the rules win.

In practice, a developer asks for code from inside their normal editor; the engine generates it, fact-checks it against our own documentation library, compiles it, repairs it if the compiler objects, and only then returns it.

## The problem it solves

AI coding assistants are powerful but unreliable. Gary Marcus, a prominent AI researcher, has spent years documenting three fundamental weaknesses of large language models — and they're exactly the three problems a business should care about before trusting AI with its codebase:

1. **They make things up.** Models generate code that looks right but references functions, libraries, or documentation that don't exist. Catching these "hallucinations" eats developer time in review — or worse, slips through and breaks a build.
2. **They're brittle.** The same request can produce clean, structured output one time and a garbled mess the next. You can't build a dependable workflow on a coin flip.
3. **They have no deterministic logic.** A model doesn't *know* the rules of a programming language the way a compiler does — it produces plausible text, not verified code. Plausible is not the same as correct.

## How the LPN-Engine answers each one

The engine treats the AI like a **fast, ambitious junior developer** — and surrounds it with the same safeguards we'd put around one: it can only cite documentation that actually exists in our own library, its output must follow a strict structure, and **every line of generated code is checked by the real compiler before a human ever sees it.** If the code fails any check, the system sends the specific error back to the AI and makes it try again — automatically, up to three times. Bad output never reaches a developer's screen.

Each Marcus critique maps to a safeguard: hallucination → documentation and compiler checks; brittleness → a required output structure, always; missing logic → the compilers, which *are* the deterministic logic, get the final say.

## Why it matters to the business

- **Privacy by architecture.** Source code, prompts, and documentation never leave the building — no third-party cloud, no data-sharing terms to review.
- **Cost.** No per-token cloud subscription. The engine runs on models we already own, locally, at no marginal cost per use.
- **Trust at the gate, not after.** Code from the engine is *guaranteed to compile* (for our strongly-typed languages) or at minimum to parse cleanly. Review time goes to judging logic and design, not hunting invented API calls.
- **One tool, all five of our languages.** Each is verified by its own real toolchain — the same ones our builds use.
- **Fits existing tools.** Developers call it directly from the editors they already use; no new IDE, no workflow change.

## An honest boundary

The engine guarantees code is *well-formed and grounded in real documentation*. It does not guarantee the logic is the right solution to a business problem — human judgment stays in the loop, where it should be. What it removes is the category of AI errors that wastes the most time: the confident, fluent, wrong answer.

<!-- <AI-Generated END> -->
