import requests
import datetime
import pandas as pd

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


def pre_process_wod_intervals(intervals_pd):
    # One hot encode workout_type (1 - 8)
    intervals['workout_type'] = intervals['workout_type'].apply(lambda x: [1 if x == i else 0 for i in range(1, 9)])



    return intervals


def convert_wod_to_df(intervals: str):
    # Convert the wod to a pandas dataframe. If there are multiple intervals, then create a row for each interval (flatten)

    # Turn the WOD json into a dictionary
    intervals_dict = intervals.to_dict()

    # Create a DataFrame from the given data
    df = pd.DataFrame(data)

    # One-hot encode 'workout_type'
    df = pd.get_dummies(df, columns=['workout_type'], prefix='workout_type')

    # Flatten 'intervals' and one-hot encode 'type'
    df = df.explode('intervals', ignore_index=True)
    df = pd.concat([df.drop(['intervals'], axis=1), df['intervals'].apply(pd.Series)], axis=1)
    df = pd.get_dummies(df, columns=['type'], prefix='interval_type')



def get_wod_date_range(start_date, end_date):

    return_list = []
    # Get a list of dates between start_date and end_date
    # Format in yyyy-mm-dd
    start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')

    # Make sure start date is before end date and either today or in the past
    if start_date > datetime.datetime.today():
        raise ValueError('Start date must be today or in the past')
    if start_date > end_date:
        raise ValueError('Start date must be before end date')


    end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')
    date_range = [start_date + datetime.timedelta(days=x) for x in range(0, (end_date-start_date).days)]
    date_range = [date.strftime('%Y-%m-%d') for date in date_range]

    for date in date_range:
        wod = get_wod(date)
        return_list.append(get_wod_intervals(wod))

    return return_list


if __name__ == '__main__':
    # Get todays date
    date = datetime.date.today()
    # Format in yyyy-mm-dd
    date = date.strftime('%Y-%m-%d')
    wod = get_wod(date)
    intervals = get_wod_intervals(wod)
    intervals = pre_process_wod_intervals(intervals)
    print(intervals)