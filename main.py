from helpers.data_processor import DataProcessor

def main():
    BRONZE = "data/bronze"
    SILVER = "data/silver"
    
    dp = DataProcessor(BRONZE, SILVER)
    
    print("--- Starting ETL Pipeline (Medallion: Bronze -> Silver) ---")
    
    # 1. Fact Results
    results = dp.process_results()
    dp.save_to_silver(results, "fact_results")
    
    # 2. Dim Athlete
    athletes = dp.process_athletes(results)
    dp.save_to_silver(athletes, "dim_athlete")
    
    # 3. Dim Club
    clubs = dp.process_clubs()
    dp.save_to_silver(clubs, "dim_club")
    
    # 4. Dim Sport (Generăm o listă simplă din rezultate)
    sports = results[['Sport']].drop_duplicates().reset_index(drop=True)
    sports['Sport_ID'] = sports.index + 1
    dp.save_to_silver(sports, "dim_sport")

    print("--- Phase 2: Silver Layer Complete! ---")

if __name__ == "__main__":
    main()