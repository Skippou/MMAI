import numpy as np
import cv2 as cv
import os

from time import time
from windowcapture import WindowCapture

# Change the working directory to the folder this script is in.
# Doing this because I'll be putting the files from each video in their own folder on GitHub
os.chdir(os.path.dirname(os.path.abspath(__file__)))

windowName = 'Mini Motorways'

# initialize the WindowCapture class


loop_time = time()

while(True):

    # get an updated image of the game
    wincap = WindowCapture(windowName)
    screenshot = wincap.get_screenshot(2)
    
    cv.imshow(windowName + " Computer Vision", screenshot)

    # debug the loop rate
    print('FPS {}'.format(1 / (time() - loop_time)))
    loop_time = time()

    # press 'q' with the output window focused to exit.
    # waits 1 ms every loop to process key presses
    if cv.waitKey(1) == ord('q'):
        cv.destroyAllWindows()
        break

print('Done')