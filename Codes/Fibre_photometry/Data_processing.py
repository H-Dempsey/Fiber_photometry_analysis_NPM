import pandas as pd
import numpy as np
import sys
import os
import cv2 as cv
from copy import deepcopy
import matplotlib.pyplot as plt
from tqdm import tqdm
from glob import glob

def wavelength_to_ledstate(wavelength):
    convert = {'415':1, '470':2, '560':4}
    return(convert[wavelength])
def ledstate_to_wavelength(ledstate):
    convert = {1:'415', 2:'470', 4:'560'}
    return(convert[ledstate])
def convert_color(value):
    convert_color = {'Region0G':'0 green','Region1R':'1 red','Region2G':'2 green','Region3R':'3 red',
                     'Region0R':'0 red','Region1G':'1 green','Region2R':'2 red','Region3G':'3 green'}
    return(convert_color[value])
def convert_str_to_list(value):
    # If "[1,2]" is found, return [1,2]
    if type(value) == str and value[0] == '[' and value[-1] == ']':
        return(eval(value))
    else:
        return(value)

def import_settings_excel_file(inputs):
    df = pd.read_excel(inputs["Settings file"], header=None, index_col=0)
    df = df.applymap(convert_str_to_list)
    list_inputs = list(df.to_dict().values())
    
    for i in range(len(list_inputs)):
        list_inputs[i]['ISOS ledstate']  = wavelength_to_ledstate(list_inputs[i]['ISOS wavelength'])
        list_inputs[i]['GCaMP ledstate'] = wavelength_to_ledstate(list_inputs[i]['GCaMP wavelength'])
        list_inputs[i]['Create grouped data']    = True
        list_inputs[i]['Grouped data file name'] = 'Grouped data'
        list_inputs[i]['Grouped data location']  = os.path.dirname(list_inputs[0]['Import location'])
    
    return(list_inputs)

def cursory_import_NPM_data(import_location):

    # Import the NPM data.
    import_files = [file for file in os.listdir(import_location) if 
                    (file.endswith(".csv") and file.startswith("~$")==False and
                     file.startswith("._")==False)]
    input_info = {'Event names':[]}
    for file in import_files:
        import_destination = os.path.join(import_location, file)
        try:
            df = pd.read_csv(import_destination)
        except:
            continue
        # Analyse the recording data file.
        if 'LedState' in df.columns:
            input_info['Colors'] = [convert_color(header) for header in df.columns if 'Region' in header]
            input_info['Wavelengths'] = [ledstate_to_wavelength(ledstate) for ledstate in df['LedState'].unique()
                           if ledstate in [1,2,4]]
        # Analyse the event time stamp files.
        elif 'Event start times (secs)' in df.columns:
            input_info['Event names'] += df['Event names'].unique().tolist()
            
    return(input_info)

def import_NPM_data(inputs):

    # Import the NPM data.
    import_files = [file for file in os.listdir(inputs['Import location']) if 
                    (file.endswith(".csv") and file.startswith("~$")==False and
                     file.startswith("._")==False)]
    inputs['Event names']       = []
    inputs['Event start times'] = []
    inputs['Event end times']   = []

    for file in import_files:
        
        import_destination = os.path.join(inputs["Import location"], file)
        try:
            df = pd.read_csv(import_destination)
        except:
            continue
        
        # Analyse the recording data file.
        if 'LedState' in df.columns:

            # Record the start time.
            inputs['Start time'] = df['Timestamp'].iloc[0]
            
            # Align the control and signal data by the corresponding timestamps.
            control       = df[df['LedState'] == inputs['ISOS ledstate']]
            control.index = range(len(control))
            control_time  = control['Timestamp']
            control_data  = control[inputs['ISOS color']]
            signal        = df[df['LedState'] == inputs['GCaMP ledstate']]
            signal.index  = range(len(signal))
            signal_time   = signal['Timestamp']
            signal_data   = signal[inputs['GCaMP color']]
            avg_diffs     = [(control_time-signal_time.shift(value)).mean() for value in range(-5,6)]
            shift_index   = pd.Series(avg_diffs).abs().argmin()
            shift_value   = range(-5,6)[shift_index]
            times         = pd.concat([control_time, signal_time.shift(shift_value)], axis=1)
            times.columns = ['Control time', 'Signal time']
            times         = times.dropna()
            data          = pd.concat([control_data, signal_data.shift(shift_value)], axis=1)
            data.columns  = ['Control data', 'Signal data']
            data          = data.dropna()
            
            # Save the aligned data.
            inputs['Control']    = data['Control data'].tolist()
            inputs['Signal']     = data['Signal data'].tolist()
            inputs['Timestamps'] = times['Signal time'].tolist()
        
        # Analyse the event time stamp files.
        elif 'Event start times (secs)' in df.columns:
            df = df.groupby('Event names').agg(list)
            inputs['Event names']       += df.index.tolist()
            inputs['Event start times'] += df['Event start times (secs)'].tolist()
            inputs['Event end times']   += df['Event end times (secs)'].tolist()
    
    # Ensure that the lengths of all stream data are the same.
    if len(inputs['Control']) != len(inputs['Signal']):
        print('The data are not the same length.')
        sys.exit()
        # smallest_len = min([len(inputs['Control']), len(inputs['Signal'])])
        # inputs['Control']    = inputs['Control'][:smallest_len]
        # inputs['Signal']     = inputs['Signal'][:smallest_len]
        # inputs['Timestamps'] = inputs['Timestamps'][:smallest_len]
    
    return(inputs)

