import cv2
import numpy as np
import os

def augment_image(img, save_base_path):
    h, w = img.shape[:2]
    # 1. 旋转不同角度
    for angle in [-15, -10, -5, 0, 5, 10, 15]:
        M = cv2.getRotationMatrix2D((w/2, h/2), angle, 1)
        rotated = cv2.warpAffine(img, M, (w, h))
        cv2.imwrite(f"{save_base_path}_rot{angle}.jpg", rotated)
    # 2. 亮度调整（不同光线）
    for beta in [-40, -20, 0, 20, 40]:
        bright = cv2.convertScaleAbs(img, alpha=1, beta=beta)
        cv2.imwrite(f"{save_base_path}_bright{beta}.jpg", bright)
    # 3. 水平翻转（模拟左右不同角度）
    flipped = cv2.flip(img, 1)
    cv2.imwrite(f"{save_base_path}_flip.jpg", flipped)
    # 4. 轻微平移（模拟手部位置变化）
    for dx, dy in [(-15,0), (15,0), (0,-15), (0,15)]:
        M = np.float32([[1,0,dx], [0,1,dy]])
        shifted = cv2.warpAffine(img, M, (w, h))
        cv2.imwrite(f"{save_base_path}_shift{dx}_{dy}.jpg", shifted)

input_dir = "original_frames"
output_dir = "augmented_frames"
os.makedirs(output_dir, exist_ok=True)

for img_file in os.listdir(input_dir):
    if img_file.endswith(".jpg"):
        img_path = os.path.join(input_dir, img_file)
        img = cv2.imread(img_path)
        base_name = os.path.splitext(img_file)[0]
        save_base = os.path.join(output_dir, base_name)
        augment_image(img, save_base)

print("数据增强完成！增强后的图片在 augmented_frames 文件夹中")