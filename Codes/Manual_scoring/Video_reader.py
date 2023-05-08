import sys
import cv2
import qdarkstyle
import numpy as np
from tabulate import tabulate
from PyQt5.QtGui import QPixmap, QImage, QKeySequence
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtWidgets import (QApplication, QLabel, QMainWindow, QSlider, QTextEdit,
    QHBoxLayout, QVBoxLayout, QWidget, QPushButton, QShortcut, QSizePolicy)

class PrintWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # create widgets and layout for the print window
        self.text_edit = QTextEdit(self)
        layout = QVBoxLayout()
        layout.addWidget(self.text_edit)
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
        
        # set the geometry of the main window
        self.setGeometry(100, 100, 500, 600)

    def print_text(self, message):
        # print some text to the text edit widget
        self.text_edit.append(message)
        
def print_keys_for_scoring(inputs):
    
    # Check whether some event keys and names are the same.
    if len(set(inputs['Event names'])) != len(inputs['Event names']):
        print('Make the event names have no duplicates.')
        sys.exit()
    if len(set(inputs['Event keys'])) != len(inputs['Event keys']):
        print('Make the event keys have no duplicates.')
        sys.exit()
    
    message = ''
    message += 'Use the space bar to pause and the left and right arrow keys to move one frame at a time.\n'
    message += 'Use the keys below to score events and press backspace to delete the last scored event.\n'
    message += 'Press the X button at the top right when you are done.\n'
    headings = ['Event types', 'Event keys', 'Event names']
    table    = [inputs[heading] for heading in headings]
    table    = list(np.array(table).T)
    message += tabulate(table, headers=headings)
    message += '\n'
    return(message)

