import PySimpleGUI as sg
from Fibre_photometry.Data_processing import cursory_import_NPM_data
import sys
import os

def recognise_bool(value):
    dict1 = {'True':True, 'False':False}
    return(dict1[value])
def convert_color(value):
    convert_color = {'0 green':'Region0G','1 red':'Region1R','2 green':'Region2G','3 red':'Region3R',
                     '0 red':'Region0R','1 green':'Region1G','2 red':'Region2R','3 green':'Region3G'}
    return(convert_color[value])
def wavelength_to_ledstate(wavelength):
    convert = {'415':1, '470':2, '560':4}
    return(convert[wavelength])

def create_loading_bar(max_value):
    # Define the layout of the window
    layout = [[sg.Text("Please wait while each folder within the master folder is analysed.")],
              [sg.ProgressBar(max_value, orientation='h', size=(30, 20), key='progressbar')]]

    # Create the window
    window = sg.Window('Loading Bar Example', layout)

    return window

def update_loading_bar(window, value):
    # Update the progress bar
    window['progressbar'].update_bar(value)

def choose_which_type_analysis(inputs):

    # Check whether there is a settings excel file.
    default = {}
    default['Settings'] = 'True'
    sg.theme("DarkTeal2")
    layout  = [
        [sg.Text("Choose how you want the analysis to be done. \n"+
                 "Choose 'Manually score videos' if you are using \n"+
                 "this for the first time. Make sure the data for \n"+
                 "each mouse are in separate folders. \n")],
        [sg.Button("Analyse one folder", 
         tooltip=("Perform peri-events analysis (including creating video \n"+
                  "snippets of events) or whole recording analysis (including \n"+
                  "peak detection).")), 
         sg.Button("Analyse many folders",
         tooltip=("Perform peri events analysis for many folders at once. \n"+
                  "This also includes grouped analysis."))],
        [sg.Button('Import settings file',
         tooltip=("Import a settings excel file that was exported after following \n"+
                  "the 'Analyse one folder' route.")), 
         sg.Button("Manually score videos",
         tooltip="Open a video in a GUI and manually events you are interested in.")]]
    window  = sg.Window('Photometry Analysis', layout)
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event=="Exit":
            window.close()
            sys.exit()
        elif event == "Analyse many folders":
            inputs['Analysis type'] = "Analyse many folders"
            window.close()
            break
        elif event == "Analyse one folder":
            inputs['Analysis type'] = "Analyse one folder"
            window.close()
            break
        elif event == 'Import settings file':
            inputs['Analysis type'] = 'Import settings file'
            window.close()
            break
        elif event == 'Manually score videos':
            inputs['Analysis type'] = 'Manually score videos'
            window.close()
            break
    
    return(inputs)

# Put in the options from an excel file.

def choose_location_for_grouped_analysis(inputs):
    
    default = {}
    default['Grouped data location'] = r"C:\Users\hazza\Desktop\Lab meeting presentation - Florey"
    sg.theme("DarkTeal2")
    layout  = []
    layout += [[sg.T("")],[sg.Text("Choose the location of the folder containing "+
                                   "many folders for analysis.", tooltip=(
                'Choose the location of a master folder that contains many subfolders \n'+
                'for analysis. Folders inside those subfolders will be ignored.'))], 
                [sg.Input(key="Grouped data location",enable_events=True,
                         default_text=default["Grouped data location"]),
                sg.FolderBrowse(key="Import2")]]
    layout += [[sg.T("")],[sg.Button("Submit")]]
    window  = sg.Window('Photometry Analysis', layout)
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event=="Exit":
            window.close()
            sys.exit()
        elif event == "Submit":
            inputs["Grouped data location"] = values["Grouped data location"]
            window.close()
            break
        
    return(inputs)

# Put in the options from an excel file.

def choose_location_for_settings_file(inputs):
    
    default = {}
    default['Settings file'] = r"D:\Eva Photometry-20230224T030147Z-001\Example folders\Settings1.xlsx"
    sg.theme("DarkTeal2")
    layout  = []
    layout += [[sg.T("")],[sg.Text("Choose the location of the settings excel file.",
                tooltip=('Choose the location of the settings excel file. These \n'+
                         'are exported automatically after progressing through the \n'+
                         '"Analyse one folder" steps.'))], 
                [sg.Input(key="Settings file",enable_events=True,
                         default_text=default["Settings file"]),
                sg.FileBrowse(key="Import2")]]
    layout += [[sg.T("")],[sg.Button("Submit")]]
    window  = sg.Window('Photometry Analysis', layout)
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event=="Exit":
            window.close()
            sys.exit()
        elif event == "Submit":
            inputs["Settings file"] = values["Settings file"]
            window.close()
            break
        
    return(inputs)

# Put in the options from an excel file.

