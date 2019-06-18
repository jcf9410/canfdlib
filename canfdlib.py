import ft
from random import randint
from constants import *
from classes import *
import binascii

def set_bit(v, index, x):
    """Set the index:th bit of v to 1 if x is truthy, else to 0, and return the new value."""
    mask = 1 << index  # Compute mask, an integer with just bit 'index' set.
    v &= ~mask  # Clear the bit indicated by the mask (if x is False)
    if x:
        v |= mask  # If x was True, set the bit indicated by the mask.
    return v  # Return the result, we're done.

##################################
#### Class definition ####
##################################

class CANFD_SPI(ft.SPI):

    def __init__(self, ft232h, cs, max_speed_hz, mode, bitorder, SPI_DEFAULT_BUFFER_LENGTH, SPI_MAX_BUFFER_LENGTH,
                 SPI_BAUDRATE):
        super(CANFD_SPI, self).__init__(ft232h, cs, max_speed_hz, mode, bitorder)

        self.SPI_DEFAULT_BUFFER_LENGTH = SPI_DEFAULT_BUFFER_LENGTH
        self.SPI_MAX_BUFFER_LENGTH = SPI_MAX_BUFFER_LENGTH
        self.SPI_BAUDRATE = SPI_BAUDRATE

        self.can_config = REG_CAN_CONFIG()
        self.opMode = NORMAL_MODE
        self.state = "idle"  # APP_STATE_INIT
        self.clk = CAN_SYSCLK_40M
        self.txFromFlash = True
        self.switchChanged = True
        self.ramInitialized = False
        self.selectedBitTime = CAN_500K_2M #CAN_500K_2M

        self.rxFlags = CAN_RX_FIFO_NO_EVENT
        self.txFlags = CAN_RX_FIFO_NO_EVENT
        self.errorFlags = CAN_ERROR_FREE_STATE

        self.txConfig = CAN_TX_FIFO_CONFIG()
        self.rxConfig = CAN_RX_FIFO_CONFIG()

        self.txObj = CAN_TX_MSGOBJ()
        self.rxObj = CAN_RX_MSGOBJ()

        self.txCounter = 0

        self.transmitBuffer = []
        self.receiveBuffer = []

        self.txchannel = CAN_FIFO_CH2
        self.rxchannel = CAN_FIFO_CH1

        self.txdlc = CAN_DLC_64

    def initialize(self):
        # Initialize
        self.reset()
        self.eccEnable()
        if not self.ramInitialized:
            self.ramInit(0xFF)
            self.ramInitialized = True

        # configure device
        self.configureObjectReset()
        self.can_config.IsoCrcEnable = 1
        self.can_config.StoreInTEF = 0  # 0?
        self.can_config.TXQEnable = 0  # should be 0?
        self.configure()

        # setup TX FIFO
        self.transmitChannelConfigureObjectReset()
        self.txConfig.FifoSize = 4  # 7
        self.txConfig.PayLoadSize = CAN_PLSIZE_64
        self.txConfig.TxPriority = 0
        self.transmitChannelConfigure()
        self.txCounter = 0

        # setup RX FIFO
        self.receiveChannelConfigureObjectReset()
        self.rxConfig.FifoSize = 15
        self.rxConfig.PayLoadSize = CAN_PLSIZE_64
        self.rxConfig.RxTimeStampEnable = 0
        self.receiveChannelConfigure()

        # Setup bit time
        self.bitTimeConfigure(self.clk, self.selectedBitTime)
        self.operationModeSelect(NORMAL_MODE)
        #self.state = APP_STATE_TEST_RAM_ACCESS

    # SPI Access Function
    def reset(self):
        spiTransmitBuffer = []
        spiTransmitBuffer.append(cINSTRUCTION_RESET << 4)
        spiTransmitBuffer.append(0)
        self._assert_cs()
        self.write(spiTransmitBuffer)
        self._deassert_cs()

    def readByte(self, address):
        spiTransmitBuffer = []
        spiTransmitBuffer.append((cINSTRUCTION_READ << 4) + ((address >> 8) & 0xF))
        spiTransmitBuffer.append(address & 0xFF)
        self._assert_cs()
        self.write(spiTransmitBuffer)
        result = self.read(1)
        self._deassert_cs()
        return int(binascii.hexlify(result), 16)

    def readWord(self, address):
        spiTransmitBuffer = []
        spiTransmitBuffer.append((cINSTRUCTION_READ << 4) + ((address >> 8) & 0xF))
        spiTransmitBuffer.append(address & 0xFF)
        self._assert_cs()
        self.write(spiTransmitBuffer)
        rx = self.read(4)
        self._deassert_cs()
        word = 0
        return int(binascii.hexlify(rx), 16)

    def readByteArray(self, address, length):
        spiTransmitBuffer = []
        spiTransmitBuffer.append((cINSTRUCTION_READ << 4) + ((address >> 8) & 0xF))
        spiTransmitBuffer.append(address & 0xFF)
        self._assert_cs()
        self.write(spiTransmitBuffer)
        response = self.read(length)
        self._deassert_cs()
        result = [byte for byte in response]
        return result

    def readWordArray(self, address, length):
        spiTransmitBuffer = []
        spiTransmitBuffer.append((cINSTRUCTION_READ << 4) + ((address >> 8) & 0xF))
        spiTransmitBuffer.append(address & 0xFF)
        self._assert_cs()
        self.write(spiTransmitBuffer)
        rx = binascii.hexlify(self.read(4 * length))
        self._deassert_cs()
        w = [int(rx[i:i + 8], 16) for i in xrange(0, len(rx), 8)]
        return w

    def writeByte(self, address, data):
        spiTransmitBuffer = []
        spiTransmitBuffer.append((cINSTRUCTION_WRITE << 4) + ((address >> 8) & 0xF))
        spiTransmitBuffer.append(address & 0xFF)
        spiTransmitBuffer.append(data)
        self._assert_cs()
        self.write(spiTransmitBuffer)
        self._deassert_cs()

    def writeWord(self, address, data):
        spiTransmitBuffer = []
        spiTransmitBuffer.append((cINSTRUCTION_WRITE << 4) + ((address >> 8) & 0xF))
        spiTransmitBuffer.append(address & 0xFF)

        # divide data in byte chunks
        data = [int(hex(int(data) >> i & 0xff).replace('L', ''), 16) for i in (24, 16, 8, 0)]
        spiTransmitBuffer = spiTransmitBuffer + data
        self._assert_cs()
        self.write(spiTransmitBuffer)
        self._deassert_cs()

    def writeByteArray(self, address, data):
        spiTransmitBuffer = []
        spiTransmitBuffer.append((cINSTRUCTION_WRITE << 4) + ((address >> 8) & 0xF))
        spiTransmitBuffer.append(address & 0xFF)
        spiTransmitBuffer = spiTransmitBuffer + data
        self._assert_cs()
        self.write(spiTransmitBuffer)
        self._deassert_cs()

    def writeByteArrayCRC(self, address, data, fromram=False):
        spiTransmitBuffer = []
        spiTransmitBuffer.append((cINSTRUCTION_WRITE_CRC << 4) + ((address >> 8) & 0xF))
        spiTransmitBuffer.append(address & 0xFF)
        if fromram:
            spiTransmitBuffer.append(len(data) >> 2)
        else:
            spiTransmitBuffer.append(len(data))
        spiTransmitBuffer = spiTransmitBuffer + data
        crcResult = self.calculateCRC16(spiTransmitBuffer)
        spiTransmitBuffer.append((crcResult >> 8) & 0xFF)
        spiTransmitBuffer.append(crcResult & 0xFF)
        self._assert_cs()
        self.write(spiTransmitBuffer)
        self._deassert_cs()

    def writeWordArray(self, address, data):
        spiTransmitBuffer = []
        spiTransmitBuffer.append((cINSTRUCTION_WRITE << 4) + ((address >> 8) & 0xF))
        spiTransmitBuffer.append(address & 0xFF)
        for word in data:
            # divide data in byte chunks
            data = [int(hex(word >> i & 0xff).replace('L', ''), 16) for i in (24, 16, 8, 0)]
            spiTransmitBuffer = spiTransmitBuffer + data
        self._assert_cs()
        self.write(spiTransmitBuffer)
        self._deassert_cs()

    # Configuration
    def configure(self):
        ciCon_word = 0x60079804
        for i in range(24, 29):
            ciCon_word = set_bit(ciCon_word, i, (self.can_config.DNetFilterCount >> i & 1))
        ciCon_word = set_bit(ciCon_word, 29, self.can_config.IsoCrcEnable)
        ciCon_word = set_bit(ciCon_word, 30, self.can_config.ProtocolExceptionEventDisable)
        ciCon_word = set_bit(ciCon_word, 16, self.can_config.WakeUpFilterEnable)
        for j, i in enumerate(range(17, 19)):
            ciCon_word = set_bit(ciCon_word, i, (self.can_config.WakeUpFilterTime >> j) & 1)
        ciCon_word = set_bit(ciCon_word, 21, self.can_config.BitRateSwitchDisable)
        ciCon_word = set_bit(ciCon_word, 8, self.can_config.RestrictReTxAttempts)
        ciCon_word = set_bit(ciCon_word, 9, self.can_config.EsiInGatewayMode)
        ciCon_word = set_bit(ciCon_word, 10, self.can_config.SystemErrorToListenOnly)
        ciCon_word = set_bit(ciCon_word, 11, self.can_config.StoreInTEF)
        ciCon_word = set_bit(ciCon_word, 12, self.can_config.TXQEnable)
        for j, i in enumerate(range(4, 8)):
            ciCon_word = set_bit(ciCon_word, i, (self.can_config.TxBandWidthSharing >> j) & 1)

        self.writeWord(cREGADDR_CiCON, ciCon_word)

    def configureObjectReset(self):
        self.can_config.DNetFilterCount = 0
        self.can_config.IsoCrcEnable = 1
        self.can_config.ProtocolExpectionEventDisable = 1
        self.can_config.WakeUpFilterEnable = 1
        self.can_config.WakeUpFilterTime = 0b11
        self.can_config.BitRateSwitchDisable = 0
        self.can_config.RestrictReTxAttempts = 0
        self.can_config.EsiInGatewayMode = 0
        self.can_config.SystemErrorToListenOnly = 0
        self.can_config.StoreInTEF = 1
        self.can_config.TXQEnable = 1
        self.can_config.TxBandWidthSharing = 0

    # Operating mode
    def operationModeSelect(self, opMode):
        for mode in (CONFIGURATION_MODE, opMode):
            byte = self.readByte(cREGADDR_CiCON + 3)
            byte = (0xF8 & byte) + mode
            self.writeByte(cREGADDR_CiCON + 3, byte)
            self.opMode = mode

    def operationModeGet(self):
        d = self.readByte(cREGADDR_CiCON + 2)
        d = (d >> 5) & 0x7
        if d == NORMAL_MODE:
            return NORMAL_MODE
        elif d == SLEEP_MODE:
            return SLEEP_MODE
        elif d == INTERNAL_LOOPBACK_MODE:
            return INTERNAL_LOOPBACK_MODE
        elif d == EXTERNAL_LOOPBACK_MODE:
            return EXTERNAL_LOOPBACK_MODE
        elif d == LISTEN_ONLY_MODE:
            return LISTEN_ONLY_MODE
        elif d == CONFIGURATION_MODE:
            return CONFIGURATION_MODE
        elif d == CLASSIC_MODE:
            return CLASSIC_MODE
        elif d == RESTRICTED_MODE:
            return RESTRICTED_MODE
        else:
            return INVALID_MODE

    # CAN transmit
    def transmitChannelConfigure(self):
        cififocon_word = 0x00046000
        address = cREGADDR_CiFIFOCON + (self.txchannel * CiFIFO_OFFSET)
        cififocon_word = set_bit(cififocon_word, 30, self.txConfig.RTREnable)
        cififocon_word = set_bit(cififocon_word, 31, 1) # txEnable
        for j, i in enumerate(range(8, 13)):
            cififocon_word = set_bit(cififocon_word, i, (self.txConfig.TxPriority >> j) & 1)
        for j, i in enumerate(range(13, 15)):
            cififocon_word = set_bit(cififocon_word, i, (self.txConfig.TxAttempts >> j) & 1)
        for j, i in enumerate(range(0, 5)):
            cififocon_word = set_bit(cififocon_word, i, (self.txConfig.FifoSize >> j) & 1)
        for j, i in enumerate(range(5, 8)):
            cififocon_word = set_bit(cififocon_word, i, (self.txConfig.PayLoadSize >> j) & 1)
        address = cREGADDR_CiFIFOCON + (self.txchannel * CiFIFO_OFFSET)
        self.writeWord(address, cififocon_word)

    def transmitChannelConfigureObjectReset(self):
        self.txConfig.RTREnable = 0
        self.txConfig.TxPriority = 0
        self.txConfig.TxAttempts = 0b11
        self.txConfig.FifoSize = 0
        self.txConfig.PayLoadSize = 0

    def receiveChannelConfigure(self):
        if self.rxchannel == CAN_FIFO_CH0:
            return -100
        cififocon_word = 0x00046000
        address = cREGADDR_CiFIFOCON + (self.rxchannel * CiFIFO_OFFSET)
        cififocon_word = set_bit(cififocon_word, 29, self.rxConfig.RxTimeStampEnable)
        cififocon_word = set_bit(cififocon_word, 31, 0)  # txEnable
        for j, i in enumerate(range(0, 5)):
            cififocon_word = set_bit(cififocon_word, i, (self.rxConfig.FifoSize >> j) & 1)
        for j, i in enumerate(range(5, 8)):
            cififocon_word = set_bit(cififocon_word, i, (self.rxConfig.PayLoadSize >> j) & 1)
        address = cREGADDR_CiFIFOCON + (self.rxchannel * CiFIFO_OFFSET)
        self.writeWord(address, cififocon_word)

    def receiveChannelConfigureObjectReset(self):
        self.rxConfig.FifoSize = 0
        self.rxConfig.PayLoadSize = 0
        self.rxConfig.RxTimeStampEnable = 0

    def bitTimeConfigure(self, clk, selectedBitTime):
        if clk == CAN_SYSCLK_40M:
            self.bitTimeConfigureNominal40MHz(selectedBitTime)
            self.bitTimeConfigureData40MHz(selectedBitTime)
        elif clk == CAN_SYSCLK_20M:
            self.bitTimeConfigureNominal20MHz(selectedBitTime)
            self.bitTimeConfigureData20MHz(selectedBitTime)
        else:
            print('CLK should be 40 MHz or 20 MHz')

    # bitTime is 500K_2M

    def bitTimeConfigureNominal40MHz(self, selectedBitTime):
        ciNbtcfg_word = 0x0F0F3E00
        if selectedBitTime in all500k:
            for j, i in enumerate(range(24, 31)): # SJW
                ciNbtcfg_word = set_bit(ciNbtcfg_word, i, (15 << j) & 1)
            for j, i in enumerate(range(16, 22)): # TSEG2
                ciNbtcfg_word = set_bit(ciNbtcfg_word, i, (15 << j) & 1)
            for j, i in enumerate(range(8, 16)): #TSEG1
                ciNbtcfg_word = set_bit(ciNbtcfg_word, i, (62 << j) & 1)
            for j, i in enumerate(range(0, 8)): #BRP
                ciNbtcfg_word = set_bit(ciNbtcfg_word, i, 0)
        elif selectedBitTime in all250k:
            for j, i in enumerate(range(24, 31)): # SJW
                ciNbtcfg_word = set_bit(ciNbtcfg_word, i, (31 << j) & 1)
            for j, i in enumerate(range(16, 22)): # TSEG2
                ciNbtcfg_word = set_bit(ciNbtcfg_word, i, (31 << j) & 1)
            for j, i in enumerate(range(8, 16)): #TSEG1
                ciNbtcfg_word = set_bit(ciNbtcfg_word, i, (126 << j) & 1)
            for j, i in enumerate(range(0, 8)): #BRP
                ciNbtcfg_word = set_bit(ciNbtcfg_word, i, 0)
        elif selectedBitTime in all1000k:
            for j, i in enumerate(range(24, 31)): # SJW
                ciNbtcfg_word = set_bit(ciNbtcfg_word, i, (7 << j) & 1)
            for j, i in enumerate(range(16, 22)): # TSEG2
                ciNbtcfg_word = set_bit(ciNbtcfg_word, i, (7 << j) & 1)
            for j, i in enumerate(range(8, 16)): #TSEG1
                ciNbtcfg_word = set_bit(ciNbtcfg_word, i, (30 << j) & 1)
            for j, i in enumerate(range(0, 8)): #BRP
                ciNbtcfg_word = set_bit(ciNbtcfg_word, i, 0)
        elif selectedBitTime == CAN_125K_500K:
            for j, i in enumerate(range(24, 31)): # SJW
                ciNbtcfg_word = set_bit(ciNbtcfg_word, i, (63 << j) & 1)
            for j, i in enumerate(range(16, 22)): # TSEG2
                ciNbtcfg_word = set_bit(ciNbtcfg_word, i, (63 << j) & 1)
            for j, i in enumerate(range(8, 16)): #TSEG1
                ciNbtcfg_word = set_bit(ciNbtcfg_word, i, (254 << j) & 1)
            for j, i in enumerate(range(0, 8)): #BRP
                ciNbtcfg_word = set_bit(ciNbtcfg_word, i, 0)
        else:
            return -1
        self.writeWord(cREGADDR_CiNBTCFG, ciNbtcfg_word)

    def bitTimeConfigureNominal20MHz(self, selectedBitTime):
        ciNbtcfg_word = 0x0F0F3E00
        if selectedBitTime in all500k:
            for j, i in enumerate(range(24, 31)): # SJW
                ciNbtcfg_word = set_bit(ciNbtcfg_word, i, (7 << j) & 1)
            for j, i in enumerate(range(16, 22)): # TSEG2
                ciNbtcfg_word = set_bit(ciNbtcfg_word, i, (7 << j) & 1)
            for j, i in enumerate(range(8, 16)): #TSEG1
                ciNbtcfg_word = set_bit(ciNbtcfg_word, i, (30 << j) & 1)
            for j, i in enumerate(range(0, 8)): #BRP
                ciNbtcfg_word = set_bit(ciNbtcfg_word, i, 0)
        elif selectedBitTime in all250k:
            for j, i in enumerate(range(24, 31)): # SJW
                ciNbtcfg_word = set_bit(ciNbtcfg_word, i, (15 << j) & 1)
            for j, i in enumerate(range(16, 22)): # TSEG2
                ciNbtcfg_word = set_bit(ciNbtcfg_word, i, (15 << j) & 1)
            for j, i in enumerate(range(8, 16)): #TSEG1
                ciNbtcfg_word = set_bit(ciNbtcfg_word, i, (162 << j) & 1)
            for j, i in enumerate(range(0, 8)): #BRP
                ciNbtcfg_word = set_bit(ciNbtcfg_word, i, 0)
        elif selectedBitTime in all1000k:
            for j, i in enumerate(range(24, 31)): # SJW
                ciNbtcfg_word = set_bit(ciNbtcfg_word, i, (3 << j) & 1)
            for j, i in enumerate(range(16, 22)): # TSEG2
                ciNbtcfg_word = set_bit(ciNbtcfg_word, i, (3 << j) & 1)
            for j, i in enumerate(range(8, 16)): #TSEG1
                ciNbtcfg_word = set_bit(ciNbtcfg_word, i, (14 << j) & 1)
            for j, i in enumerate(range(0, 8)): #BRP
                ciNbtcfg_word = set_bit(ciNbtcfg_word, i, 0)
        elif selectedBitTime == CAN_125K_500K:
            for j, i in enumerate(range(24, 31)): # SJW
                ciNbtcfg_word = set_bit(ciNbtcfg_word, i, (31 << j) & 1)
            for j, i in enumerate(range(16, 22)): # TSEG2
                ciNbtcfg_word = set_bit(ciNbtcfg_word, i, (31 << j) & 1)
            for j, i in enumerate(range(8, 16)): #TSEG1
                ciNbtcfg_word = set_bit(ciNbtcfg_word, i, (126 << j) & 1)
            for j, i in enumerate(range(0, 8)): #BRP
                ciNbtcfg_word = set_bit(ciNbtcfg_word, i, 0)
        else:
            return -1
        self.writeWord(cREGADDR_CiNBTCFG, ciNbtcfg_word)

    def bitTimeConfigureData40MHz(self, selectedBitTime):
        ciDbtcfg_word = 0x03030E00
        ciTdc_word = 0x00100200
        ciTdc_word = set_bit(ciTdc_word, 15, 0)
        ciTdc_word = set_bit(ciTdc_word, 16, 1)
        tdcValue = 0
        if selectedBitTime == CAN_500K_1M:
            # Data BR
            for j, i in enumerate(range(24, 28)):  # SJW
                ciDbtcfg_word = set_bit(ciDbtcfg_word, i, (7 << j) & 1)
            for j, i in enumerate(range(16, 20)):  # TSEG2
                ciDbtcfg_word = set_bit(ciDbtcfg_word, i, (7 << j) & 1)
            for j, i in enumerate(range(8, 13)):  # TSEG1
                ciDbtcfg_word = set_bit(ciDbtcfg_word, i, (30 << j) & 1)
            for j, i in enumerate(range(0, 8)): #BRP
                ciDbtcfg_word = set_bit(ciDbtcfg_word, i, 0)
            # SSP
            for j, i in enumerate(range(24, 30)):  # TDCV
                ciTdc_word = set_bit(ciTdc_word, i, (tdcValue << j) & 1)
            for j, i in enumerate(range(16, 9)):  # TDCO
                ciTdc_word = set_bit(ciTdc_word, i, (31 << j) & 1)
        elif selectedBitTime == CAN_500K_2M:
            # Data BR
            for j, i in enumerate(range(24, 28)):  # SJW
                ciDbtcfg_word = set_bit(ciDbtcfg_word, i, (3 << j) & 1)
            for j, i in enumerate(range(16, 20)):  # TSEG2
                ciDbtcfg_word = set_bit(ciDbtcfg_word, i, (3 << j) & 1)
            for j, i in enumerate(range(8, 13)):  # TSEG1
                ciDbtcfg_word = set_bit(ciDbtcfg_word, i, (14 << j) & 1)
            for j, i in enumerate(range(0, 8)): #BRP
                ciDbtcfg_word = set_bit(ciDbtcfg_word, i, 0)
            # SSP
            for j, i in enumerate(range(24, 30)):  # TDCV
                ciTdc_word = set_bit(ciTdc_word, i, (tdcValue << j) & 1)
            for j, i in enumerate(range(16, 9)):  # TDCO
                ciTdc_word = set_bit(ciTdc_word, i, (15 << j) & 1)
        elif selectedBitTime == CAN_500K_3M:
            # Data BR
            for j, i in enumerate(range(24, 28)):  # SJW
                ciDbtcfg_word = set_bit(ciDbtcfg_word, i, (2 << j) & 1)
            for j, i in enumerate(range(16, 20)):  # TSEG2
                ciDbtcfg_word = set_bit(ciDbtcfg_word, i, (2 << j) & 1)
            for j, i in enumerate(range(8, 13)):  # TSEG1
                ciDbtcfg_word = set_bit(ciDbtcfg_word, i, (8 << j) & 1)
            for j, i in enumerate(range(0, 8)): #BRP
                ciDbtcfg_word = set_bit(ciDbtcfg_word, i, 0)
            # SSP
            for j, i in enumerate(range(24, 30)):  # TDCV
                ciTdc_word = set_bit(ciTdc_word, i, (tdcValue << j) & 1)
            for j, i in enumerate(range(16, 9)):  # TDCO
                ciTdc_word = set_bit(ciTdc_word, i, (9 << j) & 1)
        elif selectedBitTime in (CAN_500K_4M, CAN_1000K_4M):
            # Data BR
            for j, i in enumerate(range(24, 28)):  # SJW
                ciDbtcfg_word = set_bit(ciDbtcfg_word, i, (1 << j) & 1)
            for j, i in enumerate(range(16, 20)):  # TSEG2
                ciDbtcfg_word = set_bit(ciDbtcfg_word, i, (1 << j) & 1)
            for j, i in enumerate(range(8, 13)):  # TSEG1
                ciDbtcfg_word = set_bit(ciDbtcfg_word, i, (6 << j) & 1)
            for j, i in enumerate(range(0, 8)): #BRP
                ciDbtcfg_word = set_bit(ciDbtcfg_word, i, 0)
            # SSP
            for j, i in enumerate(range(24, 30)):  # TDCV
                ciTdc_word = set_bit(ciTdc_word, i, (tdcValue << j) & 1)
            for j, i in enumerate(range(16, 9)):  # TDCO
                ciTdc_word = set_bit(ciTdc_word, i, (7 << j) & 1)
        elif selectedBitTime == CAN_500K_5M:
            # Data BR
            for j, i in enumerate(range(24, 28)):  # SJW
                ciDbtcfg_word = set_bit(ciDbtcfg_word, i, (1 << j) & 1)
            for j, i in enumerate(range(16, 20)):  # TSEG2
                ciDbtcfg_word = set_bit(ciDbtcfg_word, i, (1 << j) & 1)
            for j, i in enumerate(range(8, 13)):  # TSEG1
                ciDbtcfg_word = set_bit(ciDbtcfg_word, i, (4 << j) & 1)
            for j, i in enumerate(range(0, 8)): #BRP
                ciDbtcfg_word = set_bit(ciDbtcfg_word, i, 0)
            # SSP
            for j, i in enumerate(range(24, 30)):  # TDCV
                ciTdc_word = set_bit(ciTdc_word, i, (tdcValue << j) & 1)
            for j, i in enumerate(range(16, 9)):  # TDCO
                ciTdc_word = set_bit(ciTdc_word, i, (5 << j) & 1)
        elif selectedBitTime == CAN_500K_6M7:
            # Data BR
            for j, i in enumerate(range(24, 28)):  # SJW
                ciDbtcfg_word = set_bit(ciDbtcfg_word, i, (0 << j) & 1)
            for j, i in enumerate(range(16, 20)):  # TSEG2
                ciDbtcfg_word = set_bit(ciDbtcfg_word, i, (0 << j) & 1)
            for j, i in enumerate(range(8, 13)):  # TSEG1
                ciDbtcfg_word = set_bit(ciDbtcfg_word, i, (3 << j) & 1)
            for j, i in enumerate(range(0, 8)): #BRP
                ciDbtcfg_word = set_bit(ciDbtcfg_word, i, 0)
            # SSP
            for j, i in enumerate(range(24, 30)):  # TDCV
                ciTdc_word = set_bit(ciTdc_word, i, (tdcValue << j) & 1)
            for j, i in enumerate(range(16, 9)):  # TDCO
                ciTdc_word = set_bit(ciTdc_word, i, (4 << j) & 1)
        elif selectedBitTime in (CAN_500K_8M, CAN_1000K_8M):
            # Data BR
            for j, i in enumerate(range(24, 28)):  # SJW
                ciDbtcfg_word = set_bit(ciDbtcfg_word, i, (0 << j) & 1)
            for j, i in enumerate(range(16, 20)):  # TSEG2
                ciDbtcfg_word = set_bit(ciDbtcfg_word, i, (0 << j) & 1)
            for j, i in enumerate(range(8, 13)):  # TSEG1
                ciDbtcfg_word = set_bit(ciDbtcfg_word, i, (2 << j) & 1)
            for j, i in enumerate(range(0, 8)): #BRP
                ciDbtcfg_word = set_bit(ciDbtcfg_word, i, 0)
            # SSP
            for j, i in enumerate(range(24, 30)):  # TDCV
                ciTdc_word = set_bit(ciTdc_word, i, (1 << j) & 1)
            for j, i in enumerate(range(16, 9)):  # TDCO
                ciTdc_word = set_bit(ciTdc_word, i, (3 << j) & 1)
        elif selectedBitTime == CAN_500K_10M:
            # Data BR
            for j, i in enumerate(range(24, 28)):  # SJW
                ciDbtcfg_word = set_bit(ciDbtcfg_word, i, (0 << j) & 1)
            for j, i in enumerate(range(16, 20)):  # TSEG2
                ciDbtcfg_word = set_bit(ciDbtcfg_word, i, (0 << j) & 1)
            for j, i in enumerate(range(8, 13)):  # TSEG1
                ciDbtcfg_word = set_bit(ciDbtcfg_word, i, (1 << j) & 1)
            for j, i in enumerate(range(0, 8)): #BRP
                ciDbtcfg_word = set_bit(ciDbtcfg_word, i, 0)
            # SSP
            for j, i in enumerate(range(24, 30)):  # TDCV
                ciTdc_word = set_bit(ciTdc_word, i, (0 << j) & 1)
            for j, i in enumerate(range(16, 9)):  # TDCO
                ciTdc_word = set_bit(ciTdc_word, i, (2 << j) & 1)
        elif selectedBitTime in (CAN_250K_500K, CAN_125K_500K):
            # Data BR
            for j, i in enumerate(range(24, 28)):  # SJW
                ciDbtcfg_word = set_bit(ciDbtcfg_word, i, (7 << j) & 1)
            for j, i in enumerate(range(16, 20)):  # TSEG2
                ciDbtcfg_word = set_bit(ciDbtcfg_word, i, (7 << j) & 1)
            for j, i in enumerate(range(8, 13)):  # TSEG1
                ciDbtcfg_word = set_bit(ciDbtcfg_word, i, (30 << j) & 1)
            for j, i in enumerate(range(0, 8)): #BRP
                ciDbtcfg_word = set_bit(ciDbtcfg_word, i, 1)
            # SSP
            for j, i in enumerate(range(24, 30)):  # TDCV
                ciTdc_word = set_bit(ciTdc_word, i, (tdcValue << j) & 1)
            for j, i in enumerate(range(16, 9)):  # TDCO
                ciTdc_word = set_bit(ciTdc_word, i, (31 << j) & 1)
            for j, i in enumerate(range(16, 18)):  # TDCO
                ciTdc_word = set_bit(ciTdc_word, i, (CAN_SSP_MODE_OFF << j) & 1)
        elif selectedBitTime == CAN_250K_833K:
            # Data BR
            for j, i in enumerate(range(24, 28)):  # SJW
                ciDbtcfg_word = set_bit(ciDbtcfg_word, i, (4 << j) & 1)
            for j, i in enumerate(range(16, 20)):  # TSEG2
                ciDbtcfg_word = set_bit(ciDbtcfg_word, i, (4 << j) & 1)
            for j, i in enumerate(range(8, 13)):  # TSEG1
                ciDbtcfg_word = set_bit(ciDbtcfg_word, i, (17 << j) & 1)
            for j, i in enumerate(range(0, 8)): #BRP
                ciDbtcfg_word = set_bit(ciDbtcfg_word, i, 1)
            # SSP
            for j, i in enumerate(range(24, 30)):  # TDCV
                ciTdc_word = set_bit(ciTdc_word, i, (tdcValue << j) & 1)
            for j, i in enumerate(range(16, 9)):  # TDCO
                ciTdc_word = set_bit(ciTdc_word, i, (18 << j) & 1)
            for j, i in enumerate(range(16, 18)):  # TDCO
                ciTdc_word = set_bit(ciTdc_word, i, (CAN_SSP_MODE_OFF << j) & 1)
        elif selectedBitTime == CAN_250K_1M:
            # Data BR
            for j, i in enumerate(range(24, 28)):  # SJW
                ciDbtcfg_word = set_bit(ciDbtcfg_word, i, (7 << j) & 1)
            for j, i in enumerate(range(16, 20)):  # TSEG2
                ciDbtcfg_word = set_bit(ciDbtcfg_word, i, (7 << j) & 1)
            for j, i in enumerate(range(8, 13)):  # TSEG1
                ciDbtcfg_word = set_bit(ciDbtcfg_word, i, (30 << j) & 1)
            for j, i in enumerate(range(0, 8)): #BRP
                ciDbtcfg_word = set_bit(ciDbtcfg_word, i, 1)
            # SSP
            for j, i in enumerate(range(24, 30)):  # TDCV
                ciTdc_word = set_bit(ciTdc_word, i, (tdcValue << j) & 1)
            for j, i in enumerate(range(16, 9)):  # TDCO
                ciTdc_word = set_bit(ciTdc_word, i, (31 << j) & 1)
        elif selectedBitTime == CAN_250K_1M5:
            # Data BR
            for j, i in enumerate(range(24, 28)):  # SJW
                ciDbtcfg_word = set_bit(ciDbtcfg_word, i, (5 << j) & 1)
            for j, i in enumerate(range(16, 20)):  # TSEG2
                ciDbtcfg_word = set_bit(ciDbtcfg_word, i, (5 << j) & 1)
            for j, i in enumerate(range(8, 13)):  # TSEG1
                ciDbtcfg_word = set_bit(ciDbtcfg_word, i, (18 << j) & 1)
            for j, i in enumerate(range(0, 8)): #BRP
                ciDbtcfg_word = set_bit(ciDbtcfg_word, i, 1)
            # SSP
            for j, i in enumerate(range(24, 30)):  # TDCV
                ciTdc_word = set_bit(ciTdc_word, i, (tdcValue << j) & 1)
            for j, i in enumerate(range(16, 9)):  # TDCO
                ciTdc_word = set_bit(ciTdc_word, i, (19 << j) & 1)
        elif selectedBitTime == CAN_250K_2M:
            # Data BR
            for j, i in enumerate(range(24, 28)):  # SJW
                ciDbtcfg_word = set_bit(ciDbtcfg_word, i, (3 << j) & 1)
            for j, i in enumerate(range(16, 20)):  # TSEG2
                ciDbtcfg_word = set_bit(ciDbtcfg_word, i, (3 << j) & 1)
            for j, i in enumerate(range(8, 13)):  # TSEG1
                ciDbtcfg_word = set_bit(ciDbtcfg_word, i, (14 << j) & 1)
            for j, i in enumerate(range(0, 8)): #BRP
                ciDbtcfg_word = set_bit(ciDbtcfg_word, i, 0)
            # SSP
            for j, i in enumerate(range(24, 30)):  # TDCV
                ciTdc_word = set_bit(ciTdc_word, i, (tdcValue << j) & 1)
            for j, i in enumerate(range(16, 9)):  # TDCO
                ciTdc_word = set_bit(ciTdc_word, i, (15 << j) & 1)
        elif selectedBitTime == CAN_250K_3M:
            # Data BR
            for j, i in enumerate(range(24, 28)):  # SJW
                ciDbtcfg_word = set_bit(ciDbtcfg_word, i, (2 << j) & 1)
            for j, i in enumerate(range(16, 20)):  # TSEG2
                ciDbtcfg_word = set_bit(ciDbtcfg_word, i, (2 << j) & 1)
            for j, i in enumerate(range(8, 13)):  # TSEG1
                ciDbtcfg_word = set_bit(ciDbtcfg_word, i, (8 << j) & 1)
            for j, i in enumerate(range(0, 8)): #BRP
                ciDbtcfg_word = set_bit(ciDbtcfg_word, i, 0)
            # SSP
            for j, i in enumerate(range(24, 30)):  # TDCV
                ciTdc_word = set_bit(ciTdc_word, i, (tdcValue << j) & 1)
            for j, i in enumerate(range(16, 9)):  # TDCO
                ciTdc_word = set_bit(ciTdc_word, i, (9 << j) & 1)
        elif selectedBitTime == CAN_250K_4M:
            # Data BR
            for j, i in enumerate(range(24, 28)):  # SJW
                ciDbtcfg_word = set_bit(ciDbtcfg_word, i, (1 << j) & 1)
            for j, i in enumerate(range(16, 20)):  # TSEG2
                ciDbtcfg_word = set_bit(ciDbtcfg_word, i, (1 << j) & 1)
            for j, i in enumerate(range(8, 13)):  # TSEG1
                ciDbtcfg_word = set_bit(ciDbtcfg_word, i, (6 << j) & 1)
            for j, i in enumerate(range(0, 8)): #BRP
                ciDbtcfg_word = set_bit(ciDbtcfg_word, i, 0)
            # SSP
            for j, i in enumerate(range(24, 30)):  # TDCV
                ciTdc_word = set_bit(ciTdc_word, i, (tdcValue << j) & 1)
            for j, i in enumerate(range(16, 9)):  # TDCO
                ciTdc_word = set_bit(ciTdc_word, i, (7 << j) & 1)
        else:
            return -1
        self.writeWord(cREGADDR_CiDBTCFG, ciDbtcfg_word)
        self.writeWord(cREGADDR_CiTDC, ciTdc_word)

    def eccEnable(self):
        byte = self.readByte(cREGADDR_ECCCON)
        byte |= 0x01
        self.writeByte(cREGADDR_ECCCON, byte)
        print('ECC enabled')

    def eccDisable(self):
        byte = self.readByte(cREGADDR_ECCCON)
        byte |= ~0x01
        self.writeByte(cREGADDR_ECCCON, byte)
        print('ECC disabled')

    def ramInit(self, d):
        txd = [d for k in range(0, self.SPI_DEFAULT_BUFFER_LENGTH)]
        for i in range(cRAMADDR_START, cRAM_SIZE / self.SPI_DEFAULT_BUFFER_LENGTH, self.SPI_DEFAULT_BUFFER_LENGTH):
            self.writeByteArray(i, txd)
        print('RAM initialized')

    def calculateCRC16(self, data):
        # data is a byte array
        init = CRCBASE
        for byte in data:
            index = (init >> 8) ^ byte
            init = ((init << 8) ^ crc16_table[index]) & 0xFFFF
        return init


    def receiveMessageGet(self, nBytes):  # rxd, n):
        # fifoReg = []
        ciFifoCon = REG_CiFIFOCON()
        ciFifoSta = REG_CiFIFOSTA()
        ciFifoUa = REG_CiFIFOUA()
        n = 0

        # get FIFO registers
        address = cREGADDR_CiFIFOCON + (self.rxchannel * CiFIFO_OFFSET)
        # fifoReg = [reverse(w) for w in self.readWordArray(address, 3)]
        fifoReg = [w for w in self.readWordArray(address, 3)]

        # check that is a receive buffer
        ciFifoCon_word = fifoReg[0]
        if int(ciFifoCon_word >> 31) & 1: #TxEnable:
            return -2

        # get status
        ciFifoSta_word = fifoReg[1]

        # get address
        ciFifoUa_word = fifoReg[2]
        # TO DO: CHECK CORRECT BYTE WITH MASK

        address = ciFifoUa.UserAddress + cRAMADDR_START
        n = nBytes + 8
        # TO DO: CHECK CORRECT BYTE WITH MASK

        if int(ciFifoCon_word >> 29) & 1: #.rx.RxTimeStampEnable:
            n += 4
        if n % 4:
            n = n + 4 - (n % 4)

        # read rxObj
        if n > MAX_MSG_SIZE:
            n = MAX_MSG_SIZE
        ba = self.readByteArray(address, n)

        word = hex((ba[0] << 24) + (ba[1] << 16) + (ba[2] << 8) + ba[3])
        word = int(word, 16)
        self.rxObj.id.word = word

        word = hex((ba[4] << 24) + (ba[5] << 16) + (ba[6] << 8) + ba[7])
        word = int(word, 16)
        self.rxObj.ctrl.word = word

        rxd = [ba[i] for i in range(8, nBytes)]

        # UINC channel
        self.receiveChannelUpdate()
        return rxd

    def receiveChannelUpdate(self):
        # set UINC
        address = cREGADDR_CiFIFOCON + (self.rxchannel * CiFIFO_OFFSET) + 1
        byte = 0xFF & self.readByte(address)
        self.writeByte(address, 1)  # FF00 ???

    def receiveChannelEventGet(self):
        if self.rxchannel == CAN_FIFO_CH0:
            return -100
        ciFifoSta = REG_CiFIFOSTA()
        #.word = 0
        address = cREGADDR_CiFIFOSTA + (self.rxchannel * CiFIFO_OFFSET)
        byte = self.readByte(address)
        self.rxFlags = (byte & 0xFF) & CAN_RX_FIFO_ALL_EVENTS

    def transmitChannelEventGet(self):
        if self.txchannel == CAN_FIFO_CH0:
            return -100
        ciFifoSta = REG_CiFIFOSTA()
        #ciFifoSta.word = 0
        address = cREGADDR_CiFIFOSTA + (self.txchannel * CiFIFO_OFFSET)
        byte = self.readByte(address)
        self.txFlags = (byte & 0xFF) & CAN_TX_FIFO_ALL_EVENTS

    def dlcToDataBytes(self, dlc):
        if dlc < CAN_DLC_12:
            return dlc
        else:
            return CAN_DLC_dict[dlc]

    def transmitChannelLoad(self, nbytes, flush, txd):
        address = cREGADDR_CiFIFOCON + (self.txchannel * CiFIFO_OFFSET)
        # fifoReg = [reverse(w) for w in self.readWordArray(address, 3)]
        fifoReg = [w for w in self.readWordArray(address, 3)]
        ciFifoCon_word = fifoReg[0]
        if not (int(ciFifoCon_word >> 31) & 1):  #ciFifoCon.tx.TxEnable:
            return -2
        dataBytesInObject = self.dlcToDataBytes(self.txObj.ctrl.DLC)
        if dataBytesInObject < nbytes:
            return -3
        ciFifoSta_word = fifoReg[1]
        ciFifoUa_word = fifoReg[2]
        userAddress = ciFifoUa_word & 0xFFF
        userAddress += cRAMADDR_START
        txBuffer = [0] * nbytes

        for k in range(0, nbytes):
            if k < 4:
                txBuffer[k] = int((self.txObj.id.word >> 8 * k) & 0xFF)
            elif 4 <= k < 8:
                txBuffer[k] = int((self.txObj.ctrl.word >> 8 * (k - 4)) & 0xFF)
            else:
                txBuffer[k] = txd[k - 8]
        n = 0
        if nbytes % 4:
            n = 4 - (nbytes % 4)
            i = nbytes + 8
            for j in range(0, n):
                txBuffer[i + 8 + j] = 0

        print("txbuffer to send: {}".format(txBuffer))
        self.writeByteArray(userAddress, txBuffer)
        self.state = "idle"

        self.transmitChannelUpdate_2(flush)


    def transmitChannelUpdate_2(self, flush):
        address = cREGADDR_CiFIFOCON + (self.txchannel * CiFIFO_OFFSET) + 1
        aux = self.readByte(address - 1)
        aux = set_bit(aux, 0, 1)
        aux = set_bit(aux, 1, 1)
        self.writeByte(address - 1, aux)

        ### DEBUG: TRY TO DIRECTLY WRITE STATUS IN RX FIFOCON
        if self.operationModeGet() == INTERNAL_LOOPBACK_MODE:
            #self.writeByte(cREGADDR_CiFIFOCON + (self.rxchannel * CiFIFO_OFFSET) + 1, 1)
            self.receiveChannelUpdate()

    def transmitBitTimeConfig(self):
        txd = []
        timeConfigs = (BitTimeConfig125K, BitTimeConfig250K, BitTimeConfig500K, BitTimeConfig1M)
        timeConfigsIds = (BITTIME_CFG_125K_ID, BITTIME_CFG_250K_ID, BITTIME_CFG_500K_ID, BITTIME_CFG_1M_ID)
        for id, timeConfig in enumerate(timeConfigs):
            self.txObj.id.SID = timeConfigsIds[id]
            self.txObj.ctrl.IDE = 0
            self.txObj.ctrl.BRS = 1
            self.txObj.ctrl.FDF = 1
            txd = [0] * MAX_DATA_BYTES  # MAX_DATA_BYTES = 64
            txd[0] = timeConfig[0]
            txd[1] = timeConfig[1]
            n = 2
            for i in range(0, timeConfig[0]):
                txd[n] = timeConfig[i + 2] & 0xFF
                n += 1
                txd[n] = (timeConfig[i + 2] >> 8) & 0xFF
                n += 1
            self.txObj.ctrl.DLC = self.dataBytesToDlc(n)
            self.transmitMessageQueue(txd)

    def dataBytesToDlc(self, n):
        try:
            return CAN_DLC_inv_dict[n]
        except KeyError:
            return CAN_DLC_0

    def ramTest(self):
        # verify R/W
        # txd = [0] * MAX_DATA_BYTES
        # rxd = [0] * MAX_DATA_BYTES
        for length in range(4, MAX_DATA_BYTES + 1, 4):
            txd = [(randint(0, RAND_MAX) & 0xFF) for e in range(0, length)]
            # rxd = [0xFF] * length
            print("Data written on RAM: {}".format(txd))
            self.writeByteArray(cRAMADDR_START, txd)
            rxd = self.readByteArray(cRAMADDR_START, length)
            print("Data read on RAM: {}".format(rxd))
            # good = False
            for i in range(0, length):
                good = txd[i] == rxd[i]
                if not good:
                    print("Data mismatch!")
                    return -1
        #self.state = APP_STATE_TEST_REGISTER_ACCESS

        return 1

    def registerTest(self):
        for length in range(1, MAX_DATA_BYTES + 1):
            txd = [(randint(0, RAND_MAX) & 0x7F) for e in range(0, length)]
            self.writeByteArray(cREGADDR_CiFLTOBJ, txd)
            rxd = self.readByteArray(cREGADDR_CiFLTOBJ, length)
            print("Data written on Registers: {}".format(txd))
            print("Data read on Registers: {}".format(rxd))
            # good = False
            for i in range(0, length):
                good = txd[i] == rxd[i]
                if not good:
                    print("Data mismatch!")
                    return -1
       # self.state = APP_STATE_INIT_TXOBJ
        return 1

    def initTxObj(self):
        self.txObj.id.word = 0
        self.txObj.ctrl.word = 0

        self.txObj.id.SID = 0  # TX_RESPONSE_ID
        self.txObj.id.EID = 0

        self.txObj.ctrl.BRS = 1
        self.txObj.ctrl.DLC = self.txdlc # CAN_DLC_64
        self.txObj.ctrl.FDF = 1
        self.txObj.ctrl.IDE = 0
        self.txObj.ctrl.RTR = 0
        self.txObj.ctrl.SEQ = 1

        self.state = "idle"  # APP_STATE_RECEIVE

    def transmitMessageTasks(self, txd):
        self.txObj.id.word = 0
        self.txObj.ctrl.word = 0

        self.txObj.id.SID = self.txCounter  # TX_RESPONSE_ID
        self.txObj.id.EID = 0
        self.txObj.ctrl.BRS = 1
        self.txObj.ctrl.DLC = self.txdlc #CAN_DLC_64
        self.txObj.ctrl.FDF = 1
        self.txObj.ctrl.IDE = 0
        self.txObj.ctrl.RTR = 0
        self.txObj.ctrl.SEQ = 1
        #txd = range(0, self.dlcToDataBytes(self.txObj.ctrl.DLC))

        self.transmitChannelEventGet()

        if self.txFlags & CAN_TX_FIFO_NOT_FULL_EVENT:
            dlc = self.dlcToDataBytes(self.txObj.ctrl.DLC)
            if dlc < len(txd):
                print("Message too long! Cropping message")
                txd = txd[0:dlc]
            elif dlc > len(txd):
                print("Message too short, adding 0s")
                while len(txd) != dlc:
                    txd.append(0)
            self.transmitChannelLoad(self.dlcToDataBytes(self.txObj.ctrl.DLC), True, txd)
            self.txCounter += 1
            if self.txCounter > 0x7FF:
                self.txCounter = 0

    def receiveMessageTasks(self):
        self.receiveChannelEventGet()
        if self.rxFlags & CAN_RX_FIFO_NOT_EMPTY_EVENT:
            rxd = self.receiveMessageGet(MAX_DATA_BYTES)
            return rxd

