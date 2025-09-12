from pydicom.datadet import Dataset

from pynetdicom import AE, evt
from pynetdicom.sop_class import PatientRootQueryRetrieveInformationModelFind


class FindData:
    SUCCESS_STATUS = 0x0000
    PENDING_STATUS = 0xFF00

    def __init__(self, criteria, config, ae_factory=None):
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

        
    def _establish_connection(self):
        """Etablir la connexion DICOM"""
        self.assoc = self.ae.associate(
            self.config.HOST,
            self.config.PORT, 
            ae_title=self.config.CALLED_AET, 
            evt_handlers=handlers
        )
        return self.assoc.is_established
    
    def _execute_search(self):
        """Execute le C-FIND et traite les réponses"""
        responses = self.assoc.send_c_find(query_dataset, PatientRootQueryRetrieveInformationModelFind)
        results = []
        
        for status, identifier in responses:
            if status and status.Status == self.PENDING_STATUS:
                if identifier:
                    results.append(identifier)
            elif status and status.Status == self.SUCCESS_STATUS:
                break
        
        self.assoc.release()
        return results


    def handle_find(self, event):
        """Handle C-FIND request event"""
        ds = event.identifier
        instances = []
        fdir = self.output_dir 
        for fpath in os.listdir(fdir):
            instances.append(dcmread(os.path.join(fdir, fpath)))

        if 'QueryRetrieveLevel' not in ds :
            yield 0xC000, None
            return
        
        if ds.QueryRetrieveLevel == "PATIENT":
            if "PatientName" not in ['*', '', '?']:
                matching = [ inst for inst in instances if inst.PatientName == ds.PatientName]
        elif ds.QueryRetrieveLevel == "STUDY"
        elif ds.QueryRetrieveLevel == "SERIES"


    def _build_query_dataset(self):
        """Construit le dataset de requête"""
        ds = Dataset()
        ds.QueryRetrieveLevel = self.criteria_level
        criteria_levels = ["DATE", "PATIENT", "STUDY", "SERIES"]
        match self.criteria_level: 
            case criteria_levels[0]:
                ds.PatientName = ''
                self.criteria_level = "PATIENT"
            case criteria_level[1]:
                ds.PatientName = self.data_given
            case criteria_level[2]:
                ds.PatientName = ''
                ds.StudyInstanceUID = self.target_data_uid
            case criteria_level[3]:
                ds.PatientName = ''
                ds.SeriesInstanceUID = target_data_uid
        return ds

    def _data_uid(self, criteria):
        """Return the data UID link to the criteria"""

    def _criteria_identification(self, criteria) -> str :
        """Identify Query/Retrieve level"""
        criteria_list = ["Date", "Patient name", "Study UID", "Series UID", "Accession number", "Patient name and exam date"]
        match criteria: 
            case criteria[0]:
                self.model = PATIENT
                return "DATE"
            case riteria[1]:
                self.model = PATIENT
                return "PATIENT"
            case criteria[2]:
                self.model = STUDY
                return "STUDY"
            case criteria[3]:
                self.model = SERIES
                return "SERIES"
            

    def search_data(self, criteria):
        """Point d'entrée principal"""
        self.criteria_level = _criteria_identification(criteria)
        self.target_data_uid = criteria_instance_uid()
        
        try:
            if self._establish_connection(self):
                return self._execute_search()
            return False
        except Exception as e:
            logger.error(f"Search failed: {str(e)}")
            return False 
