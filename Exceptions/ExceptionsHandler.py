import json
from fastapi import HTTPException


class ExceptionHandler:
    @staticmethod
    def handleException(e: Exception):

        print(f"ERROR: [{type(e).__name__}] -> {str(e)}")

        match e:
            case FileNotFoundError():
                raise HTTPException(status_code=404, detail=f"Konfigurační soubor nebyl nalezen.")
                
            case json.JSONDecodeError():
                raise HTTPException(status_code=400, detail="Soubor není validní JSON.")
            
            case PermissionError():
                raise ValueError("Server nepovolil zápis souboru.")
                
            case ValueError():
                raise HTTPException(status_code=400, detail=str(e))
                
            case _:
                raise HTTPException(status_code=500, detail="Neočekávaná chyba na serveru.")