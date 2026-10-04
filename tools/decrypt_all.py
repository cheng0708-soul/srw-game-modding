#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Bulk decrypt ALL code lines found in collected sources, using the AR2 v2 base seed
# (validated: master EC878304 1434A4A4 -> F01000DC 0022C307; money 1CB46B60 17E9C729 -> 2025E838 05F5E09C)
import re, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from converter import AR2

BASE = pathlib.Path("/Users/wangluke/.hermes/cache/scratch/impact-cheats")
FILES = ["ameblo-2.txt", "ameblo-3.txt", "ameblo-4.txt", "ameblo-5.txt", "ameblo-impact.txt",
         "5ch.txt", "5ch2.txt", "5ch3.txt", "newwise-thread.txt",
         "teruyuka-impact.txt",
         "cheatroom-120.txt", "cheatroom-121.txt", "cheatroom-122.txt"]
RANGES = {"5ch2.txt": (700, 2100), "5ch3.txt": (1050, 1550), "5ch.txt": (1200, 2150)}
CODE = re.compile(r"\b([0-9A-Fa-f]{8})[\s\u3000]+([0-9A-Fa-f]{8})\b")

def main():
    a = AR2(0x05100518)
    seen = {}
    for fn in FILES:
        p = BASE / fn
        if not p.exists():
            continue
        L = p.read_text(encoding="utf-8", errors="replace").splitlines()
        lo, hi = RANGES.get(fn, (1, len(L)))
        cnt = 0
        for i, line in enumerate(L[lo-1:hi], lo):
            for m in CODE.finditer(line):
                w1, w2 = int(m.group(1), 16), int(m.group(2), 16)
                seen.setdefault((w1, w2), []).append("%s:%d" % (fn, i))
                cnt += 1
        print("# scanned %-22s hits=%d" % (fn, cnt))
    print("## unique codes:", len(seen))
    print("## note: for unit 'flag' codes the pattern is: <record+4> <- 01  (byte write)")
    for (w1, w2), tags in sorted(seen.items(), key=lambda it: it[0][0]):
        d1, d2 = a.dec_pair(w1, w2)
        print("%08X %08X => %08X %08X [%s]" % (w1, w2, d1, d2, ";".join(sorted(set(tags))[:2])))
    return 0

if __name__ == "__main__":
    sys.exit(main())