def create_annotated_video(inputs, outputs):
    
    import matplotlib
    matplotlib.use('agg')
    
    # Import the video.
    file_names         = os.listdir(inputs['Import location'])
    video_extensions   = ['.mp4','.avi','.mov','.MP4','.AVI','.MOV']
    video_name         = [file for file in file_names if file[-4:] in video_extensions and
                          file.startswith("._")==False and file.startswith("~$")==False][0]
    import_destination = os.path.join(inputs['Import location'], video_name)
    warning = "!!! Failed cap.read()"
    cap = cv.VideoCapture(import_destination)
    fps = cap.get(cv.CAP_PROP_FPS)
    video_width   = int(cap.get(cv.CAP_PROP_FRAME_WIDTH))
    video_height  = int(cap.get(cv.CAP_PROP_FRAME_HEIGHT))
    border_top    = int(video_width*0.02)
    border_bottom = int(video_width*0.3)
    border_left   = int(video_width*0.02)
    border_right  = int(video_width*0.02)
    graph_height  = border_bottom - border_top*2
    graph_width   = video_width
    final_width   = border_left + video_width + border_right
    final_height  = border_top + video_height + border_bottom
    graph_x1 = border_left
    graph_x2 = border_left + video_width
    graph_y1 = border_top  + video_height + border_top
    graph_y2 = border_top  + video_height + border_top + graph_height
    
    # Create a dictionary that converts video frames to system times.
    # video_times_path = os.path.join(inputs['Import location'], 'Video_timestamps.csv')
    # video_times = pd.read_csv(video_times_path)
    video_times_path = os.path.join(inputs['Import location'], '*Test_all_photom_videotime*')
    video_times_path = glob(video_times_path)
    video_times_path = [path for path in video_times_path if 
                        path.startswith("._")==False and path.startswith("~$")==False][0]
    video_times = pd.read_csv(video_times_path, usecols=[0], header=None)
    video_times.columns = ['Time since box turned on (secs)']
    
    # Create a variable for the signal.
    signal = outputs[inputs['Snippets signal']]
    print('Creating video snippets for '+str(len(signal.columns))+' epochs.')
    
    # Create a folder in the export location with the snipped videos.
    folder_name = 'Video snippets0'
    i = 1
    while folder_name in os.listdir(inputs['Export location']):
        folder_name = folder_name[:-1] + str(i)
        i += 1
    export_path = os.path.join(inputs['Export location'], folder_name)
    os.makedirs(export_path)
    
    # for i in tqdm(range(len(signal.columns)), ncols=70):
    for i in range(len(signal.columns)):

        event_ind = inputs['Event names'].index(inputs['Name'])
        event     = inputs['Event start times'][event_ind][i]
        start     = event + inputs['t-range'][0]
        end       = event + inputs['t-range'][1] + inputs['t-range'][0]
        # If a custom time window is selected, use that instead of the t-range.
        if inputs['Snippets window'] == 'Custom':
            start = event + inputs['Snippets window size'][0]
            end   = event + inputs['Snippets window size'][1] + inputs['Snippets window size'][0]
        # Find the closest video frame number to this system time.
        ind_start   = (video_times['Time since box turned on (secs)']-start).abs().argmin()
        ind_end     = (video_times['Time since box turned on (secs)']-end  ).abs().argmin()
        interval_secs       = video_times.loc[ind_start:ind_end,'Time since box turned on (secs)']
        interval_epoch_secs = interval_secs - event
        # If the start/end time of the window is before the start of the video,
        # make that time the start of the video.
        # The frame numbers also start from 1,2,... when they should start from 0,1,2,...
        video_times['Frame number (0-index)'] = range(len(video_times))
        start = video_times.at[ind_start, 'Frame number (0-index)']
        end   = video_times.at[ind_end,   'Frame number (0-index)']
        if start < 0:
            start = 0
        if end < 0:
            end = 0
            
        x_record = outputs['Timestamps'][i]
        y_record = signal[i]
        x_data   = list(interval_epoch_secs)
        y_data   = [np.interp(x_val, x_record, y_record) for x_val in x_data]
    
        plt.rcParams.update({'font.size': 10})
        fig = plt.figure(figsize=(graph_width/72, graph_height/72), dpi=72)
        plt.xlim(inputs['t-range'][0],inputs['t-range'][0]+inputs['t-range'][1])
        y_min = min(y_data)
        y_max = max(y_data)
        # y_min = min([min(signal[i]) for i in range(len(signal.columns))])
        # y_max = max([max(signal[i]) for i in range(len(signal.columns))])
        plt.ylim(y_min,y_max)
        plt.xlabel('Time (secs)')
        plt.ylabel(inputs['Snippets signal'])
    
        plt.tight_layout(h_pad=0)
        plt.subplots_adjust(left=0.07)
        line1, = plt.plot([], [], 'g-', lw=1.5)
        plt.axvline(x = 0, color = 'lightgray', linestyle='dashed')
        
        cap = cv.VideoCapture(import_destination)
        cap.set(cv.CAP_PROP_POS_FRAMES, start)
        result = cv.VideoWriter(os.path.join(export_path, 'Event '+str(i)+'.mp4'), 
                                cv.VideoWriter_fourcc(*'mp4v'),
                                fps, (final_width, final_height))
    
        while cap.isOpened():
            
            frame_no = int(cap.get(cv.CAP_PROP_POS_FRAMES))
            ret, frame = cap.read()
            if ret == False:
                print(warning)
                break
            frame = cv.copyMakeBorder(frame,
                                      border_top,border_bottom,border_left,border_right,
                                      cv.BORDER_CONSTANT,value=[0,0,0])
            
            # update data
            line1.set_data(x_data[:frame_no-start], y_data[:frame_no-start])
            # redraw the canvas
            fig.canvas.draw()
            # convert canvas to image
            img = np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.uint8)
            img = img.reshape(fig.canvas.get_width_height()[::-1] + (3,))
            # img is rgb, convert to opencv's default bgr
            img = cv.cvtColor(img,cv.COLOR_RGB2BGR)
            img = cv.resize(img, (graph_width, graph_height))
            
            frame[ graph_y1:graph_y2, graph_x1:graph_x2 ] = img
            result.write(frame)
            
            if int(cap.get(cv.CAP_PROP_POS_FRAMES)) == end:
                break
                
        # When everything done, release the video capture and write objects
        cap.release()
        result.release()
            
        # Closes all the frames
        cv.destroyAllWindows()
        
        plt.close()
        
