import numpy as np
import os
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import auc
from seaborn import swarmplot

def epoch_analysis(inputs):
    
    # Define variables to be used later.
    event_ind         = inputs['Event names'].index(inputs['Name'])
    event_start_times = inputs['Event start times'][event_ind]
    all_data = pd.DataFrame()
    for name in ['Timestamps','Control','Signal']:
        all_data[name] = inputs[name]
    
    # Find the time ranges.
    time_ranges = []
    excluded_events = []
    recording_start = all_data['Timestamps'].iloc[0]
    recording_end   = all_data['Timestamps'].iloc[-1]
    for i in range(len(event_start_times)):
        epoch_start = event_start_times[i]+inputs['t-range'][0]
        epoch_end   = event_start_times[i]+inputs['t-range'][1]+inputs['t-range'][0]
        if epoch_start < recording_start or epoch_end > recording_end:
            excluded_events += [i]
        else:
            time_ranges += [[epoch_start, epoch_end]]
    if len(excluded_events) > 0:
        print(f'PLEASE NOTE: {len(excluded_events)} events have been excluded from the '+
              'analysis because the epoch windows go outside of the recording period.')
        inputs['Event start times'][event_ind] = list(
            np.delete(inputs['Event start times'][event_ind], excluded_events))
        inputs['Event end times'  ][event_ind] = list(
            np.delete(inputs['Event end times'  ][event_ind], excluded_events))
    
    # Find the data ranges corresponding to these time ranges.
    timestamps = []
    control    = []
    signal     = []
    for time_range in time_ranges:
        custom_range = ((all_data['Timestamps']>time_range[0])&
                        (all_data['Timestamps']<time_range[1]))
        timestamps  += [all_data[custom_range]['Timestamps']]
        control     += [all_data[custom_range]['Control']]
        signal      += [all_data[custom_range]['Signal']]
        
    # Ensure each range is the same length.
    smallest_len = min([len(range1) for range1 in timestamps])
    for i in range(len(timestamps)):
        timestamps[i]    = timestamps[i][:smallest_len]
        control[i]       = control[i][:smallest_len]
        signal[i]        = signal[i][:smallest_len]
        timestamps[i].index = range(len(timestamps[i]))
        control[i].index    = range(len(control[i]))
        signal[i].index     = range(len(signal[i]))
            
    # Convert these lists of series to dataframes.
    timestamps = pd.concat(timestamps,axis=1)
    control    = pd.concat(control,axis=1)
    signal     = pd.concat(signal,axis=1)
    timestamps.columns = range(len(timestamps.columns))
    control.columns    = range(len(control.columns))
    signal.columns     = range(len(signal.columns))
    
    # Create a timestamps dataframe with the event time defined as 0 secs.
    timestamps_centred = timestamps.copy()
    for i in timestamps.columns:
        timestamps_centred[i] = timestamps_centred[i] - event_start_times[i]
    
    # Fitting 405 channel onto 465 channel to detrend signal bleaching.
    # Fit the control channel onto the signal channel to calculate dFF.
    linear_fit_variables = [np.polyfit(control[i],signal[i],1) for i in timestamps.columns]
    control_signal_fit = control.copy()
    for i in range(len(linear_fit_variables)):
        grad, yint = linear_fit_variables[i]
        control_signal_fit[i] = grad*control[i] + yint
    dF  = signal - control_signal_fit
    dFF = dF / control_signal_fit
    
    if inputs['Baseline type'] == 'Changing':
        
        baseline_start, baseline_end = inputs['Baseline period']
        zscore = dF.copy()
        for i in timestamps.columns:
            custom_range  = ((timestamps_centred[i]>baseline_start)&
                             (timestamps_centred[i]<baseline_end))
            baseline_mean = dF[custom_range][i].mean()
            baseline_std  = dF[custom_range][i].std()
            if baseline_std != 0:
                zscore[i] = (dF[i] - baseline_mean) / baseline_std
            else:
                zscore[i] = dF[i]*0
    
    # Find the baseline Z-Score.
    else:
        if inputs['Baseline type'] == 'Constant (overall)':
            baseline_start = inputs['Baseline period'][0]
            baseline_end   = inputs['Baseline period'][1]
        elif inputs['Baseline type'] == 'Constant (time since start)':
            baseline_start = inputs['Baseline period'][0] + inputs['Start time']
            baseline_end   = inputs['Baseline period'][1] + inputs['Start time']

        # Define variables to be used later.
        custom_range = ((all_data['Timestamps']>baseline_start)&
                        (all_data['Timestamps']<baseline_end))
        control_baseline = all_data[custom_range]['Control']
        signal_baseline  = all_data[custom_range]['Signal']
        
        # Fit the control to the signal within the baseline period.
        grad, yint = np.polyfit(control_baseline, signal_baseline, 1)
        baseline_fit = grad*control_baseline + yint
        baseline_dF  = signal_baseline - baseline_fit
        
        # Find the Z-score.
        baseline_mean = baseline_dF.mean()
        baseline_std  = baseline_dF.std()
        if baseline_std != 0:
            zscore = (dF - baseline_mean) / baseline_std
        else:
            zscore = dF[i]*0
        
    outputs = {'zScore':zscore, 'dFF':dFF, 'ISOS':control, 'Fit':dF,
               'GCaMP':signal, 'Timestamps':timestamps_centred}
    
    return(inputs, outputs)

