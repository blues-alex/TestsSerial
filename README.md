# TestsSerial
* Зависимости:
    - PySerial
    - poetry
    - plotly
    - loguru
* В папке Test/usr/bin находятся скрипты проверки
* В папке Test/usr/lib/pythonV.V/ находятся модули необходимые для работы (скопировать файлы модулей в папку модулей дистрибутива python)

* В файле Test/Controller'sTests.pdf Частичное описание работы скриптов
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
## Установка
* В корневой папке репозитория
```sh
python -m pip install pip
pip install poetry
poetry install
```

## Для запуска теста цикла необходимо:
* Скопировать модули из папки Test/usr/lib в папку .../site-packages/ установленного python
* Вписать свой компорт в модуль lmprotocol.py (как показано выше)
* Изменить путь записи бинарного файла цикла в модуле lmprotocol.py
```python
cycle_bin = '/tmp/currentCycle.bin'
```
* Перейти в папку Test/usr/bin и в файлах CheckCycle_300.py и CheckCycleView.py изменить пути записи json файлов цикла (для одноименных пути должны совпадать), теста и html  файла графика:
```python
# CheckCycle_300.py
DELTA_LOG = '/tmp/delta_interpolations.json'
CYCLE_LOG = '/tmp/cycle.json'

# CheckCycleView.py
DELTA_LOG = '/tmp/delta_interpolations.json'
CYCLE_LOG = '/tmp/cycle.json'
TEST_HTML = '/tmp/test_meassures.html'
```
* После этого из папки Test/usr/bin запустить файл CheckCycle_300.py
```sh
python CheckCycle_300.py
```
* По мере необходимости запускать (из другого окна консоли) файл CheckCycleView.py (служит для актуализации html графика)
```sh
python CheckCycleView.py
```