class Manual_Scoring_Interface(QMainWindow):
    def __init__(self, inputs):
        super().__init__()

        # Load the video file
        self.inputs = inputs
        self.cap = cv2.VideoCapture(self.inputs['Import location'])
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)

        # Create a QLabel widget to display the video
        self.video_player = QLabel()
        self.video_player.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.video_player.setAlignment(Qt.AlignCenter)
        self.video_player.setScaledContents(True)  # Added line to scale video to widget size
        self.setCentralWidget(self.video_player)

        # Create a QHBoxLayout to contain the pause button, move frame buttons, slider widget, and speed button
        self.control_layout = QHBoxLayout()

        # Create a QPushButton widget to pause and resume the video
        self.pause_button = QPushButton("Pause")
        self.pause_button.setFixedWidth(50)
        self.pause_button.clicked.connect(self.pauseVideo)
        self.control_layout.addWidget(self.pause_button)

        # Create a QPushButton widget to move the video one frame to the left
        self.move_left_button = QPushButton("<<")
        self.move_left_button.setFixedWidth(30)
        self.move_left_button.pressed.connect(self.startMoveFrameLeft)
        self.move_left_button.released.connect(self.stopMoveFrameLeft)
        self.control_layout.addWidget(self.move_left_button)

        # Create a QSlider widget to display the video progress
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))-1)
        self.slider.sliderMoved.connect(self.setPosition)
        self.control_layout.addWidget(self.slider)

        # Create a QPushButton widget to move the video one frame to the right
        self.move_right_button = QPushButton(">>")
        self.move_right_button.setFixedWidth(30)
        self.move_right_button.pressed.connect(self.startMoveFrameRight)
        self.move_right_button.released.connect(self.stopMoveFrameRight)
        self.control_layout.addWidget(self.move_right_button)

        # Create a QPushButton widget to change the speed of the video
        self.speed_button = QPushButton("Speed (1x)")
        self.speed_button.setFixedWidth(70)
        self.speed_button.clicked.connect(self.increaseSpeed)
        self.control_layout.addWidget(self.speed_button)

        # Create a QVBoxLayout to contain the video player widget and control layout
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.video_player)
        self.layout.addLayout(self.control_layout)

        # Create a QWidget to contain the layout
        self.container = QWidget()
        self.container.setLayout(self.layout)
        self.setCentralWidget(self.container)

        # Start a timer to update the video
        self.timer = QTimer()
        self.timer.timeout.connect(self.updateVideo)
        self.timer.start(30)

        self.paused = False
        
        # Set the initial speed to 1x
        self.speed = 1

        # Initialize move frame variables
        self.move_frame_left = False
        self.move_frame_right = False
        
        # Add time label.
        self.time_label = QLabel("00:00 / 00:00")
        self.control_layout.addWidget(self.time_label)

        # Create shortcuts for key bindings
        self.pause_shortcut = QShortcut(QKeySequence("Space"), self)
        self.pause_shortcut.activated.connect(self.pauseVideo)
        
        self.move_left_shortcut = QShortcut(QKeySequence(Qt.Key_Left), self)
        self.move_left_shortcut.activated.connect(self.moveFrameLeft)
        self.move_left_shortcut.setContext(Qt.ApplicationShortcut)

        self.move_right_shortcut = QShortcut(QKeySequence(Qt.Key_Right), self)
        self.move_right_shortcut.activated.connect(self.moveFrameRight)
        self.move_right_shortcut.setContext(Qt.ApplicationShortcut)
        
        self.move_up_shortcut = QShortcut(QKeySequence(Qt.Key_Up), self)
        self.move_up_shortcut.activated.connect(self.increaseSpeed)
        self.move_up_shortcut.setContext(Qt.ApplicationShortcut)

        self.move_down_shortcut = QShortcut(QKeySequence(Qt.Key_Down), self)
        self.move_down_shortcut.activated.connect(self.decreaseSpeed)
        self.move_down_shortcut.setContext(Qt.ApplicationShortcut)
        
        # Initialise the outputs variables for frame data collection.
        self.outputs = {}
        self.outputs['Event names']       = []
        self.outputs['Event start times'] = []
        self.outputs['Event end times']   = []
        self.start_stop_active_events     = []
        self.start_stop_active_indices    = []
        self.mutually_exclusive_events    = []
        self.mutually_exclusive_indices   = []
        
        # Intialise the key presses.
        self.key_press_shortcuts = {}
        for key in self.inputs['Event keys']:
            shortcut = QShortcut(QKeySequence(key), self)
            shortcut.activated.connect(lambda k=key: self.processKeyPress(k))
            self.key_press_shortcuts[key] = shortcut
        
        # Initialise the delete frame presses.
        self.delete_frame_shortcut = QShortcut(QKeySequence("Backspace"), self)
        self.delete_frame_shortcut.activated.connect(self.deleteEvent)
        
        # Add a logging window.
        # create widgets and layout for the main window
        self.print_window = PrintWindow()
        self.print_window.show()
        self.print_window.print_text(print_keys_for_scoring(inputs))

    def pauseVideo(self):
        self.paused = not self.paused
        if self.paused:
            self.pause_button.setText("Play")
        else:
            self.pause_button.setText("Pause")
            
    def updateVideo(self):
        if self.paused:
            return
        # Calculate the number of frames to skip based on the current speed
        skip_frames = int(self.speed / 2) - 1
        # Skip the appropriate number of frames
        for i in range(skip_frames):
            self.cap.grab()
        # Read the next frame from the video file
        ret, frame = self.cap.read()
        # If the video file has ended, stop the timer and return
        if not ret:
            return
        # Convert the frame to a QImage and set it as the pixmap for the video player widget
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        height, width, channels = image.shape
        qimage = QImage(image.data, width, height, channels * width, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qimage)
        self.video_player.setPixmap(pixmap)
        # Update the slider position to reflect the current frame
        position = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES)) - 1
        self.slider.setValue(position)
        
        # Update the time label text to show the current and total time of the video
        current_time = int(position / self.fps)
        total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        total_time = int(total_frames / self.fps)
        current_time_str = f"{current_time//60:02d}:{current_time%60:02d}"
        total_time_str = f"{total_time//60:02d}:{total_time%60:02d}"
        self.time_label.setText(f"{current_time_str} / {total_time_str}, {position} / {total_frames}")
        
    def setPosition(self, position):
        # Set the current frame position of the video to the value of the slider
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, position)
        
    def increaseSpeed(self):
        # Update the speed of the video and the text on the speed button
        if self.speed == 1:
            self.speed = 2
            self.speed_button.setText("Speed (2x)")
            self.timer.setInterval(15)
        elif self.speed == 2:
            self.speed = 4
            self.speed_button.setText("Speed (4x)")
            self.timer.setInterval(7)
        elif self.speed == 4:
            self.speed = 8
            self.speed_button.setText("Speed (8x)")
            self.timer.setInterval(4)
        elif self.speed == 8:
            self.speed = 16
            self.speed_button.setText("Speed (16x)")
            self.timer.setInterval(2)
        else:
            self.speed = 1
            self.speed_button.setText("Speed (1x)")
            self.timer.setInterval(30)

    def decreaseSpeed(self):
        # Update the speed of the video and the text on the speed button
        if self.speed == 1:
            self.speed = 16
            self.speed_button.setText("Speed (16x)")
            self.timer.setInterval(2)
        elif self.speed == 2:
            self.speed = 1
            self.speed_button.setText("Speed (1x)")
            self.timer.setInterval(30)
        elif self.speed == 4:
            self.speed = 2
            self.speed_button.setText("Speed (2x)")
            self.timer.setInterval(15)
        elif self.speed == 8:
            self.speed = 4
            self.speed_button.setText("Speed (4x)")
            self.timer.setInterval(7)
        else:
            self.speed = 8
            self.speed_button.setText("Speed (8x)")
            self.timer.setInterval(4)

    def startMoveFrameLeft(self):
        self.move_frame_left = True
        self.move_frame_left_timer = QTimer()
        self.move_frame_left_timer.timeout.connect(self.moveFrameLeft)
        self.move_frame_left_timer.start(30)

    def stopMoveFrameLeft(self):
        self.move_frame_left = False
        self.move_frame_left_timer.stop()

    def startMoveFrameRight(self):
        self.move_frame_right = True
        self.move_frame_right_timer = QTimer()
        self.move_frame_right_timer.timeout.connect(self.moveFrameRight)
        self.move_frame_right_timer.start(30)
                                                    
    def stopMoveFrameRight(self):
        self.move_frame_right = False
        self.move_frame_right_timer.stop()

    def moveFrameLeft(self):
        # Pause the video if it's playing
        if not self.paused:
            self.pauseVideo()
        # Calculate the new position of the video
        position = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES)) - 2
        # Make sure the new position is within the bounds of the video
        if position < 0:
            position = 0
        # Set the position of the video to the new position
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, position)
        # Read the new frame from the video file
        ret, frame = self.cap.read()
        # If the video file has ended, return
        if not ret:
            return
        # Convert the frame to a QImage and set it as the pixmap for the video player widget
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        height, width, channels = image.shape
        qimage = QImage(image.data, width, height, channels * width, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qimage)
        self.video_player.setPixmap(pixmap)
        # Update the slider position to reflect the current frame
        self.slider.setValue(position)
        
        # Update the time label text to show the current and total time of the video
        current_time = int(position / self.fps)
        total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        total_time = int(total_frames / self.fps)
        current_time_str = f"{current_time//60:02d}:{current_time%60:02d}"
        total_time_str = f"{total_time//60:02d}:{total_time%60:02d}"
        self.time_label.setText(f"{current_time_str} / {total_time_str}, {position} / {total_frames}")

    def moveFrameRight(self):
        # Pause the video if it's playing
        if not self.paused:
            self.pauseVideo()
        # Calculate the new position of the video
        position = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
        # Make sure the new position is within the bounds of the video
        if position < 0:
            position = 0
        # Set the position of the video to the new position
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, position)
        # Read the new frame from the video file
        ret, frame = self.cap.read()
        # If the video file has ended, return
        if not ret:
            return
        # Convert the frame to a QImage and set it as the pixmap for the video player widget
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        height, width, channels = image.shape
        qimage = QImage(image.data, width, height, channels * width, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qimage)
        self.video_player.setPixmap(pixmap)
        # Update the slider position to reflect the current frame
        self.slider.setValue(position)
        
        # Update the time label text to show the current and total time of the video
        current_time = int(position / self.fps)
        total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        total_time = int(total_frames / self.fps)
        current_time_str = f"{current_time//60:02d}:{current_time%60:02d}"
        total_time_str = f"{total_time//60:02d}:{total_time%60:02d}"
        self.time_label.setText(f"{current_time_str} / {total_time_str}, {position} / {total_frames}")
    
    def processKeyPress(self, key):
        frame_no = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
        frame_no -= 1
        num_frames = len(self.outputs['Event names'])
        ind = self.inputs['Event keys'].index(key)
        event_name = self.inputs['Event names'][ind]
        event_type = self.inputs['Event types'][ind]
        if event_type == 'Point event':
            self.outputs['Event names']       += [event_name]
            self.outputs['Event start times'] += [frame_no]
            self.outputs['Event end times']   += [frame_no]
            print(f'({num_frames}) Saved frame {frame_no} for {event_name}')
            self.print_window.print_text(f'({num_frames}) Saved frame {frame_no} for {event_name}')
        elif event_type == 'Mutually exclusive':
            if len(self.mutually_exclusive_events) > 0 and self.mutually_exclusive_events[-1] != event_name:
                self.outputs['Event end times'][self.mutually_exclusive_indices[-1]] = frame_no   
            if len(self.mutually_exclusive_events) == 0 or self.mutually_exclusive_events[-1] != event_name:
                self.outputs['Event names']       += [event_name]
                self.outputs['Event start times'] += [frame_no]
                self.outputs['Event end times']   += ['Empty']
                self.mutually_exclusive_events    += [event_name]
                self.mutually_exclusive_indices   += [num_frames]           
                print(f'({num_frames}) Saved frame {frame_no} for {event_name}')
                self.print_window.print_text(f'({num_frames}) Saved frame {frame_no} for {event_name}')
        elif event_type == 'Start-stop event':
            if event_name not in self.start_stop_active_events:
                self.outputs['Event names']       += [event_name]
                self.outputs['Event start times'] += [frame_no]
                self.outputs['Event end times']   += ['Empty']
                self.start_stop_active_events  += [event_name]
                self.start_stop_active_indices += [num_frames]
                start_or_stop = 'start'
            elif event_name in self.start_stop_active_events:
                active_ind = self.start_stop_active_events.index(event_name)
                event_ind  = self.start_stop_active_indices[active_ind]
                self.outputs['Event end times'][event_ind] = frame_no
                self.start_stop_active_events.remove(event_name) 
                self.start_stop_active_indices.remove(event_ind)
                start_or_stop = 'stop'
            print(f'({num_frames}) Saved frame {frame_no} for {event_name} ({start_or_stop})')
            self.print_window.print_text(f'({num_frames}) Saved frame {frame_no} for {event_name} ({start_or_stop})')
            
    def deleteEvent(self):
        if len(self.outputs['Event names']) > 0:
            event_name = self.outputs['Event names'][-1]
            start_time = self.outputs['Event start times'][-1]
            self.outputs['Event names']       = self.outputs['Event names'][:-1]
            self.outputs['Event start times'] = self.outputs['Event start times'][:-1]
            self.outputs['Event end times']   = self.outputs['Event end times'][:-1]
            ind = self.inputs['Event names'].index(event_name)
            event_type = self.inputs['Event types'][ind]
            if event_type == 'Mutually exclusive':
                self.mutually_exclusive_events  = self.mutually_exclusive_events[:-1]
                self.mutually_exclusive_indices = self.mutually_exclusive_indices[:-1]
                if len(self.mutually_exclusive_events) > 0:
                    self.outputs['Event end times'][self.mutually_exclusive_indices[-1]] = 'Empty'
            elif event_type == 'Start-stop event':
                if event_name in self.start_stop_active_events:
                    active_ind = self.start_stop_active_events.index(event_name)
                    event_ind  = self.start_stop_active_indices[active_ind]
                    self.start_stop_active_events.remove(event_name)
                    self.start_stop_active_indices.remove(event_ind)
            print(f'# Deleted frame {start_time} for {event_name}')
        else:
            print('# There are no more frames to delete')
            
def Manual_Scoring_GUI(inputs):
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    app.setStyle('Fusion')
    window = Manual_Scoring_Interface(inputs)
    window.show()
    app.exec_()
    return(window.outputs)
    