def graph_epoch_analysis(outputs):
    
    # Create a figure with the required number of subplots
    num_subplots = 0
    if 'ISOS' in outputs.keys() and 'GCaMP' in outputs.keys() and 'Fit' in outputs.keys():
        num_subplots += 1
    if 'dFF' in outputs.keys():
        num_subplots += 1
    if 'zScore' in outputs.keys():
        num_subplots += 2
    fig, axs = plt.subplots(num_subplots, 1, figsize=(8, num_subplots * 3))
    time_mean = outputs['Timestamps'].mean(axis=1)
    i = 0
    
    # Subplot 1: Control, signal and fit data vs time
    if 'ISOS' in outputs.keys() and 'GCaMP' in outputs.keys() and 'Fit' in outputs.keys():
        control_mean = outputs['ISOS'].mean(axis=1)
        control_mean = control_mean - control_mean.mean()
        axs[i].plot(time_mean, control_mean, label='Control', linewidth=1)
        signal_mean = outputs['GCaMP'].mean(axis=1)
        signal_mean = signal_mean - signal_mean.mean()
        axs[i].plot(time_mean, signal_mean, label='Signal', linewidth=1)
        fit_mean = outputs['Fit'].mean(axis=1)
        fit_mean = fit_mean - fit_mean.mean()
        axs[i].plot(time_mean, fit_mean, label='Fit', linewidth=1)
        axs[i].legend(loc='upper right')
        axs[i].set_xlabel('Time of event (secs)')
        axs[i].set_ylabel('Normalized light intensity (mV)')
        axs[i].set_title('Control, signal and fit data vs time')
        i += 1
    
    # Subplot 2: dFF vs time
    if 'dFF' in outputs.keys():
        dFF_mean = outputs['dFF'].mean(axis=1)
        dFF_error = outputs['dFF'].sem(axis=1)
        axs[i].fill_between(time_mean, dFF_mean+dFF_error, dFF_mean-dFF_error, alpha=0.5)
        axs[i].plot(time_mean, dFF_mean, linewidth=1, label='dFF')
        axs[i].set_xlabel('Time of event (secs)')
        axs[i].set_ylabel('dFF')
        axs[i].set_title('dFF vs time')
        i += 1
    
    # Subplot 3: Z-Score vs time
    if 'zScore' in outputs.keys():
        zscore_mean = outputs['zScore'].mean(axis=1)
        zscore_error = outputs['zScore'].sem(axis=1)
        axs[i].fill_between(time_mean, zscore_mean+zscore_error, zscore_mean-zscore_error, alpha=0.5)
        axs[i].plot(time_mean, zscore_mean, linewidth=1, label='Z-Score')
        axs[i].set_xlabel('Time of event (secs)')
        axs[i].set_ylabel('Z-Score')
        axs[i].set_title('Z-Score vs time')
        i += 1
    
    # Subplot 4: Z-Score AUC vs time window
    if 'zScore' in outputs.keys():
        pre_event_range = time_mean < 0
        pre_event_auc = []
        post_event_range = time_mean > 0
        post_event_auc = []
        for j in range(len(outputs['zScore'].columns)):
            pre_event_x = time_mean[pre_event_range]
            pre_event_y = outputs['zScore'].iloc[:, j][pre_event_range]
            pre_event_auc += [auc(pre_event_x, pre_event_y)]
            post_event_x = time_mean[post_event_range]
            post_event_y = outputs['zScore'].iloc[:, j][post_event_range]
            post_event_auc += [auc(post_event_x, post_event_y)]
        pre_event_auc_mean   = pd.Series(pre_event_auc).mean()
        pre_event_auc_error  = pd.Series(pre_event_auc).sem()
        post_event_auc_mean  = pd.Series(post_event_auc).mean()
        post_event_auc_error = pd.Series(post_event_auc).sem()
        axs[i].bar(['Pre-event','Post-event'], [pre_event_auc_mean, post_event_auc_mean], alpha=0.5)
        if len(outputs['zScore'].columns) > 1:
            axs[i].errorbar(['Pre-event', 'Post-event'], [pre_event_auc_mean, post_event_auc_mean], 
                            yerr=[pre_event_auc_error, post_event_auc_error], 
                            capsize=7, color='black', ls='none', elinewidth=1)
        x_scatter = len(pre_event_auc)*['Pre-event'] + len(post_event_auc)*['Post-event']
        y_scatter = pre_event_auc + post_event_auc
        scatter_df = pd.DataFrame({'X':x_scatter, 'Y':y_scatter})
        swarmplot(data=scatter_df, x="X", y="Y", ax=axs[i], color='black', size=4)
        # axs[i].scatter(x_scatter, y_scatter, s=10, marker='o', color='black')
        axs[i].set_xlabel('Time window')
        axs[i].set_ylabel('Z-Score area under curve')
        axs[i].set_title('Z-Score AUC vs time window')
        i += 1
    
    plt.tight_layout()    
    outputs['Figure'] = fig
    
    return(outputs)

