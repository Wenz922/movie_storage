
import movie_storage_sql as storage
import movies_web_generator as generator
import requests
import statistics
import random
import difflib
from colorama import Fore, Style

from movies_web_generator import write_html_data

OMDB_API_KEY = "ce56738d"
OMDB_URL = "http://www.omdbapi.com/"

HTML_FILE = 'static/index_template.html'

active_user = None

# ------------------- USER MANAGEMENT -------------------
def select_user():
    """Allow the user to select or create a profile."""
    global active_user
    users = storage.list_users()

    print("\nSelect a user:")
    for idx, user in enumerate(users, start=1):
        print(f"{idx}. {user['name']}")
    print(f"{len(users)+1}. Create new user")

    try:
        choice = int(input("Enter choice: "))
        if 1 <= choice <= len(users):
            active_user = users[choice - 1]
            print(Fore.GREEN + f"\nWelcome back, {active_user['name']}!" + Style.RESET_ALL)
        elif choice == len(users) + 1:
            name = input("Enter new username: ").strip()
            if name:
                active_user = storage.create_user(name)
                print(Fore.GREEN + f"\nUser {name} created and logged in!" + Style.RESET_ALL)
            else:
                print(Fore.RED + "Username cannot be empty." + Style.RESET_ALL)
                select_user()
        else:
            print(Fore.RED + "Invalid choice!" + Style.RESET_ALL)
            select_user()
    except ValueError:
        print(Fore.RED + "Invalid input!" + Style.RESET_ALL)
        select_user()


# ------------------- MOVIE COMMANDS -------------------
def list_movies():
    """ Retrieve and display all movies from the database only for the active user."""
    if not active_user:
        print(Fore.RED + "No user logged in!" + Style.RESET_ALL)
        return

    movies = storage.list_movies(active_user["id"])
    if not movies:
        print(Fore.YELLOW + f"\n{active_user['name']}, your movie collection is empty. Add some movies!" + Style.RESET_ALL)
    else:
        print(f"\n{active_user['name']}, you have {len(movies)} movies:")
        for movie, info in movies.items():
            print(f"{movie} ({info['year']}): {info['rating']}")


def add_movie():
    """ Retrieve and add movie to the movie database."""
    if not active_user:
        print(Fore.RED + "No user logged in!" + Style.RESET_ALL)
        return

    movies = storage.list_movies(active_user["id"])
    new_movie_name = input("\nEnter the adding movie name: ").strip()
    if not new_movie_name:
        print(Fore.YELLOW + "Movie name cannot be empty." + Style.RESET_ALL)
        return

    if new_movie_name in movies:
        print(Fore.YELLOW + f"Movie {new_movie_name} already exists in {active_user['name']}'s collection." + Style.RESET_ALL)
        return

    # Fetch from OMDb API
    try:
        res = requests.get(OMDB_URL, params={"apikey": OMDB_API_KEY, "t": new_movie_name})
        res.raise_for_status()  # raises HTTPError if status != 200

        movie_data = res.json()
        if movie_data.get("Response") == "False":
            print(Fore.RED + f"Movie not found: {new_movie_name}" + Style.RESET_ALL)
            return

        movie_title = movie_data.get("Title", new_movie_name)
        movie_year = int(movie_data.get("Year", 0))
        movie_rating = float(movie_data.get("imdbRating", 0)) if movie_data.get("imdbRating") != "N/A" else 0.0
        movie_poster = movie_data.get("Poster", "")

    except requests.exceptions.ConnectionError:
        print(Fore.RED + "Error: Cannot connect to OMDb API. Please check your internet connection." + Style.RESET_ALL)
        return
    except requests.exceptions.Timeout:
        print(Fore.RED + "Error: The OMDb API request timed out." + Style.RESET_ALL)
        return
    except requests.exceptions.HTTPError as e:
        print(Fore.RED + f"HTTP Error: {e}" + Style.RESET_ALL)
        return
    except Exception as e:
        print(Fore.RED + f"Unexpected error fetching data: {e}" + Style.RESET_ALL)
        return

    storage.add_movie(movie_title, movie_year, movie_rating, movie_poster, active_user["id"])
    print(Fore.GREEN + f"Movie '{movie_title}' from OMDb added to {active_user['name']}'s collection!" + Style.RESET_ALL)


def delete_movie():
    """ Retrieve and delete movie from the movie database."""
    if not active_user:
        print(Fore.RED + "No user logged in!" + Style.RESET_ALL)
        return

    movies = storage.list_movies(active_user["id"])
    delete_movie_name = input("\nEnter the deleting movie name: ").strip()
    if not delete_movie_name:
        print(Fore.YELLOW + "Movie name cannot be empty." + Style.RESET_ALL)
        return

    if delete_movie_name in movies:
        storage.delete_movie(delete_movie_name, active_user["id"])
        print(Fore.GREEN + f"Movie {delete_movie_name} deleted from {active_user['name']}'s collection." + Style.RESET_ALL)
    else:
        print(Fore.RED + f"Movie {delete_movie_name} not found in movies database." + Style.RESET_ALL)
    return


def update_movie():
    """ Retrieve and update movie infos of movie database."""
    if not active_user:
        print(Fore.RED + "No user logged in!" + Style.RESET_ALL)
        return

    movies = storage.list_movies(active_user["id"])
    update_movie_name = input("\nEnter movie name: ").strip()

    if not update_movie_name:
        print(Fore.YELLOW + "Movie name cannot be empty." + Style.RESET_ALL)
        return

    if update_movie_name in movies:
        movie_note = input(f"Enter movie note ({update_movie_name}): ").strip()
        storage.update_movie(update_movie_name, movie_note, active_user["id"])
        print(Fore.GREEN + f"Movie {update_movie_name} successfully updated." + Style.RESET_ALL)
    else:
        print(Fore.RED + f"Movie {update_movie_name} not found in movie database." + Style.RESET_ALL)
    return


