from PIL import Image
import numpy as np
import cv2
import matplotlib.pyplot as plt
import pathlib
import pandas as pd


def find_leftmost_subarray(arr, threshold):
    n = len(arr)
    left = None
    right = None
    
    i = 0
    while i < n:
        if arr[i] > threshold:
            left = i
            j = i
            while j < n and arr[j] > threshold:
                j += 1
            right = j - 1
            return (left, right)  
        i += 1
    
    return (None, None)



def detect_sudden_change(arr, threshold):
    n = len(arr)

    diff = np.diff(arr)

    jump_up = np.where(diff > threshold)[0]
    jump_down = np.where(diff < -threshold)[0]
    
    changes = []

    for idx in jump_up:
        changes.append({
            'index': idx,
            'from': arr[idx],
            'to': arr[idx+1],
            'change': diff[idx],
            'type': 'jump_up'
        })
    
    for idx in jump_down:
        changes.append({
            'index': idx,
            'from': arr[idx],
            'to': arr[idx+1],
            'change': diff[idx],
            'type': 'jump_down'
        })
    
    return changes



def genereate_xy_from_curve(curve_arr,y_axis = (30, 92), x_axis=(2000, 350)):
    y, x = curve_arr.shape

    y_axis_discrete = np.linspace(y_axis[0], y_axis[1], curve_arr.shape[0])[::-1]
    x_axis_discrete = np.linspace(x_axis[1], x_axis[0], curve_arr.shape[1])[::-1]

    output = []
    for temp_x in range(x):
        delta_curve = curve_arr[:, temp_x]

        if np.sum(delta_curve>0) == 0:
            continue
        elif np.sum(delta_curve>0) > len(delta_curve) / 2:
            continue

        nonzero_idx = np.where(delta_curve != 0)[0]
        gaps = np.where(np.diff(nonzero_idx) > 1)[0] + 1
        blocks = np.split(nonzero_idx, gaps)
        blocks = [block.tolist() for block in blocks]

        if len(blocks) > 1:
            temp_blocks = [block for block in blocks if len(block) > 1]
            if len(temp_blocks) > 0:
                blocks = temp_blocks

        block = blocks[-1]
        y_coord = y_axis_discrete[block]
        if len(y_coord) == 0:
            continue
        elif  len(y_coord) % 2 == 1:
            y_coord = y_coord[len(y_coord)//2]
        else:
            y_coord = (y_coord[len(y_coord)//2 - 1] + y_coord[len(y_coord)//2]) / 2

        output.append((x_axis_discrete[temp_x], y_coord))

    return output

def crop_to_axes_auto(image_path, output_path):
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    edges = cv2.Canny(gray, 50, 150)
    
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=100, 
                           minLineLength=100, maxLineGap=10)
    
    if lines is not None:
        left_x = img.shape[1]
        right_x = 0
        top_y = img.shape[0]
        bottom_y = 0
        
        for line in lines:
            x1, y1, x2, y2 = line[0]
            if abs(x1 - x2) < 10:
                left_x = min(left_x, x1, x2)
                right_x = max(right_x, x1, x2)
            if abs(y1 - y2) < 10:
                top_y = min(top_y, y1, y2)
                bottom_y = max(bottom_y, y1, y2)
        
        cropped = img[top_y+3:bottom_y-3, left_x+3:right_x-3]
        cv2.imwrite(output_path, cropped)
        return cropped
    
    return None


def process_image(image_path, gray_threshold=(70,255), y_axis_range=(22,108), x1_axis_range=(7900,2000), x2_axis_range=(2000,350)):

    image_path = pathlib.Path(image_path)
    image_name = image_path.stem

    img = cv2.imread(image_path)
    if img is None:
        return None
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, gray_threshold[0], gray_threshold[1], cv2.THRESH_BINARY_INV)
    cv2.imwrite(f"{image_name}_binary.png", binary)
    
    output = binary

    for i in range(output.shape[1]):
        if np.sum(output[:, i]>0) > output.shape[0]/2:
            left = i
            break
    output1 = output[:, left + 1:]
    output2 = output[:, :left]

    out = genereate_xy_from_curve(output1, y_axis=y_axis_range, x_axis=x2_axis_range)
    out2 = genereate_xy_from_curve(output2,  y_axis=y_axis_range, x_axis=x1_axis_range)

    cv2.imwrite(f"{image_name}_cut_2000_0.png", output1)
    cv2.imwrite(f"{image_name}_7500_2000.png", output2)


    x = [point[0] for point in out]
    y = [point[1] for point in out]

    x2 = [point[0] for point in out2]
    y2 = [point[1] for point in out2]

    fig, axes = plt.subplots(1, 2, figsize=(15, 6),sharey=True)

    axes[1].plot(x, y, 'o-', linewidth=2, markersize=1, color='#23BAC5', label='2000-350')
    axes[1].invert_xaxis()
    axes[1].set_xlabel('X')
    axes[1].set_ylabel('Y')
    axes[1].set_title('1')
    axes[1].grid(True, alpha=0.3)
    axes[1].legend()

    axes[0].plot(x2, y2, 'o-', linewidth=2, markersize=1, color='#FD763F', label='7900-2000')
    axes[0].invert_xaxis()
    axes[0].set_xlabel('X')
    axes[0].set_ylabel('Y')
    axes[0].set_title('2')
    axes[0].grid(True, alpha=0.3)
    axes[0].legend()

    plt.tight_layout()
    plt.savefig(f"{image_name}_output.png", dpi=500)


    df_x = [round(i,2) for i in x2 + x]
    df_y = [round(i,2) for i in y2 + y]

    df = pd.DataFrame({
    'X ax': df_x,
    'Y ax': df_y
    })


    return f"{image_name}_output.png", df

def main(image_path, gray_threshold=(70,255), y_axis_range=(22,108), x1_axis_range=(7900,2000), x2_axis_range=(2000,350)):
    img_path = pathlib.Path(image_path)
    crop_path = img_path.parent / f"{img_path.stem}_cropped.png"
    crop_to_axes_auto(image_path, crop_path)
    output_path = process_image(crop_path, gray_threshold, y_axis_range, x1_axis_range, x2_axis_range)
    return output_path


if __name__ == "__main__":
    # 四乙基米氏酮  (16,96)
    # 隐色结晶紫   (30,93)
    # BCIM        (22,112)

    for name, ax in zip(["四乙基3"], [(16,96)]):
        img_path = f"{name}.png"
        crop_path = f"{name}_cropped.png"
        crop_to_axes_auto(img_path,crop_path)
        result = main(crop_path,y_axis_range=ax)

        print("draw complete for", name)
