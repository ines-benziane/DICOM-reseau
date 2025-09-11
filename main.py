from core.get_data import GetData
from pynetdicom import debug_logger
from tests.connection import test_connection
from utils.colors import red, green, yellow, blue

retrieveData = GetData()

if test_connection():
    print(green( "Test connexion OK"))

series_uid = "1.3.12.2.1107.5.2.43.67042.2025090215443836422043221.0.0.0"
success = retrieveData.retrieve_series(series_uid)
print(green("Récupération réussie ! ") if success else red("Échec récupération"))
