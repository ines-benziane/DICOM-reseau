from core.get_data import GetData
from core.controller import DicomController
from pynetdicom import debug_logger
from config.server_config import TelemisConfig
from tests.test_connection import test_connection
from utils.colors import red, green, yellow, blue
from core.search_criteria import SearchCriteria

# debug_logger()

def filter_series_by_description(all_series):
    """Permet de filtrer les séries par description"""
    descriptions = set()
    for serie in all_series:
        desc = serie.get('SeriesDescription', 'N/A')
        if desc != 'N/A':
            descriptions.add(desc)
    
    if not descriptions:
        return all_series
    
    print(f"\n{blue('Available series descriptions:')}")
    unique_descriptions = list(descriptions)
    for idx, desc in enumerate(unique_descriptions, 1):
        count = sum(1 for s in all_series if s.get('SeriesDescription', '') == desc)
        print(f"  [{green(idx)}] {desc} ({count} series)")
    
    print(f"  [{yellow('0')}] Back to study selection") 
    print("\nWhich descriptions do you want to download?")
    selection = input("Enter description numbers (comma-separated, e.g., 1,3) or 0 to go back: ")
    
    if selection.strip() == '0':
        return "BACK"
    
    try:
        indices = [int(x.strip()) - 1 for x in selection.split(',')]
        selected_descriptions = [unique_descriptions[i] for i in indices if 0 <= i < len(unique_descriptions)]
        
        filtered_series = []
        for serie in all_series:
            if serie.get('SeriesDescription', '') in selected_descriptions:
                filtered_series.append(serie)
        
        return filtered_series
        
    except (ValueError, IndexError):
        print(red("Invalid selection, returning all series"))
        return all_series

controller = DicomController("tmp2")
def show_search_menu():
    print("╔══════════════════════════════════════════════════════╗")
    print("║ How would you like to search the data?               ║")
    print("║ Please choose one of the following options:          ║")
    print("║                                                      ║")
    print("║   1 - patient_name                                   ║")
    print("║   2 - patient_id                                     ║")
    print("║   3 - date                                           ║")
    print("║   4 - study_id                                       ║")
    print("╚══════════════════════════════════════════════════════╝")
    return input("> Enter your choice (name or number): ").strip().lower()


def get_search_field():
    options = {
        "1": "patient_name",
        "2": "patient_id",
        "3": "date",
        "4": "study_id",
        "patient_name": "patient_name",
        "patient_id": "patient_id",
        "date": "date",
        "study_id": "study_id"
    }

    while True:
        choice = show_search_menu()
        if choice in options:
            field = options[choice]
            print(f"\n You selected: {field}\n")
            return field
        else:
            print("\nInvalid choice. Please try again.\n")

def main():
    search_field = get_search_field()
    value = input(f"> Enter value for '{search_field}': ").strip()
    criteria_kwargs = {search_field: value}
    criteria = SearchCriteria(**criteria_kwargs)
    print(blue(f"\nSearching for {search_field} = '{value}'...\n"))
    results = controller.find(criteria)

    if not results:
        print(red("No results found."))
        return

    print(green(f"{len(results)} result(s) found:\n"))
    for idx, result in enumerate(results, 1):
        print(f"[{green(idx)}] {result}")

    while True:
        print("\nWhich studies do you want to retrieve?")
        selection = input("Enter index numbers (comma-separated, e.g., 1,3,5): ")
        
        try:
            indices = [int(x.strip()) for x in selection.split(',')]
            selected_studies = controller.select_studies_by_index(indices)
            
            all_series = []
            for study in selected_studies:
                series = controller.get_series_for_study(study.StudyInstanceUID)
                all_series.extend(series)

            filtered_series = filter_series_by_description(all_series)
            
            if filtered_series == "BACK":
                print(yellow("\nReturning to study selection..."))
                continue 
            
            print(f"\n{len(filtered_series)} series selected for download:")
            for serie in filtered_series:
                print(f"  - {serie.get('SeriesDescription', 'N/A')}")
            
            download_choice = input(f"\n{blue('Start download? (y/n): ')}")
            if download_choice.lower() == 'y':
                for serie in filtered_series:
                    anonymise = controller.anonymise()
                    success = controller.get(serie.SeriesInstanceUID)
                    print(green("✓ Downloaded") if success else red("✗ Failed"))
            
            return
                
        except ValueError:
            print(red("Invalid input format, try again"))
    while True: 
        search_field = get_search_field()
        value = input(f"> Enter value for '{search_field}': ").strip()
        criteria_kwargs = {search_field: value}
        criteria = SearchCriteria(**criteria_kwargs)
        print(blue(f"\nSearching for {search_field} = '{value}'...\n"))
        results = controller.find(criteria)

        if not results:
            print(red("No results found."))
            continue 

        print(green(f"{len(results)} result(s) found:\n"))
        for idx, result in enumerate(results, 1):
            print(f"[{green(idx)}] {result}")

        print("\nWhich studies do you want to retrieve?")
        selection = input("Enter index numbers (comma-separated, e.g., 1,3,5): ")
        
        try:
            indices = [int(x.strip()) for x in selection.split(',')]
            selected_studies = controller.select_studies_by_index(indices)
            
            all_series = []
            for study in selected_studies:
                series = controller.get_series_for_study(study.StudyInstanceUID)
                all_series.extend(series)

            while True:
                filtered_series = filter_series_by_description(all_series)
                
                if filtered_series == "BACK":
                    print(yellow("\nReturning to study selection..."))
                    break 
                
                print(f"\n{len(filtered_series)} series selected for download:")
                for serie in filtered_series:
                    print(f"  - {serie.get('SeriesDescription', 'N/A')} (UID: {serie.SeriesInstanceUID})")

                download_choice = input(f"\n{blue('Start download? (y/n): ')}")
                if download_choice.lower() == 'y':
                    for serie in filtered_series:
                        print(f"Downloading {serie.get('SeriesDescription', 'N/A')}...")
                        success = controller.get(serie.SeriesInstanceUID)
                        if success:
                            print(green(f"✓ Downloaded successfully"))
                        else:
                            print(red(f"✗ Download failed"))
                
                return  
                
        except ValueError:
            print(red("Invalid input format"))
            continue

if __name__ == "__main__":
    # test_find_logic()
    # test_find_connection()
    main()