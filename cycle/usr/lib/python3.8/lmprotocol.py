# by blues

# by blues

import serial
import time
# import curses


TIMEOUT = 1


SOH = '\x01'
# служит для обозначения начала заголовка файла
STX = '\x02'
# служит для обозначения начала передачи тела файла.
ETX = '\x03'
# служит для обозначения конца передачи тела файла и начала передачи контрольной суммы файла.
EOT = '\x04'
# служит для обозначения конца передачи файла.
ENQ = '\x05'
#  служит для обозначения конца передачи команды/запроса.
ACK = '\x06'
#  служит для подтверждения корректного приема запроса или файла контроллером.
BEL = '\x07'
# служит для обозначения истечения времени ожидания следующего байта при приеме.
WAIT = '\x11'
# служит для обозначения состояния обработки последней полученой команды/запроса
# символы в ответ на которые получен BEL игнорируются.

DONE = '\x12'
# обозначение успешного выполнения последней полученой команды/запроса.
FAIL = '\x13'
# служит для обозначения невозможности выполнения последней полученой команды/запроса.
NAK = '\x15'
# служит для индикации некорректного приема команды/запроса или файла контроллером
# (тайм-аут передачи файла, либо ошибка контрольной суммы, либо неожидаемый символ).

RS = '\x1e'
#  служит для разделения записей точек в теле файла.
US = '\x1f'
#  служит для разделения полей записи точки в теле файла.
# 0x06, 0x07, 0x11, 0x12, 0x13, 0x15


class Controller:

    def __init__(self, port='/dev/ttyUSB0'):
        self.sr = serial.Serial(port)
        self.sr.TIMEOUT = TIMEOUT
        self.sr.timeout = TIMEOUT
        self.sr.baudrate = 9600

    def byteswritting(self, scr, command):
        n = 0
        flag = True
        scr.clear()
        scr.timeout(10)
        done = b''
        for b in command:
            if flag:
                t = time.time()
                while time.time() <= (t + 3):
                    scr.addstr(1, 15, f'Pres any key: {3 - (time.time()-t):.2f} sek remaining.')
                    scr.addstr(2, 15, f'writes: {done}')
                    if scr.getch() != -1:
                        self.sr.write(bytes([b]))
                        done += bytes([b])
                        scr.addstr(3, 4, command[:n + 1].decode('utf-8', 'ignore'))
                        scr.addstr(4, 4, f"Remaining bytes: {len(command)-(n+1)}")
                        n += 1
                        break
                    if (time.time() - 3) >= t:
                        flag = False
            else:
                break

    def openPort(self):
        if self.sr.isOpen():
            pass
        else:
            self.sr.open()

    def closePort(self):
        if self.sr.isOpen():
            self.sr.close()

    def CRC16(self, s):
        poly = 0x1021
        Init = 0xffff
        crc = Init
        for b in s:
            crc ^= (ord(b) << 8)
            for _ in range(8):
                if (crc & 0x8000):
                    crc = (crc << 1) ^ poly
                else:
                    crc = (crc << 1)
        Hex = '%04x' % (crc & Init)
        return self.crcToBytes(Hex)

    def crcToBytes(self, mess):
        return bytes.fromhex(mess[:2]) + bytes.fromhex(mess[2:])

    def crcAdd(self, mess):
        return bytes(mess, 'utf-8') + self.CRC16(mess)

    def byteToStr(self, mess):
        return mess.decode('utf-8', 'replace')

    def checkData(self, data):
        if len(data):
            result = {}
            if data[0] == 35:
                result['answer'] = data[1:3]
                data, crc = data[:-2], data[-2:]
                if self.CRC16(self.byteToStr(data)) == crc:
                    result['mess'] = data[3:-1]
                    result['check'] = True
            else:
                result['answer'] = ''
                data, crc = data[:-2], data[-2:]
                if self.CRC16(self.byteToStr(data)) == crc:
                    result['mess'] = data
                    result['check'] = True
                else:
                    result['mess'] = data
                    result['check'] = False
        else:
            result = False
        return result

    def writeMessage(self, mess, mode=None):
        # print(f'Mode = {mode}')
        # if mode == 'b':
            # pass
            # # scr = curses.initscr()
            # # curses.noecho()
            # # curses.curs_set(0)
        # else:
            # pass
            # # scr = None
        # if scr:
            # curses.wrapper(self.byteswritting, mess)
        # else:
        self.sr.write(mess)
        return self.readAnswer()

    def readAnswer(self):
        result = b''
        timeout = time.time()
        data = False
        while time.time() - timeout <= TIMEOUT:
            if self.sr.readable():
                result += self.sr.read(1)
            else:
                continue
            if len(result) >= 3:
                try:
                    if result[-3] in [0x07, 0x11, 0x13, 0x15]:
                        print(f'Break reading: controller return {result}\nIn str result: {self.byteToStr(result)}')
                        data = False
                        break
                except Exception:
                    pass
                if result[-3] in [0x06, 0x12]:
                    data = self.checkData(result)
                    break
                else:
                    continue
        return data

    def GetHash(self):
        result = self.sendCommand(f'$GH{ENQ}')
        if result:
            return result['mess']
        else:
            return False

    def sendCommand(self, message, mode=None):
        message = self.crcAdd(message)
        return self.writeMessage(message, mode)

    def sendCycle(self, cycle, mode=None):  # list points in format [time in min, channels vals, .. ]
        if self.sendCommand(f"{SOH}{len(cycle):02}{STX}", mode):
            for point in cycle:
                Time, point = point[0], point[1:]
                point = [f"{chan:05}" for chan in point] + ['10000'] * (10 - len(point))
                message = self.crcAdd(f"{Time}{US}{US.join(point)}{RS}")
                if not self.writeMessage(message, mode):
                    return False
            if self.writeMessage(b'\x03', mode) and self.writeMessage(b'\x04', mode):
                return True