def graph_epoch_analysis_grouped(outputs):
    
    # Create a figure with the required number of subplots
    num_subplots = 0
    if 'ISOS' in outputs.keys() and 'GCaMP' in outputs.keys() and 'Fit' in outputs.keys():
        num_subplots += 1
    if 'dFF' in outputs.keys():
        num_subplots += 1
    if 'zScore' in outputs.keys():
        num_subplots += 2
    fig, axs = plt.subplots(num_subplots, 1, figsize=(8, num_subplots * 3))
    time_mean = outputs['Timestamps'].mean(axis=1)
    i = 0
    
    # Subplot 1: Control, signal and fit data vs time
    if 'ISOS' in outputs.keys() and 'GCaMP' in outputs.keys() and 'Fit' in outputs.keys():
        control_mean = outputs['ISOS'].mean(axis=1)
        control_mean = control_mean - control_mean.mean()
        axs[i].plot(time_mean, control_mean, label='Control', linewidth=1)
        signal_mean = outputs['GCaMP'].mean(axis=1)
        signal_mean = signal_mean - signal_mean.mean()
        axs[i].plot(time_mean, signal_mean, label='Signal', linewidth=1)
        fit_mean = outputs['Fit'].mean(axis=1)
        fit_mean = fit_mean - fit_mean.mean()
        axs[i].plot(time_mean, fit_mean, label='Fit', linewidth=1)
        axs[i].legend(loc='upper right')
        axs[i].set_xlabel('Time of event (secs)')
        axs[i].set_ylabel('Normalized light intensity (mV)')
        axs[i].set_title('Control, signal and fit data vs time')
        i += 1
    
    # Subplot 2: dFF vs time
    if 'dFF' in outputs.keys():
        if outputs['Plot different groups'] == 'Everything':
            dFF_mean = outputs['dFF'].mean(axis=1)
            dFF_error = outputs['dFF'].sem(axis=1)
            axs[i].fill_between(time_mean, dFF_mean+dFF_error, dFF_mean-dFF_error, alpha=0.5)
            axs[i].plot(time_mean, dFF_mean, linewidth=1, label='dFF')
        else:
            stat = 'dFF'
            group = outputs['Plot different groups']
            unique_names = list(set(outputs['Header '+stat].loc[group]))
            for name in unique_names:
                cols = [i for i in range(len(outputs[stat].columns))
                        if outputs['Header '+stat].loc[group][i] == name]
                zscore_mean = outputs[stat][cols].mean(axis=1)
                zscore_error = outputs[stat][cols].sem(axis=1)
                axs[i].fill_between(time_mean, zscore_mean+zscore_error, zscore_mean-zscore_error, alpha=0.5)
                axs[i].plot(time_mean, zscore_mean, linewidth=1, label=name)
        axs[i].set_xlabel('Time of event (secs)')
        axs[i].set_ylabel('dFF')
        axs[i].set_title('dFF vs time')
        axs[i].legend()
        i += 1
    
    # Subplot 3: Z-Score vs time
    if 'zScore' in outputs.keys():
        if outputs['Plot different groups'] == 'Everything':
            zscore_mean = outputs['zScore'].mean(axis=1)
            zscore_error = outputs['zScore'].sem(axis=1)
            axs[i].fill_between(time_mean, zscore_mean+zscore_error, zscore_mean-zscore_error, alpha=0.5)
            axs[i].plot(time_mean, zscore_mean, linewidth=1, label='Z-Score')
        else:
            stat = 'zScore'
            group = outputs['Plot different groups']
            unique_names = list(set(outputs['Header '+stat].loc[group]))
            for name in unique_names:
                cols = [i for i in range(len(outputs[stat].columns))
                        if outputs['Header '+stat].loc[group][i] == name]
                zscore_mean = outputs[stat][cols].mean(axis=1)
                zscore_error = outputs[stat][cols].sem(axis=1)
                axs[i].fill_between(time_mean, zscore_mean+zscore_error, zscore_mean-zscore_error, alpha=0.5)
                axs[i].plot(time_mean, zscore_mean, linewidth=1, label=name)
        axs[i].set_xlabel('Time of event (secs)')
        axs[i].set_ylabel('Z-Score')
        axs[i].set_title('Z-Score vs time')
        axs[i].legend()
        i += 1
    
    # Subplot 4: Z-Score AUC vs time window
    if 'zScore' in outputs.keys():
        pre_event_range = time_mean < 0
        pre_event_auc = []
        post_event_range = time_mean > 0
        post_event_auc = []
        for j in range(len(outputs['zScore'].columns)):
            pre_event_x = time_mean[pre_event_range]
            pre_event_y = outputs['zScore'].iloc[:, j][pre_event_range]
            pre_event_auc += [auc(pre_event_x, pre_event_y)]
            post_event_x = time_mean[post_event_range]
            post_event_y = outputs['zScore'].iloc[:, j][post_event_range]
            post_event_auc += [auc(post_event_x, post_event_y)]
        pre_event_auc_mean   = pd.Series(pre_event_auc).mean()
        pre_event_auc_error  = pd.Series(pre_event_auc).sem()
        post_event_auc_mean  = pd.Series(post_event_auc).mean()
        post_event_auc_error = pd.Series(post_event_auc).sem()
        axs[i].bar(['Pre-event','Post-event'], [pre_event_auc_mean, post_event_auc_mean], alpha=0.5)
        if len(outputs['zScore'].columns) > 1:
            axs[i].errorbar(['Pre-event', 'Post-event'], [pre_event_auc_mean, post_event_auc_mean], 
                            yerr=[pre_event_auc_error, post_event_auc_error], 
                            capsize=7, color='black', ls='none', elinewidth=1)
        x_scatter = len(pre_event_auc)*['Pre-event'] + len(post_event_auc)*['Post-event']
        y_scatter = pre_event_auc + post_event_auc
        scatter_df = pd.DataFrame({'X':x_scatter, 'Y':y_scatter})
        swarmplot(data=scatter_df, x="X", y="Y", ax=axs[i], color='black', size=4)
        # axs[i].scatter(x_scatter, y_scatter, s=10, marker='o', color='black')
        axs[i].set_xlabel('Time window')
        axs[i].set_ylabel('Z-Score area under curve')
        axs[i].set_title('Z-Score AUC vs time window')
        i += 1
    
    plt.tight_layout()    
    outputs['Figure'] = fig
    
    return(outputs)

