import pyautogui
import numpy as np
import cv2 as cv
import win32gui, win32ui, win32con
from time import time
from mss import mss



class WindowCapture:

    # properties
    w = 1920
    h = 1080
    hwnd = None
    cropped_x = 0
    cropped_y = 0
    offset_x = 0
    offset_y = 0
    top = 0
    left = 0
    width = 0
    height = 0

    # constructor
    def __init__(self, window_name):
        # find the handle for the window we want to capture
        self.hwnd = win32gui.FindWindow(None, window_name)
        if not self.hwnd:
            raise Exception('Window not found: {}'.format(window_name))

        # get the window size
        window_rect = win32gui.GetWindowRect(self.hwnd) #(left, top, right, bottom)
        self.w = window_rect[2] - window_rect[0]
        self.h = window_rect[3] - window_rect[1]
        
        

        # account for the window border and titlebar and cut them off
        border_pixels = 8
        titlebar_pixels = 30
        self.w = self.w - (border_pixels * 2)
        self.h = self.h + titlebar_pixels - border_pixels
        self.cropped_x = border_pixels
        self.cropped_y = titlebar_pixels

        #for MCC method
        self.top = window_rect[1]
        self.bottom = window_rect[3]
        self.left = window_rect[0]
        self.right = window_rect[2]

        self.top_cropped = window_rect[1]+titlebar_pixels
        self.left_cropped = window_rect[0] + border_pixels
        self.height = window_rect[3] - window_rect[1] - (border_pixels*2)-titlebar_pixels
        

        # set the cropped coordinates offset so we can translate screenshot
        # images into actual screen positions
        self.offset_x = window_rect[0] + self.cropped_x
        self.offset_y = window_rect[1] + self.cropped_y

    def get_screenshot(self,method = 1):
        if method == 1:
            # get the window image data
            hwindc = win32gui.GetWindowDC(self.hwnd)
            srcdc = win32ui.CreateDCFromHandle(hwindc)
            memdc = srcdc.CreateCompatibleDC()
            dataBitMap = win32ui.CreateBitmap()
            dataBitMap.CreateCompatibleBitmap(srcdc, self.w, self.h)
            memdc.SelectObject(dataBitMap)
            memdc.BitBlt((0, 0), (self.w, self.h), srcdc, (self.cropped_x, self.cropped_y), win32con.SRCCOPY)

            # convert the raw data into a format opencv can read
            #dataBitMap.SaveBitmapFile(memdc , 'debug.bmp')
            signedIntsArray = dataBitMap.GetBitmapBits(True)
            img = np.frombuffer(signedIntsArray, dtype=np.uint8)
            img.shape = (self.h, self.w, 4)

            # free resources
            srcdc.DeleteDC()
            memdc.DeleteDC()
            win32gui.ReleaseDC(self.hwnd, hwindc)
            win32gui.DeleteObject(dataBitMap.GetHandle())

            # drop the alpha channel, or cv.matchTemplate() will throw an error like:
            #   error: (-215:Assertion failed) (depth == CV_8U || depth == CV_32F) && type == _templ.type() 
            #   && _img.dims() <= 2 in function 'cv::matchTemplate'
            img = img[...,:3]

            # make image C_CONTIGUOUS to avoid errors that look like:
            #   File ... in draw_rectangles
            #   TypeError: an integer is required (got type tuple)
            # see the discussion here:
            # https://github.com/opencv/opencv/issues/14866#issuecomment-580207109
            img = np.ascontiguousarray(img)
        elif method == 2:
            # The simplest use, save a screen shot of the 1st monitor
            with mss() as sct:
                monitor = {"top": self.top_cropped, "left": self.left_cropped, "width": self.w, "height": self.height}
                img = np.array(sct.grab(monitor))
            
        elif method == 3:
            img = pyautogui.screenshot()
            img = np.array(img)
            img = cv.cvtColor(img,cv.COLOR_RGB2BGR)
        
        return img

    # find the name of the window you're interested in.
    # once you have it, update window_capture()
    # https://stackoverflow.com/questions/55547940/how-to-get-a-list-of-the-name-of-every-open-window
    def list_window_names(self):
        def winEnumHandler(hwnd, ctx):
            if win32gui.IsWindowVisible(hwnd):
                print(hex(hwnd), win32gui.GetWindowText(hwnd))
        win32gui.EnumWindows(winEnumHandler, None)

    # translate a pixel position on a screenshot image to a pixel position on the screen.
    # pos = (x, y)
    # WARNING: if you move the window being captured after execution is started, this will
    # return incorrect coordinates, because the window position is only calculated in
    # the __init__ constructor.
    def get_screen_position(self, pos):
        return (pos[0] + self.offset_x, pos[1] + self.offset_y)

if __name__ == "__main__":

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