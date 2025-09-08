from core.dicom_client import TelemisClient
from pynetdicom import debug_logger
debug_logger()

client = TelemisClient()
# if client.test_connection():
series_uid = "1.3.12.2.1107.5.2.43.67042.2023112817005239611160766.0.0.1"
success = client.retrieve_series(series_uid)
print("Succès !" if success else "Échec récupération")

# if client.test_connection():
#     series_uid = "1.3.12.2.1107.5.2.43.67042.2025090511243140696206469.0.0.0"
#     print(f"Test de find_studies pour la série: {series_uid}")
    
#     studies = client.find_studies(series_uid)  
#     print(f"Nombre d'études trouvées: {len(studies)}")
#     client.test_c_move("1.3.12.2.1107.5.2.43.67042.2025090511243140696206469.0.0.0")
    
    # if studies:
    #     print(f"StudyInstanceUID trouvé: {studies[0].StudyInstanceUID}")
    #     # Puis test du retrieve seulement si find fonctionne
    #     success = client.retrieve_series_direct(series_uid)
    #     print("Succès !" if success else "Échec récupération")
    # else:
    #     print("Aucune étude trouvée - problème avec find_studies")
# else:
#     print("Connexion échouée")