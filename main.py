# ===================================引脚使用========================================= #
# 激光测距模块：I2C2 P4-SCK P5-SDA
# 舵机控制：TIM4 P7 P8
# 软件IIC控制OLED屏幕：sda--> P4, scl --> P3,频率 8MHz

# ====================================导入库========================================== #

# 基本库
import sensor, image, time, pyb

# I2C通信和激光测距模块
from machine import I2C
from vl53l1x import VL53L1X

# LED灯库
from pyb import LED

# 舵机控制库
from pyb import Servo

# PID算法库
from pid import PID

# 软件IIC
from machine import SoftI2C,Pin

# 外设相关
import machine

# 128 X 64 OLED屏幕
from ssd1306x import SSD1306_I2C

# 引脚相关
from pyb import Pin

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

#I2C通信设置与测距 P4-SCK P5-SDA
i2c = I2C(2)
distance = VL53L1X(i2c)

# 舵机初始化
pan_servo=Servo(1)# P7  底
tilt_servo=Servo(2)# P8 台
pan_servo.calibration(500,2500,500)  # 底中心位置
tilt_servo.calibration(500,2500,500) # 台中心位置
pan_servo.angle(0) # 初始化底位置

# PID初始化
#pan_pid = PID(p=0.07, i=0, imax=90) #脱机运行或者禁用图像传输，使用这个PID
#tilt_pid = PID(p=0.05, i=0, imax=90) #脱机运行或者禁用图像传输，使用这个PID
pan_pid = PID(p=0.1, i=0, imax=90)#在线调试使用这个PID
tilt_pid = PID(p=0.1, i=0, imax=90)#在线调试使用这个PID

# I2C 初始化： sda--> P4, scl --> P3,频率 8MHz
i2c = SoftI2C(scl = Pin("P3") ,sda = Pin("P4"), freq = 80000)
# OLED 显示屏初始化： 128*64 分辨率,OLED 的 I2C 地址是 0x3c
oled = SSD1306_I2C(128, 64, i2c, addr=0x3c)

# 扫描I2C总线下所有设备地址，并返回对应的列表
add_list = i2c.scan()
oled.fill(255)#清屏

# 按键初始化
# 将P6、p7作为阈值控制口 OUT_PP PULL_NONE
KEY1 = Pin('P6', Pin.IN, Pin.PULL_UP)
KEY2 = Pin('P9', Pin.IN, Pin.PULL_UP)

# ====================================相关函数========================================== #

# 测距函数
def Get_Distance():
    # 延时一定要加
    time.sleep_ms(50)
    return distance.read()

# 距离常数拟合曲线
def Get_K_Curve(Dis,Cw,Ch):
    K = 1/27
    return K

# 形状分类
def Shape_Class(color_threshold,img,roi):
    Flag = "none"
    blobs = img.find_blobs([color_threshold],roi = roi)
    if len(blobs) == 1:
        b = find_max(blobs)
        img.draw_rectangle(b[0:4],color = (0, 0, 255)) # rect
        img.draw_cross(b[5], b[6],color = (0, 0, 255)) # cx, cy
        Area_ratio = b[4]/(b[2]*b[3])
        print("Area_ratio:",Area_ratio)
        if 0.72<Area_ratio<0.85:
            Flag = "circle"
        elif 0.9<Area_ratio<1.0:
            Flag = "rectangular"
        elif 0.4<Area_ratio<0.65:
            Flag = "triangle"
        return Flag
    return Flag

# 寻找最大色块
def find_max(blobs):
    max_size=0
    for blob in blobs:
        if blob[2]*blob[3] > max_size:
            max_blob=blob
            max_size = blob[2]*blob[3]
    return max_blob

