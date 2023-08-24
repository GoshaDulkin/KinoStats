from concurrent.futures import ThreadPoolExecutor
from api_functions import *
from collections import Counter

def process_csv(reader, API_KEY):
    # Rating and runtime variables
    movie_total, total_rating, total_runtime = 0, 0, 0 

    # Distribution variables
    counts, year_ratings, genre_dist, country_dist, director_dist, language_dist= {}, {}, {}, {}, {}, {}

    # Iterating through csv and making API calls using parallel processing
    with ThreadPoolExecutor() as executor:
        futures = []

        # Iterating over ratings csv and extracting info
        for row in reader:
            name = row[1] 
            year = row[2] 
            rating = float(row[-1]) 

            #API functions
            movie_id = search_movie(name, year, API_KEY)
            if movie_id == None:
                continue
            future_details = executor.submit(get_details, movie_id, API_KEY)
            future_director_details = executor.submit(get_director_details, movie_id, API_KEY)
            futures.append((future_details, future_director_details))

            movie_total += 1
            total_rating += rating
            counts[year] = 1 + counts.get(year, 0)
            year_ratings[year] = rating + year_ratings.get(year, 0)

        for future_details, future_director_details in futures:
            details = future_details.result()
            director_id, director = future_director_details.result()
            if details and director_id and director:
                runtime, language, genres, countries = details

                total_runtime += runtime / 60

                language_dist[language] = 1 + language_dist.get(language, 0)

                for genre in genres:
                    genre_dist[genre] = 1 + genre_dist.get(genre, 0)

                for country in countries:
                    country_dist[country] = 1 + country_dist.get(country, 0)

                director_dist[director] = 1 + director_dist.get(director, 0)

    # Rounding totla_runtime hours
    total_runtime = round(total_runtime)
    
    return counts, year_ratings, movie_total, total_rating, total_runtime, genre_dist, country_dist, director_dist, language_dist

def decade_rating(year_ratings, counts):
    # Decade variables
    decade_counts, decade_ratings, decade_averages = {}, {}, {}

    # Getting average decade rating
    for year, ratings in year_ratings.items():
        decade = (int(year) // 10) * 10
        decade_ratings[decade] = ratings + decade_ratings.get(decade, 0)

    # Getting total movies watched per decade
    for year, movies in counts.items():
        decade = (int(year) // 10) * 10
        decade_counts[decade] = movies + decade_counts.get(decade, 0)
    
    # Calculating decade average rating
    for decade in decade_ratings:
        decade_averages[decade] = decade_ratings[decade] / decade_counts[decade] + decade_averages.get(decade, 0)

    # Best-rated decade
    best_decade = max(decade_averages, key=lambda k: decade_averages[k])
    best_decade_avg = round(decade_averages[best_decade], 2)

    return best_decade, best_decade_avg

def top_directors(director_dist, API_KEY):
    c = Counter(director_dist)
    top_three_directors = c.most_common(3)
    director1, director2, director3 = top_three_directors[0][0], top_three_directors[1][0], top_three_directors[2][0]
    director1count, director2count, director3count = str(top_three_directors[0][1]) + " FILMS", str(top_three_directors[1][1]) + " FILMS", str(top_three_directors[2][1]) + " FILMS"
    director1id, director2id, director3id = get_director_id(director1, API_KEY), get_director_id(director2, API_KEY), get_director_id(director3, API_KEY)
    d1pic, d2pic, d3pic = get_person_image(director1id, API_KEY), get_person_image(director2id, API_KEY), get_person_image(director3id, API_KEY)
    d1pic = "https://image.tmdb.org/t/p/w185" + d1pic
    d2pic = "https://image.tmdb.org/t/p/w185" + d2pic
    d3pic = "https://image.tmdb.org/t/p/w185" + d3pic

    return director1, director2, director3, director1count, director2count, director3count, d1pic, d2pic, d3pic
