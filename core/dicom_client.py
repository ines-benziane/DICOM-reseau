from pynetdicom import AE
from pydicom import Dataset
from config.server_config import TelemisConfig
from pynetdicom.sop_class import StudyRootQueryRetrieveInformationModelFind

class TelemisClient:
    def __init__(self):
        self.ae = AE(ae_title=TelemisConfig.CALLING_AET)
        self.ae.add_requested_context(StudyRootQueryRetrieveInformationModelFind)

    def test_connection(self):
        assoc = self.ae.associate(TelemisConfig.HOST, TelemisConfig.PORT)
        if assoc.is_established:
            print("Connexion réussie !")
            assoc.release()
            return True
        else:
            print("Connexion échouée")
            return False
    
    def find_studies(self, series_instance_uid):
        #Creation of the query dataset
        ds = Dataset()
        ds.QueryRetrieveLevel = 'STUDY'
        ds.SeriesInstanceUID = series_instance_uid
        ds.StudyInstanceUID = '' # I only ask for the series of the study, never the patient's name 
        assoc = self.ae.associate(TelemisConfig.HOST, TelemisConfig.PORT)
        if assoc.is_established:
            responses = assoc.send_c_find(ds)
        assoc = self.ae.associate(TelemisConfig.HOST, TelemisConfig.PORT, ae_title=TelemisConfig.CALLED_AET)
        if assoc.is_established:
            responses = assoc.send_c_find(ds, StudyRootQueryRetrieveInformationModelFind)
        
        studies = []
        for status, identifier in responses: