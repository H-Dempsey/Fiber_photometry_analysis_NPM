import PySimpleGUI as sg
import sys

def choose_import_export_num_behaviours(inputs):
    # Choose the import location, export location and setup.
    default = {}
    default["Import location"] = r"C:\Users\hazza\Desktop\Lab meeting presentation - Florey\Example folder 1\Test_all_photom_video mouse 2_2022-09-09T15_11_45.avi"
    default["Export location"] = r"C:\Users\hazza\Desktop\Lab meeting presentation - Florey\Example folder 1"
    default["Num"]             = 4
    default["Format"]          = 'Eva/Roberta'       
    sg.theme("DarkTeal2")
    layout  = []
    layout += [[sg.T("")], [sg.Text("Choose the location of the video to score",size=(29,1),
                tooltip=("Choose the video you want to perform manual scoring on.")), 
                sg.Input(key="Import" ,enable_events=True,default_text=default["Import location"]),
                sg.FileBrowse(key="Import2")]]
    layout += [[sg.T("")], [sg.Text("Choose a folder for the export location",size=(29,1),
                tooltip=("Choose where to export the manual scoring results. \n"+
                         "Ideally this should be the same folder as the video. \n"+
                         "Please note this will overide previous manual scoring data.")),
                sg.Input(key="Export" ,enable_events=True,default_text=default["Export location"]),
                sg.FolderBrowse(key="Export2")]]
    layout += [[sg.T("")],[sg.Text("Choose how many events you want to score",
                tooltip=("Choose how many events you want to manually score. \n"+
                         "e.g. 4 events for walking, sitting, rearing, grooming.")), 
                sg.Combo(list(range(1,15+1)),key="Num",enable_events=True,default_value=default["Num"])]]
    layout += [[sg.T("")],[sg.Text("Choose the format of the NPM data.",
                tooltip=("Choose the format of your photometry data. These formats \n"+
                         "are going to be different depending on the Bonsai setup. \n\n"+
                         "OPTIONAL READING: Why do we need this information? \n"+
                         "The video should be located in the same folder as the \n"+
                         "photometry data. There is an excel file with video frames \n"+
                         "and corresponding timestamps since the NPM box was turned \n"+
                         "on. This needs to be imported, so that the video frame \n"+
                         "numbers can be mapped to time in secs. The inter-frame \n"+
                         "interval is actually inconsistent (e.g. the difference \n"+
                         "between frame 1 and 2 is 0.05 secs, frame 2 and frame \n"+
                         "3 is 0.04 secs, ...)")),
                sg.Combo(['Eva/Roberta','Leigh/Xavier','Claire'],key="Format",
                enable_events=True,default_value=default['Format'])]]
    layout += [[sg.T("")], [sg.Button("Submit")]]
    window  = sg.Window('Manual scoring GUI', layout)
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event=="Exit":
            window.close()
            sys.exit()
        elif event == "Submit":
            inputs['Import location'] = values["Import"]
            inputs['Export location'] = values["Export"]
            inputs['Num events']      = values["Num"]
            inputs['Format']          = values['Format']
            window.close()
            break
    return(inputs)

def choose_previous_or_new_settings(inputs):
    # Use the existing settings, if there is a csv file called "Manual_scoring_settings"
    # in the same place as the video import folder.
    default = {}
    default['Settings'] = 'True'
    sg.theme("DarkTeal2")
    layout  = []
    layout += [[sg.T("")],[sg.Text("Use scoring settings defined previously?",
                tooltip=("Leave this as false if it is your first time using this. \n\n"
                         "If you have previously manually scored a video, the \n"+
                         "settings for manual scoring will have been exported \n"+
                         "to the export location. Decide whether to re-use these \n"+
                         "settings. This only works when the settings are in the \n"+
                         "same folder as the import location.")), 
                sg.Combo(['True','False'],key="Settings",
                enable_events=True,default_value=default['Settings'])]]
    layout += [[sg.T("")],[sg.Button("Submit")]]
    window  = sg.Window('Manual scoring GUI', layout)
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event=="Exit":
            window.close()
            sys.exit()
        elif event == "Submit":
            inputs["Settings"] = (True if values['Settings']=='True' else False)
            window.close()
            break
    return(inputs)

def choose_manual_scoring_settings(inputs):
    default = {}
    default["Event type"] = 'Point event'
    event_types = ['Point event','Mutually exclusive','Start-stop event']
    event_keys  = ['a','b','c','d','e','f','g','h','i','j','k','l','m',
                   'n','o','p','q','r','s','t','u','v','w','x','y','z']
    sg.theme("DarkTeal2")
    layout  = [[sg.T("")], [sg.Text("Choose the event types, keys for scoring and the event names",
                tooltip=("Here is an explanation of the event types. \n\n"
                         "- Point event: press a key to record that frame of the \n"+
                         "  event. e.g. spray from a spray can. \n\n"+
                         "- Start-stop event: press a key to start an event and \n"+
                         "  press the same key to end the event. e.g. sipping \n"+
                         "  from a tube. \n\n"+
                         "- Mutually exclusive (ME) event: press a key to start an \n"+
                         "  event and press a different ME key to end that event. \n"+
                         "  e.g. to score 'walking', 'sitting' then 'rearing', \n"+
                         "  press 'w', 's' then 'r'. By default, no ME event is \n"+
                         "  active until one ME key is pressed."))], [sg.T("")], 
               [sg.Text("Types",size=(15,1)), sg.Text("Keys",size=(4,1)), sg.Text("Names",size=(20,1))]]
    for i in range(1,inputs['Num events']+1):
        layout += [
                   [sg.Combo(event_types,
                             key="Event_type"+str(i),enable_events=True,default_value=default["Event type"],size=(15,1)),
                    sg.Combo(event_keys,key="Event_key"+str(i),enable_events=True,default_value=event_keys[i-1],size=(3,1)),
                    sg.Input(key="Event_name"+str(i),enable_events=True,default_text='Event name '+str(i),size=(20,1))]]
    layout += [[sg.T("")], [sg.Button("Submit")]]
    window  = sg.Window('Manual scoring GUI', layout)
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event=="Exit":
            window.close()
            sys.exit()
        elif event == "Submit":
            inputs['Event names'] = []
            inputs['Event types'] = []
            inputs['Event keys'] = []
            for i in range(1,inputs['Num events']+1):
                inputs['Event names'] += [values['Event_name'+str(i)]]
                inputs['Event types'] += [values['Event_type'+str(i)]]
                inputs['Event keys']  += [values['Event_key' +str(i)]]
            window.close()
            break
    return(inputs)
