import time
from pathlib import Path
from pydicom import Dataset
from pynetdicom import AE, evt, StoragePresentationContexts, AllStoragePresentationContexts, build_role
from pynetdicom.sop_class import StudyRootQueryRetrieveInformationModelFind, StudyRootQueryRetrieveInformationModelGet, StudyRootQueryRetrieveInformationModelMove, MRImageStorage
from config.server_config import TelemisConfig
from pynetdicom.pdu_primitives import SCP_SCU_RoleSelectionNegotiation
from pydicom.uid import ExplicitVRLittleEndian
from pynetdicom import AllStoragePresentationContexts, ALL_TRANSFER_SYNTAXES

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



# def test_connection():
#     assoc = TelemisClient.ae.associate(TelemisConfig.HOST, TelemisConfig.PORT)
#     if assoc.is_established:
#         print("Connexion réussie !")
#         assoc.release()
#         return True
#     else:
#         print("Connexion échouée")
#         return False


class TelemisClient:
    def __init__(self):
        Path("tmp").mkdir(exist_ok=True)
        self.ae = AE(ae_title=TelemisConfig.CALLING_AET)
        self.ae.requested_contexts = StoragePresentationContexts[:127]
        self.ae.supported_contexts = AllStoragePresentationContexts
        self.ae.add_requested_context(StudyRootQueryRetrieveInformationModelGet)
        self.ae.add_supported_context(MRImageStorage, ExplicitVRLittleEndian)
        self.role_a = build_role(MRImageStorage, scp_role=True)

    def retrieve_series(self, series_instance_uid, output_dir="tmp"):
        print(f"{PURPLE}RSD appelé {RESET}")
        self.target_series_uid = series_instance_uid
        self.files_received = 0
        ds = Dataset()


        def handle_store(event):
            print(f"{YELLOW} Je suis appelé {RESET}")
            ds = event.dataset
            ds.file_meta = event.file_meta
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
        roles = []
        # for cx in StoragePresentationContexts[:127]:
        #     roles.append(build_role(cx.abstract_syntax, scp_role=True))
        scp = self.ae.start_server(("127.0.0.1", 11112), block = False, evt_handlers=handlers)  
        assoc = self.ae.associate(TelemisConfig.HOST, TelemisConfig.PORT, ae_title=TelemisConfig.CALLED_AET, ext_neg=[self.role_a], evt_handlers=handlers)

        time.sleep(10)
        # scp.shutdown()
        ds.QueryRetrieveLevel = 'SERIES'
        ds.SeriesInstanceUID = series_instance_uid

        if assoc.is_established:
            responses = assoc.send_c_get(ds, StudyRootQueryRetrieveInformationModelGet)
            for status, identifier in responses :
                if status:
                    if status.Status == 0x0000:
                        break
            assoc.release()
            print(f"Récupération terminée: {self.files_received} fichier(s)")
            return self.files_received > 0
        else:
            print("Echec de l'association pour C-GET")
            return False

