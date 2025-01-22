# Hybrid Search System TFIDF

This search system finds the top 3 lectures with the highest TFIDF scores based on a query. Then a Retrival Augmented Generation(RAG) search over the subtitle chunks of the three lectures is performed. Finally, the top 10 chunks are fed into a single Gemini agent to identify the clips that best answer the query.

