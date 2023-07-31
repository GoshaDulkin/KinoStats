from flask import Flask, render_template, request, flash
import os
import zipfile
import io
import csv
from io import BytesIO
from api_functions import *
from processing_functions import *
import plotly.graph_objects as go
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
API_KEY = os.getenv("API_KEY")
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'GET':
        return render_template("home.html")
    
    file = request.files['file']

    # Creating seekable copy of the file 
    zip_data = BytesIO(file.read())

    # Extract the zip file
    try:
        zip_file = zipfile.ZipFile(zip_data, 'r')
        ratings_csv_file = None

        # Searching for user ratings
        for filename in zip_file.namelist():
            if filename.endswith('ratings.csv'):
                ratings_csv_file = zip_file.read(filename)
                break

        if ratings_csv_file:
            csv_data = io.StringIO(ratings_csv_file.decode('utf-8'))
            reader = csv.reader(csv_data)
            next(reader)

            # CSV Processing
            counts, year_ratings, movie_total, total_rating, total_runtime, genre_dist, country_dist, director_dist, language_dist = process_csv(reader, API_KEY)
            
            # Best decade calculation
            best_decade, best_decade_avg = decade_rating(year_ratings, counts)
            
            # Top director details
            director1, director2, director3, director1count, director2count, director3count, d1pic, d2pic, d3pic = top_directors(director_dist, API_KEY)

            # Getting average total rating
            average_rating = round(total_rating / movie_total, 2)

            # Getting total values
            total_languages, total_countries, total_directors = len(language_dist), len(country_dist), len(director_dist)

            # Number of movies watched per year graph
            movie_count = sorted(counts.items())
            m_years, m_counts = zip(*movie_count)
            fig = go.Figure(data=[go.Bar(x=m_years, y=m_counts, marker=dict(color="#84F9B4"))])
            fig.update_layout(xaxis_title="",
                            yaxis_showticklabels=False, 
                            yaxis_showgrid=False,  
                            yaxis_title="",
                            plot_bgcolor='#141414',  
                            paper_bgcolor='#141414',  
                            font=dict(color='white'),
                            margin=dict(t = 15, pad=10),
            )
            fig.update_traces(hovertemplate='Year: %{x} <br>Films: %{y}</b><extra></extra>')
            config= dict(displayModeBar = False)
            movies_html = fig.to_html(full_html=False, default_width='1000px', default_height='400px', config=config)  
            
            # Genre Distribution Graph
            genre_dist = sorted(genre_dist.items(), key=lambda x: x[1])[-10:]
            
            genre, g_counts = zip(*genre_dist)
            gfig = go.Figure(data=[go.Bar(x=g_counts, y=genre, marker=dict(color="#84F9B4"), orientation='h')])
            gfig.update_layout(xaxis_title="", 
                            yaxis_showgrid=False,
                            xaxis_showgrid=False,  
                            yaxis_title="",
                            plot_bgcolor='#141414',  
                            paper_bgcolor='#141414',  
                            font=dict(color='white'),
                            margin=dict(t = 15, pad=10),
            )
            gfig.update_traces(hovertemplate='%{x}</b><extra></extra>')
            config= dict(displayModeBar = False)
            genre_html = gfig.to_html(full_html=False, default_width='450px', default_height='500px', config=config)
            
            # Language Distribution Graph
            language_dist = sorted(language_dist.items(), key=lambda x: x[1])[-10:]
            language, l_counts = zip(*language_dist)
            lfig = go.Figure(data=[go.Bar(x=l_counts, y=language, marker=dict(color="#84F9B4"), orientation='h')])
            lfig.update_layout(xaxis_title="", 
                            yaxis_showgrid=False,
                            xaxis_showgrid=False,  
                            yaxis_title="",
                            plot_bgcolor='#141414',  
                            paper_bgcolor='#141414',  
                            font=dict(color='white'),
                            margin=dict(t=15, pad=10),
            )
            lfig.update_traces(hovertemplate='%{x}</b><extra></extra>')
            config= dict(displayModeBar = False)
            language_html = lfig.to_html(full_html=False, default_width='450px', default_height='500px', config=config)

            # Country Distribution graph
            max_value = max(country_dist.values())
            def get_color(value):
                r = g = 0
                b = int(255 * value / max_value)
                return f'rgb({r}, {g}, {b})'

            graph_countries = list(country_dist.keys())
            country_values = list(country_dist.values())
            colors = [get_color(value) for value in country_values]

            cfig = go.Figure(data=go.Choropleth(
                locations=graph_countries,
                locationmode='country names',
                z=country_values,
                text=graph_countries,
                colorscale=[[0, 'rgb(140, 255, 187)'], [1, 'rgb(71, 255, 147)']],
                showscale=False,  
                marker_line_color='white', 
                hovertemplate='%{text}<br>Films: %{z}<extra></extra>',
            ))
            cfig.update_layout(
                title=None,
                geo=dict(
                    showframe=False,
                    showcoastlines=True,
                    projection_type='natural earth',
                    bgcolor='#141414',
                ),
                margin=dict(l=0, r=0, t=0, b=0),  
                width=1000,  
                height=600, 
                autosize=False,
                paper_bgcolor='#141414',
            )
            config= dict(displayModeBar = False)
            fig.update_traces(hovertemplate='Country: %{locations} <br>Movies: %{z}</b><extra></extra>')
            countries_html = cfig.to_html(config=config)

            return render_template('info.html', 
                                    movie_total=movie_total, 
                                    average_rating=average_rating, 
                                    movie_count=movie_count, 
                                    best_decade=best_decade, 
                                    best_decade_avg=best_decade_avg, 
                                    total_runtime=total_runtime,  
                                    total_countries=total_countries, 
                                    total_directors=total_directors, 
                                    total_languages=total_languages, 
                                    movies_plot=movies_html, 
                                    genre_plot=genre_html, 
                                    language_plot=language_html, 
                                    country_plot=countries_html, 
                                    director1=director1, 
                                    director2=director2, 
                                    director3=director3, 
                                    d1pic=d1pic, 
                                    d2pic=d2pic, 
                                    d3pic=d3pic, 
                                    director1count=director1count, 
                                    director2count=director2count, 
                                    director3count=director3count)

        flash(('No "ratings.csv" file found in the uploaded zip file.', 'error'))
        return render_template('home.html')
    except zipfile.BadZipFile:
        flash(('Invalid zip file.', 'error'))
        return render_template('home.html')

@app.route('/stats')
def info():
    return render_template("info.html")


if __name__ == '__main__':
    app.run(debug=True)