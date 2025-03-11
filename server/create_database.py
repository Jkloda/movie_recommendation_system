import mysql.connector.pooling
from dotenv import load_dotenv
import pandas as pd
import numpy as np

load_dotenv()
connection_pool = mysql.connector.pooling.MySQLConnectionPool(
    pool_name="moviefinder_pool",
    user=os.getenv('USER'),
    host=os.getenv('HOST'),
    password=os.getenv('PASS'),
    database=os.getenv('DATABASE')
)

def create_movie_table():
    # Set up headers for pulling data, and headers with associated types for populating table
    headers = ["genres", "keywords", "original_title", "overview", "popularity", "release_date", "runtime", "spoken_languages", "title", "cast", "director"]
    headers2 = ["original_title", "overview", "popularity", "release_date", "runtime", "spoken_languages", "title", "director"]
    types = ["TEXT", "TEXT", "FLOAT", "TEXT", "FLOAT", "TEXT", "TEXT", "TEXT"]
    # Read the csv, with desired headers and replace null values
    data = pd.read_csv('../data/movie_dataset.csv', usecols=headers)
    data = data.replace(np.nan, 0)
    # Create header and type string, while converting data values into a tuple
    columns = ", ".join([f"{header} {types[index]}" for index, header in enumerate(headers2)])
    data = [tuple(row) for row in data.values]
    # Create a batch of table creation statements
    create_table_movies = f'CREATE TABLE IF NOT EXISTS movies (id INT AUTO_INCREMENT PRIMARY KEY, {columns});'
    create_table_genres = f'CREATE TABLE IF NOT EXISTS genres (id INT AUTO_INCREMENT PRIMARY KEY, genre TEXT);'
    create_table_keywords = f'CREATE TABLE IF NOT EXISTS keywords (id INT AUTO_INCREMENT PRIMARY KEY, keyword TEXT);'
    create_table_cast = f'CREATE TABLE IF NOT EXISTS actors (id INT AUTO_INCREMENT PRIMARY KEY, actor TEXT);'
    # Create bridge tables 
    create_table_genres_bridge = f'CREATE TABLE IF NOT EXISTS movies_genres (movies_id INT, genres_id INT, PRIMARY KEY (movies_id, genres_id), FOREIGN KEY (movies_id) REFERENCES movies(id) ON DELETE CASCADE, FOREIGN KEY (genres_id) REFERENCES genres(id) ON DELETE CASCADE);'
    create_table_cast_bridge = f'CREATE TABLE IF NOT EXISTS movies_actors (movies_id INT, actors_id INT, PRIMARY KEY (movies_id, actors_id), FOREIGN KEY (movies_id) REFERENCES movies(id) ON DELETE CASCADE, FOREIGN KEY (actors_id) REFERENCES actors(id) ON DELETE CASCADE);'
    create_table_keywords_bridge = f'CREATE TABLE IF NOT EXISTS movies_keywords (movies_id INT, keywords_id INT, PRIMARY KEY (movies_id, keywords_id), FOREIGN KEY (movies_id) REFERENCES movies(id) ON DELETE CASCADE, FOREIGN KEY (keywords_id) REFERENCES keywords(id) ON DELETE CASCADE);'
    # Create a batch of insertion statements
    insert_statement_movies = f'INSERT INTO movies ({", ".join(headers2)}) VALUES (%s ,%s, %s, %s, %s, %s, %s, %s);'
    insert_statement_genres = f'INSERT INTO genres (genre) VALUES (%s);'
    insert_statement_cast = f'INSERT INTO actors (actor) VALUES (%s);'
    insert_statement_keywords = f'INSERT INTO keywords (keyword) VALUES (%s);'
    insert_statement_genres_bridge = f'INSERT INTO movies_genres (movies_id, genres_id) VALUES (%s, %s);'
    insert_statement_cast_bridge = f'INSERT INTO movies_actors (movies_id, actors_id) VALUES (%s, %s);'
    insert_statement_keywords_bridge = f'INSERT INTO movies_keywords (movies_id, keywords_id) VALUES (%s, %s);'
    # Begin by creating the tables
    try: 
        connection = connection_pool.get_connection()
        cursor = connection.cursor()
        cursor.execute(create_table_movies)
        cursor.execute(create_table_genres)
        cursor.execute(create_table_cast)
        cursor.execute(create_table_keywords)
        cursor.execute(create_table_genres_bridge)
        cursor.execute(create_table_cast_bridge)
        cursor.execute(create_table_keywords_bridge)
        # Iterate through the data
        for row in data:
            row = list(row)
            # Extract genres and delete row 
            genre_ids = []
            genres = str(row[0]) if row[0] else ""
            genres_list = genres.split()
            del row[0]
            # Extract cast and delete row
            cast_ids = []
            actors_list = []
            cast = str(row[8]) if row[8] else ""
            cast = cast.split()
            del row[8]
            # Extract keywords and delete row
            keywords_ids = []
            keywords = str(row[0]) if row[0] else ""
            keywords = keywords.split()
            del row[0]
            # Iterate actors list and join firstname to lastname
            i = 0
            while i < (len(cast) - 1):
                actors_list.append(cast[i] + ' ' + cast[i + 1])
                i = i + 2
            # Iterate genre list, check if genre exists save id if it does, insert and get id if it doesn't
            for genre in genres_list:
                select_statement = f'SELECT id FROM genres WHERE genre = %s'
                cursor.execute(select_statement, (genre,))
                genres_id = cursor.fetchone()
                if(genres_id):
                    genre_ids.append(genres_id[0])
                else:
                    cursor.execute(insert_statement_genres, (genre,))
                    row_id = cursor.lastrowid
                    genre_ids.append(row_id)
            # Iterate keywords list, check if keyword exists save id if it does, insert and get id if it doesn't
            for keyword in keywords:
                select_statement = f'SELECT id FROM keywords WHERE keyword = %s'
                cursor.execute(select_statement, (keyword,))
                keyword_id = cursor.fetchone()
                if(keyword_id):
                    keywords_ids.append(keyword_id[0])
                else:
                    cursor.execute(insert_statement_keywords, (keyword,))
                    row_id = cursor.lastrowid
                    keywords_ids.append(row_id)
            # Iterate actors list, check if actor exists save id if they do, insert and get id if they don't
            for member in actors_list:
                select_statement = f'SELECT id FROM actors WHERE actor = %s'
                cursor.execute(select_statement, (member,))
                cast_id = cursor.fetchone()
                if(cast_id):
                    cast_ids.append(cast_id[0])
                else:
                    cursor.execute(insert_statement_cast, (member,))
                    row_id = cursor.lastrowid
                    cast_ids.append(row_id)
            # Insert row data generated from headers list
            cursor.execute(insert_statement_movies, row) 
            movie_id = cursor.lastrowid
            # Insert movie id with genre id into the genre bridge table, if not exists
            for gen_id in genre_ids:
                cursor.execute('SELECT * FROM movies_genres WHERE movies_id = %s and genres_id = %s', (movie_id, gen_id))
                duplicate = cursor.fetchone()
                if(duplicate is None):
                    cursor.execute(insert_statement_genres_bridge, (movie_id, gen_id))
            # Insert keyword id with movie id into the keyword bridge table, if not exists
            for key_id in keywords_ids:
                cursor.execute('SELECT * FROM movies_keywords WHERE movies_id = %s and keywords_id = %s', (movie_id, key_id))
                duplicate = cursor.fetchone()
                if(duplicate is None):
                    cursor.execute(insert_statement_keywords_bridge, (movie_id, key_id))
            # Insert cast id with movie id into the actors bridge table, if not exists
            for cast_id in cast_ids:
                cursor.execute('SELECT * FROM movies_actors WHERE movies_id = %s and actors_id = %s', (movie_id, cast_id))
                duplicate = cursor.fetchone()
                if(duplicate is None):
                    cursor.execute(insert_statement_cast_bridge, (movie_id, cast_id))
        # Commit changes
        connection.commit()
    except Exception as e:
        print(f'error inserting {e}')
    # Close connection and cursor
    finally:
        cursor.close()
        connection.close()

print('beginning to create database, please wait, this can take 5-15 minutes or even longer for a lower spec workstation')
create_movie_table()
print('success, hooray!')