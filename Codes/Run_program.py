# Import the functions for fibre photometry analysis.
from Fibre_photometry.Create_GUI import (choose_which_type_analysis, 
    choose_location_for_grouped_analysis, analyse_many_folders, 
    choose_basic_NPM_options, choose_name_NPM_event, choose_peri_event_options, 
    choose_video_snippet_options, choose_events_for_whole_recording, 
    choose_whole_recording_options, choose_peak_detection_options,
    choose_location_for_settings_file, choose_the_groups_to_plot,
    create_loading_bar, update_loading_bar)
from Fibre_photometry.Data_processing import (import_settings_excel_file, 
    import_NPM_data, create_annotated_video, export_settings_excel_file)
from Fibre_photometry.Peri_events import (epoch_analysis, graph_epoch_analysis, 
    create_headers_for_data, export_preview_image_peri_events, 
    export_analysed_data_peri_events, combine_header_and_data, 
    graph_epoch_analysis_grouped)
from Fibre_photometry.Whole_recording import (whole_recording_analysis, 
    create_export_plots, export_whole_recording_plots, export_whole_recording_data)
from Fibre_photometry.Group_analysis import (initialize_grouped_data, add_to_grouped_data, 
    organise_grouped_data, export_grouped_plots, export_grouped_data)

# Import the functions for the manual scoring.
from Manual_scoring.Option_windows import (choose_import_export_num_behaviours, 
    choose_previous_or_new_settings, choose_manual_scoring_settings)
from Manual_scoring.Video_reader import Manual_Scoring_GUI
from Manual_scoring.Input_data_processing import (read_existing_settings_file, 
    export_manual_scoring_settings)
from Manual_scoring.Output_data_processing import (export_event_timestamps_eva_roberta, 
    export_event_timestamps_leigh_xavier, export_event_timestamps_claire)
import PySimpleGUI as sg

# Import a loading bar module.
# from tqdm import tqdm

