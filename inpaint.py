import cv2
import numpy as np
import pytesseract
from PIL import Image
import re

def extract_axis_scale_ocr(image_path):
    """
    使用OCR识别坐标轴的刻度值
    """
    # 读取图片
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # 增强对比度
    gray = cv2.equalizeHist(gray)
    
    # 分别提取x轴和y轴区域
    height, width = gray.shape
    
    # Y轴区域（左侧）
    y_axis_region = gray[int(height*0.2):int(height*0.9), :int(width*0.15)]
    
    # X轴区域（底部）
    x_axis_region = gray[int(height*0.85):height, int(width*0.1):int(width*0.9)]
    
    # 使用OCR识别文本
    y_text = pytesseract.image_to_string(y_axis_region, config='--psm 6')
    x_text = pytesseract.image_to_string(x_axis_region, config='--psm 6')
    
    # 提取数字
    y_numbers = re.findall(r'\d+\.?\d*', y_text)
    x_numbers = re.findall(r'\d+\.?\d*', x_text)
    
    # 转换为浮点数
    y_values = [float(n) for n in y_numbers]
    x_values = [float(n) for n in x_numbers]
    
    return {
        'x_axis_values': x_values,
        'y_axis_values': y_values,
        'x_range': (min(x_values), max(x_values)) if x_values else None,
        'y_range': (min(y_values), max(y_values)) if y_values else None
    }

# 使用
scale_info = extract_axis_scale_ocr('spectrum.png')
print(f"X轴范围: {scale_info['x_range']}")
print(f"Y轴范围: {scale_info['y_range']}")