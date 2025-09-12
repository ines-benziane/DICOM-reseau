from core.get_data import GetData
from core.controller import DicomController
from pynetdicom import debug_logger
from config.server_config import TelemisConfig
from tests.connection import test_connection
from utils.colors import red, green, yellow, blue

debug_logger()
# get_data = GetData("tmp2", TelemisConfig) #Injection manuelle 
# get_data = GetData()

if test_connection():
    print(green( "Test connexion : OK"))

# series_uid = "1.3.12.2.1107.5.2.43.67042.2025090215443836422043221.0.0.0"
# success = get_data.retrieve_series(series_uid)
# print(green("Récupération réussie ! ") if success else red("Échec récupération"))


controller = DicomController("tmp2")
success = controller.get("1.3.12.2.1107.5.2.43.67042.2025090215443836422043221.0.0.0")
print(green("Test récupération : OK") if success else red("Test récuparation : KO "))