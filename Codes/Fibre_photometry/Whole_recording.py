import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from sklearn.metrics import auc
import os

def whole_recording_analysis(inputs):
    
    # Define variables to be used later.
    all_data = pd.DataFrame()
    for name in ['Timestamps','Control','Signal']:
        all_data[name] = inputs[name]
    
    # Exclude data from the start of the recording.
    if inputs['Exclude type'] == 'Time from recording start':
        exclude_time = inputs['Start time'] + inputs['Remove']
    else:
        exclude_time = inputs['Remove']
    all_data = all_data[all_data['Timestamps'] > exclude_time]
    all_data.index = range(len(all_data))
    
    # Apply a moving average filter if this is needed.
    if inputs['Smoothing factor'] > 1:
        for data_type in ['Control', 'Signal']:
            all_data[data_type] = all_data[data_type].rolling(
                inputs['Smoothing factor'], min_periods=1, center=True).mean()
    
    # Fitting 405 channel onto 465 channel to detrend signal bleaching.
    # Fit the control channel onto the signal channel to calculate dFF.
    grad, yint = np.polyfit(all_data['Control'],all_data['Signal'],1)
    all_data['Fit'] = grad*all_data['Control'] + yint
    all_data['dF']  = all_data['Signal'] - all_data['Fit']
    all_data['dFF'] = all_data['dF'] / all_data['Fit']
    
    # Find the baseline Z-Score.
    if inputs['Baseline type'] == 'Entire recording':
        baseline_mean = all_data['dF'].mean()
        baseline_std  = all_data['dF'].std()
        all_data['Z-Score'] = (all_data['dF'] - baseline_mean) / baseline_std
    else:
        baseline_start, baseline_end = inputs['Baseline period']
        custom_range = ((all_data['Timestamps']>=baseline_start)&
                        (all_data['Timestamps']<=baseline_end))
        control_baseline = all_data[custom_range]['Control']
        signal_baseline  = all_data[custom_range]['Signal']
        
        # Fit the control to the signal within the baseline period.
        grad, yint = np.polyfit(control_baseline, signal_baseline, 1)
        baseline_fit = grad*control_baseline + yint
        baseline_dF  = signal_baseline - baseline_fit
        
        # Find the Z-score.
        baseline_mean = baseline_dF.mean()
        baseline_std  = baseline_dF.std()
        all_data['Z-Score'] = (all_data['dF'] - baseline_mean) / baseline_std
        
    outputs = {'zScore':all_data['Z-Score'],'dFF':all_data['dFF'],'ISOS':all_data['Control'], 
               'Fit':all_data['dF'],'GCaMP':all_data['Signal'],'Timestamps':all_data['Timestamps']}
    
    return(outputs)

def add_event_info(time, onsets, offsets, notes):
    int2 = pd.Interval(left=time[0], right=time[1])
    for i in range(len(onsets)):
        int1 = pd.Interval(left=onsets[i], right=offsets[i])
        if int1.overlaps(int2) == True:
            return(notes[i])
    return(np.nan)

