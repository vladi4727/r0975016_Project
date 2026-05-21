from helpers.data_processor import DataProcessor
from helpers.db_manager import DBManager

def main():
    # 1. Configurații structură Medallion
    BRONZE = "data/bronze"
    SILVER = "data/silver"
    GOLD = "data/gold"
    
    # DATELE DE CONECTARE MYSQL
    DB_USER = "root"
    DB_PASS = "parola"  # Înlocuiește cu parola ta reală
    DB_HOST = "localhost"
    DB_NAME = "special_olympics_r0975016"

    # 2. Inițializare motor ETL
    dp = DataProcessor(BRONZE, SILVER, GOLD)
    
    print("--- 🛠️ Starting Medallion ETL Pipeline ---")
    
    # Pasul A: Bronze -> Silver (Curățare brută)
    dp.process_bronze_to_silver()
    
    # Pasul B: Silver -> Gold (Modelare Dimensională / Star Schema)
    dp.build_gold_star_schema()
    
    # Pasul C: Gold -> MySQL Production Data Warehouse
    print("\n--- 🚀 Loading Gold Production Data into MySQL ---")
    try:
        db = DBManager(DB_USER, DB_PASS, DB_HOST, DB_NAME)
        # Încărcăm tabelele de tip Gold direct în baza de date
        db.upload_to_mysql(GOLD)
        print("--- ✅ ALL PHASES COMPLETE: Gold Data is Live in MySQL Data Warehouse! ---")
    except Exception as e:
        print(f"--- ❌ MySQL Ingestion Error: {e} ---")

if __name__ == "__main__":
    main()