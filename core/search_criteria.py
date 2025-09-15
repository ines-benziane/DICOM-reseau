class SearchCriteria:
    def __init__(self, date=None, patient_name=None, patient_id=None, study_uid=None):
        self.date = date
        self.patient_name = patient_name  
        self.patient_id = patient_id
        self.study_uid = study_uid
        
    def determine_query_level(self):
        """Détermine le niveau DICOM selon les champs remplis"""
        # if self.study_uid:
        #     return "STUDY", "STUDY_ROOT"
        # elif self.patient_id or self.patient_name:
        #     # return "STUDY", "PATIENT_ROOT"  # Cherche studies pour ce patient
        # elif self.date:
        #     return "STUDY", "STUDY_ROOT"   # Cross-patient par date
        # else:
        #     return "PATIENT", "PATIENT_ROOT"  # Liste tous les patients
        return "STUDY", "STUDY_ROOT"