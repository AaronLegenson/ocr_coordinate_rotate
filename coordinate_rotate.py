# -*- coding: utf-8 -*-

import numpy as np
import math


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


if __name__ == "__main__":
    test = {
        'orgHeight': 1000,
        'orgWidth': 900,
        'angle': 269.99,
        'x': 100, 'y': 700, 'w': 10, 'h': 10
    }
    # 入参和之前一致
    res_coordinate = coordinate_rotate_new(test)
    print(res_coordinate)
    # example: {'status': 0, 'message': 'Success', 'nodes': [[700, 900], [700, 890], [710, 890], [710, 900]]}
