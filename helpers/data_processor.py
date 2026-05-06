import pandas as pd
import os

class DataProcessor:
    def __init__(self, bronze_path, silver_path):
        self.bronze_path = bronze_path
        self.silver_path = silver_path

    def process_results(self):
        
        all_dfs = []
        files = [f for f in os.listdir(self.bronze_path) if 'Results' in f]
        
        for file in files:
            df = pd.read_excel(os.path.join(self.bronze_path, file))
            
            # Reparația aici: Scoatem extensia înainte să căutăm cifrele
            file_clean = file.replace('.xlsx', '').replace('.xls', '')
            year = [int(s) for s in file_clean.split() if s.isdigit()][0]
            df['Year'] = year
            
            # Standardizăm coloanele (2023 n-avea Summary)
            if 'Summary (all)' not in df.columns:
                df['Summary (all)'] = None
                
            all_dfs.append(df)
        
        full_results = pd.concat(all_dfs, ignore_index=True)
        # Curățăm Place: dacă e DQ, marcăm clar
        full_results['Place'] = full_results['Place'].astype(str).str.upper()
        return full_results

    def process_athletes(self, results_df):
        """Creează Dim_Athlete și aduce datele din Certifications."""
        # Luăm atleții unici din rezultate
        athletes = results_df[['Code', 'Gender', 'DOB']].drop_duplicates('Code')
        
        # Citim certificările
        cert_path = os.path.join(self.bronze_path, "Thomas More Data Certifications.xlsx")
        certs = pd.read_excel(cert_path)
        
        # Mergem atleții cu certificările (folosind Code/Athlete_Code)
        # Redenumim coloanele ca să fie curate
        certs = certs.rename(columns={'Mental Handicap (SOB has this certificate)': 'Mental_Handicap',
                                     'Unified Partner (SOB has this certificate)': 'Unified_Partner'})
        
        final_athletes = pd.merge(athletes, certs[['Code', 'Mental_Handicap', 'Unified_Partner']], 
                                 on='Code', how='left')
        return final_athletes

    def process_clubs(self):
        """Creează Dim_Club și curăță formatul pivotat."""
        path = os.path.join(self.bronze_path, "Thomas More Data Clubs.xlsx")
        df = pd.read_excel(path)
        
        # Redenumim coloanele principale
        df = df.rename(columns={'Group number': 'Club_ID', 'Name': 'Club_Name'})
        
        # Păstrăm doar datele de referință pentru Dim_Club
        dim_club = df[['Club_ID', 'Club_Name', 'Primary language', 'City', 'Province', 'Country']]
        return dim_club

    def save_to_silver(self, df, name):
        df.to_csv(os.path.join(self.silver_path, f"{name}.csv"), index=False)
        print(f"✅ Saved {name}.csv to Silver")