def choose_the_groups_to_plot(inputs):
    
    default = {}
    default['Group type'] = 'Everything'
    sg.theme("DarkTeal2")
    layout  = []
    layout += [[sg.T("")],[sg.Text('Choose what groups to plot in the grouped preview image.',
                tooltip=('Once group analysis is done, a plot is exported of all \n'+
                         'the curves in each folder. These can be color-coded and \n'+
                         'labelled by custom info.')),
                sg.Combo(['Everything','Custom name','Animal ID','Filename'],
                         default_value=default['Group type'],key='Plot different groups')]]
    layout += [[sg.T("")], [sg.Button("Submit")]]
    window  = sg.Window('Photometry Analysis', layout)
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event=="Exit":
            window.close()
            sys.exit()
        elif event == "Submit":
            inputs['Plot different groups'] = values['Plot different groups']
            window.close()
            break
        
    return(inputs)

info = {}
info['ISOS wavelength'] = 'Choose the wavelength for the control data.'
info['ISOS color'] = 'Choose the color channel for the control data.'
info['GCaMP wavelength'] = 'Choose the wavelength for the signal data.'
info['GCaMP color'] = 'Choose the color channel for the signal data.'
info['Event name'] = ('Choose the name of the event for peri-events analysis. \n'+
    'These events come from CSV file after manual scoring with the column heading \n'+
    '"Event names", "Event start times (secs)", etc.')
info['Analysis name'] = ('Choose a custom name for this folder (e.g. psilocybin-treated) \n'+
    'so analysis can be grouped in different ways (optional).')
info['Animal ID'] = 'Choose a custom name for the animal used (optional).'
info['t-range'] = ('Choose the time before each event and total window duration. For \n'+
    'example -5, 10 means extract the 5 secs before and 5 secs after each event.')
info['Baseline type'] = ('Choose the type of baseline period for the Z-score calculation. \n'+
    'If "changing" is selected, type in the secs before the event (e.g. -5, -1). \n'+
    'If "constant" is selected, type in the secs since the NPM box was turned on \n'+
    '(e.g. 2000, 2100). If "constant (time since start)" is selected, fill in the secs \n'+
    'since the start of the recording (e.g. 60, 180).')
info['Baseline period'] = ('If "changing" is the baseline period type, fill in the \n'+
    'secs before the event (e.g. -5, -1). If "constant (overall)" is the baseline period type, \n'+
    'fill in the secs since the NPM box was turned on (e.g. 2000, 2100). If \n'+
    '"constant (time since start)" is the baseline period type, fill in the secs \n'+
    'since the start of the recording (e.g. 60, 180).')
info['Create video snippets'] = ('Create video snippets where the video for each time + \n'
    'window is displayed above a live plot of the Z-score/dFF/etc. over time.')
info['Video snippet data to plot'] = 'Choose the data type to plot in the video snippet.'
info['Video snippet time type'] = ('Choose the type of time window to plot in the video \n'+
    'snippet. I recommend keeping this as "same as t-range".')
info['Video snippet time range'] = ('If "Video snippet time type" is set to "Custom", \n'+
    'Choose the time window to plot in the video snippet. It must be smaller and not \n'+
    'larger than the t-range. Otherwise, ignore this section.')
info['Export preview image'] = ('Export a preview image of the control, signal and detrended fit, \n'+
    'dFF, Z-score and area under curve over time.')
info['Plot different groups'] = ('In the preview plot of the grouped data, choose to plot \n'+
    'the custom names, animal IDs or folder names separately or everything together.')
info['Export Z-Score'] = 'Export the anlaysed Z-score data for each event.'
info['Export dFF'] = 'Export the analysed dFF data for each event.'
info['Export Fit'] = 'Export the detrended fit data for each event.'
info['Export ISOS'] = 'Export the raw control data for each event.'
info['Export GCaMP'] = 'Export the raw signal data for each event.'