# 平面圆形识别
# 返回圆形中心位置（x\y）和（w,h）即半径，以及标志量
def Circle2D_Detect(color_threshold,img):
    Flag = "circle"
    for c in img.find_circles(threshold = 1000, x_margin = 10, y_margin = 10, r_margin = 10,r_min = 2, r_max = 100, r_step = 2):
        blobs = img.find_blobs([color_threshold])
        if len(blobs) == 1:
            b = find_max(blobs)
            img.draw_rectangle(b[0:4],color = (0, 0, 255)) # rect
            img.draw_cross(b[5], b[6],color = (0, 0, 255)) # cx, cy
            Show_Str(Flag)
            return b[5],b[6],b[2],b[3],Flag
        else:
            Flag = "none"
            return 0,0,0,0,Flag
    return 0,0,0,0,Flag

# 平面矩形识别
# 返回矩形中心位置（x\y）和（w,h），以及标志量
def Ret2D_Detect(color_threshold,img):
    Flag = "rectangular"
    # 下面的`threshold`应设置为足够高的值，以滤除在图像中检测到的具有低边缘幅度的噪声矩形。最适用与背景形成鲜明对比的矩形。
    for r in img.find_rects(threshold = 10000):
        blobs = img.find_blobs([color_threshold])
        if len(blobs) == 1:
            b = find_max(blobs)
            img.draw_rectangle(b[0:4],color = (0, 255, 110)) # rect
            img.draw_cross(b[5], b[6],color = (0, 255, 110)) # cx, cy
            Show_Str(Flag)
            for p in r.corners():
                img.draw_circle(p[0], p[1], 5, color = (0, 255, 0))
            return b[5],b[6],b[2],b[3],Flag
        else:
            Flag = "none"
            return 0,0,0,0,Flag
    return 0,0,0,0,Flag

# 平面三角形识别
# 返回矩形中心位置（x\y）和（w,h），以及标志量
def Triangle2D_Detect(color_threshold,img):
    Flag = "triangle"
    # 下面的`threshold`应设置为足够高的值，以滤除在图像中检测到的具有低边缘幅度的噪声矩形。最适用与背景形成鲜明对比的矩形。
    blobs = img.find_blobs([color_threshold])
    if len(blobs) == 1:
        b = find_max(blobs)
        img.draw_rectangle(b[0:4],color = (255, 100, 110)) # rect
        img.draw_cross(b[5], b[6],color = (255, 100, 110)) # cx, cy
        Show_Str(Flag)
        return b[5],b[6],b[2],b[3],Flag
    else:
        Flag = "none"
        return 0,0,0,0,Flag

# 尺寸计算，返回边长
def Size_Calculation(Dis,Cw,Ch,Flag):
    SideLength = 0
    if Flag == "circle":
        SideLength = Dis*((Cw+Ch)/2)*Get_K_Curve(Dis,Cw,Ch)*2*PI
        return SideLength
    elif Flag == "rectangular":
        SideLength = Dis*Cw*Get_K_Curve(Dis,Cw,Ch)*2+Dis*Ch*Get_K_Curve(Dis,Cw,Ch)*2
        return SideLength
    elif Flag == "triangle":
        SideLength = Dis*Get_K_Curve(Dis,Cw,Ch)*((Cw+Ch)/2)*3
    return SideLength

# 字符绘制
def Show_Str(str_to_show):
    img.draw_string(str_x, str_y, str_to_show, color = str_color_threshold, scale = 1, mono_space = False,
                        char_rotation = 0, char_hmirror = False, char_vflip = False,
                        string_rotation = 0, string_hmirror = False, string_vflip = False)

# LED灯控制
def led_control(x):
    if   (x&1)==0: red_led.off()
    elif (x&1)==1: red_led.on()
    if   (x&2)==0: green_led.off()
    elif (x&2)==2: green_led.on()
    if   (x&4)==0: blue_led.off()
    elif (x&4)==4: blue_led.on()
    if   (x&8)==0: ir_led.off()
    elif (x&8)==8: ir_led.on()

