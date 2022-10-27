import sensor, image, time

from pid import PID
from pyb import Servo

pan_servo=Servo(1)# P7  底
tilt_servo=Servo(2)# P8 台

pan_servo.calibration(500,2500,500)  #底  500-2500  中心值1500
tilt_servo.calibration(500,2500,500) #台

red_threshold  = (11, 48, 14, 127, -12, 127)  #颜色阈值

#pan_pid = PID(p=0.07, i=0, imax=90) #脱机运行或者禁用图像传输，使用这个PID
#tilt_pid = PID(p=0.05, i=0, imax=90) #脱机运行或者禁用图像传输，使用这个PID
pan_pid = PID(p=0.1, i=0, imax=90)#在线调试使用这个PID
tilt_pid = PID(p=0.1, i=0, imax=90)#在线调试使用这个PID

sensor.reset() # 初始化摄像机传感器。
sensor.set_pixformat(sensor.RGB565) # 使用RGB565
sensor.set_framesize(sensor.QQVGA) # 速度使用QQVGA
sensor.skip_frames(10) # 让新设置生效。
sensor.set_auto_whitebal(False) # 关白平衡。。。。（导致每次开机都会自动搞出一个颜色，颜色识别会有问题）
#水平方向翻转
sensor.set_hmirror(True)
#垂直方向翻转
sensor.set_vflip(True)

clock = time.clock() # 跟踪FPS。赋值clock为现在的fps，超级低

def find_max(blobs):
    max_size=0
    for blob in blobs:
        if blob[2]*blob[3] > max_size:
            max_blob=blob
            max_size = blob[2]*blob[3]
    return max_blob


while(True):
    clock.tick() #跟踪快照之间经过的毫秒数().
    img = sensor.snapshot() # 拍一张照片，然后返回图像。

    blobs = img.find_blobs([red_threshold])  #赋值blobs为找到红色像素的值
    if blobs:
        max_blob = find_max(blobs)          #找最大的色块
        #print("cx: ", max_blob.cx())             #打印X的的位置
        #print("cy: ", max_blob.cy())             #打印Y的的位置
        pan_error = max_blob.cx()-img.width()/2    #底的误差为最大色块所在的X轴-宽（宽固定=160  /2=80）我理解为取XY中心点
        tilt_error = max_blob.cy()-img.height()/2  #台的误差为最大色块所在的Y轴-高（120）

#        print("pan_error: ", pan_error)             #打印底的偏差
        print("tilt_error: ", tilt_error)             #打印台的偏差
        '比如说现在X的距离是159 目标中心偏差159-img.width()/2=79'

        img.draw_rectangle(max_blob.rect()) # 矩形
        img.draw_cross(max_blob.cx(), max_blob.cy()) # cx, cy 交叉

        pan_output=pan_pid.get_pid(pan_error,1)/2    #底的转动=获取的PID值    get_pid(self, error, scaler)/2
        tilt_output=tilt_pid.get_pid(tilt_error,1)   #台的转动=获取的PID值    get_pid(self, error, scaler) 也可以除以2 走慢一点罢了
        '可以这样子理解，这个pid的函数是想使偏差=0'
#        print("pan_output",pan_output)
        print("tilt_output",tilt_output)
        pan_servo.angle(pan_servo.angle()-  pan_output)    #底部舵机转动的角度为上一个角度+现在的输出(偏差)角度
        tilt_servo.angle(tilt_servo.angle()+tilt_output) #上面舵机转动的角度为上一个角度-现在的输出(偏差)角度  因为是倒转 所以是减
        print("tilt_servo.angle:",tilt_servo.angle())