def analyse_many_folders(grouped_data, inputs):
    
    sg.theme("DarkTeal2")
    import_location = inputs['Grouped data location']
    col_headings = next(os.walk(import_location))[1]
    import_locations = [os.path.join(import_location, folder) for folder in col_headings]
    input_info = [cursory_import_NPM_data(import_location) for import_location in import_locations]
    
    # If there are no events for peri-event analysis, skip this folder.
    exclude_ind = [i for i in range(len(input_info)) if 'Event names' not in input_info[i].keys()]
    for ind in exclude_ind:
        col_headings.pop(ind)
        import_locations.pop(ind)
        input_info.pop(ind)
    
    # Define the column and row headings
    row_headings = ['ISOS wavelength','ISOS color','GCaMP wavelength','GCaMP color',
       'Event name','Analysis name','Animal ID','t-range','Baseline type',
       'Baseline period','Create video snippets','Video snippet data to plot',
       'Video snippet time type','Video snippet time range','Export preview image',
       'Export Z-Score','Export dFF','Export Fit',
       'Export ISOS','Export GCaMP']
    color_inputs = ['ISOS color','GCaMP color']
    epoch_inputs = ['t-range', 'Video snippet time range']
    true_bool_inputs = ['Export preview image', 'Export Z-Score']
    bool_inputs = ['Create video snippets','Export dFF','Export Fit','Export ISOS',
                   'Export GCaMP']
    
    columns = []
    header_col1  = [[sg.Text('')]]+[[sg.Text(name, tooltip=info[name])] for name in row_headings]
    columns    += [sg.Column(header_col1)]
    for i in range(len(col_headings)):
        col = [[sg.Text(col_headings[i])]]
        for j in range(len(row_headings)):
            if row_headings[j] in bool_inputs:
                col += [[sg.Combo(['True','False'],default_value='False',
                                  key=row_headings[j]+col_headings[i])]]
            elif row_headings[j] in true_bool_inputs:
                col += [[sg.Combo(['True','False'],default_value='True',
                                  key=row_headings[j]+col_headings[i])]]
            elif row_headings[j] == 'ISOS wavelength':
                default = ('415' if '415' in input_info[i]['Wavelengths'] 
                           else input_info[i]['Wavelengths'][0])
                col += [[sg.Combo(input_info[i]['Wavelengths'],default_value=default,
                                  key=row_headings[j]+col_headings[i])]]
            elif row_headings[j] == 'GCaMP wavelength':
                default = ('470' if '470' in input_info[i]['Wavelengths']
                           else input_info[i]['Wavelengths'][0])
                col += [[sg.Combo(input_info[i]['Wavelengths'],default_value=default,
                                  key=row_headings[j]+col_headings[i])]]
            elif row_headings[j] in color_inputs:
                col += [[sg.Combo(input_info[i]['Colors'],default_value=input_info[i]['Colors'][0],
                                  key=row_headings[j]+col_headings[i])]]
            elif row_headings[j] in epoch_inputs:
                col += [[sg.Input(-5, size=(7,1), key=row_headings[j]+col_headings[i]+'1'), 
                         sg.Input(10, size=(7,1), key=row_headings[j]+col_headings[i]+'2')]]
            elif row_headings[j] == 'Baseline period':
                col += [[sg.Input(-5, size=(7,1), key=row_headings[j]+col_headings[i]+'1'), 
                         sg.Input(-1, size=(7,1), key=row_headings[j]+col_headings[i]+'2')]]
            elif row_headings[j] == 'Analysis name':
                col += [[sg.Input('Event', size=(16,1), key=row_headings[j]+col_headings[i])]]
            elif row_headings[j] == 'Animal ID':
                col += [[sg.Input('WT', size=(16,1), key=row_headings[j]+col_headings[i])]]
            elif row_headings[j] == 'Event name':
                col += [[sg.Combo(input_info[i]['Event names'],default_value=input_info[i]['Event names'][0], 
                                  key=row_headings[j]+col_headings[i])]]
            elif row_headings[j] == 'Baseline type':
                col += [[sg.Combo(['Changing','Constant (overall)','Constant (time since start)'],
                                  default_value='Changing', key=row_headings[j]+col_headings[i],
                                  size=(20,1))]]
            elif row_headings[j] == 'Video snippet data to plot':
                col += [[sg.Combo(['zScore','dFF','ISOS','GCaMP','Fit'], default_value='zScore', 
                                  key=row_headings[j]+col_headings[i])]]
            elif row_headings[j] == 'Video snippet time type':
                col += [[sg.Combo(['Same as t-range', 'Custom'],key=row_headings[j]+col_headings[i],
                                  default_value='Same as t-range')]]
        columns += [sg.Column(col)]
    layout  = []
    layout += [[sg.Frame('Hover your cursor over the row headers to find out what they mean', 
                         layout=[[sg.Column([columns], scrollable=True, size=(1100,400))]])]]
    layout += [[sg.Text('Auto-fill entry from column 1'), 
                sg.Combo(row_headings, default_value=row_headings[0], key='Auto-fill value'), 
                sg.Button('Auto-fill')]]
    layout += [[sg.Text('Choose what groups to plot in the grouped preview image.',
                        tooltip=info['Plot different groups']),
                sg.Combo(['Everything','Custom name','Animal ID','Filename'],
                         default_value='Everything',key='Plot different groups')]]
    layout += [[sg.T("")], [sg.Button("Submit")]]
    
    window = sg.Window('Photometry Analysis', layout)
    
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event=="Exit":
            window.close()
            break
        if event == 'Auto-fill':
            row_heading = values['Auto-fill value']
            for i in range(len(col_headings)):
                if row_heading in ['t-range', 'Video snippet time range', 'Baseline period']:
                    window.Element(row_heading+col_headings[i]+'1').Update(
                        values[row_heading+col_headings[0]+'1'])
                    window.Element(row_heading+col_headings[i]+'2').Update(
                        values[row_heading+col_headings[0]+'2'])
                else:
                    window.Element(row_heading+col_headings[i]).Update(
                        values[row_heading+col_headings[0]])
        if event == 'Submit':
            list_inputs = []
            for col_heading in col_headings:
                inputs = {}
                inputs['Create grouped data']    = True
                inputs['Grouped data file name'] = 'Grouped data'
                inputs['Grouped data location'] = import_location
                inputs['Import location']  = os.path.join(import_location, col_heading)
                inputs['Export location']  = os.path.join(import_location, col_heading)
                inputs['Analysis']         = 'Peri-events'
                inputs['ISOS wavelength']  = values['ISOS wavelength'+col_heading]
                inputs['ISOS color']       = convert_color(values['ISOS color'+col_heading])
                inputs['ISOS ledstate']    = wavelength_to_ledstate(inputs['ISOS wavelength'])
                inputs['GCaMP wavelength'] = values['GCaMP wavelength'+col_heading]
                inputs['GCaMP color']      = convert_color(values['GCaMP color'+col_heading])
                inputs['GCaMP ledstate']   = wavelength_to_ledstate(inputs['GCaMP wavelength'])
                inputs['Name']             = values['Event name'+col_heading]
                inputs['Analysis name']    = values['Analysis name'+col_heading]
                inputs['Animal ID']        = values['Animal ID'+col_heading]
                inputs['t-range']         = [float(values['t-range'+col_heading+'1']),   
                                             float(values['t-range'+col_heading+'2'])]
                inputs['Baseline type']   = values['Baseline type'+col_heading]
                inputs['Baseline period'] = [float(values['Baseline period'+col_heading+'1']), 
                                             float(values['Baseline period'+col_heading+'2'])]
                inputs['Image']           = recognise_bool(values["Export preview image"+col_heading])
                inputs['Create snippets'] = recognise_bool(values['Create video snippets'+col_heading])
                inputs['Snippets signal'] = values['Video snippet data to plot'+col_heading]
                inputs['Snippets window'] = values['Video snippet time type'+col_heading]
                inputs['Snippets window size'] = [float(values['Video snippet time range'+col_heading+'1']),   
                                                  float(values['Video snippet time range'+col_heading+'2'])]
                inputs['Export Fit']    = recognise_bool(values['Export Fit'+col_heading])
                inputs['Export ISOS']   = recognise_bool(values['Export ISOS'+col_heading])
                inputs['Export GCaMP']  = recognise_bool(values['Export GCaMP'+col_heading])
                inputs['Export dFF']    = recognise_bool(values['Export dFF'+col_heading])
                inputs['Export zScore'] = recognise_bool(values['Export Z-Score'+col_heading])
                list_inputs += [inputs]
            grouped_data['Plot different groups'] = values['Plot different groups']
            window.close()
            break
    
    return(grouped_data, list_inputs)

