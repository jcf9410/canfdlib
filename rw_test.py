import time
import Adafruit_GPIO as GPIO
#import Adafruit_GPIO.FT232H as ft
import ft
import binascii
import canfdlib
from constants import *


dicc = {NORMAL_MODE:'NORMAL_MODE',
    SLEEP_MODE:'SLEEP_MODE',
    INTERNAL_LOOPBACK_MODE: 'INTERNAL_LOOPBACK_MODE',
    LISTEN_ONLY_MODE: 'LISTEN_ONLY_MODE',
    CONFIGURATION_MODE: 'CONFIGURATION_MODE',
    EXTERNAL_LOOPBACK_MODE: 'EXTERNAL_LOOPBACK_MODE',
    CLASSIC_MODE:'CLASSIC_MODE',
    RESTRICTED_MODE: 'RESTRICTED_MODE',
    INVALID_MODE:'INVALID_MODE'
}

# Temporarily disable FTDI serial drivers.
ft.use_FT232H()
 
ft232h = ft.FT232H()

spi = ft.SPI(ft232h, cs=3, max_speed_hz=2000000, mode=0, bitorder=ft.MSBFIRST)

cINSTRUCTION_READ = 0x03
cINSTRUCTION_WRITE = 0x02

canfd = canfdlib.CANFD_SPI(ft232h, cs, max_speed_hz, mode, bitorder, SPI_DEFAULT_BUFFER_LENGTH, SPI_MAX_BUFFER_LENGTH, SPI_BAUDRATE)

### reset ###

canfd.reset()

#### tests #####

test = int(raw_input("Select test: "))

if test == 0:
    spiTransmitBuffer = []
    address = 0xE00
    spiTransmitBuffer.append((cINSTRUCTION_READ << 4) + ((address >> 8) & 0xF))
    spiTransmitBuffer.append(address & 0xFF)
    spi._assert_cs()
    spi.write(spiTransmitBuffer)
    response = spi.read(4)
    spi._deassert_cs()

    print ('Reading OSC register with SPI. Result:')
    #print ("Hex: {}".format(hex(binascii.hexlify(response))))
    print ("32-bit word: {}".format(binascii.hexlify(response)))
    print ("Bytes: {}".format(list(response)))

if test == 1:
    spiTransmitBuffer = []
    address = 0x000
    spiTransmitBuffer.append((cINSTRUCTION_READ << 4) + ((address >> 8) & 0xF))
    spiTransmitBuffer.append(address & 0xFF)
    spi._assert_cs()
    spi.write(spiTransmitBuffer)
    response_0 = spi.read(4)
    spi._deassert_cs()
    print ('CiCON register before writing:')
    print (binascii.hexlify(response_0))
    print(list(response_0))

    spiTransmitBuffer = []
    data = [0,0,0,0]
    print("Data to write (4 bytes): ")
    print(data)
    addressW = 0x000
    spiTransmitBuffer.append((cINSTRUCTION_WRITE << 4) + ((addressW >> 8) & 0xF))
    spiTransmitBuffer.append(addressW & 0xFF)
    spiTransmitBuffer = spiTransmitBuffer + data

    spi._assert_cs()
    spi.write(spiTransmitBuffer)
    spi._deassert_cs()

    spiTransmitBuffer = []
    spiTransmitBuffer.append((cINSTRUCTION_READ << 4) + ((address >> 8) & 0xF))
    spiTransmitBuffer.append(address & 0xFF)

    spi._assert_cs()
    spi.write(spiTransmitBuffer)
    response_1 = spi.read(4)
    spi._deassert_cs()
    print ('CiCON register modified:')
    print (binascii.hexlify(response_1))
    print(list(response_1))

    # Reset
    spiTransmitBuffer = []
    spiTransmitBuffer.append(cINSTRUCTION_RESET << 4)
    spiTransmitBuffer.append(0)
    spi._assert_cs()
    spi.write(spiTransmitBuffer)
    spi._deassert_cs()

    spiTransmitBuffer = []
    spiTransmitBuffer.append((cINSTRUCTION_READ << 4) + ((address >> 8) & 0xF))
    spiTransmitBuffer.append(address & 0xFF)

    spi._assert_cs()
    spi.write(spiTransmitBuffer)
    response_1 = spi.read(4)
    spi._deassert_cs()
    print ('CiCON default:')
    print (binascii.hexlify(response_1))
    print(list(response_1))

if test == 2:
    #canfd.reset()
    canfd.initialize()
    address = 0x000
    word = canfd.readWord(address)
    byte = canfd.readByte(address)
    byteArr = canfd.readByteArray(address, 4)
    wordArr = canfd.readWordArray(address,2)
    print ('Reading CiCON as 32-bit word with CAN FD lib, using readWord:')
    print(word)
    print(hex(word))

    print ('Reading 1st byte of CiCON with CAN FD lib, using readByte:')
    print(byte)
    print(hex(byte))

    print ('Reading CiCON as array of bytes with CAN FD lib, using readByteArray:')
    print(list(byteArr))

    print ('Reading CiCON and CiNBTCFG as array of two 32-bit words with CAN FD lib, using readWordArray:')
    print(list(wordArr))