def create_export_plots(inputs, outputs):
    
    outputs['Plots'] = {}
    outputs['Dataframe'] = {}
    stats = ['zScore','dFF','ISOS','GCaMP']
    stats_to_export = [stat for stat in stats if inputs['Export '+stat] == True]
    
    for stat in stats_to_export:

        # Plot the signal data.
        fig = plt.figure(figsize=(20,4))
        ax  = fig.add_subplot()
        plt.plot(outputs['Timestamps'], outputs[stat], linewidth=1, color='green', label=stat)
        
        # Create a dictionary that converts event names to unique colors.
        event_list = list(set(inputs['Name']))
        cmap = plt.cm.get_cmap('tab20')
        event_color_point = {event_list[i]:cmap(0.1*i) for i in range(len(event_list))}
        event_color_inter = {event_list[i]:cmap(0.05+0.1*i) for i in range(len(event_list))}
        
        # Mark the baseline period.
        starts = []
        ends   = []
        events = []
        if inputs['Baseline type'] == 'Interval (secs)':
            start, end = inputs['Baseline period']
            starts += [start]
            ends   += [end]
            events += ['Baseline period']
            plt.axvspan(start, end, color='lightgray', label='Baseline period', linewidth=2)
        
        # Mark the events over the signal data.
        for i in range(len(inputs['Name'])):
            event_name        = inputs['Name'][i]
            event_ind         = inputs['Event names'].index(event_name)
            event_start_times = inputs['Event start times'][event_ind]
            event_end_times   = inputs['Event end times'][event_ind]
            for j in range(len(event_start_times)):
                start   = event_start_times[j]
                end     = event_end_times[j]
                starts += [start]
                ends   += [end]
                events += [event_name]
                if start == end:
                    plt.axvspan(start, end, color=event_color_point[event_name], label=event_name, linewidth=2)
                else:
                    plt.axvspan(start, end, color=event_color_inter[event_name], label=event_name, linewidth=2)
                    
        if inputs['Peak detection'] == True:
            
            # Plot the peaks over the top of the whole recording plot.
            light_pastel1 = [(1.000, 0.933, 0.933),(0.933, 1.000, 0.933),
                (0.933, 0.933, 1.000),(0.996, 0.933, 1.000),(0.933, 1.000, 0.996),
                (1.000, 0.957, 0.933),(0.957, 0.933, 1.000),(0.933, 0.957, 1.000),
                (0.996, 0.996, 0.933),(0.933, 0.996, 0.933),(0.933, 0.933, 0.933)]
            peaks, properties = find_peaks(outputs[stat], prominence=inputs['Prominence']) 
            plt.plot(outputs['Timestamps'][peaks], outputs[stat][peaks], "ok", markersize=5)
            for i in range(len(properties['prominences'])):
                left_bound  = properties['left_bases'][i]
                right_bound = properties['right_bases'][i]
                x_values    = outputs['Timestamps'][left_bound:right_bound]
                peak_height = properties["prominences"][i]
                peak_max    = outputs[stat][peaks[i]]
                y_baseline  = [peak_max-peak_height]*len(x_values)
                y_signal    = outputs[stat][left_bound:right_bound]
                color_index = i % len(light_pastel1)  # Wrap around the colormap index
                plt.fill_between(x_values, y_baseline, y_signal, color=light_pastel1[color_index])
            
            # Export this data, so it can be re-imported for peri-events analysis.
            peaks_df = pd.DataFrame()
            peak_times = outputs['Timestamps'][peaks].tolist()
            peaks_df['Event names']       = len(peak_times)*['Peak']
            peaks_df['Event start times (secs)'] = peak_times
            peaks_df['Event end times (secs)']   = peak_times
            peaks_df[f'Prominences ({stat})']    = list(properties['prominences'])
            peaks_df[f'Heights ({stat})']        = [outputs[stat][peaks[i]] for i in range(len(peaks))]
            export_name = 'Peaks for '+stat+'.csv'
            export_destination = os.path.join(inputs['Export location'], export_name)
            peaks_df.to_csv(export_destination, index=False)
            
        if inputs['Peak detection'] == True and inputs['Negative'] == True:
            
            # Plot the peaks over the top of the whole recording plot.
            light_pastel1 = [(1.000, 0.933, 0.933),(0.933, 1.000, 0.933),
                (0.933, 0.933, 1.000),(0.996, 0.933, 1.000),(0.933, 1.000, 0.996),
                (1.000, 0.957, 0.933),(0.957, 0.933, 1.000),(0.933, 0.957, 1.000),
                (0.996, 0.996, 0.933),(0.933, 0.996, 0.933),(0.933, 0.933, 0.933)]
            peaks, properties = find_peaks(-np.array(outputs[stat]), prominence=inputs['Prominence']) 
            plt.plot(outputs['Timestamps'][peaks], outputs[stat][peaks], "ok", markersize=5)
            for i in range(len(properties['prominences'])):
                left_bound  = properties['left_bases'][i]
                right_bound = properties['right_bases'][i]
                x_values    = outputs['Timestamps'][left_bound:right_bound]
                peak_height = properties["prominences"][i]
                peak_max    = outputs[stat][peaks[i]]
                y_baseline  = [peak_max-peak_height]*len(x_values)
                y_signal    = outputs[stat][left_bound:right_bound]
                color_index = i % len(light_pastel1)  # Wrap around the colormap index
                plt.fill_between(x_values, y_baseline, y_signal, color=light_pastel1[color_index])
            
            # Export this data, so it can be re-imported for peri-events analysis.
            peaks_df = pd.DataFrame()
            peak_times = outputs['Timestamps'][peaks].tolist()
            peaks_df['Event names']       = len(peak_times)*['Negative peaks']
            peaks_df['Event start times (secs)'] = peak_times
            peaks_df['Event end times (secs)']   = peak_times
            peaks_df[f'Prominences ({stat})']    = list(-properties['prominences'])
            peaks_df[f'Heights ({stat})']        = [outputs[stat][peaks[i]] for i in range(len(peaks))]
            export_name = 'Negative peaks for '+stat+'.csv'
            export_destination = os.path.join(inputs['Export location'], export_name)
            peaks_df.to_csv(export_destination, index=False)
        
        # Create a legend.
        handles, labels = ax.get_legend_handles_labels()
        dict1 = {}
        for i in range(len(handles)):
            dict1[labels[i]] = handles[i]
        plt.legend(dict1.values(), dict1.keys(), loc='center left', bbox_to_anchor=(1, 0.5))
        
        # Choose the time axis range to be the earliest start event and the latest end event.
        ax.set_ylabel(stat)
        ax.set_xlabel('Time (secs)')
        ax.set_title('Whole recording with events highlighted')
        plt.tight_layout()
        
        # Create raw data file.
        raw_data = pd.DataFrame()
        raw_data['Timestamps (secs)'] = outputs['Timestamps']
        raw_data['Timestamps (shifted)'] = raw_data['Timestamps (secs)'].shift()
        first_index = raw_data.index[0]
        raw_data.at[first_index,'Timestamps (shifted)'] = raw_data.at[first_index,'Timestamps (secs)']
        raw_data['Intervals'] = list(zip(raw_data['Timestamps (shifted)'], 
                                         raw_data['Timestamps (secs)']))
        raw_data[stat] = outputs[stat]
        raw_data['Events'] = raw_data['Intervals'].apply(add_event_info, 
                                onsets=starts, offsets=ends, notes=events)
        raw_data = raw_data.drop(['Timestamps (shifted)', 'Intervals'], axis=1)
        
        # Save the plots and raw data.
        outputs['Plots '+stat]    = fig
        outputs['Raw data '+stat] = raw_data
        plt.close()
        
        return(outputs)

