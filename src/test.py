import requests
from bottle import route, run, template, request, redirect, static_file, response
from datetime import datetime

API_KEY = '9807fd514bb4de158f6a48b0cdde4960'
BASE_URL = 'http://api.openweathermap.org/data/2.5/weather'

# Serve static files like CSS
@route('/static/css/<filename:path>')
def send_css(filename):
    return static_file(filename, root='./css')


# Serve static images
@route('/static/images/<filename:path>')
def send_images(filename):
    return static_file(filename, root='./images')


@route('/')
def index():
    city = request.query.city or 'Dover, Delaware'
    unit = request.query.unit or 'imperial'
    url = f'{BASE_URL}?q={city}&appid={API_KEY}&units={unit}'
    response = requests.get(url)

    if response.status_code != 200:
        return template('<b>Error: Unable to fetch weather data for {{city}}</b>', city=city)

    weather_data = response.json()

    # Extracting details
    temperature = weather_data['main']['temp']
    humidity = weather_data['main']['humidity']
    weather_description = weather_data['weather'][0]['description']

    # Date and time
    now = datetime.now()
    date = now.strftime('%B %d, %Y')
    time = now.strftime('%I:%M %p')

    svg_url = f"/weather.svg?city={city}&unit={unit}"

    return template('test.tpl', city=city, date=date, time=time,
                    temperature_f=temperature if unit == 'imperial' else None,
                    temperature_c=(temperature if unit == 'metric' else (temperature - 32) * 5 / 9),
                    humidity=humidity,
                    weather_description=weather_description,
                    svg_url=svg_url)

@route('/weather.svg')
def generate_svg():
    cities = ["Seattle", "Chicago", "Los Angeles", "Houston", "Philadelphia"]
    coordinates = {
        "Seattle": (50, 50),
        "Chicago": (250, 80),
        "Los Angeles": (80, 200),
        "Houston": (200, 230),
        "Philadelphia": (350, 100)
    }

    weather_icons = {
        "Clear": "sunny.png",
        "Rain": "rainy.png",
        "Clouds": "cloudy.png",
    }

    weather_details = {}
    for city in cities:
        url = f'{BASE_URL}?q={city}&appid={API_KEY}&units=imperial'
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            condition = data['weather'][0]['main']
            weather_details[city] = {
                "temperature": data['main']['temp'],
                "humidity": data['main']['humidity'],
                "description": data['weather'][0]['description'],
                "icon": weather_icons.get(condition, "default.png")
            }

    # Create SVG content
    svg_content = '''<svg xmlns="http://www.w3.org/2000/svg" width="500" height="300">
        <image href="/static/images/usa_map.png" x="0" y="0" width="500" height="300" />'''

    for city, details in weather_details.items():
        x, y = coordinates[city]
        svg_content += f'''
        <rect x="{x}" y="{y}" width="120" height="80" fill="lightpink" stroke="black" />
        <text x="{x + 10}" y="{y + 20}" font-size="12" fill="black">{city}</text>
        <text x="{x + 10}" y="{y + 40}" font-size="10" fill="black">Temp: {details['temperature']}°F</text>
        <text x="{x + 10}" y="{y + 55}" font-size="10" fill="black">Humidity: {details['humidity']}%</text>
        <image href="/static/images/{details['icon']}" x="{x + 70}" y="{y + 10}" width="30" height="30" />
        '''

    svg_content += '</svg>'

    # Set response headers
    response.content_type = 'image/svg+xml'
    return svg_content

@route('/search', method='POST')
def search():
    city = request.forms.get('city')
    redirect(f'/?city={city}')

# Run the application
run(host='localhost', port=8080, debug=True, reloader=True)