if test == 3:
    address = 0x000
    word = canfd.readWord(address)
    print ('Reading CiCON:')
    print(word)

    write_word = 0x600798F4
    print("Word to write: ")
    print(write_word)
    canfd.writeWord(address, write_word)
    word = canfd.readWord(address)
    print ('Reading CiCON with 0x600798F4 written on it:')
    print(word)

    canfd.reset()
    print("Resetting...")

    write_byte = 0x6F
    canfd.writeByte(address, write_byte)
    word = canfd.readWord(address)
    print ('Reading CiCON with 0x00 written on its 1st byte:')
    print(word)

    canfd.reset()
    print("Resetting...")
    write_byte_array = [0x60, 0x07, 0x98, 0xF4]
    canfd.writeByteArray(address, write_byte_array)
    word = canfd.readWord(address)
    print ('Reading CiCON with [0x60, 0x07, 0x98, 0xF4] array written on it (4 bytes):')
    print(word)

    canfd.reset()
    print("Resetting...")

    write_word_array = [0x600798F4, 0x7f0f3eff]
    canfd.writeWordArray(address, write_word_array)
    word = canfd.readWordArray(address, 2)
    print ('Reading CiCON and CiNBTCFG with [0x600798F4, 0x7f0f3eff] written on it:')
    print(word)
   # print(binascii.hexlify(bytearray([word])))

if test == 4:
    #canfd = canfdlib.CANFD_SPI(ft232h, cs, max_speed_hz, mode, bitorder, SPI_DEFAULT_BUFFER_LENGTH, SPI_MAX_BUFFER_LENGTH, SPI_BAUDRATE)
    result = canfd.ramTest()
    if result == -1:
        print("RAM test failed!")
    else:
        print ('RAM test succesful!')

if test == 5:
    #canfd = canfdlib.CANFD_SPI(ft232h, cs, max_speed_hz, mode, bitorder, SPI_DEFAULT_BUFFER_LENGTH,SPI_MAX_BUFFER_LENGTH, SPI_BAUDRATE)
    result = canfd.registerTest()
    if result == -1:
        print("Register test failed!")
    else:
        print ('Register test succesful!:')

if test == 6:
    mode = canfd.operationModeGet()
    print("After reset mode: {}".format(mode))
    print("selecting NORMAL_MODE mode")
    canfd.operationModeSelect(NORMAL_MODE)
    mode = canfd.operationModeGet()
    print("Device mode: {}".format(mode))
    print("selecting INTERNAL_LOOPBACK_MODE mode")
    canfd.operationModeSelect(INTERNAL_LOOPBACK_MODE)
    mode = canfd.operationModeGet()
    print("Device mode: {}".format(mode))
    print("selecting CONFIGURATION_MODE mode")
    canfd.operationModeSelect(CONFIGURATION_MODE)
    mode = canfd.operationModeGet()
    print("Device mode: {}".format(mode))
    print("selecting mode after init")
    canfd.initialize()
    mode = canfd.operationModeGet()
    print("Device mode: {}".format(mode))

if test == 7:
    canfd.reset()
    canfd.initialize()
    canfd.operationModeSelect(EXTERNAL_LOOPBACK_MODE)
    #print("masks: {}".format(canfd.readWord()))
    # transmit message of len = DLC (64 bytes)
    canfd.txdlc = 8
    #txd = range(0, canfd.dlcToDataBytes(canfd.txdlc))
    txd = [0, 0xA, 0xF1, 1, 13, 7, 253, 27]
    n = 8
    print("(TEST) message to transmit: {}".format(txd))
    canfd.transmitMessageTasks(txd)

    loop = raw_input("Loop? ")
    if loop == 'yes':
        while True:

            # receive message
            rxd = canfd.receiveMessageTasks()
            print ("(TEST) received message: {}".format(rxd))
            #print ("(TEST) received message: {}".format(rxd))
            if rxd is not None:
                print ("(TEST) received message: {}".format([hex(a) for a in rxd]))
                break
    else:
        #txd = range(0, canfd.dlcToDataBytes(canfd.txdlc))
        print("(TEST) message to transmit: {}".format([hex(a) for a in txd]))
        canfd.transmitMessageTasks(txd)
        rxd = canfd.receiveMessageTasks()
        print ("(TEST) received message: {}".format(rxd))

if test == 8:
    canfd.initialize()
    canfd.operationModeSelect(EXTERNAL_LOOPBACK_MODE)

    # transmit message of len = DLC (64 bytes)
    txd = range(0, canfd.dlcToDataBytes(canfd.txdlc))

    print("transmitted message: {}".format(txd))
    canfd.transmitMessageTasks(txd)
    rxd = canfd.receiveMessageTasks()
    print("received message: {}".format(rxd))

if test == 9:
    canfd.initialize()
    canfd.operationModeSelect(EXTERNAL_LOOPBACK_MODE)
    # transmit message of len = DLC (64 bytes)
    canfd.txdlc = 8
    txd = [0, 0xA, 0xF1, 1, 13, 7, 253, 27]
    print("(TEST) message to transmit: {}".format(txd))
    canfd.transmitMessageTasks(txd)
    rxd = canfd.receiveMessageTasks()
    print ("(TEST) received message: {}".format(rxd))
