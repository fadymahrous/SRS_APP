import json
import logging
from time import time
from  pathlib import Path
from configparser import ConfigParser
from LxmlRAWParser import LxmlRAWParser
import logging
import pandas as pd
from helper.DBSchema_Handler import DBSchema_Handler


def setup_logger(name, log_file, level=logging.INFO):
    """Setup a custom logger per file."""
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    handler = logging.FileHandler(log_file)        
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    logger.propagate = False  # Important! Prevents duplicate logs

    return logger

# Example usage
logger = setup_logger('module1', 'log\\app.log')

logger.info("This is a log message from module1")

class CleanWiktionaryRawLXML:
    def __init__(self)->None:
        """logger configuration"""
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler = logging.FileHandler('log\\app.log')        
        handler.setFormatter(formatter)
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(handler)
        self.logger.propagate = False  # Important! Prevents duplicate logs

        """Configuration File Setup"""
        configuration_file=Path('config\config.cfg')
        config=ConfigParser()
        try:
            config.read(configuration_file)
            self.wiktionary_raw_file=Path(config['RAW.files.locations']['wiktionaryRAW_de'])
            self.wiktionary_output_raw_file=Path(config['RAW.files.locations']['wiktionaryRAW_de_output'])
        except Exception as e:
            self.logger.exception(f"Configuration File not found, for Details {e}")
            raise e

        if not self.wiktionary_raw_file.exists:
            self.logger.exception('row wiktionary file not exist be sure file exist as per Config.cfg specefied')   
            raise Exception("Row Wiktionary File not Exist")

    def extract_cleandata_from_raw(self):
        self.logger.info("Data Extraction Started")
        startsecond=time()

        with open(self.wiktionary_output_raw_file,'w',encoding="UTF-8") as resultfile:
            try:
                scan_raw_wiktionary=LxmlRAWParser(self.wiktionary_raw_file)
                number_of_records,allrecords_result=scan_raw_wiktionary.extractpages()
            except Exception as e:
                self.logger.exception(f"Tree Scanning Failed in {int(time()-startsecond)} second details: {e}")

            self.logger.info("Data Extraction done now dumping to result.json under output directory specefied in Config.cfg")
            try:
                json.dump(allrecords_result,resultfile,ensure_ascii=False)
            except Exception as e:
                self.logger.exception(f"Json Dump of the file failed after {int(time()-startsecond)} second, details: {e}")

            self.logger.info(f"whole extraction done using lxml in {int(time()-startsecond)} second for {number_of_records} line.")
    
    def load_wiktionary_todatabase(self):
        database_handler=DBSchema_Handler()
        engine,_=database_handler.create_alchemy_engine()

        start=time()
        try:
            wiktionary_data_pd=pd.read_json(self.wiktionary_output_raw_file)
        except Exception as e:
            self.logger.exception(f"Pandas loading, as prepration to DB export failed for Details:{e}")
            raise e
        try:
            #wiktionary_data_pd.to_sql('wiktionary_de_data',engine,index=True,if_exists='append',index_label='id')
            wiktionary_data_pd.to_sql('wiktionary_de_data',engine,index=False,if_exists='append',index_label='word')
        except Exception as e:
            self.logger.exception(f"Actual loadingto Database Failed Details:{e}")
            raise e
        self.logger.info(f"Number of records loaded to the database {int(wiktionary_data_pd.count()['word'])} in {time()-start} seconds")


def main()-> None:
    lxmlmethod=CleanWiktionaryRawLXML()
    lxmlmethod.extract_cleandata_from_raw()
    lxmlmethod.load_wiktionary_todatabase()

if __name__=='__main__':
    main()
