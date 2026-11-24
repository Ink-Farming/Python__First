#!/usr/bin/env python3
"""
ldb_tool.py —— 直接查看/复制基岩版 LevelDB（存档里的 db 目录）的任意键

用法：
    python ldb_tool.py list <db目录> [键前缀]
    python ldb_tool.py size <db目录> <键名>
    python ldb_tool.py hex  <db目录> <键名> [字节数]
    python ldb_tool.py get  <db目录> <键名> <输出文件>
    python ldb_tool.py put  <db目录> <键名> <输入文件>
    python ldb_tool.py copy <源db> <源键> <目标db> <目标键>

例子：
    # 看这个存档里有哪些玩家记录
    python ldb_tool.py list "D:\\world\\db" player_server_

    # 看本地玩家数据的开头 32 字节
    python ldb_tool.py hex "D:\\world\\db" ~local_player 32

    # 把一条记录原样复制到另一个库
    python ldb_tool.py copy "旧db" player_server_xxx "新db" player_server_xxx

注意：操作前关闭游戏 / 服务器，否则 LOCK 会挡住或写坏数据。
"""

from __future__ import annotations

import sys

try:
    import leveldb
except ImportError:
    sys.exit(
        "缺少 leveldb 模块。\n"
        "请用 Python 3.12 安装：pip install amulet-leveldb\n"
        "（3.13 / 3.14 没有预编译轮子，会编译失败）"
    )


def main() -> None:
    argv = sys.argv[1:]
    if len(argv) < 3:
        print(__doc__)
        return

    cmd, path = argv[0], argv[1]

    if cmd == "list":
        prefix = argv[2].encode() if len(argv) > 2 else b""
        db = leveldb.LevelDB(path)
        n = 0
        for k in db.keys():
            if k.startswith(prefix):
                n += 1
                print(f"{k.decode('utf-8', 'replace')}\t{len(db.get(k))}")
        print(f"--- {n} keys ---")
        db.close(compact=False)

    elif cmd == "size":
        db = leveldb.LevelDB(path)
        print(len(db.get(argv[2].encode())))
        db.close(compact=False)

    elif cmd == "hex":
        db = leveldb.LevelDB(path)
        data = db.get(argv[2].encode())
        limit = int(argv[3]) if len(argv) > 3 else 96
        print(data[:limit].hex(" "))
        db.close(compact=False)

    elif cmd == "get":
        db = leveldb.LevelDB(path)
        data = db.get(argv[2].encode())
        open(argv[3], "wb").write(data)
        print(f"wrote {len(data)} bytes -> {argv[3]}")
        db.close(compact=False)

    elif cmd == "put":
        db = leveldb.LevelDB(path)
        data = open(argv[3], "rb").read()
        db.put(argv[2].encode(), data)
        db.close(compact=False)
        print(f"wrote {len(data)} bytes -> {argv[2]}")

    elif cmd == "copy":
        src_path, src_key, dst_path, dst_key = argv[1:5]
        s = leveldb.LevelDB(src_path)
        data = s.get(src_key.encode())
        s.close(compact=False)
        if data is None:
            sys.exit(f"[x] 源键不存在：{src_key}")
        d = leveldb.LevelDB(dst_path)
        d.put(dst_key.encode(), data)
        d.close(compact=False)
        print(f"copied {len(data)} bytes: {src_key} -> {dst_key}")

    else:
        print(__doc__)


if __name__ == "__main__":
    main()
