import os
import sys
import base64

# 将图标转换为 Python 代码中的 base64 字符串
def icon_to_base64():
    with open('icon.png', 'rb') as f:
        return base64.b64encode(f.read()).decode('utf-8')

# 修改主程序，添加内置图标
def modify_main_script():
    icon_base64 = icon_to_base64()
    
    with open('system_inactivity_lock.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 在导入语句后添加图标数据
    icon_code = f'''
# 内置图标数据
ICON_BASE64 = "{icon_base64}"

def get_icon_image():
    """获取内置图标"""
    import base64
    from io import BytesIO
    from PIL import Image
    icon_data = base64.b64decode(ICON_BASE64)
    return Image.open(BytesIO(icon_data))
'''
    
    # 替换图标加载代码
    content = content.replace(
        'icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), \'icon.png\')\n        image = Image.open(icon_path)',
        'image = get_icon_image()'
    )
    
    with open('system_inactivity_lock_temp.py', 'w', encoding='utf-8') as f:
        f.write(content)
        f.write(icon_code)

def build():
    # 修改主程序
    modify_main_script()
    
    # PyInstaller 打包命令
    os.system('pyinstaller --noconfirm --onefile --windowed '
              '--uac-admin '  # 请求管理员权限
              '--name "WeChat Auto Lock" '  # 输出文件名
              '--icon icon.png '  # 程序图标
              'system_inactivity_lock_temp.py')  # 临时主程序文件
    
    # 清理临时文件
    if os.path.exists('system_inactivity_lock_temp.py'):
        os.remove('system_inactivity_lock_temp.py')

if __name__ == '__main__':
    build() 