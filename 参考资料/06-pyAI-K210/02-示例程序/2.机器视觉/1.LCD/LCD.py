'''
实验名称：LCD
版本： v1.0
日期： 2019.12
作者： 01Studio
说明：编程实现LCD显示信息。需要将01Studio.bmp文件发送到开发板。
'''

import lcd,image,utime

lcd.init() #初始化LCD
lcd.clear(lcd.WHITE) #清屏白色

#显示字符
lcd.draw_string(110, 120, "Hello 01Studio!",lcd.BLACK, lcd.WHITE) #显示字符

utime.sleep(2) #延时2秒

lcd.rotation(1) #由于图像默认是240*320，因此顺时钟旋转90°。

#显示图像，必须先将01Studio.bmp文件发送到开发板才能正常运行
#发送方法：MaixPy IDE -- 工具 --发送文件到开发板
lcd.display(image.Image("01Studio.bmp"))
