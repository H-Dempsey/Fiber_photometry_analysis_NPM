import pandas as pd
import numpy as np
from tabulate import tabulate
import os
import sys

def read_existing_settings_file(inputs):
    
    event_types = ['Point event','Mutually exclusive','Start-stop event']
    event_keys  = ['a','b','c','d','e','f','g','h','i','j','k','l','m',
                   'n','o','p','q','r','s','t','u','v','w','x','y','z']
    video_folder_path  = os.path.dirname(inputs['Import location'])
    settings_file_path = os.path.join(video_folder_path, "Manual_scoring_settings.csv")
    
    if os.path.isfile(settings_file_path) == False:
        print('Make sure the "Manual_scoring_settings.csv" file is located in '+
              'the same folder as the import video file.')
        print('These are automatically created in this location after defining '+
              'new settings.')
        sys.exit()
    
    df = pd.read_csv(settings_file_path)
    inputs['Event names'] = list(df['Event names'].astype(str))
    inputs['Event types'] = list(df['Event types'].astype(str))
    inputs['Event keys']  = list(df['Event keys' ].astype(str))
    
    # Check whether a key was entered that was not allowed.
    for key in inputs['Event keys']:
        if key not in event_keys:
            print(key+' is not allowed as an event key. Only letters of the '+
                  'alphabet should be in the "Manual_scoring_settings.csv" file.')
            sys.exit()
            
    # Check whether the event types are only within 'Point event', 'Mutually 
    # exclusive' and 'Start-stop event'.
    for type1 in inputs['Event types']:
        if type1 not in event_types:
            print(type1+' is not allowed as an event type. Only "Point event", '+
                  '"Mutually exclusive" and "Start-stop event" are allowed in '+
                  'the "Manual_scoring_settings.csv" file.')
            sys.exit()
            
    return(inputs)

def export_manual_scoring_settings(inputs):
    # Export the manual scoring settings.
    headings = ['Event types', 'Event keys', 'Event names']
    table = {heading:inputs[heading] for heading in headings}
    df = pd.DataFrame(table)
    export_settings_path = os.path.join(
        os.path.dirname(inputs['Import location']), 'Manual_scoring_settings.csv')
    df.to_csv(export_settings_path, index=False)
