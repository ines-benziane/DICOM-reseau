import logging
from pynetdicom import AE
from config.server_config import TelemisConfig
from core.get_data import GetData
from pynetdicom.sop_class import Verification
from utils.colors import red, green, yellow, blue


logger = logging.getLogger(__name__)

def test_connection():
    """Test connection to Telemis server"""
    try:
        ae = AE()
        ae.add_requested_context(Verification)
        assoc = ae.associate(TelemisConfig.HOST, TelemisConfig.PORT)
        if assoc.is_established:
            logger.info("Connection to Telemis server successful")
            assoc.release()
            return True
    except Exception as e:
        logger.error(f"Connection test failed: {str(e)}")
        return False