while True:
    
    inputs = {}
    inputs = choose_which_type_analysis(inputs)
    
    if inputs['Analysis type'] == 'Import settings file':
        inputs = choose_location_for_settings_file(inputs)
        list_inputs = import_settings_excel_file(inputs)
        
        if len(list_inputs) == 1:
            inputs = list_inputs[0]
            inputs = import_NPM_data(inputs)
            inputs, outputs = epoch_analysis(inputs)
            outputs = create_headers_for_data(inputs, outputs)
            if inputs['Create snippets'] == True:
                create_annotated_video(inputs, outputs)
            if inputs['Image'] == True:
                outputs = graph_epoch_analysis(outputs)
                export_preview_image_peri_events(inputs, outputs)
            outputs = combine_header_and_data(outputs)
            export_analysed_data_peri_events(inputs, outputs)
        
        else:
            # Import the options for analysis from a settings excel file or ...
            grouped_data = initialize_grouped_data()
            grouped_data = choose_the_groups_to_plot(grouped_data)
            analyse_grouped_data = True
        
            # Run the correct code, based on the information in the settings excel file.
            # for inputs in tqdm(list_inputs, ncols=70):
            for inputs in list_inputs:
                # ... put this data in manually.
                # Run the set of NPM GUIs.
                inputs = import_NPM_data(inputs)
                inputs, outputs = epoch_analysis(inputs)
                outputs = create_headers_for_data(inputs, outputs)
            
                if inputs['Create snippets'] == True:
                    create_annotated_video(inputs, outputs)
                
                if inputs['Image'] == True:
                    outputs = graph_epoch_analysis(outputs)
                    export_preview_image_peri_events(inputs, outputs)
                
                if inputs['Create grouped data'] == True:
                    grouped_data = add_to_grouped_data(grouped_data, inputs, outputs)
                    analyse_grouped_data = True
            
                outputs = combine_header_and_data(outputs)
                export_analysed_data_peri_events(inputs, outputs)
                    
            if analyse_grouped_data == True:
                grouped_data = organise_grouped_data(grouped_data)
                grouped_data = graph_epoch_analysis_grouped(grouped_data)
                export_grouped_plots(grouped_data, inputs)
                grouped_data = combine_header_and_data(grouped_data)
                export_grouped_data(grouped_data, inputs)
                
        continue

    if inputs['Analysis type'] == "Analyse one folder":
        # ... put this data in manually.
        # Run the set of NPM GUIs.
        inputs = choose_basic_NPM_options(inputs)
        inputs = import_NPM_data(inputs)
    
        if inputs['Analysis'] == 'Peri-events':
            inputs = choose_name_NPM_event(inputs)
            inputs = choose_peri_event_options(inputs)
        
            if inputs['Create snippets'] == True:
                inputs = choose_video_snippet_options(inputs)
            
            inputs, outputs = epoch_analysis(inputs)
            outputs = create_headers_for_data(inputs, outputs)

            if inputs['Create snippets'] == True:
                create_annotated_video(inputs, outputs)
            
            if inputs['Image'] == True:
                outputs = graph_epoch_analysis(outputs)
                export_preview_image_peri_events(inputs, outputs)
            
            outputs = combine_header_and_data(outputs)
            export_analysed_data_peri_events(inputs, outputs)
    
        if inputs['Analysis'] == 'Whole recording':
            inputs = choose_events_for_whole_recording(inputs)
            inputs = choose_whole_recording_options(inputs)
        
            if inputs['Peak detection'] == True:
                inputs = choose_peak_detection_options(inputs)
            
            outputs = whole_recording_analysis(inputs)
            outputs = create_export_plots(inputs, outputs)
            export_whole_recording_plots(inputs, outputs)
        
            if inputs['Raw data'] == True:
                export_whole_recording_data(inputs, outputs)

            continue
                
        export_settings_excel_file(inputs)
        
        continue

    if inputs['Analysis type'] == 'Manually score videos':
        inputs = choose_import_export_num_behaviours(inputs)
        inputs = choose_previous_or_new_settings(inputs)
    
        if inputs['Settings'] == True:
            inputs = read_existing_settings_file(inputs)
        else:
            inputs = choose_manual_scoring_settings(inputs)
            export_manual_scoring_settings(inputs)
    
        outputs = Manual_Scoring_GUI(inputs)
        if inputs['Format'] == 'Eva/Roberta':
            outputs = export_event_timestamps_eva_roberta(inputs, outputs)
        elif inputs['Format'] == 'Leigh/Xavier':
            outputs = export_event_timestamps_leigh_xavier(inputs, outputs)
        elif inputs['Format'] == 'Claire':
            outputs = export_event_timestamps_claire(inputs, outputs)
            
        continue

    if inputs['Analysis type'] == "Analyse many folders":
        
        # Import the options for analysis from a settings excel file or ...
        inputs = choose_location_for_grouped_analysis(inputs)
        grouped_data = initialize_grouped_data()
        grouped_data, list_inputs = analyse_many_folders(grouped_data, inputs)
        analyse_grouped_data = True

        # Create the loading bar window
        window = create_loading_bar(len(list_inputs))
        event, values = window.read(timeout=100)
        for i in range(len(list_inputs)):
            
            inputs = list_inputs[i]
            # Update the progress bar at the start of each iteration
            update_loading_bar(window, i+1)

            # Your analysis code for each iteration
            # ... put this data in manually.
            # Run the set of NPM GUIs.
            inputs = import_NPM_data(inputs)
            inputs, outputs = epoch_analysis(inputs)
            outputs = create_headers_for_data(inputs, outputs)
        
            if inputs['Create snippets'] == True:
                create_annotated_video(inputs, outputs)
            
            if inputs['Image'] == True:
                outputs = graph_epoch_analysis(outputs)
                export_preview_image_peri_events(inputs, outputs)
            
            if inputs['Create grouped data'] == True:
                grouped_data = add_to_grouped_data(grouped_data, inputs, outputs)
                analyse_grouped_data = True
        
            outputs = combine_header_and_data(outputs)
            export_analysed_data_peri_events(inputs, outputs)
                
        if analyse_grouped_data == True:
            grouped_data = organise_grouped_data(grouped_data)
            grouped_data = graph_epoch_analysis_grouped(grouped_data)
            export_grouped_plots(grouped_data, inputs)
            grouped_data = combine_header_and_data(grouped_data)
            export_grouped_data(grouped_data, inputs)
            
        export_settings_excel_file(list_inputs)
        
        # Close the window
        window.close()
        continue
            
    # if inputs['Analysis type'] == "Analyse many folders":
    #     # Import the options for analysis from a settings excel file or ...
    #     inputs = choose_location_for_grouped_analysis(inputs)
    #     grouped_data = initialize_grouped_data()
    #     grouped_data, list_inputs = analyse_many_folders(grouped_data, inputs)
    #     analyse_grouped_data = True
    
    #     # Run the correct code, based on the information in the settings excel file.
    #     # for inputs in tqdm(list_inputs, ncols=70):
    #     for inputs in list_inputs:
    #         # ... put this data in manually.
    #         # Run the set of NPM GUIs.
    #         inputs = import_NPM_data(inputs)
    #         inputs, outputs = epoch_analysis(inputs)
    #         outputs = create_headers_for_data(inputs, outputs)
        
    #         if inputs['Create snippets'] == True:
    #             create_annotated_video(inputs, outputs)
            
    #         if inputs['Image'] == True:
    #             outputs = graph_epoch_analysis(outputs)
    #             export_preview_image_peri_events(inputs, outputs)
            
    #         if inputs['Create grouped data'] == True:
    #             grouped_data = add_to_grouped_data(grouped_data, inputs, outputs)
    #             analyse_grouped_data = True
        
    #         outputs = combine_header_and_data(outputs)
    #         export_analysed_data_peri_events(inputs, outputs)
                
    #     if analyse_grouped_data == True:
    #         grouped_data = organise_grouped_data(grouped_data)
    #         grouped_data = graph_epoch_analysis_grouped(grouped_data)
    #         export_grouped_plots(grouped_data, inputs)
    #         grouped_data = combine_header_and_data(grouped_data)
    #         export_grouped_data(grouped_data, inputs)
            
    #     export_settings_excel_file(list_inputs)
            
    #     continue
            