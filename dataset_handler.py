# dataset_handler.py
import pandas as pd
import logging
import os

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def process_dataset(input_file='imdb_movies.csv', output_file='movies_data.csv'):
    """
    Process the dataset with the specified column structure.
    
    Args:
        input_file (str): Path to the original dataset
        output_file (str): Path to save the processed dataset
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        logger.info(f"Processing dataset from {input_file}")
        
        # Load the dataset
        df = pd.read_csv(input_file)
        
        # Print all columns to verify structure
        logger.info(f"Dataset loaded with columns: {', '.join(df.columns)}")
        
        # Create a new DataFrame with properly mapped columns
        processed_df = pd.DataFrame()
        
        # Map the columns - IMPORTANT: preserve the original column names
        processed_df['Title'] = df['Name'] if 'Name' in df.columns else "Unknown"
        processed_df['Year'] = df['Date'] if 'Date' in df.columns else "Unknown"
        # Keep the original column name for Rating!
        processed_df['Rate'] = df['Rate'] if 'Rate' in df.columns else 0
        processed_df['Genre'] = df['Genre'] if 'Genre' in df.columns else "Unknown"
        processed_df['Type'] = df['Type'] if 'Type' in df.columns else "Unknown"
        
        # Add content details
        if 'Duration' in df.columns and 'Certificate' in df.columns:
            processed_df['Plot'] = df.apply(
                lambda row: f"{row['Type']} {row['Certificate']} rated, {row['Duration']} duration. " + 
                        f"Content warnings: " +
                        f"{'Violence: ' + str(row['Violence']) if 'Violence' in df.columns and pd.notna(row['Violence']) else ''} " +
                        f"{'Frightening: ' + str(row['Frightening']) if 'Frightening' in df.columns and pd.notna(row['Frightening']) else ''}",
                axis=1
            )
        
        # Clean data - keep rows with essential information
        processed_df = processed_df.dropna(subset=['Title', 'Rate', 'Genre'])
        
        # Save processed dataset
        logger.info(f"Saving processed dataset to {output_file}")
        processed_df.to_csv(output_file, index=False)
        
        logger.info(f"Dataset processed successfully. Total items: {len(processed_df)}")
        return True
        
    except Exception as e:
        logger.error(f"Error processing dataset: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def load_movies_data():
    """
    Load and prepare the movie dataset for the bot.
    
    Returns:
        tuple: (DataFrame of movies, list of available genres)
    """
    try:
        # Check if the processed dataset exists
        if os.path.exists('movies_data.csv'):
            logger.info("Loading existing processed dataset")
            df = pd.read_csv('movies_data.csv')
        else:
            # Check if the original dataset exists
            if os.path.exists('imdb_movies.csv'):
                logger.info("Processing original dataset")
                success = process_dataset()
                if not success:
                    logger.error("Failed to process the dataset")
                    return pd.DataFrame(), []
                df = pd.read_csv('movies_data.csv')
            else:
                logger.error("No dataset file found")
                return pd.DataFrame(), []
        
        # Log all column names to ensure they match what we expect
        logger.info(f"Loaded dataset with columns: {', '.join(df.columns)}")
        
        # Extract genres
        all_genres = []
        for genres in df['Genre'].str.split(','):
            if isinstance(genres, list):
                all_genres.extend([g.strip() for g in genres])
        
        unique_genres = sorted(list(set([g for g in all_genres if g])))
        
        logger.info(f"Dataset loaded successfully with {len(df)} items and {len(unique_genres)} genres")
        return df, unique_genres
        
    except Exception as e:
        logger.error(f"Error loading movie data: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return pd.DataFrame(), []
