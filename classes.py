import ctypes
c_uint32 = ctypes.c_uint32
c_bool = ctypes.c_bool
endianType = ctypes.LittleEndianStructure
union = ctypes.Union


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
