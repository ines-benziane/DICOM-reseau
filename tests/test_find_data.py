from core.controller import DicomController  
from core.search_criteria import SearchCriteria
from tests.test_connection import test_connection
from utils.colors import red, green, yellow, blue
from pynetdicom import debug_logger

# debug_logger()
# def test_find_logic():
#     """Test la logique SearchCriteria sans connexion PACS"""
#     print(blue("=== Test Find Logic ==="))
    
#     test_cases = [
#         ("Patient search", SearchCriteria(patient_name="MARTIN")),
#         ("Date search", SearchCriteria(date="20250101")), 
#         ("Study UID", SearchCriteria(study_uid="1.2.3.4.5"))
#     ]
    
#     for name, criteria in test_cases:
#         level, model = criteria.determine_query_level()
#         print(yellow(f"  {name}: {model} → {level}"))

def test_find_connection():
    """Test connexion FindData si PACS disponible"""
    if not test_connection():
        print(yellow("Pas de connexion PACS - skip test find"))
        return
        
    controller = DicomController("tmp2")
    try:
        results = controller.find(SearchCriteria(patient_name="DAMELINCOURT^Laurence"))
        print(green(f"Find OK: {len(results)} résultats"))
    except Exception as e:
        print(red(f"Find KO: {e}"))

# if __name__ == "__main__":
#     # test_find_logic()
#     test_find_connection()