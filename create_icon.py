from PIL import Image, ImageDraw

def create_icon():
    # 创建一个32x32的图像，背景透明
    img = Image.new('RGBA', (32, 32), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # 使用蓝色
    blue = (66, 133, 244, 255)  # Google Blue
    
    # 绘制一个简单的锁形状
    # 外框
    draw.rectangle([8, 12, 24, 28], outline=blue, width=2)
    # 锁环
    draw.arc([11, 4, 21, 14], 0, 180, fill=blue, width=2)
    
    # 保存图标
    img.save('icon.png')

if __name__ == '__main__':
    create_icon() 