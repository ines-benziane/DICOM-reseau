from pynetdicom import AE

class TelemisConfig:
    HOST = "192.168.0.172"
    PORT = 7008
    CALLING_AET = "RMN-STATION"
    CALLED_AET = "TELEMISQR"



# Nos données : getscu -aet 
# Mon AET = RMN-STATION
# AETelemis = TELEMISQR
# Je cherche = STUDY 
# La série précisemment (UID) =1.3.12.2.1107.5.2.43.67042.2023112817005239611160766.0.0.1
# Le file destination = tmp 
# L'IP de Telemis = 92.168.0.172 7008
# Ma commande :  python -m pynetdicom getscu -aet RMN-STATION -aec TELEMISQR --study -k 
# QueryRetrieveLevel=STUDY -k SeriesInstanceUID=1.3.12.2.1107.5.2.43.67042.2023112817005239611160766.0.0.1 
# -od tmp 192.168.0.172 7008