def export_whole_recording_plots(inputs, outputs):
    
    stats = ['zScore','dFF','ISOS','GCaMP','Fit']
    stats_to_export = [stat for stat in stats if inputs['Export '+stat] == True]

    for stat in stats_to_export:
        export_name = (os.path.basename(inputs['Import location']) + "_"+stat+"_" + 
                       inputs['Analysis name']    + "_" + inputs['ISOS wavelength']  + '_' +
                       inputs['ISOS color'][-2:]  + "_" + inputs['GCaMP wavelength'] + "_" +
                       inputs['GCaMP color'][-2:] + ".png")
        export_destination = os.path.join(inputs['Export location'], export_name)
        outputs['Plots '+stat].savefig(export_destination)
            
def export_whole_recording_data(inputs, outputs):
    
    stats = ['zScore','dFF','ISOS','GCaMP','Fit']
    stats_to_export = [stat for stat in stats if inputs['Export '+stat] == True
                       and inputs['Raw data'] == True]
    
    for stat in stats_to_export:
        export_name = (os.path.basename(inputs['Import location']) + "_"+stat+"_" + 
                       inputs['Analysis name']    + "_" + inputs['ISOS wavelength']  + '_' +
                       inputs['ISOS color'][-2:]  + "_" + inputs['GCaMP wavelength'] + "_" +
                       inputs['GCaMP color'][-2:] + ".csv")
        export_destination = os.path.join(inputs['Export location'], export_name)
        outputs['Raw data '+stat].to_csv(export_destination, index=False)
