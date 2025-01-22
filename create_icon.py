from PIL import Image, ImageDraw

def create_icon():
    # 创建一个32x32的图像，背景透明
    img = Image.new('RGBA', (32, 32), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # 使用蓝色和稍浅的蓝色作为高光
    blue = (66, 133, 244, 255)  # Google Blue
    light_blue = (98, 155, 247, 255)  # 稍浅的蓝色用于高光
    
    # 绘制锁体主体（圆角矩形）
    draw.rounded_rectangle([8, 13, 24, 28], radius=3, fill=blue)
    
    # 绘制锁环底部
    draw.ellipse([10, 4, 22, 16], outline=blue, width=2)
    
    # 填充锁环底部与锁体重叠的部分
    draw.rectangle([10, 10, 22, 16], fill=blue)
    
    # 添加高光效果
    draw.arc([10, 4, 22, 16], 45, 135, fill=light_blue, width=2)
    
    # 在锁体上添加钥匙孔
    draw.ellipse([14, 18, 18, 22], fill='white')
    draw.rectangle([15, 20, 17, 24], fill='white')
    
    # 保存图标
    img.save('icon.png')

if __name__ == '__main__':
    create_icon() 