import logging
import os
import sys
from itunes import iTunesHelper

def setup_logging():
    # Create logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    
    # Create console handler with formatting
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    
    # Add console handler to logger
    logger.addHandler(console_handler)
    
    return logger

def main():
    # Setup logging first
    logger = setup_logging()
    
    # Get current directory
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    logger.info("=== Starting iTunes Helper Script ===")
    logger.info(f"Base Directory: {base_dir}")
    
    try:
        # Create helper with debug logging
        logger.info("Creating iTunesHelper instance...")
        helper = iTunesHelper(base_dir=base_dir, log_level=logging.DEBUG)
        
        # Process songs.json
        logger.info("Starting to process songs.json...")
        result = helper.process_songs_json()
        
        # Check results
        logger.info(f"Processing completed with result: {result}")
            
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}", exc_info=True)
        
    logger.info("=== Script Completed ===")

if __name__ == "__main__":
    main()