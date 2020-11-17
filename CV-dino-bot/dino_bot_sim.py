from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys

from collections import deque
import random
import pickle
from io import BytesIO
import base64
import json

import cv2
import numpy as np
from PIL import Image

game_url = "chrome://dino"
chrome_driver_path = "./chromedriver"
#scripts
#create id for canvas for faster selection from DOM
init_script = "document.getElementsByClassName('runner-canvas')[0].id = 'runner-canvas'"

#get image from canvas
getbase64Script = "canvasRunner = document.getElementById('runner-canvas'); return canvasRunner.toDataURL().substring(22)"



def grab_screen(_driver):
    image_b64 = _driver.execute_script(getbase64Script)
    screen = np.array(Image.open(BytesIO(base64.b64decode(image_b64))))
    screen = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)  # RGB to Grey Scale

    screen_roi = screen[50:, :500]  # Crop Region of Interest(ROI)
    ret, thr = cv2.threshold(screen_roi,230,255,cv2.THRESH_BINARY)

    # print(thr.shape)
    # cv2.imwrite('test.png',screen)
    # cv2.waitKey(1)
    return thr



class Game:
    def __init__(self,custom_config=True):
        chrome_options = Options()
        chrome_options.add_argument("disable-infobars")
        chrome_options.add_argument("--mute-audio")
        self._driver = webdriver.Chrome(executable_path = chrome_driver_path,chrome_options=chrome_options)
        self._driver.set_window_position(x=-10,y=0)
        try:
            self._driver.get('chrome://dino')
        except:
            self._driver.execute_script("Runner.config.ACCELERATION=0")
            self._driver.execute_script(init_script)
    def get_crashed(self):
        return self._driver.execute_script("return Runner.instance_.crashed")
    def get_playing(self):
        return self._driver.execute_script("return Runner.instance_.playing")
    def restart(self):
        self._driver.execute_script("Runner.instance_.restart()")
    def press_up(self):
        self._driver.find_element_by_tag_name("body").send_keys(Keys.ARROW_UP)
    def get_score(self):
        score_array = self._driver.execute_script("return Runner.instance_.distanceMeter.digits")
        score = ''.join(score_array) # the javascript object is of type array with score in the formate[1,0,0] which is 100.
        return int(score)
    def pause(self):
        return self._driver.execute_script("return Runner.instance_.stop()")
    def resume(self):
        return self._driver.execute_script("return Runner.instance_.play()")
    def end(self):
        self._driver.close()

    def show_img(self):
        """
        Show images in new window
        """
        while True:
            # screen = (yield)
            screen = grab_screen(self._driver)
            # window_title = "logs" if graphs else "game_play"
            cv2.namedWindow("game", cv2.WINDOW_NORMAL)
            imS = cv2.resize(screen, (800, 400))
            cv2.imshow("game", screen)
            if (cv2.waitKey(1) & 0xFF == ord('q')):
                cv2.destroyAllWindows()
                break

class DinoAgent:
    def __init__(self,game): #takes game as input for taking actions
        self._game = game
        self.jump() #to start the game, we need to jump once
    def is_running(self):
        return self._game.get_playing()
    def is_crashed(self):
        return self._game.get_crashed()
    def jump(self):
        self._game.press_up()
    def duck(self):
        self._game.press_down()
    def judge(self):
        while True:
            screen = grab_screen(self._game._driver)
if __name__ == '__main__':
    game = Game()
    dino = DinoAgent(game)
    dino.judge()
    # game.press_up()
    # game.show_img()
