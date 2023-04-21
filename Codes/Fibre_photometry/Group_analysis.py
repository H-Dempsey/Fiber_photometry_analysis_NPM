import pandas as pd
import os
        
def initialize_grouped_data():
    
    stats = ['zScore','dFF','ISOS','GCaMP','Fit']
    grouped_data = {'Timestamps':[]}
    for stat in stats:
        grouped_data[stat]           = []
        grouped_data['Header '+stat] = []
    return(grouped_data)

def add_to_grouped_data(grouped_data, inputs, outputs):
    
    # Add the data to grouped_data.
    stats = ['zScore','dFF','ISOS','GCaMP','Fit']
    stats_to_export = [stat for stat in stats if inputs['Export '+stat] == True]
    grouped_data['Timestamps'] += [outputs['Timestamps']]
    for stat in stats_to_export:
        grouped_data[stat]           += [outputs[stat]]
        grouped_data['Header '+stat] += [outputs['Header '+stat]]
        
    return(grouped_data)

def organise_grouped_data(grouped_data):
    
    # Delete stats for which no data was grouped together.
    remove_keys = []
    for key in grouped_data.keys():
        if grouped_data[key] == []:
            remove_keys += [key]
    for key in remove_keys:
        grouped_data.pop(key)
    
    # Concatenate the lists of dataframes into a master dataframe.
    shortest_len = min([len(time_df) for time_df in grouped_data['Timestamps']])
    grouped_data['Timestamps'] = pd.concat(grouped_data['Timestamps'], axis=1)[:shortest_len]
    stats = ['zScore','dFF','ISOS','GCaMP','Fit']
    stats_to_export  = [stat for stat in stats if stat in grouped_data.keys()
                        if stat != 'Plot different groups']
    for stat in stats_to_export:
        grouped_data[stat] = pd.concat(grouped_data[stat], axis=1)[:shortest_len]
        grouped_data[stat].columns = range(len(grouped_data[stat].columns))
        grouped_data['Header '+stat] = pd.concat(grouped_data['Header '+stat], axis=1) 
        grouped_data['Header '+stat].columns = range(len(grouped_data['Header '+stat].columns))  
        
    return(grouped_data)

def export_grouped_plots(grouped_data, inputs):
    
    # Create a figure.
    export_destination = os.path.join(inputs['Grouped data location'], 
                                      inputs['Grouped data file name']+'.png')
    grouped_data['Figure'].savefig(export_destination)
    
def export_grouped_data(grouped_data, inputs):
    
    # Export the data.
    stats = ['zScore','dFF','ISOS','GCaMP','Fit']
    stats_to_export  = [stat for stat in stats if stat in grouped_data.keys()]
    for stat in stats_to_export:
        export_destination = os.path.join(inputs['Grouped data location'], 
                                          inputs['Grouped data file name']+'.csv')
        grouped_data[stat].to_csv(export_destination, index=False, header=False)
        