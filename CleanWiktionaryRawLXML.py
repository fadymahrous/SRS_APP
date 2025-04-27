import json
import logging
from time import time
from  pathlib import Path
from configparser import ConfigParser
from LxmlRAWParser import LxmlRAWParser

Format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"

class CleanWiktionaryRawLXML:
    def __init__(self)->None:
        logging.basicConfig(filename='log\\app.log', encoding='utf-8', level=logging.DEBUG,format=Format)
        self.logger=logging.getLogger(__name__)

        configuration_file=Path('Config\config.cfg')
        config=ConfigParser()
        try:
            config.read(configuration_file)
            self.wiktionary_raw_file=Path(config['RAW.files.locations']['wiktionaryRAW_de'])
            self.wiktionary_output_raw_file=Path(config['RAW.files.locations']['wiktionaryRAW_de_output'])
        except Exception as e:
            self.logger(f"Configuration File not found, for Details {e}")
            raise e

        if not self.wiktionary_raw_file.exists:
            self.logger.error('row wiktionary file not exist be sure file exist as per Config.cfg specefied')   
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

def main()-> None:
    lxmlmethod=CleanWiktionaryRawLXML()
    lxmlmethod.extract_cleandata_from_raw()

if __name__=='__main__':
    main()