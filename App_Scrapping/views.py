from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from bs4 import BeautifulSoup
import requests
from sentence_transformers import SentenceTransformer
import numpy as np
import faiss

class ScrapeView(APIView):
    def post(self, request):
        base_url = request.data.get('url')
        if not base_url:
            return Response({"error": "URL is required."}, status=status.HTTP_400_BAD_REQUEST)

        response = requests.get(base_url)
        if response.status_code != 200:
            return Response({"error": "Failed to fetch the website."}, status=status.HTTP_400_BAD_REQUEST)

        soup = BeautifulSoup(response.text, 'html.parser')
        content = [tag.text.strip() for tag in soup.find_all(['p', 'h1', 'h2', 'h3']) if tag.text.strip()]

        if not content:
            return Response({"error": "No content found on the website."}, status=status.HTTP_400_BAD_REQUEST)

        model = SentenceTransformer('all-MiniLM-L6-v2')
        embeddings = model.encode(content, convert_to_tensor=False)
        embeddings = np.array(embeddings)

        index = faiss.IndexFlatL2(embeddings.shape[1])
        index.add(embeddings)

        request.session['content'] = content
        request.session['embeddings'] = embeddings.tolist()

        return Response({"message": "Scraping and indexing completed.", "entries": len(content)}, status=status.HTTP_200_OK)


class SearchView(APIView):
    def post(self, request):
        """
        Endpoint to search content using FAISS.
        """
        query = request.data.get('query')
        top_k = int(request.data.get('top_k', 3))

        content = request.session.get('content')
        embeddings = request.session.get('embeddings')

        if not content or not embeddings:
            return Response({"error": "No scraped content found. Scrape first."}, status=status.HTTP_400_BAD_REQUEST)

        embeddings = np.array(embeddings)
        index = faiss.IndexFlatL2(embeddings.shape[1])
        index.add(embeddings)

        model = SentenceTransformer('all-MiniLM-L6-v2')
        query_embedding = model.encode([query], convert_to_tensor=False)
        distances, indices = index.search(np.array(query_embedding), top_k)

        results = [content[idx] for idx in indices[0]]
        return Response({"query": query, "results": results}, status=status.HTTP_200_OK)
