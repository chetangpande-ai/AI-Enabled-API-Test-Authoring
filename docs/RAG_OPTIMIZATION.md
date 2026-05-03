# RAG Optimization: Hybrid Search & Deduplication Guide

## Problem: Duplicate Test Scenarios

Your platform generated duplicate test cases because:
1. **Semantic search alone** has blind spots (similar scenarios worded differently)
2. **LLM judgment** is unreliable for deduplication 
3. **No data-level deduplication** or similarity checks

---

## Solution: 3-Layer Defense

### Layer 1: Hybrid Retrieval ✅ IMPLEMENTED
**Combines semantic + lexical search**

```python
# Uses BM25 (keyword matching) + ChromaDB (vector similarity)
retriever = get_hybrid_retriever(k=10)  # Weights: 0.5 semantic + 0.5 lexical
```

**Why it works:**
- **Semantic (0.5 weight):** Catches conceptually similar scenarios
- **Lexical/BM25 (0.5 weight):** Catches exact keyword matches

**Trade-offs:**
| Aspect | Semantic Only | Hybrid Search |
|--------|---------------|---------------|
| Exact matches | ❌ Miss worded differently | ✅ Catches via BM25 |
| Semantic similarity | ✅ Good | ✅ Better precision |
| Speed | Fast | Slightly slower (worth it) |

---

### Layer 2: Similarity Filtering ✅ IMPLEMENTED
**Deduplicates at threshold level**

```python
unique_scenarios, duplicates = filter_duplicate_scenarios(
    new_scenarios,
    existing_docs,
    similarity_threshold=0.7  # Adjust 0.5-0.8
)
```

**Similarity Threshold Tuning:**
- **0.5 (Loose):** Only remove nearly identical scenarios
- **0.7 (Recommended):** Balance between safety and coverage  
- **0.85 (Strict):** Remove anything moderately similar (may be too aggressive)

**How it works:**
1. **Fingerprinting:** SHA256 hash of normalized scenario (catches exact duplicates)
2. **Jaccard Similarity:** Compares text overlap between scenarios
3. **Filters:** Removes scenarios exceeding similarity threshold

---

### Layer 3: Fingerprinting (State Tracking) ✅ IMPLEMENTED
**Prevents regeneration of same scenarios**

```python
# Stored in state
state["scenario_fingerprints"] = {
    "hash1": "Scenario Name 1",
    "hash2": "Scenario Name 2"
}
```

**Benefits:**
- Tracks which scenarios were generated
- Enables idempotent scenario generation
- Useful for incremental updates

---

## Configuration Options

### Option A: Production (Strict Deduplication)
```python
retriever = get_hybrid_retriever(k=15)  # Retrieve more context
similarity_threshold = 0.75  # Stricter
```
**Use when:** Accuracy > Coverage (no duplicate test costs you more)

### Option B: Balanced (Recommended)
```python
retriever = get_hybrid_retriever(k=10)
similarity_threshold = 0.7
```
**Use when:** Balanced risk (default)

### Option C: Exploratory (Loose)
```python
retriever = get_hybrid_retriever(k=5)
similarity_threshold = 0.6
```
**Use when:** Coverage > Accuracy (want all possible test variations)

---

## Integration Steps

### 1. Update Dependencies
```bash
pip install rank-bm25  # For BM25 lexical search
```

### 2. Use Enhanced RAG in Your Workflow
```python
from src.utils.rag_enhanced import get_hybrid_retriever, filter_duplicate_scenarios

# Already integrated in planner.py
```

### 3. Monitor Deduplication
Check logs for:
```
Deduplication: 45 unique, 8 duplicates from 53 total
Similar scenario detected: 'Login with invalid password' (similarity: 0.78)
```

---

## Monitoring & Tuning

### Metrics to Track
1. **Deduplication Rate:** `duplicates / total_planned`
   - Target: 5-15% (sign your threshold is reasonable)
   - >30%: threshold too high (missing needed tests)
   - <2%: threshold too low (might miss duplicates)

2. **False Positives:** Manually check filtered scenarios
   - Are legitimate different scenarios being removed?

3. **Test Coverage:** Are important scenarios being created?
   - Monitor via your test results

### Tuning Formula
```
If duplicates > 20%: decrease similarity_threshold (e.g., 0.7 → 0.65)
If duplicates < 5%: increase similarity_threshold (e.g., 0.7 → 0.75)
If missing coverage: decrease threshold & increase k
```

---

## Hybrid Search Algorithm (Reference)

```
For each new scenario:
  1. Hybrid retrieve: Get top-10 results (semantic 50% + lexical 50%)
  2. Calculate fingerprint (SHA256)
  3. Calculate Jaccard similarity against each existing
  4. If similarity > threshold → flag as duplicate
  5. Otherwise → include in plan

EnsembleRetriever automatically handles ranking & deduplication
```

---

## Advanced Options (Future)

### Option 1: Semantic Reranker
Add cross-encoder reranking after retrieval:
```python
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import CrossEncoderReranker

reranker = CrossEncoderReranker(
    model=HuggingFaceCrossEncoder("cross-encoder/qnli-distilroberta-base")
)
compressed_retriever = ContextualCompressionRetriever(
    base_compressor=reranker,
    base_retriever=hybrid_retriever
)
```

### Option 2: Metadata Filtering
Filter by test type:
```python
docs = retriever.invoke(spec_str)
filtered_docs = [d for d in docs if d.metadata.get('type') != 'duplicate']
```

### Option 3: Database-Level Deduplication
Store scenario fingerprints in persistent DB instead of state:
```python
# Create scenario registry
scenario_registry = {}  # {fingerprint: scenario_metadata}
```

---

## Next Steps

1. ✅ Deploy `rag_enhanced.py`
2. ✅ Update `planner.py` 
3. **Run test:** Generate test cases for your sample API
4. **Monitor logs:** Check deduplication metrics
5. **Tune threshold:** Adjust based on deduplication rate
6. **Optional:** Implement metadata filtering for fine-tuned control

---

## FAQ

**Q: Will hybrid search slow down my pipeline?**
A: ~10-15% slower retrieval, but prevents expensive LLM re-runs. Worth it.

**Q: Should I always use k=10?**
A: Start with 10, adjust based on your corpus size:
- Small corpus (<100 scenarios): k=5-7
- Medium (100-500): k=10
- Large (>500): k=15

**Q: What if I want to regenerate all scenarios?**
A: Clear ChromaDB and restart, or reset fingerprints in state.

**Q: Can I use this with existing test data?**
A: Yes! Re-run `rag_ingestion.py` after deploying this solution.
