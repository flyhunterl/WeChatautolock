import time
import ctypes
import platform
import logging
import argparse
import win32gui
import win32con
import pywintypes
import win32api
import win32con
import win32process
import sys
import os
import pystray
from PIL import Image
import threading

def is_admin():
    """检查是否以管理员权限运行"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def restart_as_admin():
    """以管理员权限重新启动程序"""
    ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, " ".join(sys.argv), None, 1
    )
    sys.exit()

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def get_idle_time():
    """获取系统空闲时间（秒）"""
    try:
        if platform.system() == 'Windows':
            class LASTINPUTINFO(ctypes.Structure):
                _fields_ = [("cbSize", ctypes.c_uint),
                           ("dwTime", ctypes.c_uint)]
            lastInputInfo = LASTINPUTINFO()
            lastInputInfo.cbSize = ctypes.sizeof(lastInputInfo)
            ctypes.windll.user32.GetLastInputInfo(ctypes.byref(lastInputInfo))
            millis = ctypes.windll.kernel32.GetTickCount() - lastInputInfo.dwTime
            return millis / 1000.0
        else:
            raise NotImplementedError("目前仅支持Windows系统")
    except Exception as e:
        logging.error(f"获取空闲时间失败: {str(e)}")
        return 0

def is_foreground_window(handle):
    """检查窗口是否是前台窗口"""
    try:
        return handle == win32gui.GetForegroundWindow()
    except Exception as e:
        logging.error(f"检查前台窗口失败: {str(e)}")
        return False

def activate_window(handle, retries=3):
    """尝试激活窗口"""
    for attempt in range(retries):
        try:
            current_thread = win32api.GetCurrentThreadId()
            target_thread, _ = win32process.GetWindowThreadProcessId(handle)
            win32process.AttachThreadInput(current_thread, target_thread, True)
            win32gui.SetForegroundWindow(handle)
            win32gui.ShowWindow(handle, win32con.SW_RESTORE)
            win32process.AttachThreadInput(current_thread, target_thread, False)
            if is_foreground_window(handle):
                return True
            time.sleep(0.5)
        except Exception as e:
            logging.warning(f"激活窗口尝试 {attempt + 1}/{retries} 失败: {str(e)}")
            time.sleep(1)
    return False

def is_wechat_locked():
    """检查微信是否处于锁定状态"""
    try:
        wechat_window = win32gui.FindWindow("WeChatMainWndForPC", None)
        if not wechat_window:
            return False
            
        # 获取微信窗口标题
        title = win32gui.GetWindowText(wechat_window)
        return "已锁定" in title or "Locked" in title
    except Exception as e:
        logging.error(f"检查微信锁定状态失败: {str(e)}")
        return False

def lock_wechat():
    """使用快捷键锁定微信"""
    try:
        wechat_window = win32gui.FindWindow("WeChatMainWndForPC", None)
        if not wechat_window:
            logging.warning("未找到微信窗口")
            return

        target_thread, target_process = win32process.GetWindowThreadProcessId(wechat_window)
        current_thread = win32api.GetCurrentThreadId()
        
        try:
            win32process.AttachThreadInput(current_thread, target_thread, True)
            old_window = win32gui.GetForegroundWindow()
            
            if win32gui.IsIconic(wechat_window):
                win32gui.ShowWindow(wechat_window, win32con.SW_RESTORE)
            
            win32gui.SetWindowPos(wechat_window, win32con.HWND_TOPMOST, 0, 0, 0, 0, 
                                win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
            win32gui.SetWindowPos(wechat_window, win32con.HWND_NOTOPMOST, 0, 0, 0, 0, 
                                win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
            
            win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
            win32api.keybd_event(ord('L'), 0, 0, 0)
            time.sleep(0.05)
            win32api.keybd_event(ord('L'), 0, win32con.KEYEVENTF_KEYUP, 0)
            win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
            
            if old_window and old_window != wechat_window:
                win32gui.SetForegroundWindow(old_window)
                
            logging.info("微信已锁定")
            
        finally:
            try:
                win32process.AttachThreadInput(current_thread, target_thread, False)
            except:
                pass
                
    except Exception as e:
        logging.error(f"锁定微信失败: {str(e)}")

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="微信空闲锁定程序")
    parser.add_argument(
        '-t', '--time',
        type=int,
        default=120,
        help='空闲锁定时间（秒），默认120秒'
    )
    parser.add_argument(
        '-i', '--interval',
        type=int,
        default=10,
        help='检查间隔时间（秒），默认10秒'
    )
    return parser.parse_args()

class LockSettings:
    """存储锁定设置的类"""
    def __init__(self, idle_time=120):
        self.idle_time = idle_time

def create_tray_icon(stop_event, settings):
    """创建系统托盘图标"""
    try:
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'icon.png')
        image = Image.open(icon_path)
        
        def on_exit(icon):
            icon.stop()
            stop_event.set()
            
        def on_lock(icon):
            threading.Thread(target=lock_wechat).start()

        def set_idle_time(minutes):
            def handler(icon, item):
                settings.idle_time = minutes * 60
                icon.title = f"微信空闲锁定 - {minutes}分钟"
                logging.info(f"空闲时间已设置为 {minutes} 分钟")
            return handler
            
        time_items = [
            pystray.MenuItem(
                f"{minutes}分钟",
                set_idle_time(minutes),
                radio=True,
                checked=lambda item, m=minutes: settings.idle_time == m * 60
            ) for minutes in [1, 2, 3, 5, 10]
        ]
            
        menu = pystray.Menu(
            pystray.MenuItem("立即锁定", on_lock),
            pystray.MenuItem("空闲时间", pystray.Menu(*time_items)),
            pystray.MenuItem("退出", on_exit)
        )
        
        icon = pystray.Icon(
            "WeChat Lock",
            image,
            f"微信空闲锁定 - {settings.idle_time//60}分钟",
            menu
        )
        
        icon.run()
    except Exception as e:
        logging.error(f"创建系统托盘图标失败: {str(e)}")

def main():
    if not is_admin():
        logging.warning("程序未以管理员权限运行，尝试重新启动...")
        restart_as_admin()
        return

    args = parse_args()
    settings = LockSettings(args.time)
    logging.info(f"启动微信空闲锁定程序，空闲时间：{settings.idle_time}秒，检查间隔：{args.interval}秒")
    
    stop_event = threading.Event()
    tray_thread = threading.Thread(target=create_tray_icon, args=(stop_event, settings))
    tray_thread.daemon = True
    tray_thread.start()
    
    try:
        while not stop_event.is_set():
            idle_time = get_idle_time()
            logging.debug(f"当前空闲时间：{idle_time:.1f}秒")
            
            if idle_time >= settings.idle_time and not is_wechat_locked():
                threading.Thread(target=lock_wechat).start()
                
                # 等待微信锁定完成
                time.sleep(2)
                
                # 重置空闲时间检测
                while get_idle_time() < 1 and not stop_event.is_set():
                    time.sleep(1)
                
                logging.info("检测到用户活动，程序继续运行")
                
            time.sleep(args.interval)
            
    except KeyboardInterrupt:
        logging.info("程序已手动终止")
    except Exception as e:
        logging.error(f"程序运行出错: {str(e)}")
    finally:
        stop_event.set()
        logging.info("程序退出")

if __name__ == "__main__":
    main()
