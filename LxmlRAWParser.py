from  pathlib import Path
from lxml import etree
import re
from copy import copy
from typing import Tuple, List, Dict

class LxmlRAWParser:
    def __init__(self,path_of_RAW:Path):
        self.path_of_RAW=path_of_RAW

    def extractpages(self)->Tuple[int,List[Dict]]:
        number_of_records=0
        allrecords_result=[]
        """Search for tag anme using {*}<tagname> because wiktionary uses name space in the dump, which is appended to any path"""
        for _,element in etree.iterparse(self.path_of_RAW,tag='{*}page'):
            page=etree.tostring(element, encoding="unicode")
            element.clear()
            record_result={'word':None,'meta':None}
            page_header=re.search(r"<title>(.*?)<\/title>",page)
            record_result['word']=page_header.group(1) if page_header else None
            word_meta_data=re.search('(\{\{Deutsch(.*?)\}\})',page,re.DOTALL)
            record_result['meta']=word_meta_data.group(2) if word_meta_data else None
            if None not in record_result.values():
                allrecords_result.append(copy(record_result))
                number_of_records+=1
        return (number_of_records,allrecords_result)