# NPM -> choose the type of analysis
    
def choose_basic_NPM_options(inputs):

    # Choose the import location, export location and setup.
    default = {}
    default["Import location"] = r'C:\Users\hazza\Desktop\Lab meeting presentation - Florey\Example folder 1'
    default["Export location"] = r'C:\Users\hazza\Desktop\Lab meeting presentation - Florey\Example folder 1'
    default["ISOS wavelength"] = '415'
    default["ISOS color"]      = '0 green'
    default["GCaMP wavelength"]= '470'
    default["GCaMP color"]     = '0 green'
    default["Analysis"]        = 'Peri-events'
    sg.theme("DarkTeal2")
    layout  = []
    layout += [[sg.T("")], [sg.Text("Choose a folder for the import location",
                tooltip='Choose the location of the folder with the input data.'), 
                sg.Input(key="Import" ,enable_events=True,default_text=default["Import location"]),
                sg.FolderBrowse(key="Import2")]]
    layout += [[sg.T("")], [sg.Text("Choose a folder for the export location",
                tooltip='Choose the location of the folder to export data. \n'+
                        'Usually this is the same as the import folder.'),
                sg.Input(key="Export" ,enable_events=True,default_text=default["Import location"]),
                sg.FolderBrowse(key="Export2")]]
    layout += [[sg.T("")],[sg.Text("Choose the wavelength and color for the ISOS channel", size=(41,1),
                tooltip='Choose the wavelength and color for the control channel. \n'+
                        'In the photometry recording data file, the wavelengths \n'+
                        '415, 470 and 560 are labelled by the led states 1, 2 \n'+
                        'and 4 respectively. For the colors, "Region0G" means \n'+
                        '"0 green", "Region 1R" means "1 red" etc.'), 
                sg.Combo(['415', '470', '560'],key="ISOS wavelength",enable_events=True,default_value=default["ISOS wavelength"]),
                sg.Combo(['0 green', '0 red', '1 green', '1 red', '2 green', '2 red', '3 green', '3 red'],
                         key="ISOS color",enable_events=True,default_value=default["ISOS color"])]]
    layout += [[sg.T("")],[sg.Text("Choose the wavelength and color for the GCaMP channel", size=(41,1), 
                tooltip='Choose the wavelength and color for the signal channel. \n'+
                        'In the photometry recording data file, the wavelengths \n'+
                        '415, 470 and 560 are labelled by the led states 1, 2 \n'+
                        'and 4 respectively. For the colors, "Region0G" means \n'+
                        '"0 green", "Region 1R" means "1 red" etc.'), 
                sg.Combo(['415', '470', '560'],key="GCaMP wavelength",enable_events=True,default_value=default["GCaMP wavelength"]),
                sg.Combo(['0 green', '0 red', '1 green', '1 red', '2 green', '2 red', '3 green', '3 red'],
                         key="GCaMP color",enable_events=True,default_value=default["GCaMP color"])]]
    layout += [[sg.T("")],[sg.Text("Choose the type of analysis.",
                tooltip='"Peri-events" means extracting the x secs before and y \n'+
                        'secs after a single event. In here, you can also create \n'+
                        'video snippets of the event aligned with a graph of the \n'+
                        'photometry data. \n\n'+
                        '"Whole recording" means creating a plot of the whole \n'+
                        'recording. You can also annotate events over the top, \n'+
                        'perform peak analysis and annotate those peaks on the plot.'), 
                sg.Combo(['Peri-events', 'Whole recording'],
                key="Analysis",enable_events=True,default_value=default["Analysis"])]]
    layout += [[sg.T("")], [sg.Button("Submit")]]
    window  = sg.Window('Photometry Analysis', layout)
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event=="Exit":
            window.close()
            sys.exit()
        elif event == "Submit":
            if values['Analysis'] == 'Peri-events':
                inputs['Create grouped data']    = False
                inputs['Grouped data file name'] = 'Grouped data'
                inputs['Grouped data location']  = r'C:\Users\hazza\Downloads\Test 140302023'
            inputs['Import location']  = values["Import"]
            inputs['Export location']  = values["Export"]
            inputs['ISOS wavelength']  = values['ISOS wavelength']
            inputs['ISOS color']       = convert_color(values['ISOS color'])
            inputs['ISOS ledstate']    = wavelength_to_ledstate(inputs['ISOS wavelength'])
            inputs['GCaMP wavelength'] = values['GCaMP wavelength']
            inputs['GCaMP color']      = convert_color(values['GCaMP color'])
            inputs['GCaMP ledstate']   = wavelength_to_ledstate(inputs['GCaMP wavelength'])
            inputs['Analysis']         = values["Analysis"]
            window.close()
            break
    print('Import location is '+inputs['Import location'])
    print('Export location is '+inputs['Export location'])
    print('Type of analysis is '+inputs['Analysis'])
    
    return(inputs)
    
