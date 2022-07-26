from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QObject
import asyncio


def invoke_repeating(func, time):
    async def do_func_repeating():
        while True:
            await asyncio.sleep(time)
            func()

    return asyncio.create_task(do_func_repeating())


class EventLoop(QObject):
    def __init__(self, app: QApplication):
        super().__init__()
        self.running = True

        self._app = app

        app.setQuitOnLastWindowClosed(False)
        app.lastWindowClosed.connect(self.close)

    def close(self):
        if len(self._app.allWindows()) == 1:
            self.running = False

    async def run(self):
        while self.running:
            await asyncio.sleep(1)

