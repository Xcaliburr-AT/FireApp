import random

def generate_mock_weather():
    weather_conditions = ['sunny', 'cloudy', 'rainy', 'stormy']
    weather_data = []

    for i in range(7):
        day_weather = {
            'day': f'Day {i+1}',
            'temperature': random.randint(15, 35),
            'description': random.choice(weather_conditions)
        }
        weather_data.append(day_weather)
    
    return weather_data
