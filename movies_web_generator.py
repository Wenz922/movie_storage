
def load_html_data(html_file_path):
    """Loads a HTML file."""
    with open(html_file_path, 'r', encoding="utf-8") as handle:
        return handle.read()


def write_html_data(new_file_path, data):
    """Writes a HTML file."""
    with open(new_file_path, 'w', encoding="utf-8") as new_file:
        new_file.write(data)


def serialize_movie(movie_title, movie_info):
    """Serializes a movie for the website."""
    poster = movie_info.get("poster", "")
    year = movie_info.get("year", "Unknown")
    rating = movie_info.get("rating", "N/A")
    note = movie_info.get("note", "")

    output = ''
    output += '<li class="movie">\n'
    output += f'<img class="movie-poster" src="{poster}" alt="{movie_title} poster" title="{note}">\n'
    output += f'<h2 class="movie-title">{movie_title}</h2>\n'
    output += f'<p class="movie-year">{year}</p>\n'
    output += f'<p class="movie-rating">⭐ {rating}</p>\n'
    output += '</li>'
    return output