def movies_stats():
    """ Retrieve and display the average and median rating of the movie database, and its best and worst rating movie(s)."""
    if not active_user:
        print(Fore.RED + "No user logged in!" + Style.RESET_ALL)
        return

    movies = storage.list_movies(active_user["id"])
    if not movies:
        print(Fore.YELLOW + "No movies in the database to calculate stats." + Style.RESET_ALL)
        return

    movies_rating_list = [infos["rating"] for infos in movies.values()]
    average_rating = statistics.mean(movies_rating_list)
    print(Fore.GREEN + f"\nThe average rating in the movies database is {average_rating:.1f}")
    median_rating = statistics.median(movies_rating_list)
    print(f"The median rating in the movies database is {median_rating:.1f}")

    max_rate = max(movies_rating_list)
    min_rate = min(movies_rating_list)
    best_movies = []
    worst_movies = []
    for movie, infos in movies.items():
        for year, rating in infos.items():
            if rating == max_rate:
                best_movies.append(movie)
            if rating == min_rate:
                worst_movies.append(movie)
    print(f"The best movie(s) is/are: {', '.join(best_movies)}")
    print(f"The worst movie(s) is/are: {', '.join(worst_movies)}" + Style.RESET_ALL)


def random_movie():
    """ Retrieve and display a random movie, and its year, and its rating from the movie database."""
    if not active_user:
        print(Fore.RED + "No user logged in!" + Style.RESET_ALL)
        return

    movies = storage.list_movies(active_user["id"])
    if not movies:
        print(Fore.YELLOW + "No movies in the movie database." + Style.RESET_ALL)
        return
    movie, info = random.choice(list(movies.items()))
    print(Fore.GREEN + f"\nThe random movie is: {movie} ({info['year']}): {info['rating']}" + Style.RESET_ALL)


def search_movie():
    """ Retrieve and search the movie database for a movie by its name."""
    if not active_user:
        print(Fore.RED + "No user logged in!" + Style.RESET_ALL)
        return
    movies = storage.list_movies(active_user["id"])

    search_movie_by_name = input("\nEnter movie name: ").strip().lower()
    if not search_movie_by_name:
        print(Fore.YELLOW + "Movie name cannot be empty." + Style.RESET_ALL)
        return
    movie_keys = list(movies.keys())

    # Get fuzzy match
    match = None
    matches = difflib.get_close_matches(search_movie_by_name, [key.lower() for key in movie_keys], n=1, cutoff=0.6)
    if matches:
        match = matches[0]

    for movie, info in movies.items():
        if search_movie_by_name in movie.lower() or (match and match in movie.lower()):
            print(f"{movie} ({info['year']}): {info['rating']}")


def movies_sorted_by_rating():
    """ Retrieve and sort the movies by the rating of the movie."""
    if not active_user:
        print(Fore.RED + "No user logged in!" + Style.RESET_ALL)
        return
    movies = storage.list_movies(active_user["id"])
    sorted_movies = sorted(movies.items(), key=lambda x: x[1]['rating'], reverse=True)
    print(Fore.GREEN + f"\nThe movies sorted by rating are:" + Style.RESET_ALL)
    for movie, info in sorted_movies:
        print(f"{movie} ({info['year']}): {info['rating']}")


def movies_sorted_by_year():
    """
    Restrive and display the movies sorted by year in chronological order,
    asking the user whether latest should come first or last.
    """
    if not active_user:
        print(Fore.RED + "No user logged in!" + Style.RESET_ALL)
        return
    movies = storage.list_movies(active_user["id"])
    if not movies:
        print(Fore.YELLOW + "No movies in the movie database." + Style.RESET_ALL)
        return

    while True:
        sort_choice = input("\nDo you want the latest movies first? (Y/N) ").strip().lower()
        if sort_choice not in ["y", "n"]:
            print(Fore.RED + "Please enter 'Y' or 'N'" + Style.RESET_ALL)
        elif sort_choice == "y":
            sorted_movies = sorted(movies.items(), key=lambda x: x[1]["year"], reverse=True)
            break
        elif sort_choice == "n":
            sorted_movies = sorted(movies.items(), key=lambda x: x[1]["year"], reverse=False)
            break
    for movie, info in sorted_movies:
        print(f"{movie} ({info['year']}): {info['rating']}")


def generate_website():
    """ Restrive movies from database and generate a website with template."""
    if not active_user:
        print(Fore.RED + "No user logged in!" + Style.RESET_ALL)
        return
    movies = storage.list_movies(active_user["id"])
    if not movies:
        print(Fore.YELLOW + f"{active_user['name']}, you have no movies to generate." + Style.RESET_ALL)
        return

    # Open html template file
    html_data = generator.load_html_data(HTML_FILE)
    html_data_updated_title = html_data.replace("__TEMPLATE_TITLE__", f'{active_user["name"]} - Movies Database')

    output = ''
    for movie, infos in movies.items():
        output += generator.serialize_movie(movie, infos)

    new_html_file = f'static/{active_user["name"]}_movies_web.html'
    new_html_data = html_data_updated_title.replace("__TEMPLATE_MOVIE_GRID__", output)
    write_html_data(new_html_file, new_html_data)
    print(Fore.GREEN + f'{active_user["name"]} movies website was generated successfully.' + Style.RESET_ALL)


