import requests
import datetime

# url is in format: https://api-v4.concept2.com/wod/yyyy-mm-dd

def get_wod(date):
    url = 'https://api-v4.concept2.com/wod/' + date
    response = requests.get(url)
    return response.json()

def get_wod_intervals(wod):
    intervals = wod['workout']['rowerg']
    # Exclude the 'button_presses' attribute from the intervals
    intervals.pop('button_presses', None)
    return intervals


if __name__ == '__main__':
    # Get todays date
    date = datetime.date.today()
    # Format in yyyy-mm-dd
    date = date.strftime('%Y-%m-%d')
    wod = get_wod(date)
    intervals = get_wod_intervals(wod)
    print(intervals)