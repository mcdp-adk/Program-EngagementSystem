import threading
import cv2
from threading import Thread
from engagement_detect import predict
import eel
import sys
import platform

"""
原理是：
测试环境：
1、测试环境设置启动页面为vue的测试服务端口，然后将app设为None，
2、将端口和vue的public/index.html 中的eel.js绑定/
生产环境：
和正常的一样使用
"""


class NetCore(threading.Thread):

    def __init__(self):
        super().__init__()
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        self.running = True
        self.nowAttention = ""

    def getAttention(self):
        return self.nowAttention

    def run(self):
        index = 0
        frames = list()
        while self.running:
            _, frame = self.cap.read()

            if frame is None:
                break
            # 隔20帧采样
            if index % 20 == 0 and len(frames) < 8:
                frames.append(frame)
            # 凑够8帧就开始检测
            elif len(frames) == 8:
                # 这里要用多线程来处理，不然画面会卡
                # t = Thread(target=predict, args=(frames,))
                # t.start()
                level, pos = predict(frames)
                self.nowAttention = str(level)

                frames = list()

            cv2.waitKey(10)
            index += 1


def oldRun():
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    frames = list()
    index = 0
    while True:
        _, frame = cap.read()

        if frame is None:
            break
        # 隔20帧采样
        if index % 20 == 0 and len(frames) < 8:
            frames.append(frame)
        # 凑够8帧就开始检测
        elif len(frames) == 8:
            # 这里要用多线程来处理，不然画面会卡
            t = Thread(target=predict, args=(frames,))
            t.start()
            frames = list()

        cv2.imshow('image', frame)
        cv2.waitKey(10)
        index += 1


core = NetCore()


def runCoreThread():
    core.start()


@eel.expose
def getNowAttention():
    return core.getAttention()

def start_eel(develop):
    """Start Eel with either production or development configuration."""
    if develop:
        directory = 'src'
        app = None
        page = {'port': 8080}
        eel_kwargs = dict(
            mode=app,
            host="localhost",
            port=9000,
        )
    else:
        directory = 'web'
        app = 'chrome'
        page = 'index.html'
        eel_kwargs = dict(
            mode=app,
            port=0,
            size=(1920, 1080),
        )
    eel.init(directory)
    try:
        eel.start(page, **eel_kwargs)
    except EnvironmentError:
        # If Chrome isn't found, fallback to Microsoft Edge on Win10 or greater
        if sys.platform in ["win32", "win64"] and int(platform.release()) >= 10:
            eel.start(page, mode="edge", **eel_kwargs)
        else:
            raise


if __name__ == "__main__":
    core.start()
    print("Core started")
    start_eel(True)
