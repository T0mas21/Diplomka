import requests
from bs4 import BeautifulSoup
import json
import time
import os

from Enums.Strategies import ScrapperStrategy


class Scrapper:

    '''
    Create scrapper object for downloading web content
    url: website url
    timeout: after timeout request is canceled
    user_agent: user browser, so scrapper would not be blocked
    strategy: decide which content should be downloaded
    '''
    def __init__(self, url, timeout, user_agent, strategy):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": user_agent
        })

        self.url = url
        self.timeout = timeout
        self.strategy = strategy

        self.html_content = None

        
    def getContentByStrategy(self):
        self.downloadRawContent()
        
        if self.strategy == ScrapperStrategy.EXTRACT_TABLES.value:
            return self.getTable()
        
        elif self.strategy == ScrapperStrategy.EXTRACT_TEXT.value:
            return self.extractText()
        
        elif self.strategy == ScrapperStrategy.DOWNLOAD_FILE.value:
            return self.downloadFile()
        
        else:
            raise ValueError(
                f"Scrapper Error: Unsupported or invalid strategy '{self.strategy}'! "
                f"Supported strategies are: {[s.value for s in ScrapperStrategy]}"
            )
    
    '''
    Download raw web content
    '''
    def downloadRawContent(self):
        response = self.session.get(self.url, timeout=self.timeout)
        response.raise_for_status()
        
        self.html_content = response.text
        return self.html_content
    
    '''
    STRATEGY 1: Exctrat table from downloaded webcontent
    '''
    def getTable(self):
        soup = BeautifulSoup(self.html_content, 'html.parser')
        
        # Find all tables
        all_tables = soup.find_all('table')
        
        if not all_tables:
            # TODO replace print with actual logging
            print("Na stránce nebyla nalezena žádná tabulka.")
            return {}

        parsed_document = {}

        # Iterate trough each table
        for table_index, table in enumerate(all_tables):
            table_id = f"table_{table_index + 1}"
            parsed_document[table_id] = []
            
            rows = table.find_all('tr')
            if not rows:
                continue
                
            # Get columns names
            header_row = rows[0]
            headers = [th.text.strip() for th in header_row.find_all(['th', 'td'])]
            
            # Pojistka: Pokud jsou hlavičky prázdné nebo duplicitní, očíslujeme je
            headers = [headers[i] if headers[i] else f"column_{i+1}" for i in range(len(headers))]
            
            # Iterate trough data rows
            for row in rows[1:]:
                cells = row.find_all('td')
                
                # If row has different number of cells - skip
                if len(cells) != len(headers):
                    continue
                
                row_object = {}
                # Pair cell with corresponding header
                for i in range(len(headers)):
                    column_name = headers[i]
                    cell_value = cells[i].text.strip()
                    
                    # If cell contains link, save the link
                    link = cells[i].find('a')
                    if link and link.get('href'):
                        row_object[f"{column_name}_url"] = link.get('href')
                        
                    row_object[column_name] = cell_value
                
                parsed_document[table_id].append(row_object)
                
        return parsed_document
    
    """
    STRATEGY 2: Extract clean text for AI and RAG pipeline (removes layout ballast)
    """
    def extractText(self):
        if not self.html_content:
            return ""
            
        soup = BeautifulSoup(self.html_content, 'html.parser')
        
        # Remove unwanted HTML elements that contain navigation, styling or scripts
        for element in soup(["script", "style", "nav", "header", "footer", "form", "aside"]):
            element.decompose()
            
        # Get plain text and clean up whitespace chaos
        text = soup.get_text(separator="\n")
        lines = [line.strip() for line in text.splitlines()]
        clean_text = "\n".join([line for line in lines if line])
        
        return clean_text
    
    """
    STRATEGY 3: Download binary files (PDF, DOCX, ZIP) from the gathered links
    """
    def downloadFile(self, target_dir="downloads"):
        # Handles both absolute and relative URLs
        if not self.url.startswith(("http://", "https://")):
            print(f"Invalid or relative URL: {self.url}")
            return None
            
        response = self.session.get(self.url, timeout=self.timeout, stream=True)
        response.raise_for_status()
        
        # Determine the filename from URL
        filename = self.url.split("/")[-1]
        if not filename or "?" in filename:
            filename = f"file_{int(time.time())}.pdf"
            
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
            
        file_path = os.path.join(target_dir, filename)
        
        # Save file in binary chunks (prevents memory overloading for big files)
        with open(file_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                
        return file_path




