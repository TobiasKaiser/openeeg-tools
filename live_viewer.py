#!/usr/bin/env python3

import pygame
from connection import OpenEEGReader
import threading
import serial

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)


class LiveViewer(object):
    TARGET_FPS = 30.0
    TARGET_MS_PER_FRAME = int(1000.0 / TARGET_FPS)

    BUFFER_SIZE = 800

    FULL_SCALE = 1024

    class Reader(OpenEEGReader):
        def __init__(self, serial_port, live_viewer):
            super(LiveViewer.Reader, self).__init__(serial_port)
            self.live_viewer = live_viewer

        def handle_data(self, data):
            for chan_idx in range(2):
                self.live_viewer.buf[chan_idx][self.live_viewer.buf_ptr[chan_idx]] = data[chan_idx]
                self.live_viewer.buf_ptr[chan_idx] = \
                    (self.live_viewer.buf_ptr[chan_idx] + 1) % self.live_viewer.BUFFER_SIZE 

    def __init__(self, serial_port):
        self.reader = self.Reader(serial_port, self)

        self.buf = {}
        self.buf_ptr = {}
        for i in range(8):
            self.buf[i]=self.BUFFER_SIZE*[0]
            self.buf_ptr[i]=0

    def update_window(self):
        self.window.fill(WHITE)

        for chan_idx in range(2):

            for i in range(self.BUFFER_SIZE-1):
                size = 100.0

                scale_factor = size / self.FULL_SCALE

                pygame.draw.line(self.window, BLUE,
                    (i,   size*chan_idx + size - scale_factor * self.buf[chan_idx][(self.buf_ptr[chan_idx]-i)%self.BUFFER_SIZE]),
                    (i+1, size*chan_idx + size - scale_factor * self.buf[chan_idx][(self.buf_ptr[chan_idx]-i-1)%self.BUFFER_SIZE]),
                    1)
        pygame.display.update()


    def run(self):
        pygame.init()
        self.window = pygame.display.set_mode((800, 600), 0, 32)
        pygame.display.set_caption('OpenEEG live viewer')

        last_update = 0.0

        t=threading.Thread(target=self.reader.run)
        t.start()

        while True:
            
            next_update = pygame.time.get_ticks() + self.TARGET_MS_PER_FRAME
            self.update_window()
            pygame.time.wait(max(0, next_update-pygame.time.get_ticks()))
            
            print(pygame.time.get_ticks())



if __name__ == "__main__":
    LiveViewer(serial.Serial('/dev/ttyUSB0', 57600)).run()