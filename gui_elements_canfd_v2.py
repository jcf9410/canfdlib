import canfdlib
from mttkinter import mtTkinter as tk
import tkMessageBox
from Adafruit_GPIO.FT232H import FT232H
from gui_constants import *
from constants import *
import tests

class canfdgui():
    def __init__(self, inputDict=None, debug=False):
        self.inputDict = inputDict
        self.debug = debug

        self.rxd = []
        self.txd = []

        self.window = tk.Tk()
        self.window.title(window_title)
        self.window.geometry(window_size)

        self.right_frame = tk.Frame(self.window, width=450, height=100)
        self.left_frame = tk.Frame(self.window, width=250, height=100)
        self.corner_frame = tk.Frame(self.window, width=100, height=20)
        self.extra_frame = tk.Frame(self.window, width=30, height=100)
        self.window.grid_columnconfigure(1, weight=1)
        self.right_frame.grid(row=0, column=1, sticky="nsew")
        self.left_frame.grid(row=0, column=0, sticky="nsew")
        self.corner_frame.grid(row=1,column=0,sticky="sw")
        self.extra_frame.grid(row=0, column=2)

        # textbot for rx
        self.rx_box_scrollbar = tk.Scrollbar(self.left_frame)
        self.rx_box_text = tk.Text(self.left_frame, height=rx_textbox_height, width=rx_textbox_width)
        self.rx_box_scrollbar.grid(column=1, row=0,  sticky=tk.N+tk.S+tk.W)
        self.rx_box_text.grid(column=0, row=0)
        self.rx_box_scrollbar.config(command=self.rx_box_text.yview)
        self.rx_box_text.config(yscrollcommand=self.rx_box_scrollbar.set)

        # rx button
        self.receive_start_button = tk.Button(self.right_frame, text="Start RX", command = self.receive)
        self.receive_start_button.grid(column=0,row=0, pady=5)

        # clear rx box windows button
        self.clear_button = tk.Button(self.right_frame, text="Clear", command=self.clear)
        self.clear_button.grid(column=0, row=1, pady=5)

        # tx button
        self.transmit_start_button = tk.Button(self.corner_frame, text="Start TX", command=self.transmit)
        self.transmit_start_button.grid(column=2,row=0)

        # tx message
        self.tx_msg = tk.Entry(self.corner_frame, width=tx_msg_width)
        self.tx_msg.grid(column=1,row=0)

        # tx label
        self.txlbl = tk.Label(self.corner_frame, text="TX Message:")
        self.txlbl.grid(column=0, row=0)

        # rx channel button
        self.rx_channel_button = tk.Button(self.right_frame, text="Set RX channel", command=self.setRXchannel)
        self.rx_channel_button.grid(column=1, row=3, pady=5)

        # rx channel
        self.rx_channel = tk.Entry(self.right_frame, width=10)
        self.rx_channel.grid(column=1, row=4, pady=5)

        # tx channel button
        self.tx_channel_button = tk.Button(self.right_frame, text="Set TX channel", command=self.setTXchannel)
        self.tx_channel_button.grid(column=0, row=3, pady=5)

        # tx channel
        self.tx_channel = tk.Entry(self.right_frame, width=10)
        self.tx_channel.grid(column=0, row=4, pady=5)

        # reset button
        self.reset_button = tk.Button(self.right_frame, text="Reset Device", command=self.reset)
        self.reset_button.grid(column=0,row=2, pady=5)

        # opMode droplist and button
        OPTIONS = ["NORMAL_MODE","SLEEP_MODE","INTERNAL_LOOPBACK_MODE","LISTEN_ONLY_MODE","CONFIGURATION_MODE","EXTERNAL_LOOPBACK_MODE","CLASSIC_MODE","RESTRICTED_MODE","INVALID_MODE"]

        self.droplist = tk.StringVar(self.left_frame)
        self.droplist.set(OPTIONS[0])  # default value

        w = tk.OptionMenu(self.right_frame, self.droplist, *OPTIONS)
        w.grid(column=1,row=1, padx=5)

        self.opmode_button = tk.Button(self.right_frame, text="Set config mode", command=self.changemode)
        self.opmode_button.grid(column=1,row=2, pady=5)

        # stop button
        self.stop_button = tk.Button(self.right_frame, text="STOP", command=self.stop)
        self.stop_button.grid(column=1, row=0, pady=5)

        # connect button
        self.connect_button = tk.Button(self.extra_frame, text="CONNECT", command=self.connect)
        self.connect_button.grid(column=0, row=2, pady=0) # enlarge
        self.connect_button.config(height=3, width=15)

        # dlc droplist and button
        OPTIONS_dlc = ["CAN_DLC_0","CAN_DLC_1","CAN_DLC_2","CAN_DLC_3","CAN_DLC_4","CAN_DLC_5","CAN_DLC_6","CAN_DLC_7","CAN_DLC_8","CAN_DLC_12","CAN_DLC_16","CAN_DLC_20","CAN_DLC_24","CAN_DLC_32","CAN_DLC_48","CAN_DLC_64"]

        self.droplist_dlc = tk.StringVar(self.extra_frame)
        self.droplist_dlc.set(OPTIONS_dlc[-1])  # default value

        w_dlc = tk.OptionMenu(self.extra_frame, self.droplist_dlc, *OPTIONS_dlc)
        w_dlc.grid(column=0, row=0, padx=5)

        self.dlc_button = tk.Button(self.extra_frame, text="Set DLC", command=self.changedlc)
        self.dlc_button.grid(column=0, row=1, pady=5)

        self.canfd = None

        if self.debug:
           # self.window.after(1000, self.dummy_main)
            pass
        else:
            try:
                self.connect()
            except RuntimeError:
                self.rx_box_text.insert(tk.END, "Device not ready. Connect manually." + '\n')
            self.window.after(0, self.main)
        self.window.mainloop()

    def connect(self):
        if self.debug:
            print "Debug mode"
            self.rx_box_text.insert(tk.END, "Debug mode" + '\n')
        else:
            try:
                ft232h = self.inputDict["ft232h"]
                cs = self.inputDict["cs"]
                max_speed_hz = self.inputDict["max_speed_hz"]
                mode = self.inputDict["mode"]
                bitorder = self.inputDict["bitorder"]
                SPI_DEFAULT_BUFFER_LENGTH = self.inputDict["SPI_DEFAULT_BUFFER_LENGTH"]
                SPI_MAX_BUFFER_LENGTH = self.inputDict["SPI_MAX_BUFFER_LENGTH"]
                SPI_BAUDRATE = self.inputDict["SPI_BAUDRATE"]
                self.canfd = canfdlib.CANFD_SPI(ft232h, cs, max_speed_hz, mode, bitorder, SPI_DEFAULT_BUFFER_LENGTH, SPI_MAX_BUFFER_LENGTH, SPI_BAUDRATE)
                self.rx_box_text.insert(tk.END, "Device connected succesfully!" + '\n')
            except RuntimeError:
                print "An error ocurred connecting to the device!"
                self.rx_box_text.insert(tk.END, "An error ocurred connecting to the device!" + '\n')
            except TypeError:
                if inputDict == None:
                    print "Some parameter is not defined. Check the input dictionary"
                    self.rx_box_text.insert(tk.END, "An error ocurred connecting to the device!" + '\n')
                else:
                    print "Some error ocurred in the type of input parameters"
                    self.rx_box_text.insert(tk.END, "Some error ocurred in the type of input parameters" + '\n')
            except:
                print "An unexpected error ocurred!"
                self.rx_box_text.insert(tk.END, "An unexpected error ocurred! Connect manually" + '\n')


    def init(self):
        self.canfd.state = APP_STATE_INIT
        # call initialize() from button
        self.rx_box_text.insert(tk.END, 'Initializing device...' + '\n')

    def receive(self):
        # start receiving
        self.canfd.state = APP_STATE_RECEIVE
    
        # print results
        self.rx_box_text.insert(tk.END, '{}'.format(self.rxd) + '\n')

    def transmit(self):
        input = self.tx_msg.get()
        if 'test' in input:
            self.launchTest(input)
        else:
            self.txd = [int(value) for value in input.split('')]
            self.canfd.state = APP_STATE_TRANSMIT

    def setRXchannel(self):
        # set rx channel and reset
        try:
        #if self.rx_channel.get() in range(0, 32):
            channel = int(self.rx_channel.get())
            self.canfd.state = "idle"
            self.canfd.rxchannel = channel
            self.canfd.reset()
       #else:
        except ValueError:
            tkMessageBox.showinfo("Warning", "Not a valid channel.\nTry a number in range(0, 32)")

    def setTXchannel(self):
        # set tx channel and reset
        if self.tx_channel.get() in range(0,32):
            self.canfd.state = "idle"
            self.canfd.txchannel = self.tx_channel.get()
            self.canfd.reset()
        else:
            tkMessageBox.showinfo("Warning", "Not a valid channel.\nTry a number in range(0,32)")

    def pause(self):
        # put state to idle  and do nothing
        self.canfd.state = "idle"

    def stop(self):
        # put state to stop, and abort execution
        self.canfd.state = "stop"

    def clear(self):
        # clear window
        self.rx_box_text.delete('1.0', tk.END)

    def reset(self):
        self.canfd.state = "idle"
        self.canfd.reset()
        self.rx_box_text.insert(tk.END, "Resetting..." + '\n')

    def changemode(self):
        self.canfd.state = "idle"
        mode = mode_dict[self.droplist.get()]
        self.canfd.operationModeSelect()
        self.canfd.reset()

    def changedlc(self):
        self.canfd.state = "idle"
        self.canfd.txdlc = dlc_dict[self.droplist_dlc.get()]

    def launchTest(self, test):
        test_num = int(test[-1])
        print(test_num)
        try:
            if test_num < 3:
                result = tests.test_dict[test]()
            else:
                result = tests.test_dict[test](self.canfd)
            self.rx_box_text.insert(tk.END, result + '\n')
            self.canfd.reset()
        except KeyError:
            self.rx_box_text.insert(tk.END, 'Test not found' + '\n')

    def main(self):
        # put main function here
        if self.canfd != None:
            if self.canfd.state == APP_STATE_INIT:
                # Initialize
                self.canfd.initialize()
                self.canfd.state = "idle"

            elif self.canfd.state == APP_STATE_TEST_RAM_ACCESS:
                ram_test_result = self.canfd.ramTest()
                if ram_test_result == -1:
                    self.rx_box_text.insert(tk.END, 'RAM test failed!' + '\n')
                else:
                    self.rx_box_text.insert(tk.END, 'RAM test successful!' + '\n')
                self.canfd.state = "idle"

            elif self.canfd.state == APP_STATE_TEST_REGISTER_ACCESS:
                register_test_result = self.canfd.registerTest()
                if register_test_result == -1:
                    self.rx_box_text.insert(tk.END, 'Register test failed!' + '\n')
                else:
                    self.rx_box_text.insert(tk.END, 'Register test successful!' + '\n')
                self.canfd.state = "idle"

            elif self.canfd.state == APP_STATE_INIT_TXOBJ:
                self.canfd.initTxObj()

            elif self.canfd.state == APP_STATE_RECEIVE:
                self.rxd = self.canfd.receiveMessageTasks()
                self.canfd.state = "idle"

            elif self.canfd.state == APP_STATE_TRANSMIT:

                self.canfd.transmitMessageTasks(self.txd)
                self.canfd.state = "idle"

            elif self.canfd.state == APP_STATE_REQUEST_CONFIG:
                self.canfd.operationModeSelect(CONFIGURATION_MODE)
                self.canfd.state = APP_STATE_WAIT_FOR_CONFIG

            elif self.canfd.state == APP_STATE_WAIT_FOR_CONFIG:
                opMode = self.canfd.operationModeGet()
                if opMode != CONFIGURATION_MODE:
                    self.canfd.state = APP_STATE_WAIT_FOR_CONFIG
                else:
                    self.canfd.state = APP_STATE_INIT

            elif self.canfd.state == "idle":
                pass

            elif self.canfd.state == "stop":
                pass

    def dummy_main(self):
        print("Debug mode")
        self.window.after(1000, self.dummy_main)

try:
    ft232h = FT232H()
except RuntimeError:
    print("Device not found.")
    ft232h = None

inputDict = {"ft232h":ft232h,
             "cs":cs,
             "max_speed_hz":max_speed_hz,
             "mode":mode,
             "bitorder":bitorder,
             "SPI_DEFAULT_BUFFER_LENGTH":SPI_DEFAULT_BUFFER_LENGTH,
             "SPI_MAX_BUFFER_LENGTH":SPI_MAX_BUFFER_LENGTH,
             "SPI_BAUDRATE":SPI_BAUDRATE}

a = canfdgui(inputDict)