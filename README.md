# HTTP 心跳推送插件

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

- **push_url** (string): 推送服务器 URL，示例：
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

- 版本：1.0.0
- 作者：MoFox Studio
- 最低核心版本：1.0.0
- 依赖：无（使用 Python 标准库）
