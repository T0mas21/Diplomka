import os
import json
from fastapi import FastAPI, HTTPException

from Scrapping.ScrapperFactory import ScrapperFactory
from Enums.Strategies import ScrapperStrategy

from Exceptions.ExceptionsHandler import ExceptionHandler

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
                        ExceptionHandler.handleException(e)
                        
                
        return {"configs": result}
    

    @app.get("/get-content-by-configname")
    def get_by_configname(config_name: str):
        try:
            scrapper = ScrapperFactory.createScrapper(os.path.join("Config", f"{config_name}.json"))

            result = scrapper.getContentByStrategy()
            return {"status": "success", "data": result}
            
        except Exception as e:
            ExceptionHandler.handleException(e)

