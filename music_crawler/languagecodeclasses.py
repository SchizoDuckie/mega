from enum import Enum


class Language(Enum):
    ZH_TW = 297
    EN = 390
    JA = 308
    KO = 314
    TW = 304
    ZH_HK = 320
    ALL = 999

    def __str__(self):
        return str(self.value)


class Category(Enum):
    ZH_TW = 1
    EN = 2
    TW = 4
    KO_JA = 8
    ZH_HK = 16
    TV = 32
    MOVIE = 64
    JAZZ = 256
    CLASSIC = 512
    ELEC = 1024
    ALL = 999

    def __str__(self):
        return str(self.value)


class Region(Enum):
    tw = 1
    hk = 2
    sg = 3
    cn = 4

    def __str__(self):
        return str(self.value)


class LanguageCode(Enum):
    ZH_TW = 297
    EN = 390
    JA = 308
    KO = 314
    TW = 304
    ZH_HK = 320
    ALL = 999

    def __str__(self):
        return str(self.value)