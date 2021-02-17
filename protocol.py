
from scapy.all import *

def ReadPackedUInt32(x: bytes):
    readMore = True
    shift = 0
    output = 0
    while readMore:
        if len(x) == 0: raise Exception
        b = x[0]
        x = x[1:]
        if b >= 128:
            readMore = True
            b ^= 128
        else:
            readMore = False

        output |= (b << shift)
        shift += 7

    return x, output

def ReadPackedInt32(x: bytes):
    s, i = ReadPackedUInt32(x)
    if i & (1 << 31):
        i -= (1<<32)
    return s, i

def WritePackedUInt32(x):
    r = 0
    while x > 0:
        b = x & 255
        if x >= 128:
            b |= 128

        r = (r << 8) + b
        x >>= 7
    return r

def WritePackedInt32(x):
    return WritePackedUInt32(x)

class PackedUInt32(Field):
    __slots__ = [
        "name",
        "default",
        "owners",
    ]
    islist = 0
    ismutable = False
    holds_packets = 0

    def __init__(self, name, default):
        # type: (str, Any) -> None
        if not isinstance(name, str):
            raise ValueError("name should be a string")
        self.name = name
        self.default = self.any2i(None, default)
        self.owners = []  # type: List[Type[Packet]]

    def i2len(self,
              pkt,  # type: Packet
              x,  # type: Any
              ):
        # type: (...) -> int
        """Convert internal value to a length usable by a FieldLenField"""
        if isinstance(x, RawVal):
            return len(x)
        raise "Exception"

    def i2count(self, pkt, x):
        # type: (Optional[Packet], I) -> int
        """Convert internal value to a number of elements usable by a FieldLenField.
        Always 1 except for list fields"""
        return 1

    def h2i(self, pkt, x):
        # type: (Optional[Packet], Any) -> I
        """Convert human value to internal value"""
        return cast(int, x)

    def m2i(self, pkt, x):
        # type: (Optional[Packet], M) -> I
        """Convert machine value to internal value"""
        s, v = ReadPackedUInt32(cast(int, x))
        return v

    def i2m(self, pkt, x):
        # type: (Optional[Packet], Optional[I]) -> M
        """Convert internal value to machine value"""
        if x is None:
            return cast(int, 0)
        elif isinstance(x, str):
            b = WritePackedUInt32(int.from_bytes(bytes_encode(x), 'big'))
            return b
        b = WritePackedUInt32(cast(int, x))
        return b

    def addfield(self, pkt, s, val):
        # type: (Packet, bytes, Optional[I]) -> bytes
        """Add an internal value to a string
        Copy the network representation of field `val` (belonging to layer
        `pkt`) to the raw string packet `s`, and return the new string packet.
        """
        try:
            x = self.i2m(pkt, val)
            if x == 0: return s + b'\x00'
            return s + x.to_bytes((x.bit_length()+7) // 8, 'big')
        except struct.error as ex:
            raise ValueError(
                "Incorrect type of value for field %s:\n" % self.name +
                "struct.error('%s')\n" % ex +
                "To inject bytes into the field regardless of the type, " +
                "use RawVal. See help(RawVal)"
            )
    
    def getfield(self, pkt, s):
        # type: (Packet, bytes) -> Tuple[bytes, I]
        """Extract an internal value from a string
        Extract from the raw packet `s` the field value belonging to layer
        `pkt`.
        Returns a two-element list,
        first the raw packet string after having removed the extracted field,
        second the extracted field itself in internal representation.
        """
        rs, v = ReadPackedUInt32(s)
        return rs, v

class PackedInt32(PackedUInt32):
    def m2i(self, pkt, x):
        # type: (Optional[Packet], M) -> I
        """Convert machine value to internal value"""
        s, v = ReadPackedInt32(cast(int, x))
        return v

    def i2m(self, pkt, x):
        # type: (Optional[Packet], Optional[I]) -> M
        """Convert internal value to machine value"""
        if x is None:
            return cast(int, 0)
        elif isinstance(x, str):
            b = WritePackedInt32(int.from_bytes(bytes_encode(x), 'big'))
            return b
        b = WritePackedInt32(cast(int, x))
        return b

    def getfield(self, pkt, s):
        # type: (Packet, bytes) -> Tuple[bytes, I]
        """Extract an internal value from a string
        Extract from the raw packet `s` the field value belonging to layer
        `pkt`.
        Returns a two-element list,
        first the raw packet string after having removed the extracted field,
        second the extracted field itself in internal representation.
        """
        rs, v = ReadPackedInt32(s)
        return rs, v

class GameIDField(LESignedIntField):
    @staticmethod
    def intToCode(x):
        if x < 0:
            CHAR_SET = "QWXRTYLPESDFGHUJKZOCVBINMA"
            first = x & 1023
            last = (x >> 10) & int.from_bytes(b'\x0f\xff\xff', 'big')
            s = ''
            s += CHAR_SET[ first % 26 ]
            s += CHAR_SET[ first // 26 ]
            s += CHAR_SET[ last % 26 ]
            last //= 26
            s += CHAR_SET[ last % 26 ]
            last //= 26
            s += CHAR_SET[ last % 26 ]
            last //= 26
            s += CHAR_SET[ last % 26 ]
            return s
        else:
            return x.to_bytes(4, 'little').decode('utf8')

    @staticmethod
    def codeToInt(x):
        if x is None:
            return 0
        CHAR_MAP = ( 25, 21, 19, 10, 8, 11, 12, 13, 22, 15, 16, 6, 24, 23, 18, 7, 0, 3, 9, 4, 14, 20, 1, 2, 5, 17 )
        x = x.upper()
        if len(x) == 4:
            return int.from_bytes(x.encode('utf8'), 'little')
        if len(x) != 6:
            raise Exception

        s = []
        for c in x:
            i = int.from_bytes(c.encode('utf8'), 'little') - 65
            s.append(CHAR_MAP[i])
        first = (s[0] + 26 * s[1]) & 1023
        last  = (s[2] + 26 * (s[3] + 26 * (s[4] + 26 * s[5])))
        r = first | ((last << 10) & 0x3FFFFC00) | 0x80000000
        return -(1<<32)+r

    def h2i(self, pkt, x):
        return self.codeToInt(x)
    
    def i2h(self, pkt, x):
        return self.intToCode(x)

class HazelMessage(Packet):
    name = 'Message'
    
    fields_desc = [
        LEShortField('length', 0),
        ByteEnumField('tag', 0, {
            0:  'HostGame',
            1:  'JoinGame',
            2:  'StartGame',
            3:  'RemoveGame',
            4:  'RemovePlayer',
            5:  'GameData',
            6:  'GameDataTo',
            7:  'JoinedGame',
            8:  'EndGame',
            9:  'GetGameList',
            10: 'AlterGame',
            11: 'KickPlayer',
            12: 'WaitForHost',
            13: 'Redirect',
            14: 'ReselectServer',
            16: 'GetGameListV2'
        })
    ]

    def post_build(self, p, pay):
        if self.length == 0 and pay:
            l = len(pay).to_bytes(2, 'little')
            p = l + p[2:]
        return p+pay
    
    def extract_padding(self, s):
        return s[:self.length],s[self.length:]

    def guess_payload_class(self, payload):
        if self.tag == 0:
            pass
        elif self.tag == 1:
            pass
        elif self.tag == 2:
            pass
        elif self.tag == 3:
            pass
        elif self.tag == 4:
            pass
        elif self.tag == 5:
            return GameData
        elif self.tag == 6:
            pass
        elif self.tag == 7:
            pass
        elif self.tag == 8:
            pass
        elif self.tag == 9:
            pass
        elif self.tag == 10:
            pass
        elif self.tag == 11:
            pass
        elif self.tag == 12:
            pass
        elif self.tag == 13:
            pass
        elif self.tag == 14:
            pass
        elif self.tag == 16:
            pass
        super().guess_payload_class(payload)

class AmongUs(Packet):
    fields_desc = [
        ByteEnumField('type', 0,
        {
            0: 'Normal',
            1: 'Reliable',
            8: 'Hello',
            9: 'Disconnect',
            10: 'Acknowledgement',
            11: 'Fragment',
            12: 'Ping'
        }),
        ConditionalField(ShortField('nonce', None), lambda p:p.type in [1, 8]),
        ConditionalField(ByteField('hazel_version', None), lambda p:p.type == 8),
        ConditionalField(IntField('client_version', None), lambda p:p.type == 8),
        #ConditionalField(FieldLenField('username_len', 0, length_of='username'), lambda p:p.type == 8),
        #ConditionalField(StrLenField('username', '', length_from=lambda p:p.username_len), lambda p:p.type == 8),
        PacketListField('Messages', None, HazelMessage, next_cls_cb=lambda pkt,lst,cur,remain: HazelMessage if len(remain)>0 else None)
    ]

class GameDataTypes(HazelMessage):
    fields_desc = [
        LEShortField('length', 0),
        ByteEnumField('tag', 0, {
            1: 'Data',
            2: 'RPC',
            4: 'Spawn',
            5: 'Despawn',
            6: 'SceneChange',
            7: 'Ready',
            8: 'ChangeSettings'
        })
    ]

    def guess_payload_class(self, payload):
        if self.tag == 1:
            pass
        elif self.tag == 2:
            pass
        elif self.tag == 4:
            return Spawn
        elif self.tag == 5:
            return GameData
        elif self.tag == 6:
            pass
        elif self.tag == 7:
            pass
        elif self.tag == 8:
            pass
        super().guess_payload_class(payload)

class GameData(Packet):
    name = 'Game Data'
    fields_desc = [
        GameIDField('game_id', 'ERRO'),
        PacketListField('Messages', None, GameDataTypes, next_cls_cb=lambda pkt,lst,cur,remain: GameDataTypes if len(remain)>0 else None)
    ]

class TaskData(Packet):
    name = 'Task'
    fields_desc = [
        PackedUInt32('task_id', 0),
        ByteField('is_completed', 0)
    ]

class PlayerData(Packet):
    name = 'Player'
    fields_desc = [
        ByteField('player_id', None),
        FieldLenField("name_length", None, length_of="name", fmt='!B'),
        StrLenField("name", "", length_from=lambda pkt:pkt.name_length),
        PackedUInt32('color_id', 0),
        PackedUInt32('hat_id', 0),
        PackedUInt32('pet_id', 0),
        PackedUInt32('skin_id', 0),
        ByteField('flags', 0),
        FieldLenField('task_length', 0, count_of='tasks', fmt='!B'),
        PacketListField('tasts', None, TaskData, count_from=lambda p:p.task_length)
    ]

class InnerNetObjectType(HazelMessage):
    name = 'Object'
    fields_desc = [
        LEShortField('length', 0),
        ByteEnumField('tag', 0, {
            0:	'SHIP_STATUS',
            1:	'MEETING_HUD',
            2:	'LOBBY_BEHAVIOUR',
            3:	'GAME_DATA',
            4:	'PLAYER_CONTROL',
            5:	'HEADQUARTERS',
            6:	'PLANET_MAP',
            7:	'APRIL_SHIP_STATUS'
        })
    ]

    def guess_payload_class(self, payload):
        if self.tag == 0:
            pass
        elif self.tag == 1:
            pass
        elif self.tag == 2:
            pass
        elif self.tag == 3:
            return PlayerData
        elif self.tag == 4:
            pass
        elif self.tag == 5:
            pass
        elif self.tag == 6:
            pass
        elif self.tag == 7:
            pass
        super().guess_payload_class(payload)

class Component(Packet):
    fields_desc = [
        PackedUInt32('net_id', None),
        PacketField('object', None, InnerNetObjectType)
    ]

class Spawn(Packet):
    fields_desc = [
        PackedUInt32('spawn_type', None),
        PackedInt32('owner_id', None),
        ByteField('spawn_flags', None),
        PackedUInt32('component_length', 0),
        PacketListField('Messages', None, Component, count_from=lambda p:p.component_length)
    ]

if __name__ == '__main__':
    amongUs = AmongUs(type='Normal')/HazelMessage(tag=5)/GameData(game_id='REDSUS')/GameDataTypes(tag=4)/\
        Spawn(spawn_type=12, owner_id=13, spawn_flags=0, component_length=1)/Component(net_id=42)/\
        InnerNetObjectType(tag=3)/PlayerData(
            player_id=13,
            name='RED',
            color_id=0,
            flags=2,
        )/TaskData(task_id=42, is_completed=0)
    amongUs.show2()
    hexdump(amongUs)
    b = bytes(amongUs)
    amongUs2 = AmongUs(b)
    amongUs2.show2()
    hexdump(amongUs2)