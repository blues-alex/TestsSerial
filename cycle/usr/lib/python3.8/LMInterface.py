# by blues

from lmprotocol import *


class LMHandler(Controller):
    """docstring for LMHandler"""

    def __init__(self):
        super(LMHandler, self).__init__()

    def GH(self, mode=None):
        result = self.sendCommand(f'$GH{ENQ}', mode)
        return result

    def GT(self, *args, mode=None):
        return self.sendCommand(f'$GT{ENQ}', mode)

    def GV(self, *args, mode=None):
        return self.sendCommand(f'$GV{ENQ}', mode)

    def GM(self, *args, mode=None):
        return self.sendCommand(f'$GM{ENQ}', mode)

    def GC(self, *args, mode=None):
        return self.sendCommand(f'$GC{ENQ}', mode)

    def GA(self, *args, mode=None):
        return self.sendCommand(f'$GA{ENQ}', mode)

    def GS(self, *args, mode=None):
        return self.sendCommand(f'$GS{ENQ}', mode)

    def GP(self, *args, mode=None):
        return self.sendCommand(f'$GP{ENQ}', mode)

    def GL(self, *args, mode=None):
        return self.sendCommand(f'$GL{ENQ}', mode)

    def SM(self, mod=1, mode=None):
        """ 1 - режим отработки суточного графика (принимается при уже загруженном суточном графике),
            2 - режим ручного управления яркостью."""
        return self.sendCommand(f'$SM{mod}{ENQ}', mode)

    def ST(self, time, mode=None):
        """time format %H%M%d0%w%m%y ; for one item format is 00
        Формат команды: '$ ST dd dd dd dd dd dd ENQ HEX HEX '
        где "dd" значения
        часов, минут, дня месяца, дня недели, месяца, года
        """
        if (len(time) == 12) and (time.isdigit()):
            return self.sendCommand(f'$ST{time}{ENQ}', mode)
        else:
            print(f"{time} : is not valid time format!")
            return False

    def SL(self, const, mode=None):
        """значение калибровочной константы 000...031, 101..131, старшая единица
            означает положительное значение за собой.
        """
        return self.sendCommand(f'$SL{const}{ENQ}', mode)

    def SC(self, channels=[], mode=None):
        channels = [int(10000 - (chan * 100)) for chan in channels]
        if len(channels) < 10:
            channels = channels + [10000] * (10 - len(channels))
        command = f"$SC00{US}{US.join([f'{c:05d}' for c in channels])}{ENQ}"
        return self.sendCommand(command, mode)

    def SP(self, freqDivider, mode=None):
        if freqDivider <= 65535:
            command = f"{freqDivider:05d}{ENQ}"
            return self.sendCommand(command, mode)
        else:
            print(f'{freqDivider}: is not valid data.')
            return False

    def writeCycle(self, cycle, mode=None):
        """cycle in format:
        one point = [time in '%H%M', ch1%, ch%...]
        cycle is points list:
        [[time in '%H%M' , ch1%, ch%...]..]
        as:
        [['0200', 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        ['1240', 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        ['2200', 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]]
        """
        cycle = [
            [point[0]] + [int(10000 - (chan * 100))
                          for chan in point[1:]] for point in cycle]
        return self.sendCycle(cycle, mode)
