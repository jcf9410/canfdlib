import ctypes
import binascii
c_uint32 = ctypes.c_uint32
c_bool = ctypes.c_bool
endianType = ctypes.LittleEndianStructure
union = ctypes.Union
import timeit

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

def reverse(n):
    array = [int(hex(int(n) >> i & 0xff).replace('L', ''), 16) for i in (24, 16, 8, 0)]
    new = []
    for byte in array:
        aux = bin(byte).replace('0b', '')
        while len(aux) < 8:
            aux = '0' + aux
        new.append(int(aux[::-1], 2))
    return int(binascii.hexlify(bytearray(new)), 16)

def set_bit(v, index, x):
  mask = 1 << index
  v &= ~mask
  if x:
    v |= mask
  return v

def method1():
    # Struct register.
    # Reverse the bit order in each byte of the word
    reg = REG_CiCON()
    reg.IsoCrcEnable = 1
    return reverse(reg.word) #result to write

def method2():
    # Change
    return set_bit(0, 5, 1) #result to write

def method3():
    reg = REG_CiCON()
    reg.IsoCrcEnable = 1
    # reg.word is result to write

if __name__ == '__main__':
    print(timeit.timeit("method1()", setup="from __main__ import method1", number=100000))
    print(timeit.timeit("method2()", setup="from __main__ import method2", number=100000))
    print(timeit.timeit("method3()", setup="from __main__ import method3", number=100000))