def create_headers_for_data(inputs, outputs):
    
    stats = ['zScore','dFF','ISOS','GCaMP']
    stats_to_export = [stat for stat in stats if inputs['Export '+stat] == True]
    
    for stat in stats_to_export:

        # Create headers for the results.
        header = {}
        header['']        = list(outputs[stat].columns+1)
        event_ind         = inputs['Event names'].index(inputs['Name'])
        event_start_times = inputs['Event start times'][event_ind]
        header['Time of event onsets (secs)'] = event_start_times
        # Find the time to baseline after the event.
        time_mean = outputs['Timestamps'].mean(axis=1)
        if stat == 'zScore':
            BL_thresh = 0.1
            post_event_range = outputs[stat].index[time_mean > 0]
            list_baseline_times = []
            for col in outputs[stat].columns:
                found_baseline = False
                for i in post_event_range:
                    if (-BL_thresh <= outputs[stat].at[i,col] <= BL_thresh):
                        list_baseline_times += [time_mean.loc[i]]
                        found_baseline = True
                        break
                # If the signal does not return to baseline after the event, 
                # list the last possible time point.
                if found_baseline == False:
                    list_baseline_times += [time_mean.iloc[-1]]
            row_name = f'Time to baseline (between -{BL_thresh} and {BL_thresh}) after event'
            header[row_name] = list_baseline_times
        # Find the area under curve.
        pre_event_range = time_mean < 0
        pre_event_auc = []
        post_event_range = time_mean > 0
        post_event_auc = []
        for j in range(len(outputs['zScore'].columns)):
            pre_event_x = time_mean[pre_event_range]
            pre_event_y = outputs['zScore'].iloc[:, j][pre_event_range]
            pre_event_auc += [auc(pre_event_x, pre_event_y)]
            post_event_x = time_mean[post_event_range]
            post_event_y = outputs['zScore'].iloc[:, j][post_event_range]
            post_event_auc += [auc(post_event_x, post_event_y)]
        header['Pre-event AUC'] = pre_event_auc
        header['Post-event AUC'] = post_event_auc
        Zscore_max_threshold = 1
        header['Max values'] = list(outputs[stat].max())
        # Find the time point at which the max Z-score values occur.
        header['Time of max values'] = list(time_mean[outputs[stat].idxmax()])
        row_name = 'Max value above '+str(Zscore_max_threshold)+'?'
        header[row_name] = [('Yes' if max1>Zscore_max_threshold else 'No') 
                            for max1 in header['Max values']]
        header['Filename'] = [os.path.basename(inputs['Import location'])]*len(header[''])
        header['Custom name'] = [inputs['Analysis name']]*len(header[''])
        header['Animal ID'] = [inputs['Animal ID']]*len(header[''])
        header = pd.DataFrame(header).T
        outputs['Header '+stat] = header
        
    return(outputs)