# NPM -> choose the type of analysis
    
def choose_name_NPM_event(inputs):

    # Choose the type of TTL.
    
    default = {}
    default["TTL"] = inputs['Event names'][0]
    default["Custom"] = "Event"
    default["Animal ID"] = "None"
    sg.theme("DarkTeal2")
    layout  = []
    layout += [[sg.T("")],[sg.Text("Choose the name of the TTL event.", tooltip=info['Event name']), 
                sg.Combo(inputs['Event names'], key="Name", enable_events=True, default_value=default["TTL"])]]
    layout += [[sg.T("")], [sg.Text("Choose a custom name for this event.", tooltip=info['Analysis name']), 
                sg.Input(key="Analysis name",enable_events=True,default_text=default["Custom"], size=(25,1))]]
    layout += [[sg.T("")], [sg.Text("Choose an animal ID.", tooltip=info['Animal ID']), 
                sg.Input(key="Animal ID",enable_events=True,default_text=default["Animal ID"], size=(25,1))]]
    layout += [[sg.T("")], [sg.Button("Submit")]]
    window  = sg.Window('Photometry Analysis', layout)
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event=="Exit":
            window.close()
            sys.exit()
        elif event == "Submit":
            inputs['Name'] = values['Name']
            inputs['Analysis name'] = values['Analysis name']
            inputs['Animal ID']     = values['Animal ID']
            window.close()
            break
    print('The name of the event is '+inputs['Analysis name'])
    
    return(inputs)

# TDT -> peri-event TTL -> ... -> select options before running the code     

