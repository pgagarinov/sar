# No Target Product Tests

The target repo (`sar-rag-target`) is the **product being improved by the researcher**. Its code (retriever, chunker, indexer, reranker, evaluator, pipeline) changes with every research cycle. Do not write tests for it.

## What NOT to test in the target

- Retrieval quality (which chunks are returned for which queries)
- Chunking behavior (chunk sizes, overlap, IDs)
- Index creation and querying
- Reranking logic
- Evaluator metric computation
- Pipeline orchestration
- Any behavior of `src/rag/` modules

## What IS testable in the target

Only **infrastructure files** that are never edited by the researcher:
- `src/rag/paths.py` — environment variable overrides for `RAG_INDEX_CACHE_DIR` and `RAG_REPORT_PATH`
- `.claude/` skills and agents — tested indirectly by the research-loop's E2E tests

## Why

Tests on product code become anchors. The researcher improves the retriever, and a test asserting "q-001 returns auth-api-keys-1" breaks — not because something is wrong, but because the retrieval strategy changed. The researcher then wastes cycles fixing tests instead of improving the product.

The target's quality is measured by the **eval set** (`corpus/eval_set.json`), not by unit tests. The eval set is the ground truth. The researcher's job is to maximize eval metrics, not to pass unit tests.
