import cv2
import os

video_path = r"D:\jisuanji\project\video\hello.mp4"
output_dir = r"original_frames"
os.makedirs(output_dir, exist_ok=True)

# 你要的原始帧号（对应第2、3、4张）
wanted_frames = [15, 30, 45]

cap = cv2.VideoCapture(video_path)
frame_id = 0
saved_count = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break
    if frame_id in wanted_frames:
        out_path = os.path.join(output_dir, f"frame_{saved_count:04d}.jpg")
        cv2.imwrite(out_path, frame)
        saved_count += 1
        print(f"已保存第 {frame_id} 帧")
    frame_id += 1

cap.release()
print(f"完成！共截取 {saved_count} 张图片")