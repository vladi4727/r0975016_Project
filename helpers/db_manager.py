import pandas as pd
from sqlalchemy import create_engine
import os

class DBManager:
    def __init__(self, user, password, host, database):
        self.connection_string = f"mysql+mysqlconnector://{user}:{password}@{host}/{database}"
        self.engine = create_engine(self.connection_string)

    def upload_to_mysql(self, gold_path):
        """Loads all relational Star Schema CSVs from the Gold layer into MySQL."""
        files = [f for f in os.listdir(gold_path) if f.endswith('.csv')]
        
        for file in files:
            table_name = file.replace('.csv', '')
            df = pd.read_csv(os.path.join(gold_path, file))
            
            # Atomic overwrite to ensure the production warehouse is always clean
            df.to_sql(name=table_name, con=self.engine, if_exists='replace', index=False)
            print(f"✨ Production Table '{table_name}' pushed to MySQL Data Warehouse!")