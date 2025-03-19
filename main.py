import os
import logging
import random
import pandas as pd
import numpy as np
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, ConversationHandler

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# States for conversation
CHOOSING_GENRE = 0

def load_movies_data():
    """
    Load movie data directly using original column names from the dataset
    """
    try:
        # Load the dataset
        file_path = 'imdb_movies.csv'
        if not os.path.exists(file_path):
            logger.error(f"Dataset file not found: {file_path}")
            return pd.DataFrame(), []
            
        df = pd.read_csv(file_path)
        
        # Log column names
        logger.info(f"Dataset loaded with columns: {', '.join(df.columns)}")
        
        # Make sure the required columns exist
        required_columns = ['Name', 'Genre']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            logger.error(f"Missing required columns: {', '.join(missing_columns)}")
            return pd.DataFrame(), []
        
        # Clean up data - remove rows with missing values in key columns
        df = df.dropna(subset=required_columns)
        
        # Process Rate column - handle "No Rate" values
        if 'Rate' in df.columns:
            # Replace "No Rate" with NaN
            df['Rate'] = df['Rate'].replace("No Rate", np.nan)
            
            # Convert to numeric and handle errors
            df['Rate'] = pd.to_numeric(df['Rate'], errors='coerce')
            logger.info(f"Processed Rate column. Sample values: {df['Rate'].head()}")
        else:
            logger.warning("'Rate' column not found. Adding placeholder.")
            df['Rate'] = np.nan
        
        # Extract genres from the Genre column
        all_genres = []
        for genres in df['Genre'].str.split(','):
            if isinstance(genres, list):
                all_genres.extend([g.strip() for g in genres])
        
        unique_genres = sorted(list(set([g for g in all_genres if g])))
        logger.info(f"Loaded {len(df)} movies with {len(unique_genres)} unique genres")
        
        return df, unique_genres
        
    except Exception as e:
        logger.error(f"Error loading dataset: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return pd.DataFrame(), []

# Load the dataset
movies_df, available_genres = load_movies_data()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_text(
        f"Hi {user.first_name}! I'm your movie recommendation bot. "
        f"I can help you find great movies to watch based on genres.\n\n"
        f"Use /recommend to get movie recommendations.\n"
        f"Use /genres to see all available genres.\n"
        f"Use /popular to see the most popular movies.\n"
        f"Use /random to get a random movie recommendation."
    )
    return ConversationHandler.END

async def genres_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Display all available genres."""
    if not available_genres:
        await update.message.reply_text("Sorry, I couldn't load the genres. Please try again later.")
        return
    
    genres_text = ", ".join(available_genres)
    await update.message.reply_text(f"Available genres:\n{genres_text}\n\nUse /recommend to get recommendations.")

async def recommend_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start the recommendation process by asking for genre."""
    if movies_df.empty:
        await update.message.reply_text("Sorry, I couldn't load the movie database. Please try again later.")
        return ConversationHandler.END
    
    # Create a keyboard with genre buttons
    keyboard = []
    row = []
    
    for i, genre in enumerate(available_genres):
        row.append(InlineKeyboardButton(genre, callback_data=f"genre_{genre}"))
        
        # Create rows with 3 buttons each
        if (i + 1) % 3 == 0 or i == len(available_genres) - 1:
            keyboard.append(row)
            row = []
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Please select a genre:", reply_markup=reply_markup)
    
    return CHOOSING_GENRE

async def genre_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle the genre selection."""
    query = update.callback_query
    await query.answer()
    
    # Extract the genre from callback data
    genre = query.data.split('_')[1]
    
    # Filter movies by the selected genre
    filtered_movies = movies_df[movies_df['Genre'].str.contains(genre, case=False, na=False)]
    
    if filtered_movies.empty:
        await query.edit_message_text(f"Sorry, no movies found for the genre '{genre}'.")
        return ConversationHandler.END
    
    # Safe separation of rated and unrated movies
    try:
        # Use only valid numeric ratings > 0
        rated_movies = filtered_movies[filtered_movies['Rate'].notna() & (filtered_movies['Rate'] > 0)]
        unrated_movies = filtered_movies[filtered_movies['Rate'].isna() | (filtered_movies['Rate'] <= 0)]
    except Exception as e:
        logger.error(f"Error separating rated/unrated movies: {e}")
        # If there's an error in the filtering, just show all movies without filtering
        rated_movies = pd.DataFrame()
        unrated_movies = filtered_movies
    
    # Sort rated movies by Rate and get top 5
    if not rated_movies.empty:
        try:
            top_rated_movies = rated_movies.sort_values(by='Rate', ascending=False).head(5)
        except Exception as e:
            logger.error(f"Error sorting rated movies: {e}")
            top_rated_movies = rated_movies.head(5)
    else:
        top_rated_movies = pd.DataFrame()
        
    # Get up to 5 unrated movies
    top_unrated_movies = unrated_movies.head(5)
    
    # Create a response message
    response = f"🎬 {genre} Movies Recommendations 🎬\n\n"
    
    # Add rated movies section
    if not top_rated_movies.empty:
        response += "⭐ RATED MOVIES ⭐\n"
        for i, (_, movie) in enumerate(top_rated_movies.iterrows(), 1):
            name = movie['Name']
            date = movie.get('Date', 'N/A')
            rate = movie.get('Rate', 'N/A')
            
            response += f"{i}. {name} ({date})\n"
            response += f"   Rating: {rate}/10\n"
            
            # Add additional info if available
            if 'Certificate' in movie and pd.notna(movie['Certificate']):
                response += f"   Certificate: {movie['Certificate']}\n"
            
            if 'Duration' in movie and pd.notna(movie['Duration']):
                response += f"   Duration: {movie['Duration']}\n"
                
            response += "\n"
    
    # Add unrated movies section
    if not top_unrated_movies.empty:
        response += "📽️ UNRATED MOVIES 📽️\n"
        for i, (_, movie) in enumerate(top_unrated_movies.iterrows(), 1):
            name = movie['Name']
            date = movie.get('Date', 'N/A')
            
            response += f"{i}. {name} ({date})\n"
            
            # Add additional info if available
            if 'Certificate' in movie and pd.notna(movie['Certificate']):
                response += f"   Certificate: {movie['Certificate']}\n"
            
            if 'Duration' in movie and pd.notna(movie['Duration']):
                response += f"   Duration: {movie['Duration']}\n"
                
            response += "\n"
    
    response += "Use /recommend to get more recommendations or /genres to see all genres."
    
    await query.edit_message_text(response)
    return ConversationHandler.END

async def popular_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show the most popular movies overall."""
    if movies_df.empty:
        await update.message.reply_text("Sorry, I couldn't load the movie database. Please try again later.")
        return
    
    try:
        # Filter to only include movies with valid numeric ratings > 0
        rated_movies = movies_df[movies_df['Rate'].notna() & (movies_df['Rate'] > 0)]
        
        if not rated_movies.empty:
            # Sort by Rate
            top_movies = rated_movies.sort_values(by='Rate', ascending=False).head(10)
        else:
            # No rated movies
            await update.message.reply_text("No rated movies found in the database.")
            return
    except Exception as e:
        logger.error(f"Error processing popular movies: {e}")
        await update.message.reply_text("An error occurred while processing popular movies.")
        return
    
    response = "🏆 Top 10 Most Popular Movies 🏆\n\n"
    
    for i, (_, movie) in enumerate(top_movies.iterrows(), 1):
        response += f"{i}. {movie['Name']} ({movie.get('Date', 'N/A')})\n"
        response += f"   Genre: {movie['Genre']}\n"
        response += f"   Rating: {movie.get('Rate', 'N/A')}/10\n\n"
    
    await update.message.reply_text(response)

async def random_movie(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Suggest a random movie."""
    if movies_df.empty:
        await update.message.reply_text("Sorry, I couldn't load the movie database. Please try again later.")
        return
    
    # Get a random movie
    random_index = random.randint(0, len(movies_df) - 1)
    movie = movies_df.iloc[random_index]
    
    response = "🎲 Random Movie Recommendation 🎲\n\n"
    response += f"Title: {movie['Name']} ({movie.get('Date', 'N/A')})\n"
    response += f"Genre: {movie['Genre']}\n"
    
    # Check if movie has valid rating
    if pd.notna(movie.get('Rate')) and movie.get('Rate') > 0:
        response += f"Rating: {movie.get('Rate')}/10\n"
    else:
        response += "Rating: Not available\n"
    
    # Add additional details if available
    if 'Type' in movie and pd.notna(movie['Type']):
        response += f"Type: {movie['Type']}\n"
    
    if 'Certificate' in movie and pd.notna(movie['Certificate']):
        response += f"Certificate: {movie['Certificate']}\n"
    
    if 'Duration' in movie and pd.notna(movie['Duration']):
        response += f"Duration: {movie['Duration']}\n"
    
    # Add content warnings if available
    content_warnings = []
    if 'Violence' in movie and pd.notna(movie['Violence']) and movie['Violence']:
        content_warnings.append(f"Violence: {movie['Violence']}")
    if 'Frightening' in movie and pd.notna(movie['Frightening']) and movie['Frightening']:
        content_warnings.append(f"Frightening: {movie['Frightening']}")
    if 'Profanity' in movie and pd.notna(movie['Profanity']) and movie['Profanity']:
        content_warnings.append(f"Profanity: {movie['Profanity']}")
   
    
    if content_warnings:
        response += "\nContent Warnings:\n"
        response += "\n".join(content_warnings)
        
    response += "\n\nUse /random to get another random movie or /recommend to browse by genre."
    
    await update.message.reply_text(response)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    help_text = """
🤖 Movie Recommendation Bot Commands 🤖

/start - Start the bot
/recommend - Get movie recommendations by genre
/genres - See all available genres
/popular - See the most popular movies
/random - Get a random movie recommendation
/help - Show this help message

Movies are divided into RATED (with numeric ratings) and UNRATED (without ratings or marked as "No Rate") categories.
"""
    await update.message.reply_text(help_text)

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel the conversation."""
    await update.message.reply_text('Operation cancelled. Use /start to begin again.')
    return ConversationHandler.END

def main() -> None:
    """Start the bot."""
    # Create the Application
    application = Application.builder().token("7192054190:AAFAV_IsvSmNBHhgWuh_TWeaTK3V5_jA4cE").build()

    # Add conversation handler for recommendation flow
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("recommend", recommend_command)],
        states={
            CHOOSING_GENRE: [CallbackQueryHandler(genre_selected, pattern=r"^genre_")],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    
    application.add_handler(conv_handler)
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("genres", genres_command))
    application.add_handler(CommandHandler("popular", popular_command))
    application.add_handler(CommandHandler("random", random_movie))
    
    # Start the Bot
    application.run_polling()

if __name__ == "__main__":
    main()
