# token = "5348165766:AAHJ2NJwhg-p1qk0BHLQS63u3p-Nejq8Th8"
#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sys import platform

if platform == 'win32': # тестовый
    oslink = 'C:/vscode/rpg-tg-bot/'
    token = '5348165766:AAHJ2NJwhg-p1qk0BHLQS63u3p-Nejq8Th8' 
elif platform == 'linux': # продакшн
    oslink = './'
    token = '1506687912:AAF8VPByboL3t8vXGNK4k3D66SnW8B1pCuI' 
else:
    print("THIS PLATFORM DON'T SUPPORTED")
# token = '1506687912:AAF8VPByboL3t8vXGNK4k3D66SnW8B1pCuI' 
provider_token = '401643678:TEST:ebea2aab-ff87-47bc-b251-0672854602e2'
moders = [254407586,895501631]