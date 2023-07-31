import requests
import json

def search_movie(title, release_year, api_key):
    # Set up the base URL and API key
    base_url = 'https://api.themoviedb.org/3/search/movie'

    # Set the query parameters
    params = {
        'api_key': api_key,
        'query': title,
        'year': release_year
    }

    try:
        # Send the GET request
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # Raise an exception if the request fails
        data = response.json()

        if data['total_results']:
            # Retrieve movie id
            i = 0
            for movie in data['results']:
                if movie['title'] == title and movie['popularity'] > 5:
                    movie = data['results'][i]
                    break
                i+=1

            movie_id = movie['id']
            return movie_id
        else:
            print('No movie found with the given title and release year.')

    except requests.exceptions.RequestException as e:
        print('Error:', e)

def get_director_details(movie_id, api_key):
    # Set the query parameters for getting movie credits
    params = {
        'api_key': api_key
    }

    try:
        # Send the GET request to retrieve movie credits
        response = requests.get(f'https://api.themoviedb.org/3/movie/{movie_id}/credits', params=params)
        response.raise_for_status()  # Raise an exception if the request fails
        data = response.json()

        for crew_member in data['crew']:
            if crew_member['job'] == 'Director':
                return crew_member['id'], crew_member['name']

        return None, 'Director Not Found'

    except requests.exceptions.RequestException as e:
        print('Error:', e)

def get_person_image(person_id, api_key):

    # Set the query parameters for getting person details
    params = {
        'api_key': api_key
    }

    try:
        # Send the GET request to retrieve person details
        response = requests.get(f'https://api.themoviedb.org/3/person/{person_id}/images', params=params)
        response.raise_for_status()  # Raise an exception if the request fails
        data = response.json()

        return data['profiles'][0]['file_path']
    except requests.exceptions.RequestException as e:
        print('Error:', e)

def get_details(movie_id, api_key):
    # Set the query parameters for getting movie credits
    params = {
        'api_key': api_key
    }

    try:
        # Send the GET request to retrieve movie credits
        response = requests.get(f'https://api.themoviedb.org/3/movie/{movie_id}', params=params)
        response.raise_for_status()  # Raise an exception if the request fails
        data = response.json()

        runtime = data['runtime']
        language = data['spoken_languages'][0]['english_name']
        genres = []
        for genre in data['genres']:
            genres.append(genre['name'])
        countries = []
        for country in data['production_countries']:
            countries.append(country['name'])
        poster = data['poster_path']
        
        return runtime, language, genres, countries, poster

    except requests.exceptions.RequestException as e:
        print('Error:', e)

def get_director_id(director_name, api_key):
    params = {
        'api_key': api_key,
        'query': director_name,
    }

    response = requests.get('https://api.themoviedb.org/3/search/person', params=params)
    if response.status_code == 200:
        data = response.json()
        results = data.get('results', [])
        for result in results:
            if 'known_for_department' in result and result['known_for_department'] == 'Directing':
                return result['id']
    return None