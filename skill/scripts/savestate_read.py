#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""读取 PCSX2 即时档(.p2s) 里 EE 内存的指定地址。
用法: python3 savestate_read.py <file.p2s> <addr> [<addr> ...]
地址用 0x 前缀（如 0x00FD3E04）。输出每个地址的字节值 + 后续 15 字节窗口。
原理: .p2s = ZIP 容器; eeMemory.bin 条目为 zstd(zip方法93) — macOS 自带 Python3.9
的 zipfile 不支持, 故手动切 raw 再调 /opt/homebrew/bin/zstd 解压。
"""
import sys, os, struct, subprocess, tempfile


def extract_ee_memory(p2s):
    import zipfile
    z = zipfile.ZipFile(p2s)
    target = None
    for info in z.infolist():
        if info.filename == "eeMemory.bin":
            target = info
            break
    if target is None:
        raise SystemExit("eeMemory.bin not found in " + p2s)
    with open(p2s, "rb") as f:
        f.seek(target.header_offset)
        hdr = f.read(30)
        nlen, elen = struct.unpack("<HH", hdr[26:30])
        f.seek(target.header_offset + 30 + nlen + elen)
        raw = f.read(target.compress_size)
    if raw[:4] == b"\x28\xb5\x2f\xfd":
        with tempfile.NamedTemporaryFile(suffix=".zst", delete=False) as tf:
            tf.write(raw)
            tmp = tf.name
        out = tmp + ".bin"
        r = subprocess.run(["/opt/homebrew/bin/zstd", "-d", "-f", tmp, "-o", out],
                           capture_output=True, text=True)
        if not os.path.exists(out):
            raise SystemExit("zstd failed: " + r.stderr.strip())
        data = open(out, "rb").read()
        os.unlink(tmp)
        os.unlink(out)
    else:
        data = raw
    return data


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return 1
    p2s = sys.argv[1]
    addrs = [int(x, 16) for x in sys.argv[2:]]
    mem = extract_ee_memory(p2s)
    print("eeMemory size:", len(mem))
    for a in addrs:
        w = mem[a:a + 16]
        print("%08X = %02X   [%s]" % (a, mem[a], " ".join("%02X" % b for b in w)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
