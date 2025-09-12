from pathlib import Path
from pydicom import Dataset
from pynetdicom import AE, evt, StoragePresentationContexts, AllStoragePresentationContexts, build_role
from pynetdicom.sop_class import StudyRootQueryRetrieveInformationModelGet, MRImageStorage
from pydicom.uid import ExplicitVRLittleEndian
import logging

logger = logging.getLogger(__name__)

class GetData:
    MAX_CONTEXTS = 127
    SUCCESS_STATUS = 0x0000
    QUERY_LEVEL_SERIES = 'SERIES'
    
    def __init__(self, output_dir, config, ae_factory=None):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.config = config
        self.ae_factory = ae_factory if ae_factory is not None else self._default_ae_factory
        self._setup_ae()

    def _default_ae_factory(self):
        """Factory par défaut - crée un AE normal"""
        return AE(ae_title=self.config.CALLING_AET)

    def _setup_ae(self):
        """Configure Application Entity"""
        self.ae = self.ae_factory()
        self.ae.requested_contexts = StoragePresentationContexts[:self.MAX_CONTEXTS]
        self.ae.supported_contexts = AllStoragePresentationContexts
        self.ae.add_requested_context(StudyRootQueryRetrieveInformationModelGet)
        self.ae.add_supported_context(MRImageStorage, ExplicitVRLittleEndian)
        self.role_a = build_role(MRImageStorage, scp_role=True)

    def _handle_store(self, event):
        """Handle incoming DICOM store request"""
        logger.info("Received DICOM image")
        ds = event.dataset
        ds.file_meta = event.file_meta
        
        if ds.SeriesInstanceUID == self.target_series_uid:
            filename = f"{ds.SOPInstanceUID}.dcm"
            self._save_dicom_file(ds, filename)
            self.files_received += 1
        else:
            logger.warning(f"Image ignored (different series): {ds.SeriesInstanceUID}")
        
        return self.SUCCESS_STATUS

    def retrieve_data(self, series_instance_uid):
        """Point d'entrée principal"""
        self.target_series_uid = series_instance_uid
        self.files_received = 0
        
        try:
            if self._establish_connection():
                return self._execute_retrieval()
            return False
        except Exception as e:
            logger.error(f"Retrieval failed: {str(e)}")
            return False

    def _establish_connection(self):
        """Établit la connexion DICOM"""
        handlers = [(evt.EVT_C_STORE, self._handle_store)]
        self.scp = self.ae.start_server(("", 0), block=False, evt_handlers=handlers)
        
        self.assoc = self.ae.associate(
            self.config.HOST, 
            self.config.PORT, 
            ae_title=self.config.CALLED_AET, 
            ext_neg=[self.role_a], 
            evt_handlers=handlers
        )
        return self.assoc.is_established

    def _execute_retrieval(self):
        """Execute le C-GET et traite les réponses"""
        ds = self._build_query_dataset()
        responses = self.assoc.send_c_get(ds, StudyRootQueryRetrieveInformationModelGet)
        
        for status, _ in responses:
            if status and status.Status == self.SUCCESS_STATUS:
                break
        
        self.assoc.release()
        logger.info(f"Retrieval completed: {self.files_received} file(s)")
        return self.files_received > 0

    def _build_query_dataset(self):
        """Construit le dataset de requête"""
        ds = Dataset()
        ds.QueryRetrieveLevel = self.QUERY_LEVEL_SERIES
        ds.SeriesInstanceUID = self.target_series_uid
        return ds

    def _save_dicom_file(self, dataset, filename):
        """Centralise la logique de sauvegarde"""
        filepath = self.output_dir / filename
        dataset.save_as(filepath, write_like_original=False)
        logger.info(f"File received: {filename}")