# HTTP 心跳推送插件

## KUMA配置

1. **kuma状态查看设置**：在kuma主界面右上角点击“状态页面”——点击“新的状态页”——优雅填写名称和展示页地址——点击下一步——在新页面中点击“编辑页面”——填入标题和描述，然后选择屏幕中间的“添加监控项”把你刚刚优雅填写的名称输入进去，然后保存喵。然后分享当前所在的网址就可以和别人一起视奸你的bot了。

## 安装

1. 将插件目录放置到 `plugins/` 目录下
2. 确保插件文件结构正确：
   ```
   plugins/http_heartbeat/
   ├── plugin.py
   ├── config.py
   ├── manifest.json
   └── __init__.py
   ```
3. 重启应用以加载插件

## 功能介绍

HTTP 心跳推送插件用于定期向服务器发送 HTTP 心跳推送请求，使服务器了解应用程序的运行状态。

**特性：**

- ✅ 定期发送 HTTP GET 请求到指定推送服务器
- ✅ 自动在 URL 末尾追加时间戳
- ✅ 支持自定义推送间隔、超时时间
- ✅ 简洁清晰的日志输出
- ✅ 仅支持本地私网地址（确保安全性）
- ✅ 使用标准库 urllib（无额外依赖）
- ✅ 异步非阻塞实现

## 配置说明

插件配置文件自动生成在 `config/plugins/http_heartbeat/config.toml`

### 主要配置项

#### 插件设置（plugin）

- **enabled** (bool): 是否启用插件，默认 `true`

#### 推送配置（push）

- **push_url** (string): 推送服务器 URL(从kuma获取)，示例：
  - `http://localhost:3001/api/push/token?status=up&msg=OK&ping=` - 本机
  - `http://192.168.1.100:9000/api/push/abc123?status=alive&ping=` - 局域网
  - URL 末尾会自动追加当前时间戳

- **interval_seconds** (int): 推送间隔（秒），范围 1-3600，默认 10

- **timeout_seconds** (float): 单次请求超时时间（秒），范围 1-30，默认 5

- **enable_logging** (bool): 是否记录推送日志，默认 `true`

## 配置示例

```toml
[plugin]
enabled = true

[push]
# 推送到本地服务
push_url = "http://localhost:3001/api/push/token?status=up&msg=OK&ping="
interval_seconds = 10
timeout_seconds = 5.0
enable_logging = true
```

## 日志输出示例

**推送成功：**

```
✓ 心跳推送成功 | URL: http://localhost:3001/api/push/token?status=up&msg=OK&ping=
```

**推送失败：**

```
✗ 心跳推送失败 | URL: http://localhost:3001/api/push/token?status=up&msg=OK&ping= | 错误: URLError: Connection refused
```

**推送超时：**

```
✗ 心跳推送超时 | URL: http://localhost:3001/api/push/token?status=up&msg=OK&ping= | 超时时间: 5.0s
```

## 使用场景

✅ 定期通知服务器应用仍在运行  
✅ 实现无状态应用的存活探针  
✅ 在私网环境中建立应用与监控系统的连接  
✅ 作为 uptimerobot 等监控服务的替代方案

## URL 参数获取以及使用

1. **基本要求**：你先需要有一台公网服务器，并且已经优雅运行了kuma。
2. **获取URL**：在kuma中，新建监控项——监控类型选择“Push”——然后复制推送URL（请记住这个URL并且不要尝试手动访问）——然后保存即可。
3. **URL处理**：优雅运行neo主程序，等待生成配置文件后把推送URL粘贴进配置文件中。

### 注意事项

- 要确保kuma与插件配置文件中的“推送间隔”要一致，如果出现正常运行但是kuma报错，请在kuma中的监控项中增加失败重试。

## URL 参数说明

示例 URL：`http://server:port/api/push/token?status=up&msg=OK&ping=`

- `token` 或 ID：用于识别具体的应用实例
- `status=up`：标识应用状态
- `msg=OK`：消息内容
- `ping=`：末尾追加时间戳，格式为 Unix 时间戳

最终发送的 URL 示例：

```
http://server:port/api/push/token?status=up&msg=OK&ping=1710336282
```

## 安全性说明

⚠️ **本插件仅支持私网地址**

允许的地址格式：

- `localhost`, `127.0.0.1` - 本机
- `192.168.x.x` - C 类私网
- `10.x.x.x` - A 类私网
- `172.16.x.x` - 172.16.0.0/12 范围

## 技术细节

- **异步模型**：基于 asyncio 异步实现，不阻塞主线程
- **调度方式**：使用 Neo-MoFox 内置调度器（src.kernel.scheduler）
- **HTTP 实现**：使用 Python 标准库 urllib，无外部依赖
- **线程处理**：通过 `asyncio.to_thread()` 在线程池中执行阻塞 I/O

## 故障排查

| 问题       | 解决方案                                   |
| ---------- | ------------------------------------------ |
| 插件不工作 | 检查 `enabled = true`；验证 URL 是否可访问 |
| 推送失败   | 确认网络连接；检查推送服务器是否运行       |
| 超时频繁   | 增加 `timeout_seconds` 值；检查网络延迟    |
| 日志过多   | 设置 `enable_logging = false`              |

## 版本信息

- 版本：1.1.0
- 作者：qf
- 最低核心版本：1.0.0
- 依赖：无（使用 Python 标准库）
