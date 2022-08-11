import sys
from struct import *

if len(sys.argv) !=2:
    print("Insufficient arguments")
    sys.exit(-1)

file_name = sys.argv[1]
sector = 512

Len = 0
with open(file_name,"rb") as gpt:
    MBR = gpt.read(sector)
    GPT_Head = gpt.read(sector)
    Len += (sector * 2)
    N_Partition = unpack('i', GPT_Head[80:84])
    Size_Partition = unpack('i', GPT_Head[84:88])
    for i in range(0, N_Partition[0]):
        GPT_Part = gpt.read(Size_Partition[0])
    #     Type1 = unpack('IHH', GPT_Part[:8])
    #     Type2 = unpack('!II',GPT_Part[8:16])
    #     Type = Type1 + Type2
    #     # GUID 구하기
    #     GPT_Type = []
    #     for i in range(0,5):
    #         GPT_Type.append(format(Type[i], 'x'))
    #     GUID = ''.join(GPT_Type).upper()
        GUID = GPT_Part[0:16].hex().upper()

        # GUID_Types = {"00000000000000000000000000000000": "Unused Entry",
        #               "C12A7328F81F11D2BA4B00A0C93EC93B": "EFI System Partition",
        #               "EBD0A0A2B9E5443387C068B6B72699C7": "Basic Data Partition",
        #               "0FC63DAF848347728E793D69D8477DE4": "Linux Filesystem Data",
        #               "4F68BCE3E8CD4DB196E7FCAF984B709": "Root(x86-64)",
        #               "0657FD6DA4AB43C484E50933C84B4F4F": "Swap",
        #               "48465300000011AAAA1100306543ECAC": "HFS+",
        #               "7C3457EF000011AAAA1100306543ECAC": "APFS",
        #               "53746F72616711AAAA1100306543ECAC": "Core Storage",
        #               "426F6F74000011AAAA1100306543ECAC": "Boot Partition"}
        #
        # # Type 확인
        # if GUID not in GUID_Types:
        #     GUID_Type = ''
        # else:
        #     GUID_Type = GUID_Types[GUID]

        First_LBA = unpack('q', GPT_Part[32:40])
        # 실제 offset sector
        offset_Sector = First_LBA[0] * 512

        # Size 구하기
        Last_LBA  = unpack('q', GPT_Part[40:48])
        size = (Last_LBA[0] - First_LBA[0] + 1) * sector
        name = GPT_Part[56:128].decode("utf-16le")
        if GUID == '00000000000000000000000000000000':
            break
        else:
            print(GUID, offset_Sector, size)


