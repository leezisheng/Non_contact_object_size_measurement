# ====================================导入库========================================== #
# 基本库
import sensor, image, time, pyb

# I2C通信和激光测距模块
from machine import I2C
from vl53l1x import VL53L1X

# 外设相关
import machine

# ====================================初始化========================================== #

#摄像头初始化
sensor.reset()                      # Reset and initialize the sensor.
sensor.set_pixformat(sensor.RGB565) # Set pixel format to RGB565 (or GRAYSCALE)
sensor.set_framesize(sensor.QQVGA)   # Set frame size to QVGA (320x240)
#sensor.set_windowing((160, 160))
sensor.set_auto_gain(False)
#自动增益开启（True）或者关闭（False）。在使用颜色追踪时，需要关闭自动增益。
sensor.set_auto_whitebal(False)
#自动白平衡开启（True）或者关闭（False）。在使用颜色追踪时，需要关闭自动白平衡。
sensor.set_auto_exposure(False)
#enable 打开（True）或关闭（False）自动曝光。默认打开。
#如果 enable 为False， 则可以用 exposure_us 设置一个固定的曝光时间（以微秒为单位）。
sensor.skip_frames(time = 3000)     # Wait for settings take effect.
#水平方向翻转
sensor.set_hmirror(True)
#垂直方向翻转
sensor.set_vflip(True)

#时钟初始化
clock = time.clock()                # Create a clock object to track the FPS.

i2c = I2C(2)
distance = VL53L1X(i2c)

# 距离列表
distance_list = [0,0,0,0,0,0,0,0,0,0]
# 距离计数
distance_count = 0
# 距离列表填充完成
distance_fill_flag = False

# 距离中值滤波
def Average_Filter(temp_distance,temp_distance_count,temp_distance_fill_flag):
    distance_sum = 0
    distance_list[temp_distance_count] = temp_distance
    # 移动计算求均值
    if temp_distance_fill_flag == True:
        for data in distance_list:
            distance_sum = distance_sum + data

    return distance_sum/10

while(True):
    clock.tick()
    img = sensor.snapshot().lens_corr(1.8)

    # 判断距离列表是否填充完全
    if distance_count >= 9:
        distance_count = 0
        distance_fill_flag = True
    else:
        distance_count = distance_count + 1

    print("range: mm ", Average_Filter(distance.read(),distance_count,distance_fill_flag))
    time.sleep_ms(50) #一定要加
    print(clock.fps())


