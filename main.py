import subprocess
import sys
from pathlib import Path
from config.server_config import TelemisConfig

class TelemisClient:
    def __init__(self):
        Path("tmp").mkdir(exist_ok=True)
    
    def retrieve_series_subprocess(self, series_instance_uid, output_dir="tmp"):
        """Utilise la CLI getscu via subprocess pour récupérer une série"""
        Path(output_dir).mkdir(exist_ok=True)
        
        # Commande getscu qui fonctionne
        cmd = [
            sys.executable, "-m", "pynetdicom", "getscu",
            "-aet", TelemisConfig.CALLING_AET,
            "-aec", TelemisConfig.CALLED_AET,
            "--study",
            "-k", "QueryRetrieveLevel=STUDY",
            "-k", f"SeriesInstanceUID={series_instance_uid}",
            "-od", output_dir,
            TelemisConfig.HOST,
            str(TelemisConfig.PORT)
        ]
        
        try:
            print(f"Exécution de la commande: {' '.join(cmd)}")
            
            # Exécuter la commande
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60  # timeout de 60 secondes
            )
            
            # Vérifier le résultat
            if result.returncode == 0:
                print("Commande exécutée avec succès")
                print("STDOUT:", result.stdout)
                
                # Compter les fichiers récupérés
                output_path = Path(output_dir)
                files = list(output_path.glob("*.dcm")) + list(output_path.glob("MR.*"))
                print(f"Fichiers récupérés: {len(files)}")
                
                for file in files:
                    print(f"  - {file.name}")
                
                return len(files) > 0
                
            else:
                print(f"Erreur - Code de retour: {result.returncode}")
                print("STDERR:", result.stderr)
                print("STDOUT:", result.stdout)
                return False
                
        except subprocess.TimeoutExpired:
            print("Timeout - La commande a pris trop de temps")
            return False
        except Exception as e:
            print(f"Erreur lors de l'exécution: {e}")
            return False
    
    def retrieve_series_subprocess_verbose(self, series_instance_uid, output_dir="tmp"):
        """Version avec logs détaillés"""
        Path(output_dir).mkdir(exist_ok=True)
        
        cmd = [
            sys.executable, "-m", "pynetdicom", "getscu",
            "-d",  # debug mode
            "-aet", TelemisConfig.CALLING_AET,
            "-aec", TelemisConfig.CALLED_AET,
            "--study",
            "-k", "QueryRetrieveLevel=STUDY",
            "-k", f"SeriesInstanceUID={series_instance_uid}",
            "-od", output_dir,
            TelemisConfig.HOST,
            str(TelemisConfig.PORT)
        ]
        
        try:
            print(f"Exécution avec logs détaillés...")
            
            # Exécuter en temps réel avec affichage des logs
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Afficher les logs en temps réel
            for line in process.stdout:
                print(line.rstrip())
            
            process.wait()
            
            # Compter les fichiers
            output_path = Path(output_dir)
            files = list(output_path.glob("*.dcm")) + list(output_path.glob("MR.*"))
            print(f"\nFichiers récupérés: {len(files)}")
            
            return process.returncode == 0 and len(files) > 0
            
        except Exception as e:
            print(f"Erreur: {e}")
            return False

# Exemple d'utilisation
if __name__ == "__main__":
    client = TelemisClient()
    
    series_uid = "1.3.12.2.1107.5.2.43.67042.2023112817005239611160766.0.0.1"
    
    print("=== Test avec subprocess (simple) ===")
    success = client.retrieve_series_subprocess(series_uid)
    print("Succès !" if success else "Échec")
    
    print("\n=== Test avec subprocess (verbose) ===")
    success = client.retrieve_series_subprocess_verbose(series_uid)
    print("Succès !" if success else "Échec")