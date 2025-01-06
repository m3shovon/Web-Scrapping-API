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



# ++++++++++++++++++++++++++++++++++  Updated ++++++++++++++++++++++++++++++++

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from .models import ScrapedData
import requests

class ScrapeWebsiteView(APIView):
    def scrape_website(self, url, visited=None):
        if visited is None:
            visited = set()

        if url in visited or ScrapedData.objects.filter(url=url).exists():
            return []

        visited.add(url)
        scraped_data = []

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            title = soup.title.string if soup.title else "No title"
            content = soup.get_text(strip=True)

            scraped_instance, created = ScrapedData.objects.get_or_create(
                url=url,
                defaults={
                    'title': title,
                    'content': content,
                }
            )

            if created: 
                scraped_data.append({
                    'url': scraped_instance.url,
                    'title': scraped_instance.title,
                    'content': scraped_instance.content,
                })

            for link in soup.find_all('a', href=True):
                next_url = urljoin(url, link['href'])

                if urlparse(next_url).netloc == urlparse(url).netloc:
                    scraped_data.extend(self.scrape_website(next_url, visited))

        except Exception as e:
            print(f"Error scraping {url}: {e}")

        return scraped_data

    def post(self, request):
        url = request.data.get('url')
        if not url:
            return Response({'error': 'URL is required'}, status=status.HTTP_400_BAD_REQUEST)

        scraped_results = self.scrape_website(url)

        if not scraped_results:
            return Response({'message': 'No new data found or unable to scrape the website.'}, status=404)

        return Response({'data': scraped_results}, status=200)


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from .models import ScrapedData


class QueryDataView(APIView):
    """
    View to query specific details of all scraped data based on a keyword or phrase.
    """

    def get(self, request):
        query = request.query_params.get('query')
        if not query:
            return Response({'error': 'Query parameter is required'}, status=400)
        results = ScrapedData.objects.filter(
            Q(content__icontains=query) | Q(title__icontains=query)
        )

        if not results.exists():
            return Response({'message': 'No matching data found'}, status=404)
        detailed_results = []
        for result in results:
            content = result.content
            query_index = content.lower().find(query.lower())

        
            if query_index != -1:
                snippet_start = max(0, query_index - 50)  
                snippet_end = min(len(content), query_index + len(query) + 50) 
                snippet = content[snippet_start:snippet_end].replace('\n', ' ')
            else:
                snippet = "Query found but no snippet available."

            detailed_results.append({
                'id': result.id,
                'title': result.title,
                'url': result.url,
                'snippet': snippet.strip(),
                'scraped_at': result.scraped_at,
                'content_length': len(content), 
            })

        return Response({'query': query, 'results': detailed_results}, status=200)