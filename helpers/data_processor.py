import pandas as pd
import os
import re

class DataProcessor:
    def __init__(self, bronze_path, silver_path, gold_path):
        self.bronze_path = bronze_path
        self.silver_path = silver_path
        self.gold_path = gold_path
        
        # Ne asigurăm că folderele există
        os.makedirs(self.silver_path, exist_ok=True)
        os.makedirs(self.gold_path, exist_ok=True)

    def process_bronze_to_silver(self):
        """PHASE 1: Curăță și consolidează datele brute în stratul Silver."""
        print("🧹 Cleaning and consolidating raw data into Silver layer...")
        
        # 1. Consolidare Rezultate
        all_dfs = []
        # Acceptăm și .csv și .xlsx/.xls, indiferent de majuscule/minușcule
        files = [f for f in os.listdir(self.bronze_path) if 'Results' in f and f.lower().endswith(('.csv', '.xlsx', '.xls'))]
        
        for file in files:
            file_path = os.path.join(self.bronze_path, file)
            # Detectăm extensia și citim cu funcția potrivită
            if file.lower().endswith('.csv'):
                df = pd.read_csv(file_path)
            else:
                df = pd.read_excel(file_path)
            
            # Extragere an cu Regex
            year_match = re.search(r'\d{4}', file)
            df['Year'] = int(year_match.group()) if year_match else 2015
            
            if 'Summary (all)' not in df.columns:
                df['Summary (all)'] = None
                
            all_dfs.append(df)
        
        if not all_dfs:
            raise ValueError(f"❌ Nu am găsit niciun fișier de rezultate în {self.bronze_path}. Verifică folderul!")
        
        silver_results = pd.concat(all_dfs, ignore_index=True)
        silver_results['Place'] = silver_results['Place'].astype(str).str.upper().str.strip()
        silver_results.to_csv(os.path.join(self.silver_path, "silver_results.csv"), index=False)
        
        # 2. Curățare Certificări
        cert_files = [f for f in os.listdir(self.bronze_path) if 'Certifications' in f and f.lower().endswith(('.csv', '.xlsx', '.xls'))]
        if cert_files:
            cert_file = cert_files[0]
            cert_path = os.path.join(self.bronze_path, cert_file)
            certs = pd.read_csv(cert_path) if cert_file.lower().endswith('.csv') else pd.read_excel(cert_path)
            certs = certs.rename(columns={
                'Mental Handicap (SOB has this certificate)': 'Mental_Handicap',
                'Unified Partner (SOB has this certificate)': 'Unified_Partner'
            })
            certs.to_csv(os.path.join(self.silver_path, "silver_certifications.csv"), index=False)
        
        # 3. Curățare Cluburi
        club_files = [f for f in os.listdir(self.bronze_path) if 'Clubs' in f and f.lower().endswith(('.csv', '.xlsx', '.xls'))]
        if club_files:
            club_file = club_files[0]
            club_path = os.path.join(self.bronze_path, club_file)
            clubs = pd.read_csv(club_path) if club_file.lower().endswith('.csv') else pd.read_excel(club_path)
            clubs = clubs.rename(columns={'Group number': 'Club_ID', 'Name': 'Club_Name'})
            clubs.to_csv(os.path.join(self.silver_path, "silver_clubs.csv"), index=False)
        
        print("✅ Silver layer built successfully!")

    def build_gold_star_schema(self):
        """PHASE 2: Transformă datele din Silver în modelul Star Schema pentru Gold."""
        print("🏗️ Transforming Silver data into Gold Star Schema...")
        
        results_df = pd.read_csv(os.path.join(self.silver_path, "silver_results.csv"))
        certs_df = pd.read_csv(os.path.join(self.silver_path, "silver_certifications.csv"))
        clubs_df = pd.read_csv(os.path.join(self.silver_path, "silver_clubs.csv"))
        
        # 1. FACT TABLE: fact_results
        fact_results = results_df.copy()
        fact_results.to_csv(os.path.join(self.gold_path, "fact_results.csv"), index=False)
        
        # 2. DIM TABLE: dim_athlete
        athletes = results_df[['Code', 'Gender', 'DOB']].drop_duplicates('Code')
        dim_athlete = pd.merge(athletes, certs_df[['Code', 'Mental_Handicap', 'Unified_Partner']], on='Code', how='left')
        dim_athlete.to_csv(os.path.join(self.gold_path, "dim_athlete.csv"), index=False)
        
        # 3. DIM TABLE: dim_club
        dim_club = clubs_df[['Club_ID', 'Club_Name', 'Primary language', 'City', 'Province', 'Country']]
        dim_club.to_csv(os.path.join(self.gold_path, "dim_club.csv"), index=False)
        
        # 4. DIM TABLE: dim_sport
        sports = results_df[['Sport']].drop_duplicates().reset_index(drop=True)
        sports['Sport_ID'] = sports.index + 1
        sports = sports.rename(columns={'Sport': 'Sport_Name'})
        sports.to_csv(os.path.join(self.gold_path, "dim_sport.csv"), index=False)
        
        print("✅ Gold Star Schema generated successfully inside data/gold/!")