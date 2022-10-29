# @Time    : 2022.4.9
# @Author  : Xa_L
# @FileName: i2c_and_Softi2c.py

from machine import SoftI2C,Pin
import machine
import  utime
from ssd1306x import SSD1306_I2C

# I2C 初始化： sda--> P4, scl --> P3,频率 8MHz
i2c = SoftI2C(scl = Pin("P3") ,sda = Pin("P4"), freq = 80000)
# OLED 显示屏初始化： 128*64 分辨率,OLED 的 I2C 地址是 0x3c
oled = SSD1306_I2C(128, 64, i2c, addr=0x3c)

# 扫描I2C总线下所有设备地址，并返回对应的列表
add_list = i2c.scan()
oled.fill(255)#清屏

while(True):#重复执行
    oled.fill(0)#清屏
    #从0行0列开始显示hello
    oled.text("hello",10,10)
    oled.show()#OLED显示生效
    utime.sleep_ms(1000)#延时1S
    oled.fill(0)#清屏
    #从0行0列开始显示WORLD
    oled.text("WORLD",30,10)
    oled.show()#OLED显示生效
    utime.sleep_ms(1000)#延时1

