

## Projektstruktur

```plaintext
dubaro-crawler/
├── README.md
├── LICENSE
├── requirements.txt
└── crawl_dubaro_deep.py
```

---

# Dubaro Crawler

Dieses Projekt demonstriert, wie man mit Python eine Website (in diesem Fall [dubaro.de](https://www.dubaro.de/)) rekursiv crawlt und den extrahierten Inhalt in ein PDF-Dokument umwandelt.

## Inhalt

- **Web-Crawling:**  
  Mithilfe von `requests` und `BeautifulSoup` werden interne Seiten (inklusive tiefer liegender Seiten wie Produktdetailseiten und Konfigurationsseiten) abgearbeitet und der relevante Text extrahiert.

- **PDF-Erstellung:**  
  Der gesammelte Text wird in ein HTML-Template eingefügt und mit `pdfkit` (und einer portablen Version von wkhtmltopdf) in ein PDF konvertiert.

## Voraussetzungen

- **Python 3.x**  
- **Virtuelle Umgebung:**  
  Es wird empfohlen, eine virtuelle Umgebung zu nutzen, um alle benötigten Pakete isoliert zu installieren.

- **Benötigte Python-Pakete:**  
  Die notwendigen Pakete sind in `requirements.txt` gelistet:
  - `requests`
  - `beautifulsoup4`
  - `pdfkit`

- **wkhtmltopdf:**  
  pdfkit benötigt das Programm `wkhtmltopdf`.  
  - Wenn du keine Admin-Rechte hast, kannst du die portable Version von wkhtmltopdf verwenden.  
  - Stelle sicher, dass sich `wkhtmltopdf.exe` entweder im gleichen Ordner wie `crawl_dubaro_deep.py` befindet oder passe den Pfad im Code entsprechend an.

## Installation und Ausführung

1. **Repository klonen:**

   ```bash
   git clone https://github.com/dein-benutzername/dubaro-crawler.git
   cd dubaro-crawler

2. **Virtuelle Umgebung erstellen und aktivieren:**

   In Windows CMD:
   ```bash
   python -m venv env
   env\Scripts\activate
   ```
   Oder in PowerShell:
   ```powershell
   python -m venv env
   .\env\Scripts\Activate.ps1
   ```

3. **Abhängigkeiten installieren:**

   ```bash
   pip install -r requirements.txt
   ```

4. **wkhtmltopdf einrichten:**

   - Entpacke die portable Version (z. B. aus einem ZIP- oder 7z-Archiv) und platziere `wkhtmltopdf.exe` in den selben Ordner wie `crawl_dubaro_deep.py`  
     **ODER** passe im Code den Pfad zur `wkhtmltopdf.exe` an.

5. **Crawler ausführen:**

   ```bash
   python crawl_dubaro_deep.py
   ```

   Nach erfolgreicher Ausführung wird ein PDF namens `dubaro_deep.pdf` im Projektordner erstellt.

## Hinweise

- **Rechtliche Aspekte:**  
  Stelle sicher, dass du die Nutzungsbedingungen und die robots.txt von dubaro.de beachtest. Dieses Projekt dient ausschließlich zu Lernzwecken.

- **Erweiterungen:**  
  Das Projekt ist so aufgebaut, dass es mit Parametern wie `max_pages` und `max_depth` konfiguriert werden kann.  
  Du kannst den Code erweitern, um z. B. gezielt nach Produktseiten (mit bestimmten URL-Mustern) zu suchen.

---

## Lizenz

Dieses Projekt ist unter der MIT-Lizenz lizenziert – siehe [LICENSE](LICENSE) für weitere Details.
```

---

## Datei: requirements.txt

```plaintext
requests
beautifulsoup4
pdfkit
```

---

## Datei: crawl_dubaro_deep.py

```python
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
            text_elements = soup.find_all(['h1', 'h2', 'h3', 'p', 'div', 'span'])
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
    crawled_data = crawl_site(start_url, max_pages=50, max_depth=3)
    create_pdf_from_crawled_data(crawled_data, "dubaro_deep.pdf")
```

---

## Zusammenfassung

- **README.md:** Enthält eine Projektbeschreibung, Installationsanweisungen, Nutzungshinweise und rechtliche Hinweise.
- **LICENSE:** Definiert die Lizenz (hier MIT).
- **requirements.txt:** Listet alle benötigten Python-Pakete auf.
- **crawl_dubaro_deep.py:** Das Hauptskript, das den Crawler implementiert, die Inhalte sammelt und in ein PDF umwandelt.


