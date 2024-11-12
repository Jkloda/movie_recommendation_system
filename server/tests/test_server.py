import pytest 
import sys
import datetime
import json
sys.path.append('../')
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_login_success():
    response = client.post(
        'api/login',
        data=json.dumps(dict(
            username='username',
            password='password'
        )),
        content_type='application/json'
    )

    assert response.code == 200

def test_login_fail():
    response = client.post(
        'api/login',
        data=json.dumps(dict(
            username='wrong_username',
            password='password'
        ))
    )

    assert response.code == 401
    assert response.data == b'incorrect username or password'

def test_signup_success():
    dob = datetime.datetime(1992, 06, 26)
    response = client.post(
        'api/signup',
        data=json.dumps(dict(
            username='username',
            password='password',
            email='email@email.com',
            dob=dob,
            phone=07123456789
        )),
        content_type='application/json'
    )
    
    assert response.code == 201
    assert response.data == b'success'   

def test_signup_failed():
    dob = datetime.datetime(1992, 06, 26)
    response = client.post(
        'api/signup',
        data=json.dumps(dict(
            username='username',
            password='password',
            email='email@email.com',
            dob=dob
        )),
        content_type='application/json'
    )
    
    assert response.code == 400
    assert response.data == b'malformed request' 

def test_get_recommendations(client):
    response = client.get('api/recommend')
    response_data = response.data
    movies = json.load(response_data)
    is_movies = True if 'movies' in movies else False
    try:
        movies = movies['movies']
    except:
        pytest.fail('No movies returned')
     
    assert response.status_code == 200
    assert is_movies
    assert len(movies) > 0
