import pandas as pd
from sqlalchemy import create_engine
import os

class DBManager:
    def __init__(self, user, password, host, database):
        self.connection_string = f"mysql+mysqlconnector://{user}:{password}@{host}/{database}"
        self.engine = create_engine(self.connection_string)

    def upload_to_mysql(self, silver_path):
        """Incarca toate CSV-urile din Silver in MySQL."""
        files = [f for f in os.listdir(silver_path) if f.endswith('.csv')]
        
        for file in files:
            table_name = file.replace('.csv', '')
            df = pd.read_csv(os.path.join(silver_path, file))
            
            df.to_sql(name=table_name, con=self.engine, if_exists='replace', index=False)
            print(f"🚀 Table '{table_name}' uploaded to MySQL!")