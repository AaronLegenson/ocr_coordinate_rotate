OCR_COORDINATE_ROTATE项目 说明文档
===========================
该文档用于说明coordinate_rotate.py坐标旋转函数的设计思路与算法介绍，以便将来的维护与拓展工作。

****
	
|项目|OCR_COORDINATE_ROTATE|
|:--:|:--:|
|版本|v2.0|
|负责人|徐恩泽|
|完成时间|2021-05-27|


****
## 目录
* [一、概述](#一、概述)
* [二、算法说明](#二、算法说明)
    * 2.1 问题说明
    * 2.2 点坐标求解
    * 2.3 直线解析式求解
    * 2.4 点到直线距离求解
* [三、代码简析](#三、代码简析)
    * 2.5 函数`dis_spot_to_line(x0, y0, a, b)`
    * 2.6 函数`coordinate_rotate(params)`

****


## 一、概述

坐标旋转函数的说明文档。坐标旋转函数的设计是为了解决一个图片旋转前后坐标参数的转换问题。给出原始图片高宽、旋转角、旋转后图片中区域坐标，返回在原始图片中该区域坐标。以下为详细说明。

****
## 二、算法说明

![pic](https://raw.githubusercontent.com/AaronLegenson/ocr_coordinate_rotate_pic/master/rotate_3.png)

### 2.1 问题说明
```
如图所示，原图片ABCD，AB为正上边；新图片PQRS，PQ为正上边（在原图片基础上顺时针转过α角）；XYZW为图片中原本倾斜的文字段。
已知：
（1）原图片的高h0，宽w0
（2）旋转角α（单位：度，即π/180）
（3）XYZW相对P的坐标位置(x, y, w, h)，表示点X在PQRS上相对P的坐标为(x, y)，然后矩形XYZW的宽XY=w，高XW=h
求解：
（1）XYZW四个点在原图ABCD上的相对A的坐标值, 即这四个点分别与AB和AD的距离
```

### 2.2 建立坐标系
```
我们不妨先考虑旋转角α落在[0, 90)的情形，之后再将结果推广到[90, 180), [180, 270), [270, 360)的所有情况。
以新图片左下的点S为原点，SR为X轴正方向，SP为Y轴正方向建立平面直角坐标系。
```

### 2.3 点坐标求解
```
由已知, 容易求得:
PQ = SR = h0·sinα + w0·cosα
PS = QR = h0·cosα + w0·sinα

进而得到外圈坐标PQRS:
P(0, h0·cosα + w0·sinα)
Q(h0·sinα + w0·cosα, h0·cosα + w0·sinα)
R(h0·sinα + w0·cosα, 0)
S(0, 0)

外圈坐标ABCD:
A(0, h0·cosα)
B(w0·cosα, h0·cosα + w0·sinα)
C(h0·sinα + w0·cosα, w0·sinα)
D(h0·sinα, 0)

内圈坐标XYZW:
X(x, h0·cosα + w0·sinα - y)
Y(x + w, h0·cosα + w0·sinα - y)
Z(x + w, h0·cosα + w0·sinα - y - h)
W(x, h0·cosα + w0·sinα - y - h)
```

### 2.4 直线解析式求解
```
由已知ABCD坐标, 推得直线AB, BC, CD, DA的解析式:
AB: tanα / (h·cosα)·X - 1 / (h·cosα)·Y + 1 = 0
BC: - cosα / (h·cosα·sinα + w)·X - sinα / (h·cosα·sinα + w)·Y + 1 = 0
CD: - 1 / (h·sinα)·X + 1 / (h·sinα·tanα)·Y + 1 = 0
DA: - 1 / (h·sinα)·X - 1 / (h·cosα)·Y + 1 = 0
```

### 2.5 旋转前原始坐标求解
```
由点P(x0, y0)到直线l: aX + bY + 1 = 0的点到直线距离公式:
dis(P, l) = |(a·x0 + b·y0 + 1) / √(a^2 + b^2)|

在α落在[0, 90)的情况下, 只需代入以上公式分别计算XYZW四个点到直线DA和AB的距离, 即XYZW在原图片ABCD上的坐标即可.
当α落在其它区间中时，在以上过程基础上稍加推广即可得到对应结果.
特别注意, 当α落在其它区间中时, 不仅参考边(即上例中的D和AB)会发生改变, 对应的h0和w0会发生对换.
```

## 三、代码简析

### 函数`dis_spot_to_line(x0, y0, a, b)`
```
即对应2.5中提及的点到直线距离公式，不再赘述。

def dis_spot_to_line(x0, y0, a, b):
    """
    点(x0, y0)到直线ax + by + 1 = 0的距离
    :param x0:
    :param y0:
    :param a:
    :param b:
    :return: 四舍五入到整数
    """
    return round(abs((a * x0 + b * y0 + 1) / math.sqrt(a ** 2 + b ** 2)))
```

### 函数`coordinate_rotate(params)`
```
即主体函数接口。

def coordinate_rotate_new(params):
    """
    给出orgHeight, orgWidth, angle, x, y, w, h, 返回原始图中对应窗格的x, y, w, h
    :param params: 旋转后的参数，以json/dict形式传入
    :return: 原始图中对应窗格的四点坐标nodes(二维数组, 顺时针序), status(0为成功, -1为失败), message
    输入值的example: {'orgHeight': 1000, 'orgWidth': 900, 'angle': 269.99, 'x': 100, 'y': 700, 'w': 10, 'h': 10}
    返回值的example: {'status': 0, 'message': 'Success', 'nodes': [[700, 900], [700, 890], [710, 890], [710, 900]]}
    """
    org_height, org_width, angle = params.get("orgHeight"), params.get("orgWidth"), params.get("angle")
    x, y, w, h = params.get("x"), params.get("y"), params.get("w"), params.get("h")
    status = 0
    message = "Success"
    angle_type = (angle // 90) % 4  # 余数表示angle落在[0, 90), [90, 180), [180, 270), [270, 360)中的哪个区间上
    # print("angle_type:", angle_type)
    if angle % 90 == 0:  # 旋转角为90的整数倍，为避免计算式中分母出现0的情况，作特判处理，也比较简单
        if angle_type == 0:  # 对应0
            nodes_res = [
                [x, y],
                [x + w, y],
                [x + w, y + h],
                [x, y + h]
            ]
        elif angle_type == 1:  # 对应90
            nodes_res = [
                [org_width - y, x],
                [org_width - y, x + w],
                [org_width - y - h, x + w],
                [org_width - y - h, x]
            ]
        elif angle_type == 2:  # 对应180
            nodes_res = [
                [org_width - x, org_height - y],
                [org_width - x - w, org_height - y],
                [org_width - x - w, org_height - y - h],
                [org_width - x, org_height - y - h]
            ]
        else:  # angle_type == 3:  对应270
            nodes_res = [
                [y, org_height - x],
                [y, org_height - x - w],
                [y + h, org_height - x - w],
                [y + h, org_height - x]
            ]
    else:  # 旋转角不为90的整数倍，即一般情况
        nodes_res = []
        if angle_type == 0:  # 对应[0, 90)
            angle_delta = angle
            h_real, w_real = org_height, org_width
        elif angle_type == 1:  # 对应[90, 180)
            angle_delta = angle - 90.0
            h_real, w_real = org_width, org_height
        elif angle_type == 2:  # 对应[180, 270)
            angle_delta = angle - 180
            h_real, w_real = org_height, org_width
        else:  # angle_type == 3:  对应[270, 360)
            angle_delta = angle - 270.0
            h_real, w_real = org_width, org_height
        cos = math.cos(angle_delta / 180.0 * np.pi)
        sin = math.sin(angle_delta / 180.0 * np.pi)
        tan = math.tan(angle_delta / 180.0 * np.pi)
        # 依序分别为点A,B,C,D的坐标
        nodes = [
            (x, h_real * cos + w_real * sin - y),  # A坐标
            (x + w, h_real * cos + w_real * sin - y),  # B坐标
            (x + w, h_real * cos + w_real * sin - y - h),  # C坐标
            (x, h_real * cos + w_real * sin - y - h),  # D坐标
        ]
        # 直线解析式，即直线解析式Ax+By+1=0的(A,B)tuple
        lines = [
            (- 1 / (h_real * sin), - 1 / (h_real * cos)),  # DA
            (tan / (h_real * cos), - 1 / (h_real * cos)),  # AB
            (- cos / (h_real * cos * sin + w_real), - sin / (h_real * cos * sin + w_real)),  # BC
            (- 1 / (h_real * sin), 1 / (h_real * sin * tan))  # CD
        ]
        if angle_type == 0:  # [0, 90)情况下参考的直线分别为DA和AB
            for node in nodes:
                nodes_res.append([dis_spot_to_line(node[0], node[1], lines[0][0], lines[0][1]),
                                  dis_spot_to_line(node[0], node[1], lines[1][0], lines[1][1])])
        elif angle_type == 1:  # [90, 180)情况下参考的直线分别为CD和DA
            for node in nodes:
                nodes_res.append([dis_spot_to_line(node[0], node[1], lines[3][0], lines[3][1]),
                                  dis_spot_to_line(node[0], node[1], lines[0][0], lines[0][1])])
        elif angle_type == 2:  # [180, 270)情况下参考的直线分别为BC和CD
            for node in nodes:
                nodes_res.append([dis_spot_to_line(node[0], node[1], lines[2][0], lines[2][1]),
                                  dis_spot_to_line(node[0], node[1], lines[3][0], lines[3][1])])
        elif angle_type == 3:  # [270, 360)情况下参考的直线分别为AB和BC
            for node in nodes:
                nodes_res.append([dis_spot_to_line(node[0], node[1], lines[1][0], lines[1][1]),
                                  dis_spot_to_line(node[0], node[1], lines[2][0], lines[2][1])])
    result = {
        "status": status,  # 状态，当前版本下值为0，即成功
        "message": message,  # 附加信息，当前版本下值为"Success"
        "nodes": nodes_res  # 以json格式返回结果
    }
    # 输入值的example: {'orgHeight': 1000, 'orgWidth': 900, 'angle': 269.99, 'x': 100, 'y': 700, 'w': 10, 'h': 10}
    # 返回值的example: {'status': 0, 'message': 'Success', 'nodes': [[700, 900], [700, 890], [710, 890], [710, 900]]}
    return result
```
