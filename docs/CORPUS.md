# Caption Corpus (Template Engine → Planner → Generator → Validator → Corpus → Exporters)

A CPU-only, **deterministic** language-generation layer that turns the per-disease
Caption Concept Models plus the authored Template Library into a validated,
**image-independent** caption corpus, then reshapes it into training formats. No
image, no LLM/VLM, no randomness — repeated builds are byte-identical.

> **Scope note.** This milestone builds a *disease-level* caption corpus: a pure
> function of `(ontology, vocabulary, lexicon, templates)`. Image cross-join,
> instruction pairing, image-based splits, and the image-grounded per-model VLM
> converters (`CONVERTER_REGISTRY` for Qwen/InternVL/Gemma/MLX) are a later
> milestone; the frozen image-grounded stubs are left untouched.

## The five stages

1. **Template Engine** (`plantdx.templates`) — loads/validates/indexes the
   authored templates (`assets/templates/templates.json`). Templates carry
   *syntax only*: structured segments (`lit`/`slot`/`opt`/`list`) that name
   concept ids, authored so that dropping any optional slot stays grammatical.
   8 families mirror `caption_framework/02_template_spec.md`
   (short, single_sentence, two_sentence, clinical, descriptive, educational,
   dense, long). A template is *compatible* with a disease iff the disease's
   effective sign type is allowed and every required slot concept is available.
2. **Sentence Planner** (`plantdx.corpus.planner`) — fills a compatible
   template's slots with controlled realizations chosen deterministically from
   the concept model, producing a `SentencePlan` (structured, not English).
3. **Caption Generator** (`plantdx.corpus.generator`) — realizes a plan into
   English: concatenation + deterministic surface repair (whitespace,
   punctuation, articles, Oxford-comma lists, sentence capitalization that
   protects genus-abbreviated species names, terminal punctuation).
4. **Caption Validator** (`plantdx.corpus.validator`) — 12 independent checks
   that never trust the generator (defense in depth); a failing candidate is
   dropped and recorded.
5. **Corpus Builder** (`plantdx.corpus.builder`) — enumerates a bounded,
   diverse set of captions per disease, validates + de-duplicates, and hard-errors
   if any disease yields zero valid captions.
6. **Dataset Exporters** (`plantdx.exporters`) — pure reshapers of the one corpus
   into `generic` / `llava` / `paligemma` / `blip2` / `messages` formats.

## Run it

```bash
plantdx templates                      # validate + index the template library
plantdx generate                       # build the caption corpus -> artifacts/corpus/
plantdx generate --condition tomato_early_blight   # one disease
plantdx generate --crop mango          # one crop
plantdx generate --stats-only          # print corpus statistics JSON
plantdx validate                       # build + print the validation report
plantdx corpus                         # build corpus + write all exporters
plantdx corpus --format paligemma      # build corpus + one export format
plantdx corpus --all                   # build corpus + all export formats
```

## Artifacts

`artifacts/corpus/` (gitignored): `captions.json`, `captions.jsonl`,
`captions.csv`, `statistics.json`, `validation_report.json`, `checksum.txt`.
Every caption record carries its full source-checksum pin (ontology, vocabulary,
concepts, templates) plus `evidence`, `confidence`, `observable`, `concepts`, and
`language` — no metadata is lost. `artifacts/templates/` holds the derived
`template_index.json` + checksum; `artifacts/exports/<format>/` holds each
export's `data.jsonl` + `manifest.json`.

## Validators

**Template Engine (`V-TPL-1..8`)** — structural: valid enums, concept-id
legality, required/optional coherence, segment validity, hedging discipline,
healthy-vs-disease routing, declared families.

**Caption Validator (`V-CAP-1..12`)** — per caption: ontology legality (asserts
only available concepts, ≥1 defining anchor), template legality, mandatory
content present in text, no forbidden concept, no `never_appear` term, no
duplicate sentence, grammar, modifier legality, observability legality (visual
captions assert nothing non-observable), confidence = weakest link, **no severity
stage token**, and traceability (evidence + observability recomputed and matched).

## Guarantees

- **Deterministic.** No timestamps, no randomness (seed-controlled choices only);
  corpus + every export are byte-identical across runs. Golden hash pinned in
  `tests/unit/corpus/test_corpus_determinism.py`.
- **Severity-honest.** No caption asserts a severity stage — DKB phrases
  containing "severe"/"advanced" are rejected by two validators (defense in depth).
- **Traceable.** Every caption's concepts trace to the concept model, and through
  it to the DKB and its evidence; the generator only concatenates controlled phrases.
- **Fail closed.** Invalid candidates are dropped and recorded; a disease with
  zero valid captions is a hard error.
