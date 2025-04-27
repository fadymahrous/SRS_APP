#Create Tabels File Using Sql Alchemy
from sqlalchemy import URL,create_engine,MetaData,Column,Table,Integer,String,Date,ForeignKey,TIMESTAMP,insert
from configparser import ConfigParser
from pathlib import Path
import logging


FORMAT="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(filename='log\\app.log', encoding='utf-8', level=logging.DEBUG,format=FORMAT)

class DBSchema_Handler:
    def __init__(self):
        """Initialize logger"""
        self.logger=logging.getLogger(__name__)

        """Read Configuration File"""
        configuration_file=Path('config\\config.cfg')
        config=ConfigParser()
        try:
            config.read(configuration_file)
            self.database_config=config['databaseconnection']
        except Exception as e:
            self.logger.exception(f"Configuration file not exist for Details:{e}")
            raise e        


    def create_alchemy_engine(self)->create_engine:
        metadata_obj = MetaData()
        url_object = URL.create(
            self.database_config['driver'],
            username=self.database_config['username'],
            password=self.database_config['password'],
            host=self.database_config['host'],
            database=self.database_config['database'])
        
        """Connect tot the Database and test Connection"""
        engine=create_engine(url_object)
        try:
            with engine.connect() as conn:
                self.logger.info(f"Database Connection test Passed, Horray ...")
        except Exception as e:
            self.logger.exception(f"Database Connection Faile for Deatils:{e}")
            raise e
        return engine,metadata_obj


    def createschema(self)->None:
        engine,metadata_obj = self.create_alchemy_engine()
        self.wiktionary_de_data = Table(
            "wiktionary_de_data",
            metadata_obj,
            Column("id", Integer, primary_key=True),
            Column("word", String),
            Column("meta",String),
        )

        self.user_words = Table(
            "user_words",
            metadata_obj,
            Column("user_id", Integer, ForeignKey("user_words.id")),
            Column("word_id", Integer,ForeignKey("wiktionary_de_data.id")),
            Column("last_seen",Date),
            Column("raised_to_user",Integer),
            Column("quality",Integer)

        )

        self.users_authority = Table(
            "users_authority",
            metadata_obj,
            Column("user_id", Integer, primary_key=True),
            Column("username", String),
            Column("email",String),
            Column("password",String),
            Column("group_id",Integer,ForeignKey("groups_authority.id")),
            Column("creation_date",TIMESTAMP),
            Column("last_login",TIMESTAMP),
        )

        self.groups_authority = Table(
            "groups_authority",
            metadata_obj,
            Column("id", Integer, primary_key=True),
            Column("groupname",String),
            Column("group_authority",Integer),
        )
        metadata_obj.create_all(engine)
        try:
            with engine.connect() as conn:
                conn.execute(insert(self.groups_authority).values(id=1, groupname='Default',group_authority=0))
                conn.commit()
        except Exception as e:
            self.logger.exception(f'Cant add default group to the table, this is normal if the user group already exist for Details: {e}')
            raise e

def main()-> None:
    connect_to_db=DBSchema_Handler()
    connect_to_db.createschema()

if __name__=='__main__':
    main()