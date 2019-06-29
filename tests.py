import binascii
import ft
from constants import *

ft232h = None
spi = None

def init():
    ft.use_FT232H()
    global ft232h
    global spi
    ft232h = ft.FT232H()
    spi = ft.SPI(ft232h, cs=3, max_speed_hz=20000000, mode=0, bitorder=ft.MSBFIRST)

def spi_reset():
    spiTransmitBuffer = []
    spiTransmitBuffer.append(cINSTRUCTION_RESET << 4)
    spiTransmitBuffer.append(0)
    spi._assert_cs()
    spi.write(spiTransmitBuffer)
    spi._deassert_cs()

def test1():
    init()
    spi_reset()
    spiTransmitBuffer = []
    address = 0xE00
    spiTransmitBuffer.append((cINSTRUCTION_READ << 4) + ((address >> 8) & 0xF))
    spiTransmitBuffer.append(address & 0xFF)
    spi._assert_cs()
    spi.write(spiTransmitBuffer)
    response = spi.read(4)
    spi._deassert_cs()

    result = 'Reading OSC register with SPI. Result:\n32-bit word: {word}\nBytes: {bytes}'.format(bytes=list(response), word=binascii.hexlify(response))
    return result

def test2():
    init()
    spi_reset()
    spiTransmitBuffer = []
    address = 0x000
    spiTransmitBuffer.append((cINSTRUCTION_READ << 4) + ((address >> 8) & 0xF))
    spiTransmitBuffer.append(address & 0xFF)
    spi._assert_cs()
    spi.write(spiTransmitBuffer)
    response_0 = spi.read(4)
    spi._deassert_cs()

    result = 'CiCON register before writing:\n32-bit word: {word}\nBytes: {bytes}\n'.format(bytes=list(response_0),word=binascii.hexlify(response_0))

    spiTransmitBuffer = []
    data = [0, 0, 0, 0]
    result = result + "Data to write (4 bytes): {}\n".format(data)

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

    result = result + 'CiCON register modified:\n32-bit word: {word}\nBytes: {bytes}\n'.format(bytes=list(response_1),word=binascii.hexlify(response_1))
    return result

def test3(canfd):
    canfd.reset()
    address = 0x000
    word = canfd.readWord(address)
    result = 'Reading CiCON: {}\n:'.format(word)

    write_word = 0x600798F4
    result = result + "Word to write: {}\n".format(write_word)
    canfd.writeWord(address, write_word)
    word = canfd.readWord(address)
    result = result + 'Reading CiCON with {write_word} written on it: {word}\n'.format(write_word=write_word, word=word)

    canfd.reset()
    result = result + "Resetting...\n"

    write_byte = 0x6F
    canfd.writeByte(address, write_byte)
    word = canfd.readWord(address)
    result = result + 'Reading CiCON with {write_byte} written on its 1st byte: {word}'.format(write_byte=write_byte, word=word)

    canfd.reset()
    result = result + "Resetting...\n"

    write_byte_array = [0x60, 0x07, 0x98, 0xF4]
    canfd.writeByteArray(address, write_byte_array)
    word = canfd.readWord(address)
    result = result + 'Reading CiCON with {write_byte_array} array written on it (4 bytes): {word}\n'.format(write_byte_array=write_byte_array, word=word)

    canfd.reset()
    result = result + "Resetting...\n"

    write_word_array = [0x600798F4, 0x7f0f3eff]
    canfd.writeWordArray(address, write_word_array)
    word = canfd.readWordArray(address, 2)
    result = result + 'Reading CiCON and CiNBTCFG with {write_word_array} written on it: {word}\n'.format(write_word_array=write_word_array, word=word)

    return result

def test4(canfd):
    canfd.reset()
    result = canfd.ramTest()
    if result == -1:
        result = "RAM test failed!\n"
    else:
        result = 'RAM test succesful!\n'
    return result

def test5(canfd):
    canfd.reset()
    result = canfd.registerTest()
    if result == -1:
        result = "Register test failed!\n"
    else:
        result = 'Register test succesful!\n'
    return result

def test6(canfd):
    canfd.reset()
    mode = canfd.operationModeGet()
    result = "Mode after reset: {}\n".format(mode)
    result = result + 'selecting NORMAL_MODE\n'

    canfd.operationModeSelect(NORMAL_MODE)
    mode = canfd.operationModeGet()
    result = result + "Device mode: {}\n".format(mode) + 'Selecting INTERNAL_LOOPBACK_MODE\n'

    canfd.operationModeSelect(INTERNAL_LOOPBACK_MODE)
    mode = canfd.operationModeGet()
    result = result + "Device mode: {}\n".format(mode) + 'Selecting CONFIGURATION_MODE\n'

    canfd.operationModeSelect(CONFIGURATION_MODE)
    mode = canfd.operationModeGet()
    result = result +  "Device mode: {}\n".format(mode) + 'Initialazing...\n'

    canfd.initialize()
    mode = canfd.operationModeGet()
    result = result + "Device mode after init: {}\n".format(mode)
    return result

def test7(canfd):
    canfd.initialize()
    canfd.operationModeSelect(EXTERNAL_LOOPBACK_MODE)
    canfd.txdlc = 8
    txd = [0, 0xA, 0xF1, 1, 13, 7, 253, 27]
    result = 'Message to transmit: {}\n'.format(txd)
    canfd.transmitMessageTasks(txd)
    # receive message
    rxd = canfd.receiveMessageTasks()
    result = result +"Received message: {}\n".format(rxd)
    return result


test_dict = {
    'test1': test1,
    'test2': test2,
    'test3': test3,
    'test4': test4,
    'test5': test5,
    'test6': test6,
    'test7': test7
}

#test_dict['1']()