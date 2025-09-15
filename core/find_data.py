from pydicom.dataset import Dataset
from .search_criteria import SearchCriteria
from pynetdicom import AE, evt
from pynetdicom.sop_class import (
    PatientRootQueryRetrieveInformationModelFind,
    StudyRootQueryRetrieveInformationModelFind
)
import logging 
from utils.colors import red, green, yellow, blue
from tabulate import tabulate

logger = logging.getLogger(__name__)

class FindData:
    SUCCESS_STATUS = 0x0000
    PENDING_STATUS = 0xFF00
    PATIENT_LEVEL = "PATIENT" 
    STUDY_LEVEL = "STUDY"
    SERIES_LEVEL = "SERIES"

    def __init__(self, config, ae_factory=None):
        self.config = config
        self.ae_factory = ae_factory if ae_factory is not None else self._default_ae_factory
        self._setup_ae()

    def _default_ae_factory(self):
        """Factory par défaut - crée un AE normal"""
        return AE(ae_title=self.config.CALLING_AET)

    def _setup_ae(self):
        """Configure Application Entity"""
        self.ae = self.ae_factory()
        self.ae.add_requested_context(PatientRootQueryRetrieveInformationModelFind)
        self.ae.add_requested_context(StudyRootQueryRetrieveInformationModelFind)
        print(f"Debug: AE configuré avec {len(self.ae.requested_contexts)} contextes")

        
    def _establish_connection(self) -> bool:
        """Etablir la connexion DICOM"""
        self.assoc = self.ae.associate(
            self.config.HOST,
            self.config.PORT, 
            ae_title=self.config.CALLED_AET, 
        )
        return self.assoc.is_established
    
    def _execute_search(self, query_dataset) -> list :
        """Execute le C-FIND et traite les réponses"""
        responses = self.assoc.send_c_find(query_dataset, self.sop_class)
        results = []
        
        results_id = []
        for status, identifier in responses:
            if status and status.Status == self.PENDING_STATUS:
                # if identifier:
                #     results_id.append([
                #     identifier.get('PatientName', 'N/A'),
                #     identifier.get('PatientID', 'N/A'),
                #     identifier.get('StudyDate', 'N/A')
                #     ])
                    results.append(identifier)
            elif status and status.Status == self.SUCCESS_STATUS:
                break
        
        if results_id:
            headers = ['Nom', 'ID Patient', 'Date Étude']
            print(tabulate(results_id, headers=headers))
        self.assoc.release()
        return results


    def _build_query_dataset(self, search_criteria: SearchCriteria, query_level: str):
        """Construit le dataset de requête selon SearchCriteria"""
        ds = Dataset()
        ds.QueryRetrieveLevel = query_level
        
        if search_criteria.patient_id:
            ds.PatientID = search_criteria.patient_id
        else :
            ds.PatientID = ''

        if search_criteria.patient_name:
            ds.PatientName = search_criteria.patient_name
        else:
            ds.PatientName = '' 

        if search_criteria.study_uid:
            ds.StudyInstanceUID = search_criteria.study_uid
        else:
            ds.StudyInstanceUID = '' 
            
        if search_criteria.date:
            ds.StudyDate = search_criteria.date
        else:
            ds.StudyDate = ''
            
        ds.StudyDescription = ''
        ds.PatientID = ds.PatientID if hasattr(ds, 'PatientID') else ''
        
        return ds
    

    def search_data(self, search_criteria: SearchCriteria) -> list:
        """Point d'entrée principal avec SearchCriteria"""
        query_level, info_model = search_criteria.determine_query_level()
        
        if info_model == "PATIENT_ROOT":
            self.sop_class = PatientRootQueryRetrieveInformationModelFind
        else:
            self.sop_class = StudyRootQueryRetrieveInformationModelFind
            
        try:
            if self._establish_connection():
                query_dataset = self._build_query_dataset(search_criteria, query_level)
                return self._execute_search(query_dataset)
            return []
        except Exception as e:
            logger.error(f"Search failed: {str(e)}")
            return []

    def get_series_for_study(self, study_instance_uid, patient_id=None):
        """Récupère toutes les séries d'une étude donnée"""
        ds = Dataset()
        ds.QueryRetrieveLevel = "SERIES"
        ds.StudyInstanceUID = study_instance_uid
        
        ds.SeriesInstanceUID = ''
        ds.SeriesDescription = ''
        ds.SeriesNumber = ''
        ds.Modality = ''
        ds.NumberOfSeriesRelatedInstances = ''
        
        self.sop_class = StudyRootQueryRetrieveInformationModelFind
        
        try:
            if self._establish_connection():
                return self._execute_search(ds)
            return []
        except Exception as e:
            logger.error(f"Series search failed: {str(e)}")
            return []