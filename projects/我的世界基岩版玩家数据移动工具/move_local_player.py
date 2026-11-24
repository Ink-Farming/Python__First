#!/usr/bin/env python3
"""
move_local_player.py —— 搬运基岩版存档里的「本地玩家数据」（~local_player）

适用场景：
    单人存档 / 本地世界之间转移角色：背包、末影箱、坐标、等级、状态效果……
    这些在 LevelDB 里只对应一个键：~local_player

不适用场景：
    服务器存档（键是 player_server_<uuid>）→ 这种请用 merge_players.py
    服务器记录和本地记录结构不同，直接按字节塞进 ~local_player 通常识别不了。

用法：
    python move_local_player.py show  <db目录>
    python move_local_player.py copy  <源db> <目标db> [--dry-run]

示例：
    python move_local_player.py show "D:\\worlds\\WorldA\\db"
    python move_local_player.py copy "D:\\worlds\\WorldA\\db" "D:\\worlds\\WorldB\\db"

注意：
    * 操作前请关闭游戏 / 服务器（LevelDB 有 LOCK，运行中写入会损坏数据）
    * copy 会覆盖目标库的 ~local_player，旧值自动备份到 <目标db>\\.local-backup\\<时间戳>\\
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

KEY = b"~local_player"


def backup(dst_db: str, data: bytes) -> Path:
    stamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    d = Path(dst_db) / ".local-backup" / stamp
    d.mkdir(parents=True, exist_ok=True)
    out = d / "local_player.bin"
    out.write_bytes(data)
    return out


def cmd_show(db_path: str) -> None:
    db = leveldb.LevelDB(db_path)
    data = db.get(KEY)
    total = sum(1 for _ in db.keys())
    db.close(compact=False)
    if data is None:
        print(f"[!] {db_path} 里没有 ~local_player（这个库可能还没有本地玩家，或它是纯服务器库）")
        print(f"[i] 该库共有 {total} 个键")
        return
    print(f"[i] 库：{db_path}")
    print(f"[i] 总键数：{total}")
    print(f"[i] ~local_player：{len(data)} 字节")
    print(f"[i] 开头字节：{data[:16].hex(' ')}")


def cmd_copy(src: str, dst: str, dry: bool) -> None:
    s = leveldb.LevelDB(src)
    data = s.get(KEY)
    s.close(compact=False)
    if data is None:
        sys.exit(f"[x] 源库里没有 ~local_player：{src}")

    print(f"[i] 源 ~local_player：{len(data)} 字节")

    if dry:
        print("[i] --dry-run：没有写入")
        return

    d = leveldb.LevelDB(dst)
    old = d.get(KEY)
    if old is not None:
        p = backup(dst, old)
        print(f"[i] 目标库原有 {len(old)} 字节，已备份到 {p}")
    d.put(KEY, data)
    d.close(compact=False)

    d = leveldb.LevelDB(dst)
    now = d.get(KEY)
    d.close(compact=False)
    print("[ok] 逐字节校验通过" if now == data else "[x] 校验失败")


def main() -> None:
    argv = sys.argv[1:]
    if not argv:
        print(__doc__)
        return
    cmd = argv[0]
    if cmd == "show" and len(argv) >= 2:
        cmd_show(argv[1])
    elif cmd == "copy" and len(argv) >= 3:
        cmd_copy(argv[1], argv[2], "--dry-run" in argv)
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
