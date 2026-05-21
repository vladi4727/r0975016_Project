from helpers.data_processor import DataProcessor
from helpers.db_manager import DBManager

def main():
    # 1. Medallion architecture paths configuration
    BRONZE = "data/bronze"
    SILVER = "data/silver"
    GOLD = "data/gold"
    
    # MySQL Database Connection Details
    DB_USER = "root"
    DB_PASS = "parola"  # Replace with your actual database password
    DB_HOST = "localhost"
    DB_NAME = "special_olympics_r0975016"

    # 2. Initialize the ETL Data Processor
    dp = DataProcessor(BRONZE, SILVER, GOLD)
    
    print("--- 🛠️ Starting Medallion ETL Pipeline ---")
    
    # Step A: Bronze -> Silver (Data Cleaning & Consolidation)
    dp.process_bronze_to_silver()
    
    # Step B: Silver -> Gold (Dimensional Modeling / Star Schema)
    dp.build_gold_star_schema()
    
    # Step C: Gold -> MySQL Production Data Warehouse Ingestion
    print("\n--- 🚀 Loading Gold Production Data into MySQL ---")
    try:
        db = DBManager(DB_USER, DB_PASS, DB_HOST, DB_NAME)
        # Upload Gold tables directly into production warehouse
        db.upload_to_mysql(GOLD)
        print("--- ✅ ALL PHASES COMPLETE: Gold Data is Live in MySQL Data Warehouse! ---")
    except Exception as e:
        print(f"--- ❌ MySQL Ingestion Error: {e} ---")

if __name__ == "__main__":
    main()