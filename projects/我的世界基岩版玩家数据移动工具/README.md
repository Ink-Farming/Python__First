# 我的世界基岩版玩家数据移动工具

直接读写 Minecraft 基岩版存档里的 `db`（LevelDB），搬运玩家数据。
不改存档其它内容，只 `get` + `put` 指定的键。

## 三个脚本

| 脚本 | 干什么 | 用在什么场景 |
|---|---|---|
| `merge_players.py` | 搬服务器玩家数据（`player_server_<uuid>` + `player_<uuid>`） | 服务器换周目 / 换存档，把老玩家的背包坐标带过去 |
| `move_local_player.py` | 搬本地玩家数据（`~local_player`） | 单人存档之间转移角色 |
| `ldb_tool.py` | 通用查看/复制任意键 | 排查问题：到底有哪些键、多大、开头字节长什么样 |

## 先决条件

1. **Python 3.12**（重要：`amulet-leveldb` 只有 cp311 / cp312 的预编译轮子，3.13 / 3.14 会现场编译 C++，基本必失败）
2. 安装依赖：

```bash
pip install -r requirements.txt
```

3. **关闭游戏 / 服务器**。LevelDB 有 `LOCK` 文件，运行中写入会损坏存档。

## 键名对照（先搞清你要搬哪一种）

| 键 | 含义 |
|---|---|
| `~local_player` | 单人 / 本地世界的玩家，一个存档只有一个 |
| `player_server_<uuid>` | 服务器上的玩家，每个账号一条 |
| `player_<uuid>` | 玩家身份记录（MsaId / SelfSignedId），跟着服务器玩家走 |

> 服务器记录和本地记录**结构不同**，不能直接互换。服务器 → 服务器、本地 → 本地，才能按字节搬。

## 用法

### 1. 搬服务器玩家数据

```bash
# 先空跑，确认「旧库」里确实有 player_server_*
python merge_players.py "旧存档/db" "新存档/db" --dry-run

# 确认没问题再真写（同名键的旧值会自动备份）
python merge_players.py "旧存档/db" "新存档/db"
```

输出示例：

```text
[i] 旧库：player_server_* 19 条，其他 player_* 35 条
      player_server_0f9578e4-...   87167 字节
      ...
[ok] 写入 54 条
[ok] 逐字节校验通过
```

参数顺序是 **旧库 → 新库**，脚本不看文件夹名字，写反了它不会帮你纠正。
如果源库里没有玩家数据，它会打印「没有找到玩家数据，什么都没做」直接退出。

### 2. 搬本地玩家数据

```bash
python move_local_player.py show "存档/db"
python move_local_player.py copy "旧存档/db" "新存档/db" --dry-run
python move_local_player.py copy "旧存档/db" "新存档/db"
```

### 3. 排查问题

```bash
python ldb_tool.py list "存档/db" player_server_
python ldb_tool.py hex  "存档/db" ~local_player 32
python ldb_tool.py copy "旧db" player_server_xxx "新db" player_server_xxx
```

## 安全设计

- 只处理 `player_` / `player_server_` / `~local_player` 这些键，其它一个字节不碰；
- 覆盖前把目标库的旧值备份到 `<db>\.player-backup\<时间戳>\` 或 `<db>\.local-backup\<时间戳>\`；
- 写完重新打开数据库，**逐字节回读校验**；
- 不调用 `compact`，避免整库重写（游戏下次启动会自己整理）。

## 常见坑

- **`.ldb` 不能用十六进制编辑器改**：LevelDB 是 SSTable，带 CRC32C 校验，改一个字节整库就废；
- **普通 `leveldb` 库打不开基岩版**：Mojang 把 Snappy 换成了 zlib，必须用 `amulet-leveldb` / `leveldb-mcpe` 这类打过补丁的绑定；
- **Bedrock 的 NBT 不是标准 NBT**：字符串长度是 2 字节小端，标准 NBT 解析器经常读崩；
- **别在服务器运行时替换 db**：先停服，再换文件夹，换完再开。

## 免责

仅供自己存档维护使用。备份永远是最重要的一步——操作前把整个世界文件夹复制一份。
