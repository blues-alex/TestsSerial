#!/usr/bin/env python3

from LMInterface import *
# from loguru import *

CHANNELS = 12

h = LMHandler()
h.SM(2)
for ch in range(CHANNELS):
    
    h.SC([0]*ch + [0.1] +[0]*(CHANNELS - ch - 1))
    print(f"Канал {ch+1} PWM: Нажмите ENTER что бы установить 23% в канале.")
    input()
    h.SC([0]*ch + [23] +[0]*(CHANNELS - ch - 1))
    print(f"Канал {ch+1} Аналог(23%) : Нажмите ENTER что бы перейти к следующему каналу.")
    input()

h.SM(1)
