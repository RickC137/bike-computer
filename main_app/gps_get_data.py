import serial
import time
import os

'''
Data for neo-6m goes from start gprmc and ends with gpgll
so knowing that we can create a bulk edit that will update 
once for each total packet
Only want this data from them
lat/long and dir from gpgll pos 2 - lat, 3 - lat dir, 4 - lon, 5 - lon dir
time from gprmc pos 2
km/h ie speed from gpvtg pos 7 - speed, pos 8 - k
skip gga and gsv and gsa
'''
#path='/home/pi/Projects'
path='E:/Coding/Python_Projects/raspberry_pi/'

class GpsObject:
    lat_val = 0
    lon_val = 0
    lat_dir = ''
    lon_dir = ''
    speed = 0
    time = ''
    is_valid = False

    def set_default(self):
        self.is_valid = False
        self.lat_dir = ''
        self.lon_dir = ''
        self.lat_val = 0
        self.lon_val = 0
        self.time = ''
        self.speed = 0

    def __str__(self):
        return "This is the lat/lon: " + str(self.lat_val) + str(self.lat_dir) + " / " + str(self.lon_val) + str(self.lon_dir) +" \nThis is the time: "+str(self.time)+"\nThis is the speed: "+ str(self.speed) +"\n"

    def parse_str(self):
        return str(self.time)+","+str(self.speed)+","+str(self.lat_val)+","+str(self.lat_dir)+","+str(self.lon_val)+","+str(self.lon_dir)+"\n"

class GpsParser:
    def parseGPS(self, data, response):
        if response.is_valid:
            response.set_default()
        data_strip = data.split(',')
        if data_strip[0] == '$GPGLL':
            if data_strip[6] == 'V':
                #print ('no satellite data available')
                return
            time = data_strip[5][0:2] + ":" + data_strip[5][2:4] + ":" + data_strip[5][4:6]
            #print("-----------")
            lat = self.decode(data_strip[1])
            lon = self.decode(data_strip[3])
            #lat =0
            #lon =0
            response.lat_val = lat
            response.lon_val = lon
            response.time = time
            response.lat_dir = data_strip[2]
            response.lon_dir = data_strip[4]
            response.is_valid = True
        if data_strip[0] == '$GPVTG':
            if data_strip[1] is not None and data_strip[1] != '':
                response.speed = data_strip[7]

    def decode(self, coord):
        l = list(coord)
        for i in range(0,len(l)-1):
                if l[i] == "." :
                        break
        base = l[0:i-2]
        degi = l[i-2:i]
        degd = l[i+1:]
        baseint = int(''.join(base))
        degiint = int(''.join(degi))
        degdint = float(''.join(degd))
        degdint = degdint / (10**len(degd))
        degs = degiint + degdint
        full = float(baseint) + (degs/60)
        
        return full

    def setup(self):
        self.use_test_data = True
        self.running = True
        self.f = open(path+'/test_data/gps_stationary_test_data.txt', 'r')
        self.handleFiles()

        #DISPLAY=:0 xinput --set-prop 'ADS7846 Touchscreen' 'Coordinate Transformation Matrix' 0 -1 1 1 0 0 0 0 1
        #mport = 'COM4'
        #used if getting from usb device
        #mport = '/dev/serial/by-id/usb-u-blox_AG_-_www.u-blox.com_u-blox_7_-_GPS_GNSS_Receiver-if00'
        mport='/dev/serial0'
        if self.use_test_data == False:
            self.ser = serial.Serial(
                port = mport,
                baudrate = 9600,
                timeout = 2,
                bytesize = serial.EIGHTBITS,
                parity = serial.PARITY_NONE,
                stopbits = serial.STOPBITS_ONE
            )

        self.response = GpsObject()

    def log_to_file(self, response):
        self.write_file.write(response)
        self.write_file.flush()

    def log_to_csv(self, response):
        self.program_file.write(response)
        self.program_file.flush()

    def stopApp(self):
        self.running = False

    def run(self):
        self.setup()
        while self.running:
            try:
                data = ''
                if self.use_test_data:
                    data = self.f.readline()
                    #print(data)
                    if data is None or data == '':
                        break
                else:
                    data = self.ser.readline().decode()
                self.parseGPS(data, self.response)
                if self.response.is_valid:
                    self.log_to_file(response=str(self.response))
                    self.log_to_csv(response=self.response.parse_str())
                    if self.use_test_data:
                        time.sleep(1)
                if self.use_test_data:
                    self.beta_test_gps.write(data)
                    self.beta_test_gps.flush()
                else:
                    print(str(self.response))
            except Exception as e:
                print(e)

    def handleFiles(self):
        self.renameFiles(path+'/test_data/test_output%s.txt')
        self.write_file = open(path+'/test_data/test_output0.txt', 'w')

        self.renameFiles(path+'/test_data/test_csv_output%s.txt')
        self.program_file = open(path+'/test_data/test_csv_output0.txt', 'w')

        self.renameFiles(path+'/test_data/test_gps_input%s.txt')
        self.beta_test_gps = open(path+'/test_data/test_gps_input0.txt', 'w')

    def renameFiles(self, fileName):
        i = 0
        while os.path.exists(fileName % i) and i < 3:
            i += 1

        for x in range(i):
            source = str(fileName%x)
            dest = str(fileName%str(x+1))
            os.rename(source, dest)



if __name__ == '__main__':
    gpsParse = GpsParser()
    gpsParse.run()
