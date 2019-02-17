#!/usr/bin/env python3

import struct
import serial

# See http://openeeg.sourceforge.net/doc/modeeg/firmware/modeeg-p2.c
# struct modeeg_packet
# {
#     uint8_t     sync0;      // = 0xA5
#     uint8_t     sync1;      // = 0x5A
#     uint8_t     version;    // = 2
#     uint8_t     count;      // packet counter. Increases by 1 each packet
#     uint16_t    data[6];    // 10-bit sample (= 0 - 1023) in big endian (Motorola) format
#     uint8_t     switches;   // State of PD5 to PD2, in bits 3 to 0
# };

PACKET_LENGTH = 17

class OpenEEGReader:
    def __init__(self, serial_port):
        self.port = serial_port

    def process_packet(self, buf):
        data = [0]*6
        sync0, sync1, version, count, \
            data[0], data[1], data[2], data[3], data[4], data[5], switches \
            = struct.unpack(">BBBBHHHHHHB",buf)
        if not (sync0 == 0xA5 and sync1 == 0x5A):
            raise Exception("OpenEEG sync lost.")
        print(data)

    def run(self):
        sync_found=False
        buf=bytearray()
        while not sync_found:
            buf+=self.port.read()
            print(buf)
            if not sync_found:
                for i in range(len(buf)-1):
                    if buf[i] == 0xA5 and buf[i+1]==0x5A:
                        buf = buf[i:]
                        sync_found = True
        while True:
            buf+=self.port.read()
            while len(buf)>=PACKET_LENGTH:
                packet, buf = buf[:PACKET_LENGTH], buf[PACKET_LENGTH:]
                self.process_packet(packet)

if __name__ == "__main__":
    OpenEEGReader(serial.Serial('/dev/ttyUSB0', 57600)).run()