def choose_peri_event_options(inputs):
    
    default = {}
    default["t-range"]          = [-10,20]
    default["Baseline type"]    = 'Changing'
    default["Baseline period"]  = [-10,-5]
    default["Image"]            = 'True'
    default["Video"]            = 'False'
    default["zScore"]           = 'True'
    default["dFF"]              = 'False'
    default["Fit"]              = 'False'
    default["ISOS"]             = 'False'
    default["GCaMP"]            = 'False'
    sg.theme("DarkTeal2")
    layout = [[sg.T("")],
        [sg.Text("Choose the t-range (time before event, duration of window) (secs)", 
                 tooltip=info['t-range']), 
         sg.Input(key="TRANGE1",enable_events=True,
                  default_text=default["t-range"][0],size=(10,1)), 
         sg.Input(key="TRANGE2",enable_events=True,
                  default_text=default["t-range"][1],size=(10,1))],[sg.T("")],
        [sg.Text("Choose the baseline period (secs)", tooltip=info['Baseline type']), 
         sg.Combo(['Changing','Constant (overall)','Constant (time since start)'],
                  key="Baseline type",enable_events=True,
                  default_value=default["Baseline type"],size=(20,1)),
         sg.Input(key="BASELINE1",enable_events=True,
                  default_text=default["Baseline period"][0],size=(10,1)),
         sg.Input(key="BASELINE2",enable_events=True,
                  default_text=default["Baseline period"][1],size=(10,1))],[sg.T("")],
        [sg.Text("Create video snippets of epochs?", tooltip=info['Create video snippets']), 
         sg.Combo(['True','False'],key="Video",enable_events=True,
                  default_value=default['Video'])],[sg.T("")],
        [sg.Text("Save preview image of data?", tooltip=info['Export preview image']), 
         sg.Combo(['True','False'],key="Image",enable_events=True,
                  default_value=default['Image'])],[sg.T("")],
        [sg.Text("Save Z-Score data to CSV?", tooltip=info['Export Z-Score']), 
         sg.Combo(['True','False'],key="zScore",enable_events=True,
                  default_value=default['zScore'])],[sg.T("")],
        [sg.Text("Save dFF data to CSV?", tooltip=info['Export dFF']), 
         sg.Combo(['True','False'],key="dFF",enable_events=True,
                  default_value=default['dFF'])],[sg.T("")],
        [sg.Text("Save ISOS data to CSV?", tooltip=info['Export ISOS']), 
         sg.Combo(['True','False'],key="ISOS",enable_events=True,
                  default_value=default['ISOS'])],[sg.T("")],
        [sg.Text("Save GCaMP data to CSV?", tooltip=info['Export GCaMP']), 
         sg.Combo(['True','False'],key="GCaMP",enable_events=True,
                  default_value=default['GCaMP'])],[sg.T("")],
        [sg.Text("Save ISOS-GCaMP fit data to CSV?", tooltip=info['Export Fit']), 
         sg.Combo(['True','False'],key="Fit",enable_events=True,
                  default_value=default['Fit'])],[sg.T("")],
        [sg.Button("Submit")]]
    window = sg.Window('Photometry Analysis', layout)
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event=="Exit":
            window.close()
            sys.exit()
        elif event == "Submit":
            inputs['t-range']         = [float(values['TRANGE1']),   
                                         float(values['TRANGE2'])]
            inputs['Baseline type']   = values['Baseline type']
            inputs['Baseline period'] = [float(values['BASELINE1']), 
                                         float(values['BASELINE2'])]
            inputs['Image']           = recognise_bool(values["Image"])
            inputs['Create snippets'] = recognise_bool(values['Video'])
            inputs['Export Fit']    = recognise_bool(values['Fit'])
            inputs['Export ISOS']   = recognise_bool(values['ISOS'])
            inputs['Export GCaMP']  = recognise_bool(values['GCaMP'])
            inputs['Export dFF']    = recognise_bool(values['dFF'])
            inputs['Export zScore'] = recognise_bool(values['zScore'])
            window.close()
            break
        
    return(inputs)
    
def choose_video_snippet_options(inputs):
    
    # Choose the type of TTL.
    default = {}
    default["Signal"] = 'zScore'
    default["Window"] = 'Same as t-range'
    default["Window size"] = ([0,0] if 't-range' not in inputs.keys() else inputs['t-range'])
    sg.theme("DarkTeal2")
    layout  = [[sg.T("")],
        [sg.Text("Choose the signal to plot.", tooltip=info['Video snippet data to plot']), 
          sg.Combo(['ISOS', 'GCaMP', 'dFF', 'zScore', 'Fit'], key='Signal', 
                  enable_events=True, default_value=default["Signal"])], [sg.T("")],
        [sg.Text("Choose the time window to plot.", tooltip=info['Video snippet time type']), 
          sg.Combo(['Same as t-range', 'Custom'],key='Window',
                  enable_events=True, default_value=default["Window"])], [sg.T("")],
        [sg.Text("Choose the time before event and duration of window (secs).", 
                  tooltip=info['Video snippet time range'], key="Window size", visible=False), 
          sg.Input(key="Window size 1",enable_events=True, 
                  default_text=default["Window size"][0], size=(10,1),visible=False),
          sg.Input(key="Window size 2",enable_events=True, 
                  default_text=default["Window size"][1], size=(10,1),visible=False)]]
    layout += [[sg.T("")], [sg.Button("Submit")]]
    window  = sg.Window('Photometry Analysis', layout)
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event=="Exit":
            window.close()
            sys.exit()
        if values["Window"] == "Custom":
            window.Element("Window size").Update(visible=True)
            window.Element("Window size 1").Update(visible=True)
            window.Element("Window size 2").Update(visible=True)
        if values["Window"] == "Same as t-range":
            window.Element("Window size").Update(visible=False)
            window.Element("Window size 1").Update(visible=False)
            window.Element("Window size 2").Update(visible=False)
        if event == "Submit":
            inputs['Snippets signal'] = values['Signal']
            inputs['Snippets window'] = values['Window']
            inputs['Snippets window size'] = [float(values['Window size 1']),   
                                              float(values['Window size 2'])]
            window.close()
            break
    
    return(inputs)    

