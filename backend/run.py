#!/usr/bin/python3

import os
import sys
import logging
import time
import pyads
from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO, send, emit, Namespace
import threading
from threading import Timer
from queue import Queue


# ToDo: Serve Production Version from nginx

#############
# PYADS AREA
#############
class BC9000:
    def __init__(self, connection_string: pyads.Connection, offset=1):
        self.conn = connection_string
        self.deviceName = 'BC9000'
        self.dValues_quick = {}
        self.dValues_slow = {}
        self.MotorNum = offset
        self.lock_quick = False
        self.lock_slow = False
        # 66 Byte Struct
        self.create_symbol_links(offset)


    def create_symbol_links(self, offset):
        self.MotorNum = offset
        self.offset = (offset - 1) * 80
        # Connection area
        if not self.conn.is_open:
            self.conn.open()
        # Memory area
        self.dValues_quick = {
            'command': self.conn.get_symbol(index_group=pyads.INDEXGROUP_MEMORYBYTE, index_offset=self.offset, plc_datatype=pyads.PLCTYPE_INT),
            'seccommand': self.conn.get_symbol(index_group=pyads.INDEXGROUP_MEMORYBYTE, index_offset=self.offset + 2, plc_datatype=pyads.PLCTYPE_INT),
            'targetpos': self.conn.get_symbol(index_group=pyads.INDEXGROUP_MEMORYBYTE, index_offset=self.offset + 4, plc_datatype=pyads.PLCTYPE_DINT),
            'actpos': self.conn.get_symbol(index_group=pyads.INDEXGROUP_MEMORYBYTE, index_offset=self.offset + 8, plc_datatype=pyads.PLCTYPE_DINT),
            'state': self.conn.get_symbol(index_group=pyads.INDEXGROUP_MEMORYBYTE, index_offset=self.offset + 16, plc_datatype=pyads.PLCTYPE_INT),
            'error': self.conn.get_symbol(index_group=pyads.INDEXGROUP_MEMORYBYTE, index_offset=self.offset + 18, plc_datatype=pyads.PLCTYPE_SINT),
            'config': self.conn.get_symbol(index_group=pyads.INDEXGROUP_MEMORYBYTE, index_offset=self.offset + 58, plc_datatype=pyads.PLCTYPE_INT),
            'distmeas': self.conn.get_symbol(index_group=pyads.INDEXGROUP_MEMORYBYTE, index_offset=self.offset + 60, plc_datatype=pyads.PLCTYPE_DINT),
                        }

        self.dValues_slow = {
            'currA1': self.conn.get_symbol(index_group=pyads.INDEXGROUP_MEMORYBYTE, index_offset=self.offset + 12, plc_datatype=pyads.PLCTYPE_SINT),
            'currA2': self.conn.get_symbol(index_group=pyads.INDEXGROUP_MEMORYBYTE, index_offset=self.offset + 13, plc_datatype=pyads.PLCTYPE_SINT),
            'currB1': self.conn.get_symbol(index_group=pyads.INDEXGROUP_MEMORYBYTE, index_offset=self.offset + 14, plc_datatype=pyads.PLCTYPE_SINT),
            'currB2': self.conn.get_symbol(index_group=pyads.INDEXGROUP_MEMORYBYTE, index_offset=self.offset + 15, plc_datatype=pyads.PLCTYPE_SINT),
            'loadangle': self.conn.get_symbol(index_group=pyads.INDEXGROUP_MEMORYBYTE, index_offset=self.offset + 19, plc_datatype=pyads.PLCTYPE_SINT),
            'R32':  self.conn.get_symbol(index_group=pyads.INDEXGROUP_MEMORYBYTE, index_offset=self.offset + 20, plc_datatype=pyads.PLCTYPE_UINT),
            'R33': self.conn.get_symbol(index_group=pyads.INDEXGROUP_MEMORYBYTE, index_offset=self.offset + 22, plc_datatype=pyads.PLCTYPE_UINT),
            'R34': self.conn.get_symbol(index_group=pyads.INDEXGROUP_MEMORYBYTE, index_offset=self.offset + 24, plc_datatype=pyads.PLCTYPE_UINT),
            'R35': self.conn.get_symbol(index_group=pyads.INDEXGROUP_MEMORYBYTE, index_offset=self.offset + 26, plc_datatype=pyads.PLCTYPE_UINT),
            'R36': self.conn.get_symbol(index_group=pyads.INDEXGROUP_MEMORYBYTE, index_offset=self.offset + 28, plc_datatype=pyads.PLCTYPE_UINT),
            'R37': self.conn.get_symbol(index_group=pyads.INDEXGROUP_MEMORYBYTE, index_offset=self.offset + 30, plc_datatype=pyads.PLCTYPE_UINT),
            'R38': self.conn.get_symbol(index_group=pyads.INDEXGROUP_MEMORYBYTE, index_offset=self.offset + 32, plc_datatype=pyads.PLCTYPE_UINT),
            'R39': self.conn.get_symbol(index_group=pyads.INDEXGROUP_MEMORYBYTE, index_offset=self.offset + 34, plc_datatype=pyads.PLCTYPE_UINT),
            'R40': self.conn.get_symbol(index_group=pyads.INDEXGROUP_MEMORYBYTE, index_offset=self.offset + 36, plc_datatype=pyads.PLCTYPE_UINT),
            'R41': self.conn.get_symbol(index_group=pyads.INDEXGROUP_MEMORYBYTE, index_offset=self.offset + 38, plc_datatype=pyads.PLCTYPE_UINT),
            'R42': self.conn.get_symbol(index_group=pyads.INDEXGROUP_MEMORYBYTE, index_offset=self.offset + 40, plc_datatype=pyads.PLCTYPE_UINT),
            'R43': self.conn.get_symbol(index_group=pyads.INDEXGROUP_MEMORYBYTE, index_offset=self.offset + 42, plc_datatype=pyads.PLCTYPE_UINT),
            'R44': self.conn.get_symbol(index_group=pyads.INDEXGROUP_MEMORYBYTE, index_offset=self.offset + 44, plc_datatype=pyads.PLCTYPE_UINT),
            'R45': self.conn.get_symbol(index_group=pyads.INDEXGROUP_MEMORYBYTE, index_offset=self.offset + 46, plc_datatype=pyads.PLCTYPE_UINT),
            'R46': self.conn.get_symbol(index_group=pyads.INDEXGROUP_MEMORYBYTE, index_offset=self.offset + 48, plc_datatype=pyads.PLCTYPE_UINT),
            'virtposlimit': self.conn.get_symbol(index_group=pyads.INDEXGROUP_MEMORYBYTE, index_offset=self.offset + 50, plc_datatype=pyads.PLCTYPE_DINT),
            'virtneglimit': self.conn.get_symbol(index_group=pyads.INDEXGROUP_MEMORYBYTE, index_offset=self.offset + 54, plc_datatype=pyads.PLCTYPE_DINT),
            'diststate': self.conn.get_symbol(index_group=pyads.INDEXGROUP_MEMORYBYTE, index_offset=self.offset + 64, plc_datatype=pyads.PLCTYPE_INT),
            'distlatch': self.conn.get_symbol(index_group=pyads.INDEXGROUP_MEMORYBYTE, index_offset=self.offset + 66, plc_datatype=pyads.PLCTYPE_DINT),
            'homespeed': self.conn.get_symbol(index_group=pyads.INDEXGROUP_MEMORYBYTE, index_offset=self.offset + 70, plc_datatype=pyads.PLCTYPE_UINT),
            'homeacc': self.conn.get_symbol(index_group=pyads.INDEXGROUP_MEMORYBYTE, index_offset=self.offset + 72, plc_datatype=pyads.PLCTYPE_UINT),
            'reserve1': self.conn.get_symbol(index_group=pyads.INDEXGROUP_MEMORYBYTE, index_offset=self.offset + 74, plc_datatype=pyads.PLCTYPE_INT),
            'reserve2': self.conn.get_symbol(index_group=pyads.INDEXGROUP_MEMORYBYTE, index_offset=self.offset + 76, plc_datatype=pyads.PLCTYPE_INT),
            'reserve3': self.conn.get_symbol(index_group=pyads.INDEXGROUP_MEMORYBYTE, index_offset=self.offset + 78, plc_datatype=pyads.PLCTYPE_INT)
        }

    def get_values_quick(self):
        if not self.conn.is_open:
            self.conn.open()
        self.dEmitter = {key: self.dValues_quick[key].read() for key in self.dValues_quick}
        self.dEmitter['plc_running'] = True if self.conn.read_state()[1] == 0 else False
        self.dEmitter['MotorNum'] = str(self.MotorNum)
        return self.dEmitter

    def get_values_slow(self):
        if not self.conn.is_open:
            self.conn.open()
        self.dEmitter = {key: self.dValues_slow[key].read() for key in self.dValues_slow}
        return self.dEmitter

    def set_value(self, name: str, value):
        try:
            if not self.conn.is_open:
                self.conn.open()
            if name in self.dValues_quick:
                sym:pyads.AdsSymbol = self.dValues_quick[name]
                sym.write(value)
            elif name in self.dValues_slow:
                sym: pyads.AdsSymbol = self.dValues_slow[name]
                sym.write(value)
            else:
                raise NameError(f'{name} is no object in {self.__class__.__name__}')

        except:
            logging.error(f'Unable to write {name} to value {value} in {self.__class__.__name__}')
            logging.error(f'{sys.exc_info()[1]}')
            logging.error(f'Error on line {sys.exc_info()[-1].tb_lineno}')


