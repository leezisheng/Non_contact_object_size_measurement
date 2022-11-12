# -*- coding: UTF-8 -*-
'''
@Project ：曲线拟合 
@File    ：train.py
@Author  ：leeqingshui
@Date    ：2022/11/11 3:32 
'''
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import axes3d
import math

from model import Polynomial
from sklearn.model_selection import train_test_split

# =========================================全局变量==============================================

# 直径列表
Z = [565, 565, 565, 565, 565, 565, 565, 565, 484, 484, 484, 484, 484, 484, 484, 484, 400, 400, 400, 400, 400, 400,
     400, 400, 310, 310, 310, 310, 310, 310, 310, 310]
# 距离列表
Y = [800, 1058, 1435, 1718, 2040, 2400, 2680, 2950, 800, 1058, 1435, 1718, 2040, 2400, 2680, 2950, 800, 1058, 1435,
     1718, 2040, 2400, 2680, 2950, 800, 1058, 1435, 1718, 2040, 2400, 2680, 2950]
# 像素列表
X = [93, 71, 52, 44, 37, 32, 29, 25, 79, 60, 45, 36, 31, 27, 24, 21, 66, 50, 37, 31, 26, 22, 20, 17, 50, 38, 28, 25,
     20, 17, 15, 14]

# ======================================绘制三维可视化图表========================================

# 创建一个图框
fig = plt.figure()
ax = fig.add_subplot(projection='3d')

ax.set_xlabel('Weight(mm)')
ax.set_ylabel('Distance(mm)')
ax.set_zlabel('pixels')

ax.scatter(X, Y, Z, c='r',label='Scatter plot of CO2 concentration')

ax.legend()

plt.show()

# ======================================训练拟合曲线模型========================================

# 建立训练器模型
train_model = Polynomial(
                         temp_list = X,      # 直径列表
                         verify_list = Y,    # 距离列表
                         cc_list = Z,        # 像素列表
                         poly_degree = 2     # 多项式次数
                         )

# 训练后模型
poly_model = train_model.train_model(save_model_dir = 'C:\\Users\\lee\\Desktop\\电赛\\2022山西省电赛\\非接触尺寸测量\\曲线拟合'+"\\")

# 模型预测
predict_pixels_list = train_model.predict_model(
                                            test_temp_list = X,
                                            test_verify_list = Y,
                                            )
for data in predict_pixels_list:
    data = abs(data)

print(predict_pixels_list)

# ======================================绘制三维可视化图表========================================

# +++++++++++++++++++++++++++++++++预测结果与实际结果对比散点图++++++++++++++++++++++++++++++++++++
# 创建一个图框
fig = plt.figure()
ax = fig.add_subplot(projection='3d')

x = X
y = Y
z = Z
p = predict_pixels_list

ax.set_xlabel('Weight(mm)')
ax.set_ylabel('Distance(mm)')
ax.set_zlabel('pixels')

ax.scatter(x, y, z, c='r',label='Scatter plot of true pixels')
ax.scatter(x, y, p, c='b',label='Scatter plot of predict pixels')

ax.legend()

plt.show()

# ======================================评估模型========================================
# 计算MSE
MSE = train_model.evaluate_model(Z , predict_pixels_list)
