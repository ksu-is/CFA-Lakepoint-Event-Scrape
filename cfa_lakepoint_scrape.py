from ics import Event, Calendar
import datetime
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
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
    # Initialize Chrome WebDriver
    service = Service('/Users/joshuamadrigal/Downloads/chromedriver-mac-x64/chromedriver')  # Update with your Chrome WebDriver path
    driver = WebDriver(service=service)

    url = 'https://lakepointsports.com/calendar/'

    # Navigate to the webpage
    driver.get(url)

    # Find all elements with the class name 'event'
    events_scraped = driver.find_elements(By.CLASS_NAME, "event")

    # Parse events using WebDriver methods
    google_cal = parse_events(events_scraped)

    # Close the WebDriver
    driver.quit()

    return google_cal

def parse_events(events_scraped):
    print('Parsing events...', len(events_scraped), events_scraped)
    # Create a calendar
    cal = Calendar()

    cal_list = []

    for event in events_scraped:
        try:
            # Extract event details using WebDriver methods
            date = event.find_element(By.CLASS_NAME, 'day').text.strip()
            day_of_week = event.find_element(By.CLASS_NAME, 'day-of-week').text.strip()
            time = event.find_element(By.CLASS_NAME, 'time').text.strip()
            event_name = event.find_element(By.CLASS_NAME, 'title').text.strip()
            venue = event.find_element(By.CLASS_NAME, 'venue').text.strip().replace('@', '')

            # Format date
            month_year = event.find_element(By.CLASS_NAME, 'date').text.strip()
            start_datetime_str = f"{day_of_week}, {month_year} {time.split('-')[0]}"
            end_datetime_str = f"{day_of_week}, {month_year} {time.split('-')[1]}"

            start_datetime = datetime.datetime.strptime(start_datetime_str, '%a, %b %d %Y %I:%M %p')
            end_datetime = datetime.datetime.strptime(end_datetime_str, '%a, %b %d %Y %I:%M %p')

            e = Event()
            e.name = event_name
            e.begin = start_datetime
            e.end = end_datetime

            cal.events.add(e)

            cal_list.append({
                'summary': event_name,
                'start': {
                    'dateTime': start_datetime.isoformat(),
                    'timeZone': 'America/New_York',
                },
                'end': {
                    'dateTime': end_datetime.isoformat(),
                    'timeZone': 'America/New_York',
                },
                'location': venue
            })
        except Exception as e:
            print('Error occurred during parsing event:', e)

    return cal_list

def add_to_google_calendar(google_cal, cal_id):
    client_secrets = 'credentials.json' 
    scopes = ['https://www.googleapis.com/auth/calendar']

    flow = InstalledAppFlow.from_client_secrets_file(client_secrets, scopes)
    creds = flow.run_local_server(port=0)
    service = build('calendar', 'v3', credentials=creds)

    # Get the calendar ID from credentials.py
    cal_id = credentials.calendar 
    print("Calendar ID:", cal_id)

    for event in google_cal:

        try:
            service.events().insert(calendarId=cal_id, body=event).execute()
        except Exception as error:
            print(f'Error: ', error)

if __name__ == '__main__':
    main()