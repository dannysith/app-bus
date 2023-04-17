import requests
from datetime import datetime, timedelta
import time
from twilio.rest import Client

# Set up Twilio client for SMS notifications
account_sid = 'AC12bf20ab981be82cea94579e2b39d604'
auth_token = '8bff0ea4cd91f04615d7a1a766fb00b6'
client = Client(account_sid, auth_token)

# Set up VTA API endpoint and headers
url = 'https://api.511.org/transit/vta'
headers = {'Authorization': 'ad537c7947d746f3200bba0db2b4cc5a93710c9020588c34659cf241066da82f'}

# Set up departure time (in HH:MM format)
departure_time = '09:00'

# Set up time interval to check for available schedules (in seconds)
check_interval = 60*5

# Loop to check for available schedules
while True:
    # Get current time
    now = datetime.now().strftime('%H:%M')

    # Check if current time is within 15 minutes of departure time
    if now == departure_time or datetime.strptime(now, '%H:%M') + timedelta(minutes=15) == datetime.strptime(departure_time, '%H:%M'):
        # Make API request for available schedules
        params = {'operator_id': 'VT', 'api_key': 'your_api_key'}
        response = requests.get(url + '/schedules', params=params, headers=headers)

        # Parse response to get best route based on traffic
        schedules = response.json()['data']
        best_route = None
        min_duration = float('inf')
        for schedule in schedules:
            if schedule['attributes']['departure_time'] == departure_time:
                for route in schedule['relationships']['routes']['data']:
                    response = requests.get(url + '/routes/' + route['id'], headers=headers)
                    duration = response.json()['data']['attributes']['travel_time']['duration']
                    if duration < min_duration:
                        best_route = route
                        min_duration = duration

        # Send SMS notification with best route information
        if best_route is not None:
            message = client.messages.create(
                body='Best route for departure at {}: {} ({})'.format(departure_time, best_route['attributes']['long_name'], best_route['attributes']['description']),
                from_='your_twilio_number',
                to='user_phone_number'
            )
            print('Notification sent:', message.sid)

    # Wait for next check interval
    time.sleep(check_interval)
