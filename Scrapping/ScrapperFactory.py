import json

from Scrapping.Scrapper import Scrapper


class ScrapperFactory:

    '''
    Extract information from json config and create scrapper object
    '''
    @staticmethod
    def createScrapper(filename):
        with open(filename, "r", encoding="utf-8") as f:
            config_data = json.load(f)
            
        req_setup = config_data.get("request_config", {})
        url = req_setup.get("url")
        timeout = req_setup.get("timeout", 10)
        
        extractor_setup = config_data.get("data_extractor", {})
        strategy = extractor_setup.get("strategy")

        user_agent = req_setup.get("user_agent", "Mozilla/5.0")
        
        if not url:
            raise ValueError("Factory Error: 'url' is missing in the configuration!")
            
        return Scrapper(url=url, timeout=timeout, user_agent=user_agent, strategy=strategy)
