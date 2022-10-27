#实验名称：人脸检测
#翻译和注释：01Studio
#参考链接：http://blog.sipeed.com/p/675.html

import sensor,lcd,time
import KPU as kpu

#设置摄像头
sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
#sensor.set_vflip(1)    #设置摄像头后置

lcd.init() #LCD初始化

clock = time.clock()

#1、从Flash加载模型。将模型烧录到开发板Flash。烧录方法参考pdf教程。
#task = kpu.load(0x300000) 

#2、从SD加载模型卡上。将kmodel文件通过读卡器拷贝到SD卡。
task = kpu.load("/sd/facedetect.kmodel") 

#模型描参数
anchor = (1.889, 2.5245, 2.9465, 3.94056, 3.99987, 5.3658, 5.155437, 6.92275, 6.718375, 9.01025)

#初始化yolo2网络
a = kpu.init_yolo2(task, 0.5, 0.3, 5, anchor)

while(True):
    clock.tick()
    img = sensor.snapshot()
    code = kpu.run_yolo2(task, img) #运行yolo2网络

    #识别到人脸就画矩形表示
    if code:
        for i in code:
            print(i)
            b = img.draw_rectangle(i.rect())

    #LCD显示
    lcd.display(img)

    print(clock.fps())   #打印FPS
