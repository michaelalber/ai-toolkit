# Third-party evaluation data

Cases in these files are derived from upstream datasets. Every row carries a `source` block
(dataset, file, pinned commit, license, upstream id). Regenerate with
`python -m ollama_evals.vendor_import` using the exact commands below; nothing is fetched at
run time.

## `bfcl_irrelevance.jsonl` — Berkeley Function Calling Leaderboard (BFCL v3)

- **Source:** [gorilla-llm/Berkeley-Function-Calling-Leaderboard](https://huggingface.co/datasets/gorilla-llm/Berkeley-Function-Calling-Leaderboard),
  file `BFCL_v3_irrelevance.json`, commit `61fc0608cfd831fcfbbaa676ebdfef0ed963eeda`
- **License:** Apache-2.0 (dataset card). Copyright the Gorilla / BFCL authors, UC Berkeley.
- **Citation:** Patil et al., *The Berkeley Function Calling Leaderboard (BFCL): From Tool Use
  to Agentic Evaluation of Large Language Models*, ICML 2025.
- **What it tests:** none of the offered tools fits the request, so the model must answer
  without calling one. Scored by code (`tool_use` with `expected: {"no_call": true}`).
- **Changes:** tool names have `.` replaced by `_`; BFCL's Python type names are mapped to
  JSON Schema (`dict`→`object`, `float`→`number`, `tuple`→`array`, `any`→unconstrained).
- **Selection:** a fixed-seed (7) sample of 60 of the 240 items, each reviewed by hand.
  [Epoch AI's review](https://epoch.ai/benchmarks/berkeley-function-calling-leaderboard/review)
  found mislabelled irrelevance items, and so did this review: 16 were dropped because an
  offered tool fits the question, or plausibly does. 44 remain.

  | Dropped | Why |
  |---|---|
  | irrelevance_16 | `calculate_projectile_range` answers "how far ... launched at angle theta" |
  | irrelevance_18 | `calculate_vector_angle` plausibly answers the momentum-angle question |
  | irrelevance_22 | `magnetic_field_intensity` answers the question exactly |
  | irrelevance_26 | `thermodynamics_calc_gas_pressure` plausibly answers the heated-chamber question |
  | irrelevance_46 | `get_exchange_rate` is a reasonable step toward a price in India |
  | irrelevance_54 | `movies_search` can plausibly find the highest-grossing movie |
  | irrelevance_74 | `investment_analysis_calculate_profit` is a direct step to rate of return |
  | irrelevance_101 | `get_average_monthly_temperature` is relevant to the best month to visit |
  | irrelevance_108 | `emission_estimator` is relevant to reducing CO2 emissions |
  | irrelevance_111 | the eco-friendly product locator plausibly fits the in-store search |
  | irrelevance_129 | `personality_assessment_evaluate` fits the request (inputs missing, not tool) |
  | irrelevance_144 | `search_holy_books` plausibly answers "what is a holy book" |
  | irrelevance_160 | `most_frequent_visitor` overlaps the visit-frequency question |
  | irrelevance_174 | `music_theory_primary_triads` gives the I-IV-V chords common in pop |
  | irrelevance_222 | `grocery_store_item_details` may include nutrition facts |
  | irrelevance_237 | `get_route_to_location` is relevant to finding the nearest pharmacy |

  ```
  python -m ollama_evals.vendor_import bfcl BFCL_v3_irrelevance.json \
      datasets/bfcl_irrelevance.jsonl --commit 61fc0608cfd831fcfbbaa676ebdfef0ed963eeda \
      --limit 60 --exclude irrelevance_16,irrelevance_18,irrelevance_22,irrelevance_26,irrelevance_46,irrelevance_54,irrelevance_74,irrelevance_101,irrelevance_108,irrelevance_111,irrelevance_129,irrelevance_144,irrelevance_160,irrelevance_174,irrelevance_222,irrelevance_237
  ```

## `ifeval.jsonl` — IFEval (Instruction-Following Eval)

- **Source:** [google/IFEval](https://huggingface.co/datasets/google/IFEval), file
  `ifeval_input_data.jsonl`, commit `966cd89545d6b6acfd7638bc708b98261ca58e84`
- **License:** Apache-2.0 (dataset card). Copyright Google LLC.
- **Citation:** Zhou et al., *Instruction-Following Evaluation for Large Language Models*,
  arXiv:2311.07911, 2023.
- **What it tests:** prompts with instructions code can verify ("no commas", "at least 300
  words", "end with this phrase"). Scored by code (`ifeval` scorer); a case passes only if
  every instruction is followed. No judge.
- **Changes:** prompts and instruction arguments are unchanged; `null` arguments are dropped.
  The checks in `src/ollama_evals/scorers/ifeval.py` are an independent re-implementation of
  IFEval's published instruction definitions (strict mode only), not Google's verifier code.
- **Selection:** 387 of 541 prompts — every prompt whose instructions are all among the 20
  types checkable without an NLP library. The 154 dropped prompts use at least one of
  `language:response_language`, `length_constraints:number_sentences`,
  `change_case:capital_word_frequency`, `change_case:english_capital` or
  `change_case:english_lowercase`. Scores are therefore not comparable to published IFEval
  numbers; they compare models with each other here.

  ```
  python -m ollama_evals.vendor_import ifeval ifeval_input_data.jsonl \
      datasets/ifeval.jsonl --commit 966cd89545d6b6acfd7638bc708b98261ca58e84
  ```

## License text

Both datasets are licensed under the Apache License 2.0; the full text is in
[`LICENSE-APACHE-2.0.txt`](LICENSE-APACHE-2.0.txt)
(from <https://www.apache.org/licenses/LICENSE-2.0.txt>).
