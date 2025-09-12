from pathlib import Path
from core.get_data import GetData
from config.server_config import TelemisConfig

class DicomController:
    """Controller DICOM pour orchestrer les opérations FIND, SELECT, GET"""
    
    def __init__(self, output_dir="tmp", config=None, get_service=None):
        self.output_dir = output_dir
        self.config = config or TelemisConfig
        self.get_service = get_service or self._create_default_get_service()
        # self.find_service = find_service or self._create_default_find_service()
        
        self._current_search_results = []

    def _create_default_get_service(self):
        """Factory par défaut pour GetData"""
        return GetData(self.output_dir, self.config)
    
    # def _create_default_find_service(self):
    #     """Factory par defaut pour FindData"""
    #     return FindData(self.config)
    
    def get(self, series_uid):
        """C-GET Retrieve Data"""
        return self.get_service.retrieve_data(series_uid)

    # def find(self, criteria):
    #     """C-FIND Search Data"""
    #     return self.find_service.search_data(criteria)
