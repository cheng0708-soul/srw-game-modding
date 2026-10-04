#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AR2 v2 (PAR2/GS2v2) 解码器 — 移植自 pyriell/omniconvert 的 ar2.c (misfire RE)
用途: 把日站"机体变更码"(如 3C6CC12C 1456E7A6) 解码成 PCSX2 可用的原始码。
输出格式: 解码后 8位地址 + 8位值 (第一nibble为码类型: 0=8bit 1=16bit 2=32bit 7=位操作)
"""
import sys, re, pathlib

TBL = [
 [0x00,0x1F,0x9B,0x69,0xA5,0x80,0x90,0xB2,0xD7,0x44,0xEC,0x75,0x3B,0x62,0x0C,0xA3,0xA6,0xE4,0x1F,0x4C,0x05,0xE4,0x44,0x6E,0xD9,0x5B,0x34,0xE6,0x08,0x31,0x91,0x72],
 [0x00,0xAE,0xF3,0x7B,0x12,0xC9,0x83,0xF0,0xA9,0x57,0x50,0x08,0x04,0x81,0x02,0x21,0x96,0x09,0x0F,0x90,0xC3,0x62,0x27,0x21,0x3B,0x22,0x4E,0x88,0xF5,0xC5,0x75,0x91],
 [0x00,0xE3,0xA2,0x45,0x40,0xE0,0x09,0xEA,0x42,0x65,0x1C,0xC1,0xEB,0xB0,0x69,0x14,0x01,0xD2,0x8E,0xFB,0xFA,0x86,0x09,0x95,0x1B,0x61,0x14,0x0E,0x99,0x21,0xEC,0x40],
 [0x00,0x25,0x6D,0x4F,0xC5,0xCA,0x04,0x39,0x3A,0x7D,0x0D,0xF1,0x43,0x05,0x71,0x66,0x82,0x31,0x21,0xD8,0xFE,0x4D,0xC2,0xC8,0xCC,0x09,0xA0,0x06,0x49,0xD5,0xF1,0x83],
]

def swab32(k):
    return ((k & 0xFF) << 24) | ((k >> 8 & 0xFF) << 16) | ((k >> 16 & 0xFF) << 8) | ((k >> 24) & 0xFF)

def nibble_flip(b):
    return ((b << 4) | (b >> 4)) & 0xFF

def ar2decrypt(code, typ, seed):
    code &= 0xFFFFFFFF
    if typ == 7:
        if seed & 1:
            typ = 1
        else:
            return (~code) & 0xFFFFFFFF
    tmp = [(code >> (8*i)) & 0xFF for i in range(4)]  # tmp[0]=LSB .. tmp[3]=MSB
    s = seed & 0x1F
    s1 = (seed + 1) & 0x1F
    s2 = (seed + 2) & 0x1F
    s3 = (seed + 3) & 0x1F
    if typ == 0:
        tmp[3] ^= TBL[0][s]; tmp[2] ^= TBL[1][s]; tmp[1] ^= TBL[2][s]; tmp[0] ^= TBL[3][s]
    elif typ == 1:
        tmp[3] = nibble_flip(tmp[3]) ^ TBL[0][s]
        tmp[2] = nibble_flip(tmp[2]) ^ TBL[2][s]
        tmp[1] = nibble_flip(tmp[1]) ^ TBL[3][s]
        tmp[0] = nibble_flip(tmp[0]) ^ TBL[1][s]
    elif typ == 2:
        tmp[3] = (tmp[3] + TBL[0][s]) & 0xFF
        tmp[2] = (tmp[2] + TBL[1][s]) & 0xFF
        tmp[1] = (tmp[1] + TBL[2][s]) & 0xFF
        tmp[0] = (tmp[0] + TBL[3][s]) & 0xFF
    elif typ == 3:
        tmp[3] = (tmp[3] - TBL[3][s]) & 0xFF
        tmp[2] = (tmp[2] - TBL[2][s]) & 0xFF
        tmp[1] = (tmp[1] - TBL[1][s]) & 0xFF
        tmp[0] = (tmp[0] - TBL[0][s]) & 0xFF
    elif typ == 4:
        tmp[3] = ((tmp[3] ^ TBL[0][s]) + TBL[0][s]) & 0xFF
        tmp[2] = ((tmp[2] ^ TBL[3][s]) + TBL[3][s]) & 0xFF
        tmp[1] = ((tmp[1] ^ TBL[1][s]) + TBL[1][s]) & 0xFF
        tmp[0] = ((tmp[0] ^ TBL[2][s]) + TBL[2][s]) & 0xFF
    elif typ == 5:
        tmp[3] = ((tmp[3] - TBL[1][s]) ^ TBL[0][s]) & 0xFF
        tmp[2] = ((tmp[2] - TBL[2][s]) ^ TBL[1][s]) & 0xFF
        tmp[1] = ((tmp[1] - TBL[3][s]) ^ TBL[2][s]) & 0xFF
        tmp[0] = ((tmp[0] - TBL[0][s]) ^ TBL[3][s]) & 0xFF
    elif typ == 6:
        tmp[3] = (tmp[3] + TBL[0][s]) & 0xFF
        tmp[2] = (tmp[2] - TBL[1][s1]) & 0xFF
        tmp[1] = (tmp[1] + TBL[2][s2]) & 0xFF
        tmp[0] = (tmp[0] - TBL[3][s3]) & 0xFF
    else:
        pass
    return tmp[0] | (tmp[1] << 8) | (tmp[2] << 16) | (tmp[3] << 24)

def ar2encrypt(code, typ, seed):
    code &= 0xFFFFFFFF
    if typ == 7:
        if seed & 1:
            typ = 1
        else:
            return (~code) & 0xFFFFFFFF
    tmp = [(code >> (8*i)) & 0xFF for i in range(4)]
    s = seed & 0x1F
    s1 = (seed + 1) & 0x1F
    s2 = (seed + 2) & 0x1F
    s3 = (seed + 3) & 0x1F
    if typ == 0:
        tmp[3] ^= TBL[0][s]; tmp[2] ^= TBL[1][s]; tmp[1] ^= TBL[2][s]; tmp[0] ^= TBL[3][s]
    elif typ == 1:
        tmp[3] = nibble_flip(tmp[3] ^ TBL[0][s])
        tmp[2] = nibble_flip(tmp[2] ^ TBL[2][s])
        tmp[1] = nibble_flip(tmp[1] ^ TBL[3][s])
        tmp[0] = nibble_flip(tmp[0] ^ TBL[1][s])
    elif typ == 2:
        tmp[3] = (tmp[3] - TBL[0][s]) & 0xFF
        tmp[2] = (tmp[2] - TBL[1][s]) & 0xFF
        tmp[1] = (tmp[1] - TBL[2][s]) & 0xFF
        tmp[0] = (tmp[0] - TBL[3][s]) & 0xFF
    elif typ == 3:
        tmp[3] = (tmp[3] + TBL[3][s]) & 0xFF
        tmp[2] = (tmp[2] + TBL[2][s]) & 0xFF
        tmp[1] = (tmp[1] + TBL[1][s]) & 0xFF
        tmp[0] = (tmp[0] + TBL[0][s]) & 0xFF
    elif typ == 4:
        tmp[3] = ((tmp[3] - TBL[0][s]) ^ TBL[0][s]) & 0xFF
        tmp[2] = ((tmp[2] - TBL[3][s]) ^ TBL[3][s]) & 0xFF
        tmp[1] = ((tmp[1] - TBL[1][s]) ^ TBL[1][s]) & 0xFF
        tmp[0] = ((tmp[0] - TBL[2][s]) ^ TBL[2][s]) & 0xFF
    elif typ == 5:
        tmp[3] = ((tmp[3] ^ TBL[0][s]) + TBL[1][s]) & 0xFF
        tmp[2] = ((tmp[2] ^ TBL[1][s]) + TBL[2][s]) & 0xFF
        tmp[1] = ((tmp[1] ^ TBL[2][s]) + TBL[3][s]) & 0xFF
        tmp[0] = ((tmp[0] ^ TBL[3][s]) + TBL[0][s]) & 0xFF
    elif typ == 6:
        tmp[3] = (tmp[3] - TBL[0][s]) & 0xFF
        tmp[2] = (tmp[2] + TBL[1][s1]) & 0xFF
        tmp[1] = (tmp[1] - TBL[2][s2]) & 0xFF
        tmp[0] = (tmp[0] + TBL[3][s3]) & 0xFF
    else:
        pass
    return tmp[0] | (tmp[1] << 8) | (tmp[2] << 16) | (tmp[3] << 24)

class AR2:
    def __init__(self, key=0x05100518):
        self.set_seed(key)
    def set_seed(self, key):
        k = swab32(key)
        self.seed = [k & 0xFF, (k >> 8) & 0xFF, (k >> 16) & 0xFF, (k >> 24) & 0xFF]
    def dec_pair(self, w1, w2):
        return (ar2decrypt(w1, self.seed[0], self.seed[1]),
                ar2decrypt(w2, self.seed[2], self.seed[3]))

def find_initial(master=(0xEC878304, 0x1434A4A4)):
    cands = [0x05100518, 0xEC878304, 0x1434A4A4, 0x0E3C7DF2, 0x1853E59E,
             0xDEADFACE, 0x00000000, 0xFFFFFFFF, 0x18051005]
    for c in cands:
        a = AR2(c)
        aa, vv = a.dec_pair(*master)
        print("  key=%08X -> master addr=%08X val=%08X %s" % (c, aa, vv, "<== DEADFACE HIT" if aa == 0xDEADFACE else ""))
        if aa == 0xDEADFACE:
            return c, vv
    return None, None

DEMO = [
 ("master", "EC878304 1434A4A4"),
 ("G-3", "3C6CC12C 1456E7A6"),
 ("CharZaku", "3C6CC02C 1456E7A6"),
 ("G-3 vE7A8", "3C6CC12C 1456E7A8"),
 ("G-3 vE7AC", "3C6CC12C 1456E7AC"),
 ("G-3 vE7A1", "3C6CC12C 1456E7A1"),
 ("Sazabi E7A6", "3C6CF32C 1456E7A6"),
 ("Sazabi E7A8", "3C6CF32C 1456E7A8"),
 ("Sazabi E7AC", "3C6CF32C 1456E7AC"),
 ("Sazabi E7A1", "3C6CF32C 1456E7A1"),
 ("Bigina L1", "3C6CFA2C 1456E7A6"),
 ("Bigina L2", "3C6CFA31 1456E74D"),
 ("Bigina L3", "4C6CFA26 1456E5F5"),
 ("Bigina L4", "3C6CFA2E 1456E74E"),
 ("Bastole", "3C6C0A2C 1456E7A6"),
 ("Linek", "3C6C0E2C 1456E7A6"),
 ("GreatM E7A6", "3C6C0F2C 1456E7A6"),
 ("Zambot3", "3C6C172C 1456E7A6"),
 ("Kurojishi", "3C6CB72C 1456E7A6"),
 ("Dancouga", "3C6C2F2C 1456E7A6"),
 ("Texasmac?", "3C6C232C 1456E7A6"),
 ("Dunbine-Td", "3C6C042C 1456E7A6"),
 ("Bilbine", "3C6C062C 1456E7A6"),
 ("AmuroSuit?", "3C6AA530 1456E7A6"),
 ("QuatroSuit?", "3C6A9F30 1456E7A6"),
]

def main():
    print("== step1: find initial AR2 key (candidates) ==")
    k0, newkey = find_initial()
    if k0 is None:
        print("NO CANDIDATE MATCHED — need source dig.")
        return 1
    print("\n== step2: decrypt demo list (seed chain: initial %08X -> master -> %08X) ==" % (k0, newkey))
    a = AR2(k0)
    for label, s in DEMO:
        w1, w2 = (int(s.split()[0], 16), int(s.split()[1], 16))
        d1, d2 = a.dec_pair(w1, w2)
        if d1 == 0xDEADFACE:
            a.set_seed(d2)
            print("%-12s %s  =>  DEADFACE, new seed = %08X" % (label, s, d2))
            continue
        e1 = ar2encrypt(d1, a.seed[0], a.seed[1])
        e2 = ar2encrypt(d2, a.seed[2], a.seed[3])
        ok = "OK" if (e1 == w1 and e2 == w2) else "RT-MISMATCH"
        print("%-12s %s  =>  %08X %08X  [%s]" % (label, s, d1, d2, ok))
    return 0

if __name__ == "__main__":
    sys.exit(main())
