import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import pdfkit

def crawl_site(start_url, max_pages=50, max_depth=3):
    """
    Crawlt die Website ab der start_url bis zu einer maximalen Anzahl an Seiten (max_pages)
    und bis zu einer maximalen Tiefe (max_depth). Es werden nur interne Seiten (gleiche Domain)
    verfolgt.
    """
    visited = set()
    pages_content = []
    # Queue mit Tupeln: (URL, aktuelle Tiefe)
    queue = [(start_url, 0)]
    domain = urlparse(start_url).netloc

    while queue and len(visited) < max_pages:
        url, depth = queue.pop(0)
        if url in visited or depth > max_depth:
            continue
        try:
            print(f"Crawling (Tiefe {depth}): {url}")
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            visited.add(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Text aus verschiedenen relevanten Tags sammeln.
            # Hier kannst du Tags ergänzen, falls nötig (z.B. auch 'li', 'span', etc.).
            text_elements = soup.find_all(['h1', 'h2', 'h3', 'p', 'div', 'span'])
            # Zusammenführen, dabei überflüssige Leerzeichen entfernen.
            page_text = "\n".join(elem.get_text(strip=True) for elem in text_elements)
            pages_content.append({'url': url, 'text': page_text})
            
            # Falls noch nicht die maximale Tiefe erreicht ist, alle internen Links hinzufügen.
            if depth < max_depth:
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    full_url = urljoin(url, href)
                    # Nur Links der gleichen Domain berücksichtigen
                    if urlparse(full_url).netloc == domain and full_url not in visited:
                        queue.append((full_url, depth + 1))
        except Exception as e:
            print("Fehler beim Abrufen von", url, ":", e)
    return pages_content

def create_pdf_from_crawled_data(crawled_data, pdf_filename):
    """
    Fügt die gesammelten Inhalte in ein HTML-Template ein und wandelt es in ein PDF um.
    """
    html_content = """
    <html>
    <head>
        <meta charset='utf-8'>
        <style>
            body { font-family: Arial, sans-serif; }
            h2 { color: #2E6DA4; }
            pre { white-space: pre-wrap; }
            hr { margin: 20px 0; }
        </style>
    </head>
    <body>
    """
    for page in crawled_data:
        html_content += f"<h2>{page['url']}</h2>"
        html_content += f"<pre>{page['text']}</pre>"
        html_content += "<hr>"
    html_content += "</body></html>"

    # Konfiguration: wkhtmltopdf.exe liegt im selben Ordner.
    config = pdfkit.configuration(wkhtmltopdf="wkhtmltopdf.exe")
    pdfkit.from_string(html_content, pdf_filename, configuration=config)
    print(f"PDF wurde erstellt: {pdf_filename}")

if __name__ == "__main__":
    start_url = "https://www.dubaro.de/"
    # max_pages und max_depth kannst du anpassen, um mehr Seiten bzw. tiefere Ebenen zu crawlen.
    crawled_data = crawl_site(start_url, max_pages=50, max_depth=3)
    create_pdf_from_crawled_data(crawled_data, "dubaro_deep.pdf")
