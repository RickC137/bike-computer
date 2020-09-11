from PyQt5 import QtGui
from PyQt5.QtGui import QPainter, QBrush, QPen, QIcon, QColor, QFont
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QHBoxLayout, QWidget, QAction, qApp, QPlainTextEdit, QStackedWidget, QPushButton, QComboBox
import sys
import threading
import time
from datetime import datetime, timezone, date, time
import pytz
import geopy.distance
from threading import Thread

from gps_get_data import GpsParser

# this is the default home dir
#path='/home/pi/Projects'
path='E:/Coding/Python_Projects/raspberry_pi/'


#This thread handles getting data from gps
class write_thread(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.is_running = False

    def run(self):
        self.gpsParser = GpsParser()
        self.gpsParser.run()
    
    def endit(self):
        self.gpsParser.stopApp()

#This thread handles displaying the data to screen
'''
class display_thread(Thread):
    def __init__(self):
        Thread.__init__(self)
    
    def run(self):
        App = QApplication(sys.argv)
        window = Window()
        window.show()
        sys.exit(App.exec())
'''

class Window(QMainWindow):
    def __init__(self):
        super(Window, self).__init__()
        self.InitWindow()



    def InitWindow(self):
        self.setAppMenu()
        self.setGeometry(0,0,320,480)
        self.Stack = QStackedWidget()
        self.stack1 = MainApp()
        self.stack2 = LoggerApp()
        self.stack3 = OptionsApp()
        self.stack1.setObjectName("Main")
        self.stack2.setObjectName("Logger")
        self.stack3.setObjectName("Options")
        windows = [self.Stack, self.stack1.objectName(), self.stack2.objectName(), self.stack3.objectName()]
        self.homeStack = MainMenu(windows=windows)
        self.Stack.addWidget(self.stack1)
        self.Stack.addWidget(self.stack2)
        self.Stack.addWidget(self.stack3)
        self.Stack.addWidget(self.homeStack)
        self.Stack.setCurrentIndex(3)
        
        widget = QWidget()
        widget = self.Stack
        self.setCentralWidget(widget)

    def setAppMenu(self):
        exitApp = QAction(QIcon('exit.png'), '&Exit', self)
        exitApp.setShortcut('Ctrl+Q')
        exitApp.setStatusTip('Exit Application')
        exitApp.triggered.connect(qApp.quit)
        
        menubar = self.menuBar()

        mainApp = QAction("Start App", self)
        mainApp.setStatusTip("Go to main page")
        mainApp.setShortcut('Ctrl+H')
        mainApp.triggered.connect(self.gotoMain)

        menuApp = QAction("Exit Session", self)
        menuApp.setStatusTip("Finish Session")
        menuApp.setShortcut('Ctrl+M')
        menuApp.triggered.connect(self.gotoMenu)

        debugApp = QAction("Debugger", self)
        debugApp.setStatusTip("Go to see gps log")
        debugApp.setShortcut('Ctrl+D')
        debugApp.triggered.connect(self.gotoDebugger)

        optionsApp = QAction("Options", self)
        optionsApp.setStatusTip("Go to the options page")
        optionsApp.setShortcut('Ctrl+O')
        optionsApp.triggered.connect(self.gotoOptions)

        appMenu = menubar.addMenu('&Apps')
        appMenu.addAction(menuApp)
        appMenu.addAction(mainApp)
        appMenu.addAction(debugApp)
        appMenu.addAction(optionsApp)
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(exitApp)

    def gotoMain(self):
        self.Stack.setCurrentIndex(0)


    def gotoDebugger(self):
        self.Stack.setCurrentIndex(1)


    def gotoMenu(self):
        self.stack1.reset_session()
        self.Stack.setCurrentIndex(3)

    def gotoOptions(self):
        self.Stack.setCurrentIndex(2)

    
    


class MyLabel(QLabel):
    def __init__(self):
        super(MyLabel, self).__init__()

class LoggerApp(QWidget):
    def __init__(self):
        super(LoggerApp, self).__init__()
        layout = QHBoxLayout()
        self.log_file = open(path+'/test_data/test_gps_input.txt','r')
        self.label = TextBoxLog()
        layout.addWidget(self.label)
        self.setLayout(layout)
        self.log_update()
    
        
    def log_update(self):
        log_output = self.log_file.readline()
        if log_output is not None and log_output != '':
            self.label.appendPlainText(str(log_output))
        
        QTimer.singleShot(100, self.log_update)

class MainApp(QWidget):
    def __init__(self):
        super(MainApp, self).__init__()
        self.avg_speed = 0
        self.total_speed = 0
        self.speed_amount = 0
        self.total_distance = 0
        self.set_init_distance = False
        self.old_lat = -1
        self.old_lon = -1
        self.app_started = False
        self.app_status_strs = ['Start', 'Pause', 'Resume']
        self.app_button_display = self.app_status_strs[0]

        #fonts
        latlon_font = QFont("Times", 15, QFont.Bold)
        speed_font = QFont("cursive", 50, QFont.Bold)
        time_font = QFont("Gadget", 15, QFont.Bold)

        self.use_mph = True
        self.program_file = open(path+'/test_data/test_csv_output.txt','r')
        self.time_lbl = QLabel("time", self, font=time_font)
        self.speed_lbl = QLabel("0", self, font=speed_font)
        self.avg_speed_lbl = QLabel("0", self, font=speed_font)
        self.total_distance_lbl= QLabel("total distance",self, font=latlon_font)
        self.lat_lbl = QLabel("lat", self, font=latlon_font)
        self.lon_lbl = QLabel("lon", self, font=latlon_font)
        self.speed_lbl.move(85,95)
        self.avg_speed_lbl.move(90, 250)
        self.speed_lbl.setAlignment(Qt.AlignCenter)
        self.avg_speed_lbl.setAlignment(Qt.AlignCenter)
        self.total_distance_lbl.move(235, 400)
        self.total_distance_lbl.setFixedWidth(200)
        self.avg_speed_lbl.setFixedWidth(150)
        self.speed_lbl.setFixedWidth(150)
        self.time_lbl.move(210, 0)
        self.time_lbl.setFixedWidth(200)
        self.lat_lbl.move(10,400)
        self.lat_lbl.setFixedWidth(200)
        self.lon_lbl.setFixedWidth(200)
        self.lon_lbl.move(120,400)
        self.button = QPushButton(self.app_button_display, self)
        self.button.move(120, 350)
        self.button.clicked.connect(self.set_app_status)

        self.update_values()

    def calculate_cur_avg_speed(self, cur_speed):
        hold_val = self.avg_speed
        self.total_speed += cur_speed
        self.speed_amount += 1
        try:
            self.avg_speed = self.total_speed/self.speed_amount # should never be a division by zero
        except:
            self.avg_speed = hold_val

    def calculate_distance_traveled(self, lat, lon):
        if self.set_init_distance == False:
            self.old_lat = lat
            self.old_lon = lon
            self.set_init_distance = True

        else:
            coords1 = (self.old_lat, self.old_lon)
            coords2 = (lat, lon)
            distance = 0
            if self.use_mph == False:
                distance = geopy.distance.distance(coords1, coords2).km
            else:
                distance = geopy.distance.distance(coords1, coords2).miles
            self.total_distance += distance

        self.total_distance_lbl.setText(str(self.total_distance)[:4])



    def update_values(self):
        # keep reading data dont save though unless app is running
        sys_output = self.program_file.readline()
        if self.app_started:
            if sys_output is not None and sys_output != '':
                data_strip = sys_output.split(',')
                self.time_lbl.setText(str(self.set_time_zone(data_strip[0])))
                speed_val = data_strip[1]
                if self.use_mph:
                    speed_val = float(speed_val) * 0.62137119223733
                self.calculate_cur_avg_speed(speed_val)
                self.avg_speed_lbl.setText(str(self.avg_speed)[:4])
                self.speed_lbl.setText(str(speed_val)[:4])
                self.lat_lbl.setText(str(data_strip[2])[:8])
                self.lon_lbl.setText(str(data_strip[4])[:8])
                self.calculate_distance_traveled(data_strip[2], data_strip[4])

        QTimer.singleShot(100, self.update_values)

    def paintEvent(self, event):
        super(MainApp, self).paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(QPen(Qt.blue, 8, Qt.SolidLine))
        painter.drawEllipse(60,40,200,200)

    #reset everything if user exits/ goes to main menue
    def reset_session(self):
        self.avg_speed = 0
        self.total_speed = 0
        self.speed_amount = 0
        self.total_distance = 0
        self.set_init_distance = False
        self.old_lat = -1
        self.old_lon = -1
        self.app_button_display = self.app_status_strs[0]
    
    def set_app_status(self):
        if self.app_started == False:
            self.app_started = True
            self.app_button_display = self.app_status_strs[1]
        elif self.app_started == True:
            self.app_started = False
            self.app_button_display = self.app_status_strs[2]
        self.button.setText(self.app_button_display)


    #set the timezone based on what the user inputed
    def set_time_zone(self, utc_time):
        self.utc_time = utc_time
        time_val = time(*map(int, self.utc_time.split(':')))
        dt = datetime.combine(date.today(), time_val)
        if selected_timezone == 'Eastern':
            dt = dt.replace(tzinfo=timezone.utc).astimezone(tz=pytz.timezone('US/EASTERN'))
        elif selected_timezone == 'Central':
            dt = dt.replace(tzinfo=timezone.utc).astimezone(tz=pytz.timezone('US/CENTRAL'))
        elif selected_timezone == 'Mountain':
            dt = dt.replace(tzinfo=timezone.utc).astimezone(tz=pytz.timezone('US/MOUNTAIN'))
        elif selected_timezone == 'Pacific':
            dt = dt.replace(tzinfo=timezone.utc).astimezone(tz=pytz.timezone('US/PACIFIC'))
        return dt.time()

class MainMenu(QWidget):
    def __init__(self, windows):
        super(MainMenu, self).__init__()
        self.windows = windows
        i = 0
        self.Stack = self.windows.pop(0)
        if windows is not None:
            for x in self.windows:
                val = str(x)
                if val == 'Main':
                    val = 'Start App'
                button = QPushButton(val, self)
                button.setObjectName(str(x))
                button.setToolTip("This is the : " + str(x))
                button.move(100, 50+i)
                button.clicked.connect(self.on_click)
                i += 25


    def on_click(self):
        sendingButton = self.sender()
        win = sendingButton.objectName()
        if str(win) == 'Main':
            self.Stack.setCurrentIndex(0)
        elif str(win) == 'Logger':
            self.Stack.setCurrentIndex(1)
        elif str(win) == 'Options':
            self.Stack.setCurrentIndex(2)


class OptionsApp(QWidget):
    
    def __init__(self):
        super(OptionsApp, self).__init__()
        self.timeChoice = QLabel('Current timezone: ' + selected_timezone, self)
        self.timeChoice.move(100,50)
        self.timeChoice.setFixedWidth(200)

        comboBox = QComboBox(self)
        comboBox.addItem("Eastern")
        comboBox.addItem("Central")
        comboBox.addItem("Mountain")
        comboBox.addItem("Pacific")
        comboBox.move(100,100)

        comboBox.activated[str].connect(self.time_zones)

    def time_zones(self, text):
        global selected_timezone
        if text == 'Eastern':
            selected_timezone = 'Eastern'
        elif text == 'Central':
            selected_timezone = 'Central'
        elif text == 'Mountain':
            selected_timezone = 'Mountain'
        elif text == 'Pacific':
            selected_timezone = 'Pacific'
        self.timeChoice.setText('Current timezone: ' + selected_timezone)


class TextBoxLog(QPlainTextEdit):
    def __init__(self):
        super(TextBoxLog, self).__init__()
        self.setReadOnly(True)
        self.appendPlainText("Some words")


if __name__ =='__main__':
    global selected_timezone
    selected_timezone = 'Eastern'
    try:
        t1 = write_thread()
        t1.start()
        App = QApplication(sys.argv)
        window = Window()
        window.show()
        App.exec_()
        print('Thread 2 is done')
        t1.endit() # this will stop thread1 when thread2 is terminated
        print("All Done")

    except Exception as e:
        t1.endit()
        print("This is the exception: " + str(e))