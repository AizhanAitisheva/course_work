# debug_dataset.py
import pandas as pd
import logging
import os

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def debug_dataset(filename='imdb_movies.csv'):
    """
    Debug and print detailed information about the dataset's structure.
    Run this script before running the bot to verify your dataset.
    """
    try:
        if not os.path.exists(filename):
            logger.error(f"File not found: {filename}")
            return
            
        logger.info(f"Reading dataset from {filename}")
        df = pd.read_csv(filename)
        
        # Print basic information
        logger.info(f"Dataset shape: {df.shape}")
        logger.info(f"Columns: {', '.join(df.columns)}")
        
        # Print data types
        logger.info("Column data types:")
        for col, dtype in df.dtypes.items():
            logger.info(f"  {col}: {dtype}")
        
        # Print sample values
        logger.info("Sample values for each column:")
        for col in df.columns:
            sample_values = df[col].dropna().head(3).tolist()
            logger.info(f"  {col}: {sample_values}")
        
        # Check for missing values
        missing_values = df.isnull().sum()
        logger.info("Missing values per column:")
        for col, count in missing_values.items():
            if count > 0:
                logger.info(f"  {col}: {count} missing values")
        
        # Print first few rows
        logger.info("First 3 rows of the dataset:")
        for i, row in df.head(3).iterrows():
            logger.info(f"Row {i}:")
            for col in df.columns:
                logger.info(f"  {col}: {row[col]}")
        
        # If there's a 'Genre' column, analyze the genres
        if 'Genre' in df.columns:
            all_genres = []
            for genres in df['Genre'].str.split(','):
                if isinstance(genres, list):
                    all_genres.extend([g.strip() for g in genres])
            
            unique_genres = sorted(list(set([g for g in all_genres if g])))
            logger.info(f"Unique genres found: {', '.join(unique_genres)}")
            
            # Count genre occurrences
            from collections import Counter
            genre_counts = Counter(all_genres)
            top_genres = genre_counts.most_common(10)
            logger.info("Top 10 genres by frequency:")
            for genre, count in top_genres:
                if genre:  # Only print non-empty genres
                    logger.info(f"  {genre}: {count}")
        
    except Exception as e:
        logger.error(f"Error debugging dataset: {e}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    debug_dataset()
