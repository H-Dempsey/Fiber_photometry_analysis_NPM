import pandas as pd
import numpy as np
import os
import sys
import cv2
from glob import glob
from tqdm import tqdm

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
def rename_cols(value):
    convert_new = {"G0":"Region0G","R1":"Region1R","G2":"Region2G","R3":"Region3R",
                   "R0":"Region0R","G1":"Region1G","R2":"Region2R","G3":"Region3G",
                   "SystemTimestamp":"Timestamp"}
    if value in convert_new.keys():
        return(convert_new[value])
    else:
        return(value)

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
            df.columns = [rename_cols(col) for col in df.columns]
            recording_start_time2 = df['Timestamp'].iloc[0]
            found_recording_file = True
            break
    if found_recording_file == False:
        print('Could not find file that contains the photometry neural recording data.')
        sys.exit()

    # Find the start time of the recording in milliseconds since midnight.
    recording_start_time = df['ComputerTimestamp'].iloc[0]
    # Convert to milliseconds since the recording started.
    video_times = video_times - recording_start_time
    # Convert milliseonds to seconds.
    video_times = video_times / 1000

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

def export_event_timestamps_claire(inputs, outputs):
    
    # Create a dictionary that converts video frames to system times.
    import_location = os.path.dirname(inputs['Import location'])
    video_times_path = os.path.join(import_location, '*video timestamp*')
    video_times_path = glob(video_times_path)[0]
    video_times = pd.read_csv(video_times_path, usecols=['Timestamp.Timestamp'])['Timestamp.Timestamp']
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
    
    # Export this data, so it can be used by the Fibre photometry GUI.
    new_video_times_name = 'Test_all_photom_videotime_secs_since_box_turned_on.csv'
    new_video_times_path = os.path.join(import_location, new_video_times_name)
    video_times.to_csv(new_video_times_path, index=False, header=False)
    total_duration = video_times.iloc[-1] - video_times.iloc[0]
    last_frame_number = video_times.index[-1]
    convert = video_times.to_dict()
    def convert_frames_to_secs(frame):
        return(convert[frame])
    
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

def check_video_integrity(inputs):
    
    print("\nChecking that the extracted frame numbers are accurate.")
    
    # Create an array of the image frame numbers with corresponding numpy arrays.
    input_video   = os.path.basename(inputs['Import location'])
    export_folder = os.path.dirname(inputs['Import location'])
    new_folder    = f"Extracted frames from {input_video}"
    image_folder  = os.path.join(export_folder, new_folder)
    image_paths   = glob(os.path.join(image_folder, "*.png"))
    image_arrays  = {int(os.path.basename(path)[:-4]): cv2.imread(path) for path in image_paths}
    
    # Go through the video and check that the frame numbers are accurate.
    i = 0
    contact_Harry = False
    cap = cv2.VideoCapture(inputs['Import location'])
    mostly_accurate_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    pbar = tqdm(total=mostly_accurate_count)
    
    while True:
        
        grabbed = cap.grab()
        if not grabbed:
            break
        
        if i in image_arrays.keys():
            ret, frame = cap.retrieve()
            if not ret:
                print("Something is wrong with the frame checking.")
            if not np.array_equal(image_arrays[i], frame):
                contact_Harry = True
        
        i += 1
        pbar.update(1)
        
        if i > pbar.total:
            pbar.total = i
            pbar.refresh()
    
    pbar.close()
    if contact_Harry:
        print("\nThe frame numbers are not all accurate.")
    else:
        print("\nAll frame numbers are accurate.")
    
    # Check that the number of frames i is the same as the number of data rows.
    video_times_path = os.path.join(export_folder, 'VideoOutput*')
    if len(glob(video_times_path)) == 0:
        print('Could not find the video timestamps file starting with "VideoOutput".')
        sys.exit()
        
    video_times_path = glob(video_times_path)[0]
    video_times = pd.read_csv(video_times_path, usecols=[0], header=None)[0]
    if len(video_times) == i and len(video_times) == mostly_accurate_count:
        print("Video length matches the video timestamps length.")
    else:
        print("Video length does NOT match the videotimestamp length.")
        contact_Harry = True
        
    if contact_Harry:
        print("***Contact Harry about fixing the videos for manual scoring***")