#############
# FLASK AREA
#############
class Appl:
    def __init__(self, queue: Queue):
        app = Flask(__name__, static_folder="../dist/static", template_folder="../dist")
        app.config['SECRET_KEY'] = 'secret!'
        self.app = app  # Save app for decorator usage
        self.socketio = SocketIO(app, cors_allowed_origins='*')
        self.queue = queue
        self.socketio.on_namespace(CustomMethods(self.queue))
        self._port = 5000
        self._debug = True

        # Routing
        @app.route('/', defaults={'path': ''})
        @app.route('/<path:path>')
        def catch_all(path):
            return render_template("index.html")

    def run(self):
        self.socketio.run(self.app, debug=self._debug, host='0.0.0.0', port=int(self._port))


class CustomMethods(Namespace):
    def __init__(self, workQ:Queue):
        Namespace.__init__(self)
        self.workQ = workQ
        self.dTransfer = {}

    def on_req_DeviceType(self):
        self.dTransfer = self.workQ.queue[0]
        logging.info(f'Device Type requested. Returning {self.dTransfer["DeviceType"]}')
        return self.dTransfer['DeviceType']

    def on_MotorNum_changed(self, MotorNum):
        self.num = int(MotorNum)
        self.dTransfer = self.workQ.queue[0]
        self.dTransfer['MotorChanged'] = True
        self.dTransfer['MotorNum'] = self.num
        self.workQ.put(self.dTransfer)

    def on_set_value(self, name, value):
        self.dTransfer = self.workQ.queue[0]
        if self.dTransfer['Device'] is not None:
            self.dev_instance:BC9000 = self.dTransfer['Device']
            self.dev_instance.set_value(name, value)

    def on_connect(self):
        logging.info('socket connected')

    def on_disconnect(self):
        logging.info('socket disconnected')


