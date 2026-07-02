import os
import json
from fastapi import FastAPI, HTTPException

from Scrapping.ScrapperFactory import ScrapperFactory
from Enums.Strategies import ScrapperStrategy


app = FastAPI()

#CONFIG_DIR = os.path.join(os.path.dirname(__file__), "Config")
CONFIG_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Config"))

class Api():
    
    @app.get("/get-options")
    def get_options():
        result = []
    
        # Iterate trough config dir
        for root, dirs, files in os.walk(CONFIG_DIR):
            
            # Ignore enums
            if "Enums" in root.split(os.sep):
                continue
                
            for file in files:
                # JSON only
                if file.endswith(".json"):
                    file_path = os.path.join(root, file)
                    
                    try:
                        # Open json
                        with open(file_path, "r", encoding="utf-8") as f:
                            data = json.load(f)
                        
                        # Exctract metadata
                        metadata = data.get("metadata", {})
                        
                        # Save the result
                        result.append({
                            "name": metadata.get("name", "Neznámý název"),
                            "description": metadata.get("description", "Bez popisu")
                        })

                    except Exception as e:
                        # TODO replace with actual log
                        # Pokud by byl nějaký soubor poškozený, zaznamenáme chybu a pokračujeme dál
                        result.append({
                            "file_name": file,
                            "error": f"Nepodařilo se načíst soubor: {str(e)}"
                        })
                
        return {"configs": result}
    

    @app.get("/get-content-by-configname")
    def get_by_configname(config_name: str):

        scrapper = ScrapperFactory.createScrapper("Config\\" + config_name + ".json")

        if scrapper is None:
            raise HTTPException(
                status_code=404, 
                detail=f"Configuration name '{config_name}' was not found."
            )
        
        try:            
            result = scrapper.getContentByStrategy()
            return {"status": "success", "data": result}
            
        except ValueError as e:
            # Chytí jak chybu z Enumu (neplatný string), tak z naší metody else větve
            print(f"ERROR: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))

