import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os
import srt

srt_path = '../raw_srt_files'

documents = []
for filename in os.listdir(srt_path):
    if filename.endswith('.srt'):
        file_path = os.path.join(srt_path, filename)
        with open(file_path, 'r', encoding='utf-8') as file:
            raw_content = file.read()
            raw_srt_chunks = list(srt.parse(raw_content))
            # print(raw_srt_chunks)
            cleaned_content = ' '.join([chunk.content for chunk in raw_srt_chunks])
            documents.append(cleaned_content)
        
documents = [str(doc) for doc in documents]
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(documents)

query = input('Qestion:')
query_vec = vectorizer.transform([query])


results = cosine_similarity(X, query_vec)

for idx, score in enumerate(results[:, 0]):
    print(f"Document {idx + 1}: Similarity = {score:.4f}")

