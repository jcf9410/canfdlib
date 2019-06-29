import ctypes
c_uint32 = ctypes.c_uint32
c_bool = ctypes.c_bool
endianType = ctypes.LittleEndianStructure
#endianType = ctypes.BigEndianStructure
union = ctypes.Union

#CAN Control Register
class REG_CiCON_bits(endianType):
    _fields_ = [
        ("TxBandWidthSharing", c_uint32, 4),
        ("AbortAllTx", c_uint32, 1),
        ("RequestOpMode", c_uint32, 3),
        ("OpMode", c_uint32, 3),
        ("TXQEnable", c_uint32, 1),
        ("StoreInTEF", c_uint32, 1),
        ("SystemErrorToListenOnly", c_uint32, 1),
        ("EsiInGatewayMode", c_uint32, 1),
        ("RestrictReTxAttempts", c_uint32, 1),
        ("unimplemented3", c_uint32, 3),
        ("BitRateSwitchDisable", c_uint32, 1),
        ("unimplemented2", c_uint32, 1),
        ("WakeUpFilterTime", c_uint32, 2),
        ("WakeUpFilterEnable", c_uint32, 1),
        ("unimplemented1", c_uint32, 1),
        ("ProtocolExceptionEventDisable", c_uint32, 1),
        ("IsoCrcEnable", c_uint32, 1),
        ("DNetFilterCount", c_uint32, 5),
               ]
class REG_CiCON(union):
    _anonymous_ = ("bit",)
    _fields_ = [
        ("bit",    REG_CiCON_bits),
        ("word", c_uint32)
               ]

class REG_CAN_CONFIG_bits(endianType):
    _fields_ = [
        ("TxBandWidthSharing", c_uint32, 4),
        ("TXQEnable", c_uint32, 1),
        ("StoreInTEF", c_uint32, 1),
        ("SystemErrorToListenOnly", c_uint32, 1),
        ("EsiInGatewayMode", c_uint32, 1),
        ("RestrictReTxAttempts", c_uint32, 1),
        ("BitRateSwitchDisable", c_uint32, 1),
        ("WakeUpFilterTime", c_uint32, 2),
        ("WakeUpFilterEnable", c_uint32, 1),
        ("ProtocolExceptionEventDisable", c_uint32, 1),
        ("IsoCrcEnable", c_uint32, 1),
        ("DNetFilterCount", c_uint32, 5),
               ]

class REG_CAN_CONFIG(union):
    _anonymous_ = ("bit",)
    _fields_ = [
        ("bit",    REG_CAN_CONFIG_bits),
        ("word", c_uint32)
               ]

#Nominal Bit Time Configuration Register

class REG_CiNBTCFG_bits(endianType):
    _fields_ = [
        ("BRP", c_uint32, 8),
        ("TSEG1", c_uint32, 8),
        ("unimplemented2", c_uint32, 1),
        ("TSEG2", c_uint32, 7),
        ("unimplemented1", c_uint32, 1),
        ("SJW", c_uint32, 7),
    ]

class REG_CiNBTCFG(union):
    _anonymous_ = ("bit",)
    _fields_ = [
        ("bit",    REG_CiNBTCFG_bits),
        ("word", c_uint32)
               ]

#Data Bit Time Configuration Register
class REG_CiDBTCFG_bits(endianType):
    _fields_ = [
        ("BRP", c_uint32, 8),
        ("unimplemented3", c_uint32, 3),
        ("TSEG1", c_uint32, 5),
        ("unimplemented2", c_uint32, 4),
        ("TSEG2", c_uint32, 4),
        ("unimplemented1", c_uint32, 4),
        ("SJW", c_uint32, 4),
    ]
class REG_CiDBTCFG(union):
    _anonymous_ = ("bit",)
    _fields_ = [
        ("bit",    REG_CiDBTCFG_bits),
        ("word", c_uint32)
               ]

# Transmitter Delay Compensation Register
class REG_CiTDC_bits(endianType):
    _fields_ = [
        ("unimplemented4", c_uint32, 6),
        ("EdgeFilterEnable", c_uint32, 1),
        ("SID11Enable", c_uint32, 1),
        ("unimplemented3", c_uint32, 6),
        ("TDCMode", c_uint32, 2),
        ("unimplemented2", c_uint32, 1),
        ("TDCOffset", c_uint32, 7),
        ("unimplemented1", c_uint32, 2),
        ("TDCValue", c_uint32, 6),
    ]