###############
# RUNTIME AREA
###############
class Runtime(threading.Thread):
    def __init__(self, workQ:Queue, socket:SocketIO):
        threading.Thread.__init__(self)
        self.workQ = workQ
        self.dTransfer = {
            'DeviceType': '',
            'Device': None,
            'MotorChanged': False,
            'MotorNum': 1
        }
        self.workQ.put(self.dTransfer)
        self.dev = None
        self.dDataquick = {}
        self.dDataquick_bck = {}
        self.dDataslow = {}
        self.dDataslow_bck = {}
        self.socket = socket
        self.SENDER_AMS = '192.168.178.56.1.1'
        self.PLC_AMS = '192.168.178.200.1.1'
        self.PLC_IP = '192.168.178.200'
        self.PLC_USERNAME = 'pi'
        self.PLC_PASSWORD = 'raspberry'
        self.ROUTE_NAME = 'RouteToPC '
        self.HOSTNAME = '192.168.178.56'
        self.jobs_registered = False
        self._isWin = False
        if os.name == 'nt':
            self._isWin = True

    def run(self):
        # Loop
        #       Detect Connection state
        #       get type
        #       pull initial values
        #       connect on-change handlers
        #       write values from Frontend
        try:
            while True:
                if self.dev is None:
                    self.check_connection()
                    self.add_route_beckhoff()

                elif not self.jobs_registered:
                    self.quickjob = ThreadedTimer(0.1, self.send_data_quick)
                    self.slowjob = ThreadedTimer(2.5, self.send_data_slow)
                    self.jobs_registered = True
                else:
                    self.check_motornum()
                    time.sleep(1)

        except pyads.ADSError:
            logging.error('Connection to device was lost')
            logging.error(f'{sys.exc_info()[1]}')
            logging.error(f'Error on line {sys.exc_info()[-1].tb_lineno}')


        finally:
            if hasattr(self, 'quickjob'):
                self.quickjob.stop()
            if hasattr(self, 'slowjob'):
                self.slowjob.stop()
            self.jobs_registered = False


    def check_motornum(self):
        if self.dTransfer['MotorChanged']:
            self.dev.create_symbol_links(self.dTransfer.get('MotorNum'))
            self.dTransfer['MotorChanged'] = False

    def send_data_quick(self):
        if self.dev is not None:
            self.dDataquick = self.dev.get_values_quick()
            if self.dDataquick != self.dDataquick_bck:
                self.socket.emit('update_values_quick', self.dDataquick)
                self.dDataquick_bck = self.dDataquick
        else:
            logging.info('Device got overwritten')

    def send_data_slow(self):
        if self.dev is not None:
            self.dDataslow = self.dev.get_values_slow()
            if self.dDataslow != self.dDataslow_bck:
                self.socket.emit('update_values_slow', self.dDataslow)
                self.dDataslow_bck = self.dDataslow
        else:
            logging.info('Device got overwritten')

    # Create Route on PLC Side
    def add_route_beckhoff(self):
        if self._isWin:
            return
        pyads.open_port()
        pyads.set_local_address(self.SENDER_AMS)
        pyads.add_route_to_plc(self.SENDER_AMS, self.HOSTNAME, self.PLC_IP, self.PLC_USERNAME, self.PLC_PASSWORD, route_name=self.ROUTE_NAME)
        pyads.close_port()

    def check_connection(self):
        # Create Route on Client Side -> Win: Route has to be added via TwinCatRouter,
        # Linux Route is added on first connection
        # Todo: Add Routine to change ports on failure (pyads.TC2_PLC1 f.e.)
        pyads.PORT_BC = 800
        if self._isWin:
            self.plc = pyads.Connection(self.PLC_AMS, pyads.PORT_BC)
        else:
            self.plc = pyads.Connection(self.PLC_AMS, pyads.PORT_BC, self.PLC_IP)
        with self.plc as plc:
            try:
                if plc.read_device_info()[0] == 'COUPLER_PLC' and plc.read_state()[0] == 5:
                    self.dev = BC9000(plc, self.dTransfer.get('MotorNum'))
                    self.dTransfer['DeviceType'] = self.dev.deviceName
                    self.dTransfer['Device'] = self.dev
                elif plc.read_state()[0] != 5:
                    logging.warning(f'Device ADS State not ready. PLC state is {"running" if plc.read_state()[1]==0 else "stopped"}')
                else:
                    logging.error('Device type not implemented yet')

            except pyads.ADSError:
                logging.error(f'Device not connected or no ADS Server started on {self.PLC_AMS}')

            except:
                logging.error('Unknown error occured')


