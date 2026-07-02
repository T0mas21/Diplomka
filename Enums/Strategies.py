from enum import Enum

class ScrapperStrategy(Enum):
    EXTRACT_TABLES = "extract_tables"
    EXTRACT_TEXT = "extract_text"
    DOWNLOAD_FILE = "download_file"

    @classmethod
    def has_value(cls, value: str) -> bool:
        """Helper method to check if a string is a valid strategy."""
        return value in cls._value2member_map_


STRATEGY_DESCRIPTIONS = {
    ScrapperStrategy.EXTRACT_TABLES: "Automatická detekce a extrakce HTML tabulek.",
    ScrapperStrategy.EXTRACT_TEXT: "Extrakce čistého textu ořezaného o HTML balast (pro RAG).",
    ScrapperStrategy.DOWNLOAD_FILE: "Přímé stahování binárních souborů (PDF, DOCX).",
}