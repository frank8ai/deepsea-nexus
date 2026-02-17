# L0 Abstract - Search Recall Execution

Return high-confidence recall results for user queries with explicit source evidence and predictable quality. 触发条件：user query contains memory triggers (`还记得`, `上次`, `之前提到`) OR query intent is historical lookup; first-pass top1 relevance is below `0.35` OR top3 median relevance is below `0.25`。核心产出：top-k recall results with relevance, source, and snippet; search quality record (latency, relevance, pass/fail gate decision)。
