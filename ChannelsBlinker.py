#!/usr/bin/python3

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
    # print(data)
    return data


def GetHash():
    result = sendCommand(f'$GH{ENQ}')
    if result:
        return result['mess']
    else:
        return False


def sendCommand(message):
    message = crcAdd(message)
    # print(message)
    if len(message) > 20:
        print([i for i in message[6:-3].split(b'\x1f')])
    else:
        # print(message)
        pass
    return writeMessage(message)


def CheckChannels():
    sendCommand(f'$SM2{ENQ}')
    for i in range(12):
        channels = ['10000' for c in range(11)]
        for n in range(10):
            mess = "\x1f".join(channels[:i] + [f"{10000-n:05}"] + channels[i:])
            sendCommand(f'$SC00\x1f{mess}{ENQ}')
            # time.sleep(0.05)
    sendCommand(f'$SM1{ENQ}')


def main():
    while True:
        time.sleep(0.8)
    # with open('/tmp/logs/controller_version.log', 'w') as fw:
        # fw.write(repr(sendCommand(f'$GV{ENQ}')))
        sendCommand(f'$SM2{ENQ}')
    # mess = '\x1f'.join(['10000' for i in range(12)])
    # sendCommand(f"$SCff\x1f{mess}{ENQ}")
    # for n in range(100):
        # sendCommand(f"$SCff\x1f{mess}{ENQ}")
        print(sendCommand(f'$GV{ENQ}'))
        channels = ['10000'] * 11
        for i in range(12):
            mess = "\x1f".join(channels[:i]+ [f"00990"] + channels[i:])
            print(sendCommand(f"$SC01\x1f{mess}{ENQ}"))
            print(sendCommand(f'$GC{ENQ}')['mess'].split(b'\x1f'))
            time.sleep(0.1)
        sendCommand(f"$SM1{ENQ}")
    # CheckChannels()

if __name__ == '__main__':
    main()
