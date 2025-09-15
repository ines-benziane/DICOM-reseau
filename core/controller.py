from config.server_config import TelemisConfig
from pathlib import Path
from core.get_data import GetData
from core.find_data import FindData
from core.search_criteria import SearchCriteria 

class DicomController:
    """Controller DICOM pour orchestrer les opérations FIND, SELECT, GET"""
    
    def __init__(self, output_dir="tmp", config=None, get_service=None, find_service=None):
        self.output_dir = output_dir
        self.config = config or TelemisConfig
        self.get_service = get_service or self._create_default_get_service()
        self.find_service = find_service or self._create_default_find_service()
        
        self._current_search_results = []

    def select_studies_by_index(self, indices):
        """Sélectionne des études par numéro d'index"""
        if not self._current_search_results:
            return []
        
        selected_studies = []
        for idx in indices:
            if 1 <= idx <= len(self._current_search_results):
                selected_studies.append(self._current_search_results[idx-1])
            
        return selected_studies

    def _create_default_get_service(self):
        """Factory par défaut pour GetData"""
        return GetData(self.output_dir, self.config)
    
    def _create_default_find_service(self):
        """Factory par defaut pour FindData"""
        return FindData(self.config)
    
    def get(self, series_uid):
        """C-GET Retrieve Data"""
        return self.get_service.retrieve_data(series_uid)

    def find(self, search_criteria: SearchCriteria): 
        """C-FIND Search Data avec SearchCriteria"""
        results = self.find_service.search_data(search_criteria)
        self._current_search_results = results
        return results

    def get_series_for_study(self, study_instance_uid):
        """Récupère les séries d'une étude via FindData"""
        return self.find_service.get_series_for_study(study_instance_uid)

    def download_series(self, series_instance_uid):
        """Télécharge une série via GetData (méthode existante)"""
        return self.get_service.retrieve_data(series_instance_uid)