from PySide6.QtCore import QObject, QTimer


class SplashSequenceManager(QObject):
    def __init__(self, bridge, parent=None):
        super().__init__(parent)
        self.bridge = bridge
        self.steps = []
        self.current_index = 0
        self.done_callback = None

    def add_step(self, message, delay_ms=1000):
        self.steps.append((message, delay_ms))

    def start(self, on_done=None):
        self.current_index = 0
        self.done_callback = on_done
        self._next_step()

    def _next_step(self):
        if self.current_index >= len(self.steps):
            if self.done_callback:
                self.done_callback()
            return

        message, delay = self.steps[self.current_index]
        self.bridge.setMessage(message)
        self.current_index += 1
        QTimer.singleShot(delay, self._next_step)
