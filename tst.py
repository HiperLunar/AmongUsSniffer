
from scapy.all import *

class TestSLF(Packet):
    fields_desc=[ FieldLenField("len", None, length_of="data"),
                  StrLenField("data", "", length_from=lambda pkt:pkt.len) ]

amongUs = TestSLF(data='HELLO')
amongUs.show2()
hexdump(amongUs)
b = bytes(amongUs)
amongUs2 = TestSLF(b)
amongUs2.show2()
hexdump(amongUs2)