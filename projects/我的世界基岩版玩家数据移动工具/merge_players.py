#!/usr/bin/env python3
"""
merge_players.py —— 把旧存档 db 里的服务器玩家数据原样搬进新存档 db

只复制这两类键，别的一个字节都不碰：
    player_server_<uuid>   玩家完整数据（背包 / 坐标 / 等级 / 末影箱 …）
    player_<uuid>          玩家身份记录（MsaId / SelfSignedId）

用法（先关服务器！）：
    python merge_players.py <旧db目录> <新db目录> [--dry-run] [--only-server]

    --dry-run       只统计和列出，不写入
    --only-server   只搬 player_server_*，不搬身份记录

脚本会：
  1. 读出旧库里所有玩家相关键并打印
  2. 把新库里将被覆盖的旧值备份到 <新db>\\.player-backup\\<时间戳>\\
  3. 批量写入，回读逐字节校验

换存档时请先 --dry-run 确认「源库」里确实有 player_server_<uuid>，
参数顺序是「旧库 → 新库」，写反了不会自动纠正。
"""

from __future__ import annotations

import datetime as dt
import sys
from pathlib import Path

try:
    import leveldb
except ImportError:
    sys.exit(
        "缺少 leveldb 模块。\n"
        "请用 Python 3.12 安装：pip install amulet-leveldb\n"
        "（3.13 / 3.14 没有预编译轮子，会编译失败）"
    )


def is_player_key(k: bytes) -> bool:
    return k.startswith(b"player_server_") or k.startswith(b"player_")


def main() -> None:
    argv = [a for a in sys.argv[1:] if not a.startswith("--")]
    flags = {a for a in sys.argv[1:] if a.startswith("--")}
    if len(argv) < 2:
        print(__doc__)
        sys.exit(1)

    src_db, dst_db = argv[0], argv[1]
    dry = "--dry-run" in flags
    only_server = "--only-server" in flags

    src = leveldb.LevelDB(src_db)
    keys = [k for k in src.keys() if is_player_key(k)]
    if only_server:
        keys = [k for k in keys if k.startswith(b"player_server_")]
    data = {k: src.get(k) for k in keys}
    src.close(compact=False)

    n_server = sum(1 for k in keys if k.startswith(b"player_server_"))
    print(f"[i] 旧库：player_server_* {n_server} 条，其他 player_* {len(keys) - n_server} 条")
    for k in keys:
        print(f"      {k.decode('utf-8', 'replace'):<55} {len(data[k]):>8} 字节")

    if dry:
        print("[i] --dry-run：没有写入")
        return
    if not data:
        print("[!] 旧库里没有找到玩家数据，什么都没做")
        return

    dst = leveldb.LevelDB(dst_db)
    overridden = {k: dst.get(k) for k in data if k in dst}
    if overridden:
        stamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
        bak_dir = Path(dst_db) / ".player-backup" / stamp
        bak_dir.mkdir(parents=True, exist_ok=True)
        for k, v in overridden.items():
            (bak_dir / (k.decode("utf-8", "replace") + ".bin")).write_bytes(v)
        print(f"[i] 目标库已有 {len(overridden)} 条同名键，旧值已备份到 {bak_dir}")

    dst.putBatch(data)
    dst.close(compact=False)

    dst = leveldb.LevelDB(dst_db)
    after = {k: dst.get(k) for k in data}
    dst.close(compact=False)

    bad = [k for k, v in data.items() if after.get(k) != v]
    print(f"[ok] 写入 {len(data)} 条")
    print("[ok] 逐字节校验通过" if not bad else f"[x] 校验失败：{bad}")


if __name__ == "__main__":
    main()