def combine_header_and_data(outputs):
    
    stats = ['zScore','dFF','ISOS','GCaMP','Fit']
    stats_to_export = [stat for stat in stats if 'Header '+stat in outputs.keys()]
    
    for stat in stats_to_export:
        # Convert the header to a dataframe and add more columns.
        header = outputs['Header '+stat]
        header = header.reset_index()
        num_extra_lines = len(header.index) - 1
        header.insert(1, 'Mean', ['Mean of events']+num_extra_lines*[''])
        header.insert(1, 'Time', ['Time stamps (secs)']+num_extra_lines*[''])
        
        # Format the results.
        blank_col   = pd.Series(len(outputs[stat])*[''], name='index')
        data_mean = outputs[stat].mean(axis=1)
        data_mean.name = 'Mean'
        time_mean = outputs['Timestamps'].mean(axis=1)
        time_mean.name = 'Time'
        outputs[stat] = pd.concat([blank_col, time_mean, data_mean, outputs[stat]], axis=1)
        
        # Add the headers to the results.
        outputs[stat] = pd.concat([header, outputs[stat]])
        outputs[stat].index = range(len(outputs[stat]))
    
    return(outputs)

def export_preview_image_peri_events(inputs, outputs):
    
    export_name = (os.path.basename(inputs['Import location']) + "_" + inputs['Animal ID'] + "_" +
                   inputs['Analysis name']    + "_" + inputs['ISOS wavelength']  + '_' +
                   inputs['ISOS color'][-2:]  + "_" + inputs['GCaMP wavelength'] + "_" +
                   inputs['GCaMP color'][-2:] + ".png")
    export_destination = os.path.join(inputs['Export location'], export_name)
    outputs['Figure'].savefig(export_destination)

def export_analysed_data_peri_events(inputs, outputs):
    
    stats = ['zScore','dFF','ISOS','GCaMP','Fit']
    stats_to_export = [stat for stat in stats if inputs['Export '+stat] == True]
    for stat in stats_to_export:
        export_name = (os.path.basename(inputs['Import location']) + '_' + inputs['Analysis'] + 
                       "_"+stat+"_" + '_' + inputs['Analysis name'] + "_" + 
                       inputs['ISOS wavelength'] + '_' + inputs['ISOS color'][-2:] + "_" + 
                       inputs['GCaMP wavelength'] + "_" + inputs['GCaMP color'][-2:] + ".csv")
        export_destination = os.path.join(inputs['Export location'], export_name)
        outputs[stat].to_csv(export_destination, index=False, header=False)
