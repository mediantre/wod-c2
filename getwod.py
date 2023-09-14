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




def convert_wod_to_df(data: dict):
    # Convert the wod to a pandas dataframe. If there are multiple intervals, then create a row for each interval (flatten)

    # One-hot encode 'workout_type'
    workout_type_encoded = [0] * 14
    workout_type_encoded[data['workout_type']] = 1

    # Turn the workout type into a dict
    workout_type_dict = {
        'workout_type_' + str(i): workout_type_encoded[i] for i in range(len(workout_type_encoded))
    }
    # print(workout_type_dict)

    # Create a list to hold interval data
    intervals_data = []

    # Extract interval data into separate columns
    
    # check if there are intervals

    if data.get('intervals') is not None:
        for interval in data['intervals']:
            interval_type = [0, 0, 0]
            interval_type[interval['type']] = 1
            intervals_data.append({
                'duration': interval['duration'],
                'rest_duration': interval['rest_duration'],
                'interval_type_0': interval_type[0],
                'interval_type_1': interval_type[1],
                'interval_type_2': interval_type[2],

                # Optional attributes below

                'target_pace': interval.get('target_pace', None),
                'target_pace_type_0': 1 if interval.get('target_pace_type') == 0 else 0,
                'target_pace_type_1': 1 if interval.get('target_pace_type') == 1 else 0,
                'target_pace_type_2': 1 if interval.get('target_pace_type') == 2 else 0,
                'target_rate': interval.get('target_rate', None),
                'target_hr': interval.get('target_hr', None),
            })

    # print(intervals_data)

    # Flatten  the intervals data into a dataframe (have one row for all intervals)

    # make the intervals data into one long dict with column names like target_prace_interval_0, target_pace_interval_1, etc.
    intervals_data_flattened = {}
    for i, interval in enumerate(intervals_data):
        for key, value in interval.items():
            intervals_data_flattened[key + '_interval_' + str(i)] = value

    # print(intervals_data_flattened)
    

    # Create a dataframe from the flattened intervals data
    df = pd.DataFrame(intervals_data_flattened, index=[0])

    # Add the one hot encoded workout type to the dataframe
    df = df.assign(**workout_type_dict)

    # Add the other attributes to the dataframe (duration, split_duration target_rate target_pace target_pace_type target_hr)

    df['duration'] = data.get('duration', None)
    df['split_duration'] = data.get('split_duration', None)
    df['target_rate'] = data.get('target_rate', None)
    df['target_pace'] = data.get('target_pace', None)

    df['target_pace_type_0'] = 1 if data.get('target_pace_type') == 0 else 0
    df['target_pace_type_1'] = 1 if data.get('target_pace_type') == 1 else 0
    df['target_pace_type_2'] = 1 if data.get('target_pace_type') == 2 else 0
    df['target_hr'] = data.get('target_hr', None)


    return df



def get_wod_date_range(start_date: datetime.date, end_date: datetime.date):

    return_list = []
    # Get a list of dates between start_date and end_date
    # Format in yyyy-mm-dd
    # start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
    # end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')

    # Make sure start date is before end date and either today or in the past
    if start_date > datetime.date.today():
        raise ValueError('Start date must be today or in the past')
    if start_date > end_date:
        raise ValueError('Start date must be before end date')


    # end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')
    # start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
    date_range = [start_date + datetime.timedelta(days=x) for x in range(0, (end_date-start_date).days)]
    date_range = [date.strftime('%Y-%m-%d') for date in date_range]

    print(date_range)

    for date in date_range:
        wod = get_wod(date)
        return_list.append(get_wod_intervals(wod))

    return return_list


if __name__ == '__main__':
    # Get todays date
    # date = datetime.date.today()
    # # Format in yyyy-mm-dd
    # date = date.strftime('%Y-%m-%d')
    # wod = get_wod(date)
    # intervals = get_wod_intervals(wod)

    # intervals_df = convert_wod_to_df(intervals)
    # print(intervals_df)
    

    # Get wod for past 30 days (use today as end date)
    start_date = datetime.date.today() - datetime.timedelta(days=30)
    # start_date = start_date.strftime('%Y-%m-%d')
    end_date = datetime.date.today()
    # end_date = end_date.strftime('%Y-%m-%d')

    wod_date_range = get_wod_date_range(start_date, end_date)

    df = pd.DataFrame()

    for wod in wod_date_range:

        wod_df = convert_wod_to_df(wod)

        print(wod_df)

        

        # Add the wod to the dataframe
        df = pd.concat([df, wod_df], axis=0, ignore_index=True, sort=False)

        # Replace NaN values with None
        df = df.where(pd.notna(df), None)

        

    print(df)

    # Export the dataframe to a csv
    df.to_csv('wod.csv', index=False)
