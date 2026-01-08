import csv
import logging
import time
from pathlib import Path

from thefuzz import fuzz

from data.movie import Movie
from searcher import SearchBoi

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def get_csv(path: Path):
    with open(path, encoding='utf-8') as f:
        reader = csv.reader(f)
        return [row for row in reader]


def get_fuzzy(movies: list[Movie], title):
    if exists := max(
        (res for res in movies if fuzz.ratio(res.name.lower(), title) > 80),
        key=lambda res: fuzz.ratio(res.name.lower(), title),
        default=None,
    ):
        return exists
    return None


def get_fuzzy_alias(movie_list: list[Movie], title: str):
    best_match: tuple[Movie | None, int] = (None, 0)

    for movie in movie_list:
        if not (best_score := max([fuzz.ratio(alias.lower(), title) for alias in movie.aliases], default=None)):
            continue

        if best_score >= 80 and best_score > best_match[1]:
            best_match = (movie, best_score)
        elif best_score >= 80 and best_score == best_match[1]:
            log.warning(f"{best_match[0]} and {movie} have the same score")
    return best_match[0]


def get_match(movies: list[Movie], title: str):
    for i, result in enumerate(movies):
        if result.name.lower() == title:
            return result
    movie = get_fuzzy(movies, title)
    if not movie:
        movie = get_fuzzy_alias(movies, title)
    return movie


def build_movie_list() -> list[Movie]:
    read = get_csv(Path(__file__).parent / 'utils' / 'moviesheetcsv.csv')
    match_list: list[Movie] = []
    log.info("Began building movie list")
    for name, year, watched in read[1:]:
        name: str = name.lower()
        results: list[Movie] = SearchBoi().search_with_year(movie_name=name, year=year, length=30, watched=watched)
        time.sleep(0.1)

        if not (match := get_match(movies=results, title=name)):
            # log.warning(f"Movie not found for {name}")
            continue

        match_list.append(match)

    log.info(f"Found and built {len(match_list)} movies")

    return match_list


# if __name__ == '__main__':
#     main()
