from sqlalchemy import create_engine, text


# Define the database URL
DB_URL = "sqlite:///data/movies.db"

# Create the engine
engine = create_engine(DB_URL, echo=True)

# ------------------- TABLE CREATION -------------------
with engine.begin() as connection:
    connection.execute(text("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
    """))

with engine.begin() as connection:
    connection.execute(text("""
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            year INTEGER NOT NULL,
            rating REAL NOT NULL,
            poster TEXT,
            user_id INTEGER NOT NULL,
            note TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """))


# ------------------- USER FUNCTIONS -------------------
def list_users():
    """ Retrieve all users from the database."""
    with engine.connect() as conn:
        result = conn.execute(text("SELECT id, name FROM users"))
        users = result.fetchall()
        return [{"id": row[0], "name": row[1]} for row in users]


def create_user(name):
    """Create a new user with the given name."""
    with engine.begin() as conn:
        conn.execute(text("INSERT INTO users (name) VALUES (:name)"),
                            {"name": name})
        result = conn.execute(text("SELECT id, name FROM users WHERE name = :name"),
                                    {"name": name})
        row = result.fetchone()
        return {"id": row[0], "name": row[1]}


# ------------------- MOVIE FUNCTIONS -------------------
def list_movies(user_id):
    """Retrieve all movies from the database for a given user_id."""
    with engine.connect() as conn:
        result = conn.execute(text("SELECT title, year, rating, poster, note FROM movies WHERE user_id = :uid"),
                        {"uid": user_id})
        movies = result.fetchall()

    return {row[0]: {"year": row[1], "rating": row[2], "poster": row[3], "note": row[4]} for row in movies}


def add_movie(title, year, rating, poster, user_id):
    """Add a new movie to the database for the given user."""
    with engine.begin() as conn:
        try:
            conn.execute(text("INSERT INTO movies (title, year, rating, poster, user_id) VALUES (:title, :year, :rating, :poster, :uid)"),
                               {"title": title, "year": year, "rating": rating, "poster": poster, "uid": user_id})
        except Exception as e:
            print(f"Error: {e}")


def delete_movie(title, user_id):
    """Delete a movie from the database by movie title for the given user."""
    with engine.begin() as conn:
        try:
            result = conn.execute(text("DELETE FROM movies WHERE title = :title AND user_id = :uid"),
                                        {"title": title, "uid": user_id})
        except Exception as e:
            print(f"Error: {e}")


def update_movie(title, note, user_id):
    """Update a movie's note in the database for the given user."""
    with engine.begin() as conn:
        try:
            result = conn.execute(text("UPDATE movies SET note = :note WHERE title = :title AND user_id = :uid"),
                                        {"title": title, "note": note, "uid": user_id})
        except Exception as e:
            print(f"Error: {e}")
