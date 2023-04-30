# TestsSerial
* Зависимости:
    - PySerial
* В папке cycle/usr/bin находятся скрипты проверки
* В папке cycle/usr/ находятся модули необходимые для работы (скопировать файлы модулей в папку модулей дистрибутива python)

* В файле cycle/Controller'sTests.pdf Частичное описание работы скриптов
* Для установки активного serial порта необходимо указать порт в модуле lmprotocol.py
```python
...
class Controller:

    def __init__(self, port='/dev/ttyUSB0'):
        self.sr = serial.Serial(port)
        self.sr.TIMEOUT = TIMEOUT
        self.sr.timeout = TIMEOUT
        self.sr.baudrate = 9600
...
```
