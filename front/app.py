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


@eel.expose
def say_hello_py(x):
    print('Hello from %s' % x)


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
    print("Opening python...")
    start_eel(True)