def choose_events_for_whole_recording(inputs):

    default = {}
    default['Analysis name'] = 'Whole recording'
    
    # Column for selecting the event names.
    checkbox_cols = []
    for event_name in inputs['Event names']:
        checkbox_cols += [[sg.Checkbox(event_name, default=False, key=event_name)]]
    sg.theme("DarkTeal2")
    layout  = [[sg.T("")]]
    layout += [[sg.Text("Choose a custom name for this analysis",
                tooltip=info['Analysis name']),
                sg.Input(key="Analysis name",enable_events=True, size=(20,1),
                          default_text=default["Analysis name"])], [sg.T("")]] 
    layout += [[sg.Text("Choose events to display.",
                tooltip=('Choose the events to display over the top of the whole \n'+
                'recording plot. This will be annotated as a color with a legend.'))]]
    layout += [checkbox_cols]
    layout += [[sg.T("")], [sg.Button("Submit")]]
    window  = sg.Window('Photometry Analysis', layout)
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event=="Exit":
            window.close()
            sys.exit()
        if event == "Submit":
            inputs['Analysis name'] = values['Analysis name']
            inputs['Name'] = [event_name for event_name in inputs['Event names']
                              if values[event_name] == True]
            window.close()
            break 
        
    return(inputs)

# TDT -> whole recording -> ... -> select options before running the code

def choose_whole_recording_options(inputs):

    default = {}
    default['Exclude type'] = 'Time from recording start'
    default["Remove"]  = 60
    default["Baseline period"] = [4800,5000]
    default['Baseline type'] = 'Entire recording'
    default['Smoothing factor'] = 1
    default['Raw data'] = 'False'
    default['zScore']  = 'True'
    default['dFF']     = 'False'
    default['Fit']     = 'False'
    default['ISOS']    = 'False'
    default['GCaMP']   = 'False'
    sg.theme("DarkTeal2")        
    layout = [[sg.T("")],
        [sg.Text("Choose how much data to\nexclude from the start (secs)",
         tooltip=('Exclude the artifact from the start of the recording. \n'+
                  'You can choose "time from recording start" and fill in e.g. \n'+
                  '"60" secs. You can also choose "overall time" and fill in e.g. \n'+
                  '"2000" secs. This is the time since the box was turned on, \n'+
                  'and it can be found in the recording data file (which has \n'+
                  'LedStates, Region0G, Region1R, etc.)')),
         sg.Combo(['Time from recording start','Overall time'],key="Exclude type",enable_events=True,
                  default_value=default["Exclude type"]),
         sg.Input(key="Remove",enable_events=True,
                  default_text=default["Remove"], size=(8,1))], [sg.T("")],
        [sg.Text("Choose the baseline period",
         tooltip=('If "entire recording" is the baseline period type, the whole \n'+
                  'recording is used as the baseline period. If "Interval (overall \n'+
                  'time)" is used, enter the start and end time in secs since the \n'+
                  'box was turned on. This is the type of time data used in \n'+
                  'the photometry data file (with Region0G, Region1R, etc.) If \n'+
                  '"Interval (time since start) is used, enter the start and end times \n'+
                  'in secs since the start of the recording (e.g. 60 secs to 180 \n'+
                  'secs since the recording started).')), 
         sg.Combo(['Entire recording','Interval (overall time)','Interval (time since start)'],
                  key="Baseline type",enable_events=True, default_value=default["Baseline type"], size=(21,1)),
         sg.Input(key="BASELINE1",enable_events=True,visible=False,
                  default_text=default["Baseline period"][0],size=(10,1)),
         sg.Input(key="BASELINE2",enable_events=True,visible=False,
                  default_text=default["Baseline period"][1],size=(10,1))], [sg.T("")],
        [sg.Text("Smooth data using a moving average filter", 
                 tooltip='Choose the window size for the moving average filter. \n'+
                 'e.g. if 11 is chosen, find the 5 samples to the left and 5 to \n'+
                 'the right of one data point, average them (including the centre \n'+
                 'point) and replace that data point with the average.'),
         sg.Input(key="Smoothing factor",enable_events=True,
                  default_text=default["Smoothing factor"], size=(8,1))], [sg.T("")],
        [sg.Text("Perform peak detection",
         tooltip=("Detect peaks in the whole recording plot. More information \n"+
                  "will be provided in the next window after clicking 'Submit'.")), 
         sg.Combo(['True','False'],key="Peak detection",enable_events=True,
                  default_value=default['Raw data'])], [sg.T("")],
        [sg.Text("Export the raw data",
         tooltip=("Export an excel file with a time column, the signal column \n"+
                  "and an event column for the whole recording plot.")), 
         sg.Combo(['True','False'],key="Raw data",enable_events=True,
                  default_value=default['Raw data'])], [sg.T("")],
        [sg.Text("Create Z-Score plot?",
         tooltip="Create a whole recording plot of Z-Score vs time."), 
         sg.Combo(['True','False'],key="zScore",enable_events=True,
                  default_value=default['zScore'])], [sg.T("")],
        [sg.Text("Create dFF plot?",
         tooltip="Create a whole recording plot of dFF vs time."), 
         sg.Combo(['True','False'],key="dFF",enable_events=True,
                  default_value=default['dFF'])], [sg.T("")],
        [sg.Text("Create ISOS plot?",
         tooltip="Create a whole recording plot of ISOS vs time."), 
         sg.Combo(['True','False'],key="ISOS",enable_events=True,
                  default_value=default['ISOS'])], [sg.T("")],
        [sg.Text("Create GCaMP plot?",
         tooltip="Create a whole recording plot of GCaMP vs time."), 
         sg.Combo(['True','False'],key="GCaMP",enable_events=True,
                  default_value=default['GCaMP'])], [sg.T("")],
        [sg.Text("Create ISOS-GCaMP fit plot?",
         tooltip="Create a whole recording plot of the fit vs time."), 
         sg.Combo(['True','False'],key="Fit",enable_events=True,
                  default_value=default['Fit'])], [sg.T("")],
        [sg.Button("Submit")]]
    window = sg.Window('Photometry Analysis', layout)
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event=="Exit":
            window.close()
            sys.exit()
        if values["Baseline type"] == "Entire recording":
            window.Element("BASELINE1").Update(visible=False)
            window.Element("BASELINE2").Update(visible=False)
        if values["Baseline type"] in ['Interval (overall time)', 
                                       'Interval (time since start)']:
            window.Element("BASELINE1").Update(visible=True)
            window.Element("BASELINE2").Update(visible=True)
        if event == "Submit":
            inputs['Exclude type'] = values['Exclude type']
            inputs['Remove'] = float(values['Remove'])
            inputs['Baseline type'] = values['Baseline type']
            inputs['Baseline period'] = [float(values['BASELINE1']), 
                                         float(values['BASELINE2'])]
            inputs['Smoothing factor'] = int(values['Smoothing factor'])
            inputs['Export ISOS']   = recognise_bool(values['ISOS'])
            inputs['Export GCaMP']  = recognise_bool(values['GCaMP'])
            inputs['Export Fit']    = recognise_bool(values['Fit'])
            inputs['Export dFF']    = recognise_bool(values['dFF'])
            inputs['Export zScore'] = recognise_bool(values['zScore'])
            inputs['Raw data']      = recognise_bool(values['Raw data'])
            inputs['Peak detection'] = recognise_bool(values['Peak detection'])
            window.close()
            break
    
    return(inputs)

