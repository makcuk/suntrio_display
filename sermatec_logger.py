import struct
import socket
from enum import Enum
from time import sleep

class Cmd(object):
    INFO = 0x98
    GRID = 0x9a
    PV = 0x0b
    HZ = 0x99

class Sermatec:
    logger_ip = "pvdisplay.local"

    data_init = [0xfe, 0x55, 0x64, 0x14, 0x98, 0x00, 0x00, 0x4c, 0xae]
    request_pv = [0xfe,0x55,0x64,0x14,0x0b,0x00,0x00,0xdf,0xae]
    request_hz= [0xfe, 0x55 ,0x64 ,0x14 ,0x0a ,0x00, 0x00,0xde,0xae]
    request_daily = [0xfe ,0x55 ,0x64 ,0x14 ,0x99 ,0x00 ,0x00 ,0x4d, 0xae]


    def connect(self, logger_ip, logger_port = 8899):
        self.logger_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.logger_socket.settimeout(3)
        self.logger_socket.connect((self.logger_ip, 8899))

    def get_data(self, debug = False):
        step = 2
        pv_power = 0
        daily_power = 0
        for req in (self.request_pv, self.request_daily, self.request_daily):
            self.logger_socket.sendall(bytes(req))
            reply = self.logger_socket.recv(1550)
            command = reply[4]
            if debug: print("command", command)
            if command == Cmd.INFO:
                serial = reply[13:39]
                version = int.from_bytes(reply[7:9], "big")
                if debug: print(serial, version)
            elif command == Cmd.PV:
                reply_a = []
                for i in range(7, reply[6], step):
#                print(i, ":", reply[i:i+step].hex(), int.from_bytes(reply[i:i+step], "big")) #, int.from_bytes(reply[i:i+4], "big"))
                    reply_a.append(int.from_bytes(reply[i:i+step], "big"))
                if debug: 
                    print("PV1", reply_a[2],'W', reply_a[3]/10,'V', reply_a[4]/10, 'A')
                    print("PV2", reply_a[5],'W', reply_a[6]/10,'V', reply_a[7]/10, 'A')
                pv_power = reply_a[2]+reply_a[5]
            elif command == Cmd.HZ:

                reply_a = []
                for i in range(7, reply[6], step):
#                print(i, ":", reply[i:i+step].hex(), int.from_bytes(reply[i:i+step], "big")) #, int.from_bytes(reply[i:i+4], "big"))
                    reply_a.append(int.from_bytes(reply[i:i+step], "big"))
                if debug: print("daily", reply_a[0]/10, "total", reply_a[2])
                daily_power = reply_a[0]/10
            sleep(1)
        return (pv_power, daily_power)

if __name__ == "__main__":
        sm = Sermatec()
        sm.connect("pvdisplay.local")
        print(sm.get_data())

