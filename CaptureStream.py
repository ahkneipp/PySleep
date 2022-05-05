import serial
import sys

class CaptureStream:
    def __init__(self, serial_device, baud_rate = 115200):
        self.recordBuffer = []
        self.serObj = serial.Serial(serial_device, baud_rate)

    def __iter__(self):
        return self

    def __next__(self):
        return self.get_next()

    def peek(self):
        if self.available():
            return self.recordBuffer[0]
        else:
            return None

    def get_next(self, blocking=True):
        if blocking:
            while not self.available():
                self.read_serial()
        if not self.available():
            return None
        return self.recordBuffer.pop(0)

    def available(self):
        return len(self.recordBuffer)

    def read_serial(self):
        t_line = self.serObj.readline().decode('utf-8')
        #Started in the middle of a chunk and didn't catch the start
        if "T_us" not in t_line:
            t_line = self.serObj.readline().decode('utf-8')
        f_line = self.serObj.readline().decode('utf-8')
        record = self.serial_line_to_record(t_line, f_line)
        # We're out of phase, grab the frequency for the time line we accidentally read and try again
        if record is None:
            record = self.serial_line_to_record(f_line, self.serObj.readline().decode('utf-8'))
        self.recordBuffer.append(record)
        pass

    def serial_line_to_record(self, t_line, f_line):
        rval = {}
        t_fields = t_line.split(";")
        f_fields = f_line.split(";")
        t_T = int(t_fields[0].split('=')[1])
        f_T = int(f_fields[0].split('=')[1])
        # We're out of phase
        if t_T != f_T:
            return None
        T = t_T/1000000
        chan = int(t_fields[1].split('=')[1])
        N = int(t_fields[3].split('=')[1])
        Ts = int(t_fields[4].split('=')[1])/1000000
        t_data = [float(x.strip()) for x in t_fields[5].split(',')]
        f_data = [float(x.strip()) for x in f_fields[5].split(',')]
        t = [x*Ts for x in range(t_T, t_T + N)]
        f = [x*(1/(Ts*N)) for x in range((N//2)+1)]
        rval['T'] = T
        rval['Channel'] = chan
        rval['N'] = N
        rval['Ts'] = Ts
        rval['Time Data'] = t_data
        rval['Freq Data'] = f_data
        rval['Time Axis'] = t
        rval['Freq Axis'] = f
        #rval['Raw Time Line'] = t_line
        #rval['Raw Freq Line'] = f_line
        return rval

    def close(self):
        if self.serObj is not None:
            self.serObj.close()

if __name__ == '__main__':
    cs = CaptureStream("/dev/ttyACM0")
    for record in cs:
        print(f"Got record with timestamp {record['T']}!")
        #print(record['Raw Time Line'])
        #print(record['Raw Freq Line'])

