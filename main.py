from helpers.data_processor import DataProcessor
from helpers.db_manager import DBManager

def main():
    # 1. Configurații
    BRONZE = "data/bronze"
    SILVER = "data/silver"
    
    # DATELE TALE DE CONECTARE (Pune parola setata la instalare)
    DB_USER = "root"
    DB_PASS = "parola" 
    DB_HOST = "localhost"
    DB_NAME = "special_olympics_r0975016"

    # 2. Pornim motorul de procesare
    dp = DataProcessor(BRONZE, SILVER)
    
    print("--- 🛠️ Starting ETL Pipeline (Bronze -> Silver) ---")
    results = dp.process_results()
    dp.save_to_silver(results, "fact_results")
    
    athletes = dp.process_athletes(results)
    dp.save_to_silver(athletes, "dim_athlete")
    
    clubs = dp.process_clubs()
    dp.save_to_silver(clubs, "dim_club")
    
    # Dim Sport simplu
    sports = results[['Sport']].drop_duplicates().reset_index(drop=True)
    sports['Sport_ID'] = sports.index + 1
    dp.save_to_silver(sports, "dim_sport")

    # 3. 🚀 BONUS: Încărcarea în MySQL (Medallion: Silver -> Gold/Prod)
    print("\n--- 🏗️ Starting Database Ingestion (MySQL Bonus) ---")
    try:
        db = DBManager(DB_USER, DB_PASS, DB_HOST, DB_NAME)
        db.upload_to_mysql(SILVER)
        print("--- ✅ Phase 2 COMPLETE: Data is live in MySQL! ---")
    except Exception as e:
        print(f"--- ❌ MySQL Error: {e} ---")

if __name__ == "__main__":
    main()