def export_settings_excel_file(list_inputs):
    
    list_inputs1 = deepcopy(list_inputs)
    
    # If only one folder is analysed, make list_inputs a one-element list.
    if type(list_inputs1) != list:
        list_inputs1 = [list_inputs1]
        export_location = list_inputs1[0]['Export location']
    else:
        export_location = list_inputs1[0]['Grouped data location']
    
    # Create a list of inputs that are not needed to re-create the analysis.
    inputs_exclude = ['Settings', 'Event start times', 'Event end times', 
        'Event names', 'Start time', 'Control', 'Signal', 'Timestamps',
        'ISOS ledstate', 'GCaMP ledstate', 'Create grouped data',
        'Grouped data file name', 'Grouped data location', 'Analysis type']
    
    # Remove these inputs.
    for i in range(len(list_inputs1)):
        for input1 in inputs_exclude:
            if input1 in list_inputs1[i].keys():
                list_inputs1[i].pop(input1)
    
    # Export this datarame.
    # If a settings file already exists, create a new one with a number at the end.
    export = pd.DataFrame(list_inputs1).T
    export_name = 'Settings0.xlsx'
    i = 1
    while export_name in os.listdir(export_location):
        export_name = export_name[:8] + str(i) + '.xlsx'
        i += 1
    export_path = os.path.join(export_location, export_name)
    export.to_excel(export_path, header=False)
    print('Saved ' + export_name)
