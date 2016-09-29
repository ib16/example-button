import mraa
import threading

def reset_button_pressing(button):
    button.pressing = False

def button_callback(button):
    if not button.pressing:
        button.pressing = True
        button.timer = threading.Timer(0.3, reset_button_pressing, args=[button])
        button.timer.start()
        if button.on_press is not None:
            print("go")
            if button.knob is not None:
                button.on_press(button, button.knob)
            else:
                button.on_press(button, None)

class Button:
    b_io = None
    on_press = None
    pressing = False
    timer = None  # Timer
    knob = None

    def __init__(self, knob):
        self.b_io = mraa.Gpio(33)
        self.b_io.dir(mraa.DIR_IN)
        self.b_io.mode(mraa.MODE_PULLUP)
        self.b_io.isr(mraa.EDGE_FALLING, button_callback, self)
        self.knob = knob

    def get_status(self):
        return self.b_io.read()


def callback(sender):
    position = sender.get_position()
    print("knob callback: %d" % (position))
    if sender.on_position_change is not None:
        sender.on_position_change(position)

class Knob:
    s1 = None
    s2 = None
    on_position_change = None

    def __init__(self):
        self.s1 = mraa.Gpio(31)  # J19-4
        self.s1.dir(mraa.DIR_IN)
        self.s1.mode(mraa.MODE_PULLUP)
        self.s1.isr(mraa.EDGE_BOTH, callback, self)

        self.s2 = mraa.Gpio(32)  # J19-5
        self.s2.dir(mraa.DIR_IN)
        self.s2.mode(mraa.MODE_PULLUP)
        self.s2.isr(mraa.EDGE_BOTH, callback, self)

    def get_position(self):
        s1_val = self.s1.read()
        s2_val = self.s2.read()
        if s1_val == 1 and s2_val == 1:
            return 1
        elif s1_val == 1 and s2_val == 0:
            return 2
        elif s1_val == 0 and s2_val == 0:
            return 3
        elif s1_val == 0 and s2_val == 1:
            return 4

    def inspect(self):
        print("s1: %d, s2: %d" % (self.s1.read(), self.s2.read()))
