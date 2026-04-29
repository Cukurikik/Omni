import urllib.request
import xml.etree.ElementTree as ET

def fetch_arxiv_papers(query="cat:cs.CV", max_results=10):
    url = f"http://export.arxiv.org/api/query?search_query={query}&max_results={max_results}"
    response = urllib.request.urlopen(url)
    data = response.read().decode('utf-8')
    root = ET.fromstring(data)
    
    papers = []
    for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
        title = entry.find('{http://www.w3.org/2005/Atom}title').text
        summary = entry.find('{http://www.w3.org/2005/Atom}summary').text
        papers.append({"title": title.replace('\n', ' '), "summary": summary.replace('\n', ' ')})
        
    return papers
