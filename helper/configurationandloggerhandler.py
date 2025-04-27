import logging
from time import time
from  pathlib import Path
from configparser import ConfigParser

class ConfigurationAndLoggerHandler:
    def __init__(self)->None:
        """Setup a default Hardcoded log for the helper."""
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler = logging.FileHandler('log\\helper.log')        
        handler.setFormatter(formatter)
        self.internallogger = logging.getLogger('Configuration-Logger-help')
        self.internallogger.setLevel(logging.INFO)
        self.internallogger.addHandler(handler)
        self.internallogger.propagate = False  # Important! Prevents duplicate logs

    def read_configuration(self,configuration_section_to_read:str,locationpath='config\\config.cfg'):
        configuration_file=Path(locationpath)
        config=ConfigParser()
        try:
            with open(configuration_file,'r') as conf:
                config.read_file(conf)
        except Exception as e:
            self.internallogger.exception(f"Configuration File not {locationpath} found, for Details {e}")
            raise e
        try:
            self.configurationp_part=config[configuration_section_to_read]
            return self.configurationp_part
        except Exception as e:
            self.internallogger.exception(f"This configuration part provided {configuration_section_to_read} not in condifuration file, Config parser cant find it Details: {e}")
            raise e

    def setup_logger(self,name, log_file, level=logging.INFO):
        """Setup a custom logger per file."""
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        try: 
            log_file=Path(log_file)
            handler = logging.FileHandler(log_file)        
        except Exception as e:
            self.internallogger(f"The log Destination is not right for Details: {e}")
            raise e
        handler.setFormatter(formatter)
        logger = logging.getLogger(name)
        logger.setLevel(level)
        logger.addHandler(handler)
        logger.propagate = False  # Important! Prevents duplicate logs
        return logger
    #logger=setup_logger('UserManagement','UserManagement_API.log')