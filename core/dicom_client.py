import time
from pathlib import Path
from pynetdicom import AE, evt
from pydicom import Dataset
from config.server_config import TelemisConfig
from pynetdicom.sop_class import StudyRootQueryRetrieveInformationModelFind, StudyRootQueryRetrieveInformationModelGet, StudyRootQueryRetrieveInformationModelMove
from pynetdicom import StoragePresentationContexts
from pynetdicom import AllStoragePresentationContexts

RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
PURPLE = '\033[95m'
CYAN = '\033[96m'
WHITE = '\033[97m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'
RESET = '\033[0m'

class TelemisClient:
    def __init__(self):
        Path("tmp").mkdir(exist_ok=True)
        self.ae = AE(ae_title=TelemisConfig.CALLING_AET)
        self.ae.add_requested_context(StudyRootQueryRetrieveInformationModelFind)
        self.ae.add_requested_context(StudyRootQueryRetrieveInformationModelGet)

        for context in AllStoragePresentationContexts:
            self.ae.add_supported_context(context.abstract_syntax)
        
        for context in StoragePresentationContexts:
            self.ae.add_requested_context(context.abstract_syntax)

        self.ae.acse_timeout = 30
        self.ae.dimse_timeout = 30
        self.ae.network_timeout = 30
        self.ae.maximum_pdu_size = 16382
        
    def test_connection(self):
        assoc = self.ae.associate(TelemisConfig.HOST, TelemisConfig.PORT)
        if assoc.is_established:
            print("Connexion réussie !")
            assoc.release()
            return True
        else:
            print("Connexion échouée")
            return False
   
        
    def retrieve_series_direct(self, series_instance_uid, output_dir="tmp"):
        Path(output_dir).mkdir(exist_ok=True)
        self.target_series_uid = series_instance_uid
        self.files_received = 0
        def handle_store(event):
            print(f"{YELLOW} Je suis appelé {RESET}")
            ds = event.dataset
            if ds.SeriesInstanceUID == self.target_series_uid:
                filename = f"{ds.SOPInstanceUID}.dcm"
                filepath = Path("tmp") / filename
                ds.save_as(filepath, write_like_original=False)
                print(f"Fichier reçu: {filename}")
                self.files_received += 1
            else:
                print(f"Image ignorée (autre série): {ds.SeriesInstanceUID}")
            return 0x0000
    
        
        handlers = [(evt.EVT_C_STORE, handle_store)]  
        scp = self.ae.start_server(("", 0), block=False, evt_handlers=handlers)  
        
        ds = Dataset()
        ds.QueryRetrieveLevel = 'STUDY'
        ds.SeriesInstanceUID = series_instance_uid

        time.sleep(1)
        print(f"{GREEN} 00 {RESET}")
        port = scp.socket.getsockname()[1]
        print(f"SCP écoute sur port: {port}")
        
        
        assoc = self.ae.associate(TelemisConfig.HOST, TelemisConfig.PORT, ae_title=TelemisConfig.CALLED_AET)
        if assoc.is_established:
            responses = assoc.send_c_get(ds, StudyRootQueryRetrieveInformationModelGet)
            print(f"{GREEN} 02 {RESET}")
            for status, identifier in responses :
                if status:
                    print(f"{GREEN} 03 \n {RESET}")
                    print(f"{RED}C-GET Status: 0x{status.Status:04x} {RESET}")
                    if status.Status == 0x0000:
                        print(f"{GREEN} 04 {RESET}")
                        break
            assoc.release()
            print(f"{GREEN} 05 {RESET}")
            print(f"Récupération terminée: {self.files_received} fichier(s)")
            return self.files_received > 0
        else:
            print(f"{GREEN} 04 {RESET}")
            print("Echec de l'association pour C-GET")
            return False

