import sys
import os
import csv
from CaptureStream import CaptureStream

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <directory>")
        sys.exit(1)
    if not os.path.isdir(sys.argv[1]) and not os.path.isfile(sys.argv[1]):
        os.mkdir(sys.argv[1])
    cs = CaptureStream("/dev/ttyACM0")
    for record in cs:
        allRecords = [{'t':record['Time Axis'][i],'td':record['Time Data'][i],'f':record['Freq Axis'][i],'fd':record['Freq Data'][i]} for i in range(len(record['Freq Axis']))]
        extraTimeRecords = [{'t':record['Time Axis'][i],'td':record['Time Data'][i]} for i in range(len(record['Freq Axis'])+1,len(record['Time Axis']))]
        with open(os.path.join(sys.argv[1],f"{int(record['T'])}.csv"),'w', newline='') as file:
            cfile = csv.DictWriter(file,['t','td','f','fd'])
            cfile.writeheader()
            cfile.writerows(allRecords)
            cfile.writerows(extraTimeRecords)
        print(f"Wrote record for T = {record['T']}")



