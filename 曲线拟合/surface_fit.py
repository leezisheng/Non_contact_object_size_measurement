# -*- coding: UTF-8 -*-
'''
@Project ：曲面拟合
@File    ：curve_fit.py
@Author  ：leeqingshui
@Date    ：2022/11/11 3:03
'''
from matplotlib import pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm

# 处理符号问题
def fun(x):
    np.round(x,2)
    if x>=0: return '+'+str(x)
    else: return str(x)

# 求解系数
def get_res(X, Y, Z, n):
    # 求方程系数
    sigma_x = 0
    for i in X: sigma_x += i
    sigma_y = 0
    for i in Y: sigma_y += i
    sigma_z = 0
    for i in Z: sigma_z += i
    sigma_x2 = 0
    for i in X: sigma_x2 += i * i
    sigma_y2 = 0
    for i in Y: sigma_y2 += i * i
    sigma_x3 = 0
    for i in X: sigma_x3 += i * i * i
    sigma_y3 = 0
    for i in Y: sigma_y3 += i * i * i
    sigma_x4 = 0
    for i in X: sigma_x4 += i * i * i * i
    sigma_y4 = 0
    for i in Y: sigma_y4 += i * i * i * i
    sigma_x_y = 0
    for i in range(n):
        sigma_x_y += X[i] * Y[i]
    # print(sigma_xy)
    sigma_x_y2 = 0
    for i in range(n): sigma_x_y2 += X[i] * Y[i] * Y[i]
    sigma_x_y3 = 0
    for i in range(n): sigma_x_y3 += X[i] * Y[i] * Y[i] * Y[i]
    sigma_x2_y = 0
    for i in range(n): sigma_x2_y += X[i] * X[i] * Y[i]
    sigma_x2_y2 = 0
    for i in range(n): sigma_x2_y2 += X[i] * X[i] * Y[i] * Y[i]
    sigma_x3_y = 0
    for i in range(n): sigma_x3_y += X[i] * X[i] * X[i] * Y[i]
    sigma_z_x2 = 0
    for i in range(n): sigma_z_x2 += Z[i] * X[i] * X[i]
    sigma_z_y2 = 0
    for i in range(n): sigma_z_y2 += Z[i] * Y[i] * Y[i]
    sigma_z_x_y = 0
    for i in range(n): sigma_z_x_y += Z[i] * X[i] * Y[i]
    sigma_z_x = 0
    for i in range(n): sigma_z_x += Z[i] * X[i]
    sigma_z_y = 0
    for i in range(n): sigma_z_y += Z[i] * Y[i]
    # print("-----------------------")
    # 给出对应方程的矩阵形式
    a = np.array([[sigma_x4, sigma_x3_y, sigma_x2_y2, sigma_x3, sigma_x2_y, sigma_x2],
                  [sigma_x3_y, sigma_x2_y2, sigma_x_y3, sigma_x2_y, sigma_x_y2, sigma_x_y],
                  [sigma_x2_y2, sigma_x_y3, sigma_y4, sigma_x_y2, sigma_y3, sigma_y2],
                  [sigma_x3, sigma_x2_y, sigma_x_y2, sigma_x2, sigma_x_y, sigma_x],
                  [sigma_x2_y, sigma_x_y2, sigma_y3, sigma_x_y, sigma_y2, sigma_y],
                  [sigma_x2, sigma_x_y, sigma_y2, sigma_x, sigma_y, n]])
    b = np.array([sigma_z_x2, sigma_z_x_y, sigma_z_y2, sigma_z_x, sigma_z_y, sigma_z])
    # 高斯消元解线性方程
    res = np.linalg.solve(a, b)
    return res

def matching_3D(X, Y, Z):
    n = len(X)
    res = get_res(X, Y, Z, n)
    # 输出方程形式
    print("z=%.6s*x^2%.6s*xy%.6s*y^2%.6s*x%.6s*y%.6s" % (
    fun(res[0]), fun(res[1]), fun(res[2]), fun(res[3]), fun(res[4]), fun(res[5])))
    # 画曲面图和离散点
    fig = plt.figure()  # 建立一个空间
    ax = fig.add_subplot(111, projection='3d')  # 3D坐标

    n = 256
    u = np.linspace(0, 3000, n)  # 创建一个等差数列
    x, y = np.meshgrid(u, u)  # 转化成矩阵

    # 给出方程
    z = res[0] * x * x + res[1] * x * y + res[2] * y * y + res[3] * x + res[4] * y + res[5]
    # 画出曲面
    ax.plot_surface(x, y, z, rstride=3, cstride=3, cmap=cm.jet)
    # 画出点
    ax.scatter(X, Y, Z, c='r')
    plt.show()
    return res[0],res[1],res[2],res[3],res[4],res[5]

# 计算误差
def Measure_Error(X, Y, Z, temp_res_0,temp_res_1,temp_res_2,temp_res_3,temp_res_4,temp_res_5):
    temp_Z_list = []
    for i in range(len(X)):
        temp_Z_list.append(temp_res_0*X[i]*X[i]-temp_res_1*X[i]*Y[i]+temp_res_2*Y[i]*Y[i]+temp_res_3*X[i]-temp_res_4*Y[i]+temp_res_5)
    for i in range(len(X)):
        print("predict: "+str(temp_Z_list[i])+"true: "+str(Z[i]))

#主函数
if __name__ == '__main__':
    # 直径列表
    Z = [565, 565, 565, 565, 565, 565, 565, 565, 484, 484, 484, 484, 484, 484, 484, 484, 400, 400, 400, 400, 400, 400,
         400, 400, 310, 310, 310, 310, 310, 310, 310, 310]
    # 距离列表
    Y = [800, 1058, 1435, 1718, 2040, 2400, 2680, 2950, 800, 1058, 1435, 1718, 2040, 2400, 2680, 2950, 800, 1058, 1435,
         1718, 2040, 2400, 2680, 2950, 800, 1058, 1435, 1718, 2040, 2400, 2680, 2950]
    # 像素列表
    X = [93, 71, 52, 44, 37, 32, 29, 25, 79, 60, 45, 36, 31, 27, 24, 21, 66, 50, 37, 31, 26, 22, 20, 17, 50, 38, 28, 25,
         20, 17, 15, 14]

    res_0,res_1,res_2,res_3,res_4,res_5 = matching_3D(X, Y, Z)
    Measure_Error(X, Y, Z, res_0, res_1, res_2, res_3, res_4, res_5)