class REG_CiTDC(union):
    _anonymous_ = ("bit",)
    _fields_ = [
        ("bit",    REG_CiTDC_bits),
        ("word", c_uint32)
               ]

#Time Stamp Configuration Register
class REG_CiTSCON_bits(endianType):
    _fields_ = [
        ("unimplemented2", c_uint32, 14),
        ("TimeStampEOF", c_uint32, 1),
        ("TBCEnable", c_uint32, 1),
        ("unimplemented1", c_uint32, 6),
        ("TBCPrescaler", c_uint32, 10),
    ]
class REG_CiTSCON(union):
    _anonymous_ = ("bit",)
    _fields_ = [
        ("bit",    REG_CiTSCON_bits),
        ("word", c_uint32)
               ]

class rxBF_bits(endianType):
    _fields_ = [
        ("PayLoadSize", c_uint32, 3),
        ("FifoSize", c_uint32, 5),
        ("unimplemented4", c_uint32, 13),
        ("FRESET", c_uint32, 1),
        ("unimplemented3", c_uint32, 1),
        ("UINC", c_uint32, 1),
        ("TxEnable", c_uint32, 1),
        ("unimplemented2", c_uint32, 1),
        ("RxTimeStampEnable", c_uint32, 1),
        ("unimplemented1", c_uint32, 2),
        ("RxOverFlowIE", c_uint32, 1),
        ("RxFullIE", c_uint32, 1),
        ("RxHalfFullIE", c_uint32, 1),
        ("RxNotEmptyIE", c_uint32, 1),
    ]

class txBF_bits(endianType):
    _fields_ = [
        ("PayLoadSize", c_uint32, 3),
        ("FifoSize", c_uint32, 5),
        ("unimplemented4", c_uint32, 1),
        ("TxAttempts", c_uint32, 2),
        ("TxPriority", c_uint32, 5),
        ("unimplemented3", c_uint32, 5),
        ("FRESET", c_uint32, 1),
        ("TxRequest", c_uint32, 1),
        ("UINC", c_uint32, 1),
        ("TxEnable", c_uint32, 1),
        ("RTREnable", c_uint32, 1),
        ("unimplemented2", c_uint32, 1),
        ("TxAttemptIE", c_uint32, 1),
        ("unimplemented1", c_uint32, 1),
        ("TxEmptyIE", c_uint32, 1),
        ("TxHalfFullIE", c_uint32, 1),
        ("TxNotFullIE", c_uint32, 1),
    ]

class REG_CiFIFOCON(union):
    _fields_ =[("rx", rxBF_bits),
               ("tx", txBF_bits),
               ("word", c_uint32)
               ]

class CAN_TX_FIFO_CONFIG(endianType):
    _fields_ = [
        ("RTREnable", c_uint32, 1),
        ("TxPriority", c_uint32, 5),
        ("TxAttempts", c_uint32, 2),
        ("FifoSize", c_uint32, 5),
        ("PayLoadSize", c_uint32, 3)]

class CAN_RX_FIFO_CONFIG(endianType):
    _fields_ = [
        ("RxTimeStampEnable",  c_uint32,1),
        ("FifoSize", c_uint32, 5),
        ("PayLoadSize", c_uint32, 3)]

class CAN_MSGOBJ_ID_bits(endianType):
    _fields_ = [
        ("unimplemented1", c_uint32, 2),
        ("SID11", c_uint32, 1),
        ("EID", c_uint32, 18),
        ("SID", c_uint32, 11),
        ]

class CAN_MSGOBJ_ID(union):
    _anonymous_ = ("bit",)
    _fields_ = [
        ("bit", CAN_MSGOBJ_ID_bits),
        ("word", c_uint32)
               ]

class CAN_TX_MSGOBJ_CTRL_bits(endianType):
    _fields_ = [
        ("unimplemented1", c_uint32, 16),
        ("SEQ", c_uint32, 7),
        ("ESI", c_uint32, 1),
        ("FDF", c_uint32, 1),
        ("BRS", c_uint32, 1),
        ("RTR", c_uint32, 1),
        ("IDE", c_uint32, 1),
        ("DLC", c_uint32, 4),
        ]
