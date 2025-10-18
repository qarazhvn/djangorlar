from django.shortcuts import render, redirect
from datetime import datetime
import pytz

# Counter (in memory, resets when server restarts)
counter_value = 0

def home(request):
    return render(request, 'main/home.html')

def users_list(request):
    users = [
        {'full_name': 'Aidar Bek', 'age': 22},
        {'full_name': 'Dana Ali', 'age': 20},
        {'full_name': 'Sanzhar Nur', 'age': 25},
    ]
    return render(request, 'main/users.html', {'users': users})

def city_time(request):
    selected_city = request.GET.get('city', 'Almaty')
    cities = {
        'Almaty': 'Asia/Almaty',
        'Calgary': 'America/Edmonton',
        'Moscow': 'Europe/Moscow',
        'UTC': 'UTC'
    }
    tz = pytz.timezone(cities[selected_city])
    city_time = datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')
    return render(request, 'main/city_time.html', {
        'cities': cities.keys(),
        'selected_city': selected_city,
        'city_time': city_time,
    })

def counter(request):
    global counter_value
    if 'add' in request.GET:
        counter_value += 1
    elif 'reset' in request.GET:
        counter_value = 0
    return render(request, 'main/counter.html', {'counter': counter_value})
