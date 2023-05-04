#!/usr/bin/python3

# by blues
# script for check channels

import serial
import time

TIMEOUT = 1

US = '\x1f'
ENQ = '\x05'

sr = serial.Serial('/dev/ttyUSB0')
sr.timeout = TIMEOUT
sr.baudrate = 9600


def CRC16(s):
    poly = 0x1021
    Init = 0xffff
    # xor = 0x0001
    crc = Init
    for b in s:
        crc ^= (ord(b) << 8)
        for _ in range(8):
            if (crc & 0x8000):
                crc = (crc << 1) ^ poly
            else:
                crc = (crc << 1)
    Hex = '%04x' % (crc & Init)
    return crcToBytes(Hex)


def crcToBytes(mess):
    return bytes.fromhex(mess[:2]) + bytes.fromhex(mess[2:])


def crcAdd(mess):
    return bytes(mess, 'utf-8') + CRC16(mess)


def byteToStr(mess):
    return mess.decode('utf-8', 'replace')


def checkData(data):
    if len(data):
        result = {}
        if data[0] == 35:
            result['answer'] = data[1:3]
            data, crc = data[:-2], data[-2:]
            if CRC16(byteToStr(data)) == crc:
                result['mess'] = data[3:-1]
                result['check'] = True
        else:
            result['answer'] = ''
            data, crc = data[:-2], data[-2:]
            if CRC16(byteToStr(data)) == crc:
                result['mess'] = data
                result['check'] = True
            else:
                result['mess'] = data
                result['check'] = False
    else:
        result = False
    return result


def writeMessage(mess):
    result = b''
    sr.write(mess)
    timeout = time.time()
    data = False
    while time.time() - timeout <= TIMEOUT:
        result += sr.read(1)
        if len(result) >= 3:
            try:
                if result[-3] in [21, 19, 7]:
                    print(f'Break reading: controller return {byteToStr(result)}')
                    data = False
                    break
            except Exception:
                pass
            if result[-3] in [6, 18]:
                data = checkData(result)
                break
            else:
                continue
    return data


def GetHash():
    result = sendCommand(f'$GH{ENQ}')
    if result:
        return result['mess']
    else:
        return False


def sendCommand(message):
    message = crcAdd(message)
    return writeMessage(message)


def CheckChannels():
    sendCommand(f'$SM2{ENQ}')
    # for i in range(7):
    #     channels = ['10000' for c in range(12)]
    #     for n in range(50):
    #         mess = "\x1f".join(channels[:i] + [f"{10000-(n*1):05}"] + channels[i:])
    #         sendCommand(f'$SC00\x1f{mess}{ENQ}')
    # mess = "\x1f".join(["09999" for c in range(12)])
    # sendCommand(f'$SC00\x1f{mess}{ENQ}')
    # time.sleep(3)
    mess = "\x1f".join(["10000" for c in range(12)])
    sendCommand(f'$SC00\x1f{mess}{ENQ}')
    time.sleep(3)
    for ch in range(10000, 9990, -1):
        val = f"{ch:05}"
        print(val)
        mess = "\x1f".join([val for c in range(12)])
        sendCommand(f'$SC00\x1f{mess}{ENQ}')
        time.sleep(1)
    mess = "\x1f".join(["10000" for c in range(12)])
    sendCommand(f'$SC00\x1f{mess}{ENQ}')
    time.sleep(3)
    sendCommand(f'$SM1{ENQ}')


def main():
    CheckChannels()


if __name__ == '__main__':
    main()
