import sys
from struct import *

if len(sys.argv) !=2:
    print("Insufficient arguments")
    sys.exit(-1)

file_name = sys.argv[1]
RunOffInit = 0
inited = False

Size = 0
Common_Attribute = 16

with open(file_name,"rb") as NTFS:
    BootSector = NTFS.read(512)
    BytePerSetor = unpack('h',BootSector[11:13])[0]
    cluster = unpack('b', BootSector[13:14])
    SectorPerCluster = cluster[0]
    start = unpack('q', BootSector[48:56])
    MFT_Start = start[0] * SectorPerCluster * BytePerSetor

    # MFT 시작으로 이동
    NTFS.seek(MFT_Start)
    # 1024 byte를 읽음.
    MFT = NTFS.read(SectorPerCluster * BytePerSetor)

    # MFT Entry Header
    MFT_Entry_Header = MFT[:48]
    MFT_Fixup = unpack('h', MFT_Entry_Header[6:8])
    MFT_Entry_size = unpack('i', MFT_Entry_Header[28:32])
    FixupSize = (MFT_Fixup[0]+1)*2
    Attribute = 48+FixupSize
    ReadForSize = 8

    while True:
        # Fixup의 갯수 + 원본 * 바이트 수 2
        Entry = MFT[Attribute:Attribute+ReadForSize]
        # 각 Entry Type, Size 입력
        Entry_type = unpack('i', Entry[:4])[0]
        Entry_Size = unpack('i', Entry[4:8])[0]

        # FF FF FF FF
        if Entry_type == -1:
            break

        # 80(hex)이 아니면
        if Entry_type != 128:
            Attribute += Entry_Size

        else:
            Eni = MFT[Attribute:Attribute+Entry_Size]
            Attribute += Entry_Size
            RunList_Offset = unpack('h', Eni[Common_Attribute+16:Common_Attribute+18])[0]

            # 총 사이즈 의미
            Allocate_size = unpack('q', Eni[Common_Attribute+24: Common_Attribute+32])[0]

            # RunList가 여러 개 있을 경우 베이스를 저장하기 위해서 사용
            RunOffset = 0
            while True:

                RunList = Eni[RunList_Offset:RunList_Offset + 1].hex()
                if int(RunList) == 00:
                    break

                # RunList 읽기
                RunLen = RunList_Offset+1+int(RunList[1])
                RunOff = RunLen + int(RunList[0])

                # RunList Length, Offset 둘을 읽음
                RunList_Len = int.from_bytes(Eni[RunList_Offset + 1:RunLen], "little") * SectorPerCluster * BytePerSetor
                if not inited:
                    RunList_Off = int.from_bytes(Eni[RunLen:RunOff], "little")
                    RunOffInit = RunList_Off
                    inited = True
                else:
                    RunList_Off = int.from_bytes(Eni[RunLen:RunOff], "little") + RunOffInit

                # RunList Offset + Length(byte) + Offset(byte) + 1(own)
                RunList_Offset = RunList_Offset + int(RunList[1]) + int(RunList[0]) + 1
                Size += RunList_Len
                print(RunList_Off, RunList_Len)
            print(Size)