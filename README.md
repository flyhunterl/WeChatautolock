# WeChat Auto Lock

一个自动锁定微信的小工具，当系统空闲指定时间后自动锁定微信窗口。

## 功能特点

- 系统托盘运行，不占用任务栏
- 可自定义空闲时间（1-10分钟）
- 支持手动立即锁定
- 自动检测系统空闲状态
- 支持开机自启动

## 使用方法

### 方法一：直接运行（推荐）

1. 下载解压获得 `WeChat Auto Lock.exe`
2. 双击运行，允许管理员权限
[WeChat Auto Lock.zip](https://github.com/user-attachments/files/18491110/WeChat.Auto.Lock.zip)


### 方法二：从源码运行

1. 确保已安装 Python 3.6 或更高版本
2. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```
3. 运行程序：
   ```bash
   python system_inactivity_lock.py
   ```

## 命令行参数

- `-t, --time`: 空闲锁定时间（秒），默认120秒
- `-i, --interval`: 检查间隔时间（秒），默认10秒

## 系统要求

- Windows 7/8/10/11
- Python 3.6+
- 微信 PC 版本

## 依赖项

- pywin32
- pystray
- Pillow

## 注意事项

- 程序需要管理员权限运行
- 请确保微信已经登录
- 程序会自动以管理员权限重启

## License

MIT License 
