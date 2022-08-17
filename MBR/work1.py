import sys
from struct import *

if len(sys.argv) != 2:
    print("Insufficient arguments\n")
    print("syntax : work1 <FileName>\n")
    print("sample: work1 test.dd\n")
    sys.exit(-1)

file_name = sys.argv[1]
sector = 512
partition_size = 16
EBR_Start = 0
inner_EBR_List = []
initialed = False

Partition_Types = {
    # "00": "Free",
    "01": "FAT12",
    "04": "FAT16",
    # "05": "EBR",
    "07": "NTFS",
    "0B": "CHS FAT32",
    "0C": "LBA FAT32"
}

with open(file_name,"rb") as mbr:
    MBR = mbr.read(sector)
    boot_code = MBR[0:446]
    partition_Table_Entry = MBR[446:510]
    signature = MBR[510:512]

    partition_List = [partition_Table_Entry[:partition_size], partition_Table_Entry[16:32],
                      partition_Table_Entry[32:48], partition_Table_Entry[48:64]]

    while partition_List:
        entry = partition_List.pop(0)
        boot = entry[:1]
        Partition_type = entry[4:5].hex()
        if Partition_type in Partition_Types:
            start = unpack('<I', entry[8:12])
            size = unpack('<I', entry[12:16])
            Partition_size = size[0] * sector
            if not initialed:
                Partition_start = start[0] * sector
            else:
                Partition_start = inner_EBR_List.pop(0) + start[0] * sector
            print(Partition_Types[Partition_type], Partition_start, Partition_size)
        elif Partition_type == '05':
            # print(Partition_Types[Partition_type])
            start = unpack('<I', entry[8:12])
            inner_EBR_Start = 0
            # EBR을 처음으로 시작했다면 시작 포인트를 전역변수에 저장 아니면
            # 전역변수 값에서 값을 더해 파일 읽기 헤더를 움직인다.
            if not initialed:
                EBR_Start = EBR_Start + start[0] * sector
                inner_EBR_Start = EBR_Start
                initialed = True
            else:
                inner_EBR_Start = EBR_Start + start[0] * sector
            inner_EBR_List.append(inner_EBR_Start)

            mbr.seek(inner_EBR_Start)
            EBR = mbr.read(sector)
            partition_List.append(EBR[446:462])
            partition_List.append(EBR[462:478])
            partition_List.append(EBR[478:494])
            partition_List.append(EBR[494:510])
        else:
            continue
