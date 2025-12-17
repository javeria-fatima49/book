import logging
import sys
import traceback
from src.main import app
import uvicorn

# Setup logging to see all errors
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    try:
        logger.info("Starting server on http://0.0.0.0:8001")
        uvicorn.run(app, host="0.0.0.0", port=8001, log_level="debug")
    except Exception as e:
        logger.error(f"Error starting server: {e}")
        traceback.print_exc()