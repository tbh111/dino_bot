from pynq.overlays.base import BaseOverlay
from pynq.lib.video import *
from pynq.lib import Pmod_IO
import cv2
import time
import numpy as np

class DinoAgent:
    def __init__(self):
        base = BaseOverlay("base.bit")
        print("Base Initialized")
        self.pmod_up = Pmod_IO(base.PMODA, 0, 'out')
        print("pmod A Initialized")
        self.pmod_down = Pmod_IO(base.PMODB, 2, 'out')
        print("pmod B Initialized")

        frame_out_w = 1920
        frame_out_h = 1080
        #Mode_in = VideoMode(frame_out_w, frame_out_h,24)
        Mode_out = VideoMode(frame_out_w, frame_out_h, 8)
        self.hdmi_in = base.video.hdmi_in
        self.hdmi_in.configure()
        print(self.hdmi_in.mode)
        
        self.hdmi_in.start()
        print("HDMI In Initialized")

        self.hdmi_out = base.video.hdmi_out
        #self.hdmi_out.configure(Mode_out,PIXEL_RGB)
        self.hdmi_out.configure(Mode_out,PIXEL_GRAY)
        self.hdmi_out.start()
        #print(self.hdmi_in.mode)
        print(self.hdmi_out.mode)
        print("HDMI Out Initialized")
        #self.hdmi_in.tie(self.hdmi_out)
        self.flag=1

        print("Game start")
        self.jump()
        self.flag=0
        self.bitwise_mode = 0

    def jump(self):
        if self.flag == 0:
            self.pmod_up.write(1)
        else:
            self.pmod_up.write(0)

    def duck(self):
        self.pmod_down.write(0)
        #time.sleep(0.1)
        self.pmod_up.write(1)

    def video_pipeline(self):
        try:
            while True:
                try:
                    inframe = self.hdmi_in.readframe()
                    inframe_gray = cv2.cvtColor(inframe, cv2.COLOR_BGR2GRAY)
                    ret, thr = cv2.threshold(inframe_gray, 150, 255, cv2.THRESH_BINARY)
                    thr = thr[300:480,:]
                    if ((thr[40:50,1100 ])==0).all():
                        cv2.bitwise_not(thr,thr)
                        self.bitwise_mode = 1
                    else:
                        self.bitwise_mode = 0
                    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
                    thr1 = cv2.morphologyEx(thr, cv2.MORPH_CLOSE, kernel)
                    self.judge(thr1)
                    #cv2.rectangle(thr,(240,0),(480,375),(255,255,255),2)
                    outframe = self.hdmi_out.newframe()
                    outframe[10:680,100:1380] = inframe_gray[:670,:]
                    outframe[690:870,100:1380] = thr
                    
                    cv2.line(thr1, (1100, 40), (1100, 50), (0, 0, 0), 2)
                    
                    outframe[880:1060,100:1380] = thr1
                    
                    inframe.freebuffer()
                    self.hdmi_out.writeframe(outframe)
                except KeyboardInterrupt:
                    self.hdmi_out.close()
                    self.hdmi_in.close()
                    print('close pipeline')
                    raise
                except ValueError:
                    self.hdmi_out.close()
                    self.hdmi_in.close()
                    print('val err close pipeline')
                    raise
        except KeyboardInterrupt:
                self.hdmi_out.close()
                self.hdmi_in.close()
                print('close pipeline')
                raise

    def judge(self, img):
        if self.bitwise_mode == 0:
            img_slice = img[135:180,200:240]
        else:
            img_slice = img[135:180,200:270]
        if((img_slice==0).any() and self.flag==0):
            self.jump()
            print('jump')
            self.flag=1
        elif((img_slice==0).any() and self.flag==1):
            self.jump()
            print('not jump')
        elif((img_slice==255).all()):
            self.flag=0
            

if __name__ == '__main__':
    dino = DinoAgent()
    dino.video_pipeline()
