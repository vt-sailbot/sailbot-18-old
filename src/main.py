#!/usr/bin/python

import time
from modules.server import ServerThread
import threading
import json
from modules.location import Location
import logging
import tornado.websocket
import modules.calc
try:
    import modules.gps
except ImportError:
    pass
import modules.utils
import modules.logging

# Variables and constants

data = {'category': 'data', 'timestamp': 0, 'location': Location(0, 0),
        'heading': 0, 'speed': 0, 'wind_dir': 0, 'roll': 0, 'pitch': 0,
        'yaw': 0, 'state': 0}

target_locations = []
boundary_locations = []

values = {'debug': False, 'port': 8888, 'log_name': 'sailbot.log',
          'transmission_delay': 5, 'eval_delay': 30}



## ----------------------------------------------------------

class DataThread(threading.Thread):

    """ Transmits the data object to the server thread
    """

    server_thread = None

    def send_data(self, data):

        # do not log any data here, doing so would create an infinite loop

        try:
            server_thread.send_data(data)
        except tornado.websocket.WebSocketClosedError:
            print('Could not send data because the socket is closed.')

    def run(self):
        global server_thread

        # set up logging
        logging.getLogger().addHandler(modules.logging.WebSocketLogger(self))
        
        logging.info('Starting the data thread!')
        
        # set up server
        server_thread = ServerThread(name='Server', kwargs={'port': values['port'], 'target_locations': target_locations, 'boundary_locations': boundary_locations})
        server_thread.start()
        
        # start logging GPS data
        try:
            gpsp = modules.gps.GPSPoller()
            gpsp.start()
        except NameError:
            logging.critical("GPS not configured properly!")
        
        while True:
            server_thread.send_data(modules.utils.getJSON(data))
            logging.debug('Data sent to the server %s'
                         % json.dumps(json.loads(modules.utils.getJSON(data))))
            time.sleep(float(values['transmission_delay']))


## ----------------------------------------------------------

class MotorThread(threading.Thread):

    def set(self, property, value):
        try:
            f = open('/sys/class/rpi-pwm/pwm0/' + property, 'w')
            f.write(value)
            f.close()
        except:
            logging.error('Error writing to: ' + property + ' value: ' + value)

    def setServo(self, angle):
        self.set('servo', str(angle))

    def configureServos(self):
        self.set('delayed', '0')
        self.set('mode', 'servo')
        self.set('servo_max', '180')
        self.set('active', '1')

    def run(self):
        self.configureServos()


## ----------------------------------------------------------

if __name__ == '__main__':
    try:
        threading.current_thread().setName('Main')

        modules.utils.setup_config(values)
        modules.utils.setup_locations(target_locations, boundary_locations)

        logging.info('Beginning SailBOT autonomous navigation routines....')

        data_thread = DataThread(name='Data')
        motor_thread = MotorThread(name='Motor')

        data_thread.start()
        motor_thread.start()
    except KeyboardInterrupt:
        logging.critical('Program terminating!')


            