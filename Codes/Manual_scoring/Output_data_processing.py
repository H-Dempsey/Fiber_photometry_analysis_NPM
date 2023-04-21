import pandas as pd
import os
import sys
from glob import glob

# Define auxiliary functions.
def latency_to_first(list1):
    if len(list1) == 0:
        return(0)
    else:
        return(list1[0][0])
def duration(list1):
    if len(list1) == 0:
        return(0)
    else:
        list_durations = [tuple1[1]-tuple1[0] for tuple1 in list1]
        sum_durations  = sum(list_durations)
        return(sum_durations)
def enlist(list1):
    return([list1])

def export_event_timestamps_leigh_xavier(inputs, outputs):
    
    # Create a dictionary that converts video frames to system times.
    import_location = os.path.dirname(inputs['Import location'])
    video_times_path = os.path.join(import_location, 'VideoOutput*')
    if len(glob(video_times_path)) == 0:
        print('Could not find the video timestamps file starting with "VideoOutput".')
        sys.exit()
    video_times_path = glob(video_times_path)[0]
    video_times = pd.read_csv(video_times_path, usecols=[0], header=None)[0]
    video_times.index = range(len(video_times))
    # Find the start time of the recording in milliseconds since midnight.
    recording_times_path = os.path.join(import_location, 'PhotometryData_CompTimes*')
    if len(glob(recording_times_path)) == 0:
        print('Could not find the recording timestamps file starting with "PhotometryData_CompTimes".')
        sys.exit()
    recording_times_path = glob(recording_times_path)[0]
    recording_times = pd.read_csv(recording_times_path)['ComputerTimestamp']
    recording_start_time = recording_times.iloc[0]
    # Convert to milliseconds since the recording started.
    video_times = video_times - recording_start_time
    # Convert milliseonds to seconds.
    video_times = video_times / 1000
    # Find the time since the box was turned on.
    import_files = [file for file in os.listdir(import_location) if 
                    (file.endswith(".csv") and file.startswith("~$")==False)]
    found_recording_file = False
    for file in import_files:
        import_destination = os.path.join(import_location, file)
        try:
            df = pd.read_csv(import_destination)
        except:
            continue
        if 'LedState' in df.columns:
            recording_start_time2 = df['Timestamp'].iloc[0]
            found_recording_file = True
            break
    if found_recording_file == False:
        print('Could not find file that contains the photometry neural recording data.')
        sys.exit()
    # Convert video_times to video time since the NPM box was turned on.
    video_times = video_times + recording_start_time2
    # Export this data, so it can be used by the Fibre photometry GUI.
    new_video_times_name = 'Test_all_photom_videotime_secs_since_box_turned_on.csv'
    new_video_times_path = os.path.join(import_location, new_video_times_name)
    video_times.to_csv(new_video_times_path, index=False, header=False)
    total_duration = video_times.iloc[-1] - video_times.iloc[0]
    last_frame_number = video_times.index[-1]
    convert = video_times.to_dict()
    def convert_frames_to_secs(frame):
        return(convert[frame])
    
    # Process the output data in a format that is usable for the rest of the analysis.
    raw_data = pd.DataFrame(outputs)
    raw_data = raw_data.rename(columns={'Event start times': 'Event start times (frames)', 
                                        'Event end times':   'Event end times (frames)'})
    data_cols_frames = ['Event start times (frames)', 'Event end times (frames)']
    data_cols_secs   = ['Event start times (secs)',   'Event end times (secs)']
    raw_data[data_cols_frames] = raw_data[data_cols_frames].replace({'Empty':last_frame_number})
    raw_data[data_cols_secs]   = raw_data[data_cols_frames].applymap(convert_frames_to_secs)
    outputs['Raw data'] = raw_data
    outputs['Total duration (secs)'] = total_duration
    
    # Export the raw data.
    import_name = os.path.basename(inputs['Import location'])
    export_name = 'Timestamps for '+import_name+'.csv'
    export_destination = os.path.join(inputs['Export location'], export_name)
    outputs['Raw data'].to_csv(export_destination, index=False)
    
    return(outputs)