def choose_peak_detection_options(inputs):
    
    # Choose the type of TTL.
    default = {}
    default["Prominence"] = 3
    default["Negative"] = 'False'
    default["Detection type"] = 'Entire recording'
    default["Detection interval"] = [0,1000]
    sg.theme("DarkTeal2")
    layout  = [[sg.T("")],
        [sg.Text("Choose the minimum prominence for peak detection.",
         tooltip=("Choose the minimum prominence threshold for a peak to be \n"+
                  "detected. Prominence allows the peak height to be measured \n"+
                  "starting from the surrounding baseline. It is defined as the \n"+
                  "minimum height to descend from one peak to reach a higher peak.")),
         sg.Input(key="Prominence",enable_events=True,
                  default_text=default["Prominence"], size=(8,1))], [sg.T("")],
        [sg.Text("Also include negative peaks?",
         tooltip=("Choose whether to repeat the same peak analysis but for \n"+
                  "negative peaks. This works by multiplying all the signal data \n"+
                  "by -1, and repeating the analysis above.")), 
         sg.Combo(['True','False'],key="Negative peaks",enable_events=True,
                  default_value=default['Negative'])], [sg.T("")],
        [sg.Text("Choose where to detect peaks.",
         tooltip=('If "entire recording" is the detection type, peaks will be \n'+
                  'detection within the whole recording. If "Interval (overall \n'+
                  'time)" is used, enter the start and end time in secs since the \n'+
                  'box was turned on. This is the type of time data used in \n'+
                  'the photometry data file (with Region0G, Region1R, etc.) If \n'+
                  '"Interval (time since start) is used, enter the start and end times \n'+
                  'in secs since the start of the recording (e.g. 60 secs to 180 \n'+
                  'secs since the recording started).')), 
         sg.Combo(['Entire recording','Interval (overall time)','Interval (time since start)'],
                  key="Detection type",enable_events=True, 
                  default_value=default["Detection type"], size=(21,1)),
         sg.Input(key="Detection1",enable_events=True,visible=False,
                  default_text=default["Detection interval"][0],size=(10,1)),
         sg.Input(key="Detection2",enable_events=True,visible=False,
                  default_text=default["Detection interval"][1],size=(10,1))], [sg.T("")],
        [sg.Button("Submit")]]
    window  = sg.Window('Photometry Analysis', layout)
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event=="Exit":
            window.close()
            sys.exit()
        if values["Detection type"] == "Entire recording":
            window.Element("Detection1").Update(visible=False)
            window.Element("Detection2").Update(visible=False)
        if values["Detection type"] in ['Interval (overall time)', 
                                        'Interval (time since start)']:
            window.Element("Detection1").Update(visible=True)
            window.Element("Detection2").Update(visible=True)            
        if event == "Submit":
            inputs['Prominence'] = float(values['Prominence'])
            inputs['Negative'] = recognise_bool(values['Negative peaks'])
            inputs['Detection type'] = values['Detection type']
            inputs['Detection interval'] = [float(values['Detection1']), 
                                            float(values['Detection2'])]
            window.close()
            break
    
    return(inputs) 