class CAN_TX_MSGOBJ_CTRL(union):
    _anonymous_ = ("bit",)
    _fields_ = [
        ("bit", CAN_TX_MSGOBJ_CTRL_bits),
        ("word", c_uint32)
               ]

class CAN_TX_MSGOBJ(endianType):
    _fields_ = [
        ("id", CAN_MSGOBJ_ID),
        ("ctrl", CAN_TX_MSGOBJ_CTRL),
        ("CAN_MSG_TIMESTAMP", c_uint32)
    ]

class CAN_RX_MSGOBJ_CTRL_bits(endianType):
    _fields_ = [
        ("unimplemented2", c_uint32, 16),
        ("FilterHit", c_uint32, 5),
        ("unimplemented1", c_uint32, 2),
        ("ESI", c_uint32, 1),
        ("FDF", c_uint32, 1),
        ("BRS", c_uint32, 1),
        ("RTR", c_uint32, 1),
        ("IDE", c_uint32, 1),
        ("DLC", c_uint32, 4),
        ]
class CAN_RX_MSGOBJ_CTRL(union):
    _anonymous_ = ("bit",)
    _fields_ = [
        ("bit", CAN_RX_MSGOBJ_CTRL_bits),
        ("word", c_uint32)
               ]

class CAN_RX_MSGOBJ(endianType):
    _fields_ = [
        ("id", CAN_MSGOBJ_ID),
        ("ctrl", CAN_RX_MSGOBJ_CTRL),
        ("CAN_MSG_TIMESTAMP", c_uint32)
    ]

class rxBF2_bits(endianType):
    _fields_ = [
        ("unimplemented2", c_uint32, 19),
        ("FifoIndex", c_uint32, 5),
        ("unimplemented1", c_uint32, 4),
        ("RxOverFlowIE", c_uint32, 1),
        ("RxFullIE", c_uint32, 1),
        ("RxHalfFullIE", c_uint32, 1),
        ("RxNotEmptyIE", c_uint32, 1),
    ]

class txBF2_bits(endianType):
    _fields_ = [
        ("unimplemented2", c_uint32, 19),
        ("FifoIndex", c_uint32, 5),
        ("TxAborted", c_uint32, 1),
        ("TxLostArbitration", c_uint32, 1),
        ("TxError", c_uint32, 1),

        ("TxAttemptIF", c_uint32, 1),
        ("unimplemented1", c_uint32, 1),
        ("TxEmptyIF", c_uint32, 1),
        ("TxHalfFullIE", c_uint32, 1),
        ("TxNotFullIF", c_uint32, 1),
    ]

class REG_CiFIFOSTA(union):
    # _anonymous_ = ("bit",)
    _fields_ = [
        ("tx", txBF2_bits),
        ("rx", rxBF2_bits),
        ("word", c_uint32)
    ]

class REG_CiFIFOUA_bits(endianType):
    _fields_ = [
        ("unimplemented1", c_uint32, 20),
        ("UserAddress", c_uint32, 12),
    ]

class REG_CiFIFOUA(union):
    _anonymous_ = ("bit",)
    _fields_ = [
        ("bit", REG_CiFIFOUA_bits),
        ("word", c_uint32)
    ]

class REG_CiTREC_bits(endianType):
    _fields_ = [
        ("unimplemented1", c_uint32, 10),
        ("TxErrorStateBusOff", c_uint32, 1),
        ("TxErrorStatePassive", c_uint32, 1),
        ("RxErrorStatePassive", c_uint32, 1),
        ("TxErrorStateWarning", c_uint32, 1),
        ("RxErrorStateWarning", c_uint32, 1),
        ("ErrorStateWarning", c_uint32, 1),
        ("TxErrorCount", c_uint32, 8),
        ("RxErrorCount", c_uint32, 8),
    ]

class REG_CiTREC(union):
    _anonymous_ = ("bit",)
    _fields_ = [
        ("bit", REG_CiTREC_bits),
        ("word", c_uint32)
    ]

class payLoad(union):
    _fields_ = [
        ("On", c_bool),
        ("Dlc", c_uint32),
        ("Mode", c_bool),
        ("Counter", c_uint32),
        ("Delay", c_uint32),
        ("BRS", c_bool)
    ]
    #flags.word = X