def export_event_timestamps_eva_roberta(inputs, outputs):
    
    # Create a dictionary that converts video frames to system times.
    import_location = os.path.dirname(inputs['Import location'])
    video_times_path = os.path.join(import_location, '*Test_all_photom_videotime*')
    video_times_path = glob(video_times_path)[0]
    video_times = pd.read_csv(video_times_path, usecols=[0], header=None)[0]
    video_times.index = range(len(video_times))
    total_duration = video_times.iloc[-1] - video_times.iloc[0]
    last_frame_number = video_times.index[-1]
    convert = video_times.to_dict()
    def convert_frames_to_secs(frame):
        return(convert[frame])
    
    # Process the output data in a format that is usable for the rest of the analysis.
    raw_data = pd.DataFrame(outputs)
    raw_data = raw_data.rename(columns={'Event start times': 'Event start times (frames)', 
                                        'Event end times':   'Event end times (frames)'})
    data_cols_frames = ['Event start times (frames)', 'Event end times (frames)']
    data_cols_secs   = ['Event start times (secs)',   'Event end times (secs)']
    raw_data[data_cols_frames] = raw_data[data_cols_frames].replace({'Empty':last_frame_number})
    raw_data[data_cols_secs]   = raw_data[data_cols_frames].applymap(convert_frames_to_secs)
    outputs['Raw data'] = raw_data
    outputs['Total duration (secs)'] = total_duration
    
    # Export the raw data.
    import_name = os.path.basename(inputs['Import location'])
    export_name = 'Timestamps for '+import_name+'.csv'
    export_destination = os.path.join(inputs['Export location'], export_name)
    outputs['Raw data'].to_csv(export_destination, index=False)
    
    return(outputs)

# def export_analysed_data(inputs, outputs):
    
#     raw_data = outputs['Raw data']
#     raw_data['Event times'] = list(zip(raw_data['Event start times (secs)'], raw_data['Event end times (secs)']))
#     event_intervals = raw_data.groupby('Event names').agg(list)['Event times']

#     # Create a pandas series of empty lists.
#     empty_lists = [[] for i in range(len(inputs['Event names']))]
#     all_events = pd.Series(empty_lists, index=inputs['Event names'])
#     for event_name in event_intervals.index:
#         all_events[event_name] = event_intervals[event_name]
    
#     # This is data in frames.
#     analysed_data = {}
#     analysed_data['Frequency']               = all_events.apply(len)
#     analysed_data['Latency to first (secs)'] = all_events.apply(latency_to_first)
#     analysed_data['Duration (secs)']         = all_events.apply(duration)
#     analysed_data['Total duration (secs)']   = outputs['Total duration (secs)']
#     analysed_data['Duration/total time (%)'] = (analysed_data['Duration (secs)'] / 
#                                                 analysed_data['Total duration (secs)']) * 100

#     # Create an data sheet for exporting.
#     analysis = pd.DataFrame(analysed_data)
#     for col in analysis.columns:
#         analysis[col] = analysis[col].apply(enlist)
#     analysis = pd.DataFrame(analysis.stack().to_dict())
    
#     # Convert the header to rows.
#     header = analysis.columns
#     header = pd.MultiIndex.to_frame(header).T
#     analysis = pd.concat([header, analysis])
#     analysis.columns = range(len(analysis.columns))
#     video_name = os.path.basename(inputs['Import location'])
#     index_col = pd.Series(['Video path','',video_name], index=[0,1,2])
#     index_col = pd.Series(['Video duration','',video_name], index=[0,1,2])
#     analysis.index = [0,1,2]
#     analysis = pd.concat([index_col, analysis], axis=1)
#     outputs['Analysed data'] = analysis
    
#     # Export the raw data.
#     import_name = os.path.basename(inputs['Import location'])
#     export_name = 'Analysed data for '+import_name+'.csv'
#     export_destination = os.path.join(inputs['Export location'], export_name)
#     outputs['Analysed data'].to_csv(export_destination, index=False, header=False)

#     return(outputs)