# OLED屏幕显示函数
def OLED_Show(v_Distance,SideLength,v_Flag_Class):
    time.sleep_ms(1000)
    #清屏
    oled.fill(0)

    oled.text("range: mm",0,0)
    #OLED显示生效
    oled.show()

    oled.text(str(v_Distance),0,10)
    #OLED显示生效
    oled.show()

    oled.text("SideLength:mm",0,20)
    #OLED显示生效
    oled.show()

    oled.text(str(SideLength),0,30)
    #OLED显示生效
    oled.show()

    oled.text("Object class:",0,40)
    #OLED显示生效
    oled.show()

    oled.text(v_Flag_Class,0,50)
    #OLED显示生效
    oled.show()

# ====================================全局变量========================================== #

# 距离
v_Distance = 0
# 颜色阈值
red_threshold   = [4, 30, 5, 127, -1, 127]
grean_threshold = [4, 43, -82, -15, 13, 58]
blue_threshold  = [4, 90, -70, 127, -64, -23]
black_threshold = [18, 36, -66, -21, -37, 36]
white_threshold = [19, 100, -7, 127, 4, 127]
# 颜色阈值列表
back_threshold  = [blue_threshold,grean_threshold,red_threshold]
# 颜色计数
color_count = 0
# 圆周率Pi值
PI = 3.14159263
# 字符相关设置
str_x = 10
str_y = 10
str_color_threshold = (100,200,200)
# 检测确认次数
Detect_times = 10
# 测量计数变量
v_Measure_Count = 0
# 模式1 中心ROI设置
Center_ROI = (50,50,40,40)
# ROI统计阈值
color_threshold = []
# LED相关
red_led   = LED(1)
green_led = LED(2)
blue_led  = LED(3)
ir_led    = LED(4)
# 舵机移动变量：非PID控制
servo_angle_count = 0
# 工作模式
Work_Mode = 0
# 测量次数：满十次计算平均值
measure_times_count = 0
# 尺寸数组：用于滤波
SideLength_list = [0,0,0,0,0,0,0,0,0,0]
# 尺寸总和
SideLength_sum = 0
# KEY1按下标志

# KEY2按下标志


# ===================================工作模式=========================================== #
# 二维物体尺寸测量： 第一题、第二题
def object_2D_Detect(img):
    # 蓝绿灯闪烁
    led_control(2)
    time.sleep_ms(50)
    led_control(4)

    # 像素颜色统计
    Center_Statistics = img.get_statistics(roi=Center_ROI)
    color_threshold   = [Center_Statistics.l_mode()-20,Center_Statistics.l_mode()+20,Center_Statistics.a_mode()-20,Center_Statistics.a_mode()+20,Center_Statistics.b_mode()-20,Center_Statistics.b_mode()+20]
    print("ROI color_threshold : ",color_threshold)

    # 种类识别
    # 这里ROI应该根据目标物体具体尺寸和距离进行修改
    v_Flag_Class = Shape_Class(color_threshold,img,roi = (0,0,160,120))

    # 模式1：测量平面目标物体边长、几何形状和目标与测量头的距离
    if v_Flag_Class == "circle":
        Object_cx,Object_cy,Object_w,Object_h,Flag = Circle2D_Detect(color_threshold,img)
        v_Distance = Get_Distance()
        SideLength = Size_Calculation(v_Distance,Object_w,Object_h,Flag)
        # 输出尺寸
        led_control(1)
        time.sleep_ms(100)
        led_control(0)

        add_list = i2c.scan()
        if len(add_list) >= 1:
            try:
                OLED_Show(int(v_Distance),int(SideLength),v_Flag_Class)
                print("range: mm ", v_Distance)
                print("SideLength:mm",SideLength)
                print("Object class:",v_Flag_Class)
                # 绿灯亮起：测量完成
                led_control(2)
            except:
                print("The OLED screen has unstable power supply")
    elif v_Flag_Class == "rectangular":
        Object_cx,Object_cy,Object_w,Object_h,Flag = Ret2D_Detect(color_threshold,img)
        v_Distance = Get_Distance()
        SideLength = Size_Calculation(v_Distance,Object_w,Object_h,Flag)
        # 输出尺寸
        led_control(1)
        time.sleep_ms(100)
        led_control(0)

        add_list = i2c.scan()
        if len(add_list) >= 1:
            try:
                OLED_Show(int(v_Distance),int(SideLength),v_Flag_Class)
                print("range: mm ", v_Distance)
                print("SideLength:mm",SideLength)
                print("Object class:",v_Flag_Class)
                # 绿灯亮起：测量完成
                led_control(2)
            except:
                print("The OLED screen has unstable power supply")
    elif v_Flag_Class == "triangle":
        Object_cx,Object_cy,Object_w,Object_h,Flag = Triangle2D_Detect(color_threshold,img)
        v_Distance = Get_Distance()
        SideLength = Size_Calculation(v_Distance,Object_w,Object_h,Flag)
        # 输出尺寸
        led_control(1)
        time.sleep_ms(100)
        led_control(0)

        add_list = i2c.scan()
        if len(add_list) >= 1:
            try:
                OLED_Show(int(v_Distance),int(SideLength),v_Flag_Class)
                print("range: mm ", v_Distance)
                print("SideLength:mm",SideLength)
                print("Object class:",v_Flag_Class)
                # 绿灯亮起：测量完成
                led_control(2)
            except:
                print("The OLED screen has unstable power supply")
    else:
        Show_Str("Could not find Object")
        print("未检测到任何物体")