###############
# GENERAL AREA
###############
class ThreadedTimer(object):
    def __init__(self, interval, function, *args, **kwargs):
        self._timer = None
        self.interval = interval
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.is_running = False
        self.start()

    def _run(self):
        self.is_running = False
        try:
            self.function(*self.args, **self.kwargs)
            self.start()
        except:
            logging.error("Unable to run threaded function")
            logging.error(f'{sys.exc_info()[1]}')
            logging.error(f'Error on line {sys.exc_info()[-1].tb_lineno}')


    def start(self):
        if not self.is_running:
            self._timer = Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        self._timer.cancel()
        self.is_running = False


def init_logging():
    log_format = f"%(asctime)s [%(processName)s] [%(name)s] [%(levelname)s] %(message)s"
    log_level = logging.DEBUG
    if getattr(sys, 'frozen', False):
        folder = os.path.dirname(sys.executable)
    else:
        folder = os.path.dirname(os.path.abspath(__file__))
    # noinspection PyArgumentList
    logging.basicConfig(
        format=log_format,
        level=log_level,
        force=True,
        handlers=[
            logging.FileHandler(filename=f'{folder}\\debug.log', mode='w', encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ])


if __name__ == "__main__":
    init_logging()
    q = Queue()
    App = Appl(q)
    rt = Runtime(q, App.socketio)
    rt.daemon = True
    rt.start()
    # Move Runtime to another Thread
    App.run()
