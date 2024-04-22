from ics import Event, Calendar
import datetime
import requests
from bs4 import BeautifulSoup
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import credentials

def main():
    try:
        google_cal = scrape_events()
        add_to_google_calendar(google_cal, credentials.calendar)
        print('Lakepoint Sports events have been added to your Google Calendar!')

    except Exception as error:
        print('Error: ', error)

def scrape_events():
    lakepoint_url = ('https://lakepointsports.com/calendar/')
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    with requests.session() as s: 
        try:
            r = s.get(lakepoint_url, headers=headers)
            soup = BeautifulSoup(r.content, 'html.parser')
            events_scraped = soup.find_all('div', class_='event')
            google_cal = parse_events(events_scraped)

        except Exception as error:
            print('Error: Please try again', error)
            google_cal = []

    return google_cal

def parse_events(events_scraped):
    # Create a calendar
    cal = Calendar()
    # Initialize empty list for google calendar API
    cal_list = []
    
    for event in events_scraped:
        try: 
        date = event.find('span', class_='event-date').text.strip()
        time = event.find('span', class_='event-time').text.strip()
        event_name = event.find('h3', class_='event-title').text.strip()

        start_datetime_str = f'{date} {time.split("-")[0]}'
        end_datetime_str = f'{date} {time.split("-")[1]}'

        start_datetime = datetime.datetime.strptime(start_datetime_str, '%B %d, %Y %I:%M %p')
        end_datetime = datetime.datetime.strptime(end_datetime_str, '%B %d, %Y %I:%M %p')

        e = Event()
        e.name = event_name
        e.begin = start_datetime
        e.end = end_datetime
        e.description = "Event from {} to {}".format(start_time, end_time)

            cal.events.add(e)

            # Add to list formatted for Google Calendar API
            cal_list.append({
                'summary': 'Work Shift',
                'description': f"Shift from {start_time} to {end_time}",
                'start': {
                    'dateTime': f'{start_datetime.isoformat()}-08:00',
                    'timeZone': 'America/Vancouver',
                },
                'end': {
                    'dateTime': f'{end_datetime.isoformat()}-08:00',
                    'timeZone': 'America/Vancouver',
                },
            })

    # Write the calendar to an .ics file
    with open('shifts.ics', 'w') as f:
        f.writelines(cal)
    return cal_list


def add_to_google_calendar(google_cal, cal_id):  
    client_secrets = 'credentials.json'
    scopes = ['https://www.googleapis.com/auth/calendar']

    # Initializing Google Calendar API service
    flow = InstalledAppFlow.from_client_secrets_file(client_secrets, scopes)
    creds = flow.run_local_server(port=0)
    service = build('calendar', 'v3', credentials=creds)

    for event in google_cal:

        try:
                service.events().insert(calendarId=cal_id, body=event).execute()
        
        except Exception as error:
            print(f'Error: ', error)


if __name__ == '__main__':
    main()