# ====================================主函数============================================ #

# 开始工作提示，绿灯亮灭
led_control(2)
time.sleep_ms(5000)
led_control(0)

while(True):
    clock.tick()
    # 畸变矫正
    img = sensor.snapshot().lens_corr(1.8)

    # 按键1被按下，Work_Mode = 1
    KEY1_Flag = KEY1.value()
    if(KEY1_Flag == 0):
        time.sleep_ms(20)
        if(KEY1_Flag == 0):
            Work_Mode = 1

    if(Work_Mode == 0):
        pan_servo.angle(60)
        object_2D_Detect(img)

    elif(Work_Mode == 1):

        # 二维物体尺寸测量： 第三题自动寻找目标测量
        # 赋值blobs为找到背景板像素的值
        blobs = img.find_blobs([back_threshold[color_count]])

        # 检测到目标物体，启动PID调节
        if blobs:
            max_blob = find_max(blobs) #找最大的色块
            #print("cx: ", max_blob.cx())             #打印X的的位置
            #print("cy: ", max_blob.cy())             #打印Y的的位置
            pan_error = max_blob.cx()-80   #底的误差为最大色块所在的X轴-宽（宽固定=160  /2=80）我理解为取XY中心点
            tilt_error = max_blob.cy()-60  #台的误差为最大色块所在的Y轴-高（120）

            print("pan_error: ", pan_error)             #打印底的偏差
            print("tilt_error: ", tilt_error)             #打印台的偏差
            '比如说现在X的距离是159 目标中心偏差159-img.width()/2=79'

            img.draw_rectangle(max_blob.rect()) # 矩形
            img.draw_cross(max_blob.cx(), max_blob.cy()) # cx, cy 交叉

            pan_output=pan_pid.get_pid(pan_error,1)/2     #底的转动=获取的PID值    get_pid(self, error, scaler)/2
            tilt_output=tilt_pid.get_pid(tilt_error,1)   #台的转动=获取的PID值    get_pid(self, error, scaler) 也可以除以2 走慢一点罢了
            '可以这样子理解，这个pid的函数是想使偏差=0'
            #print("pan_output",pan_output)
            #print("tilt_output",tilt_output)
            pan_servo.angle(pan_servo.angle()-  pan_output)    #底部舵机转动的角度为上一个角度+现在的输出(偏差)角度 因为是倒转 所以是减
            tilt_servo.angle(tilt_servo.angle()+tilt_output) #上面舵机转动的角度为上一个角度-现在的输出(偏差)角度  因为是倒转 所以是加
            #print("tilt_servo.angle:",tilt_servo.angle())

            if( -20 <= pan_error <= 20 and -20 <= tilt_error <= 20):

                # 像素颜色统计
                Center_Statistics = img.get_statistics(roi=(max_blob.x(), max_blob.y(), max_blob.w(), max_blob.h()))
                color_threshold   = back_threshold[color_count]
                print("ROI color_threshold : ",color_threshold)

                # 种类识别
                v_Flag_Class = Shape_Class(color_threshold,img,roi = (max_blob.x(),max_blob.y(),max_blob.w(),max_blob.h()))
                print(v_Flag_Class)

                # 模式1：测量平面目标物体边长、几何形状和目标与测量头的距离
                if v_Flag_Class == "circle":
                    # 输出尺寸
                    led_control(1)
                    time.sleep_ms(100)
                    led_control(0)
                    Object_cx,Object_cy,Object_w,Object_h,Flag = Circle2D_Detect(color_threshold,img)
                    v_Distance = Get_Distance()
                    SideLength = Size_Calculation(v_Distance,Object_w,Object_h,Flag)

                    add_list = i2c.scan()
                    if len(add_list) >= 1:
                        try:
                            OLED_Show(int(v_Distance),int(SideLength),v_Flag_Class)
                            print("range: mm ", v_Distance)
                            print("SideLength:mm",SideLength)
                            print("Object class:",v_Flag_Class)
                            # 绿灯亮起：测量完成
                            led_control(2)
                        except:
                            print("The OLED screen has unstable power supply")
                elif v_Flag_Class == "rectangular":
                    # 输出尺寸
                    led_control(1)
                    time.sleep_ms(100)
                    led_control(0)
                    Object_cx,Object_cy,Object_w,Object_h,Flag = Ret2D_Detect(color_threshold,img)
                    v_Distance = Get_Distance()
                    SideLength = Size_Calculation(v_Distance,Object_w,Object_h,Flag)

                    add_list = i2c.scan()
                    if len(add_list) >= 1:
                        try:
                            OLED_Show(int(v_Distance),int(SideLength),v_Flag_Class)
                            print("range: mm ", v_Distance)
                            print("SideLength:mm",SideLength)
                            print("Object class:",v_Flag_Class)
                            # 绿灯亮起：测量完成
                            led_control(2)
                        except:
                            print("The OLED screen has unstable power supply")
                elif v_Flag_Class == "triangle":
                    # 输出尺寸
                    led_control(1)
                    time.sleep_ms(100)
                    led_control(0)
                    Object_cx,Object_cy,Object_w,Object_h,Flag = Triangle2D_Detect(color_threshold,img)
                    v_Distance = Get_Distance()
                    SideLength = Size_Calculation(v_Distance,Object_w,Object_h,Flag)

                    add_list = i2c.scan()
                    if len(add_list) >= 1:
                        try:
                            OLED_Show(int(v_Distance),int(SideLength),v_Flag_Class)
                            print("range: mm ", v_Distance)
                            print("SideLength:mm",SideLength)
                            print("Object class:",v_Flag_Class)
                            # 绿灯亮起：测量完成
                            led_control(2)
                        except:
                            print("The OLED screen has unstable power supply")
                else:
                    Show_Str("Could not find Object")
                    print("未检测到任何物体")
        else:
            if(servo_angle_count == 180):
                servo_angle_count = 0
                if(color_threshold == 2):
                    color_count = 0
                else:
                    color_count = color_count + 1
            tilt_servo.angle(90)
            time.sleep_ms(50)
            servo_angle_count = servo_angle_count + 1
            pan_servo.angle(servo_angle_count)

    print(clock.fps())
