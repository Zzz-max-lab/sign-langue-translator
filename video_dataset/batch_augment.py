import cv2
import os
import numpy as np

# ========== 配置参数 ==========
RAW_VIDEO_DIR = "raw_videos"          # 存放原始视频的文件夹
OUTPUT_DIR = "augmented_data"         # 增强图片输出根文件夹
FRAME_INTERVAL_SEC = 0.5              # 每隔0.5秒截一帧
START_OFFSET_SEC = 0.5                # 跳过视频开头0.5秒（准备动作）
END_OFFSET_SEC = -0.5                 # 跳过视频结尾0.5秒（收尾动作）
# ==============================

def extract_frames(video_path, interval_sec, start_sec, end_sec):
    """从视频中按时间间隔截取帧，返回帧列表（numpy数组）"""
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps <= 0:
        return []
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps

    start_frame = int(max(0, start_sec * fps))
    end_frame = int(min(total_frames - 1, (duration + end_sec) * fps))
    interval_frames = max(1, int(round(fps * interval_sec)))

    frames = []
    frame_id = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if start_frame <= frame_id <= end_frame:
            if (frame_id - start_frame) % interval_frames == 0:
                frames.append(frame)
        frame_id += 1
    cap.release()
    return frames

def augment_image(img, save_base_path):
    """对一张图片进行数据增强，保存多个变体"""
    h, w = img.shape[:2]
    # 1. 旋转
    for angle in [-15, -10, -5, 0, 5, 10, 15]:
        M = cv2.getRotationMatrix2D((w/2, h/2), angle, 1)
        rotated = cv2.warpAffine(img, M, (w, h))
        cv2.imwrite(f"{save_base_path}_rot{angle}.jpg", rotated)
    # 2. 亮度调整
    for beta in [-40, -20, 0, 20, 40]:
        bright = cv2.convertScaleAbs(img, alpha=1, beta=beta)
        cv2.imwrite(f"{save_base_path}_bright{beta}.jpg", bright)
    # 3. 水平翻转
    flipped = cv2.flip(img, 1)
    cv2.imwrite(f"{save_base_path}_flip.jpg", flipped)
    # 4. 平移
    for dx, dy in [(-15,0), (15,0), (0,-15), (0,15)]:
        M = np.float32([[1,0,dx], [0,1,dy]])
        shifted = cv2.warpAffine(img, M, (w, h))
        cv2.imwrite(f"{save_base_path}_shift{dx}_{dy}.jpg", shifted)

def main():
    if not os.path.exists(RAW_VIDEO_DIR):
        print(f"错误：找不到 {RAW_VIDEO_DIR} 文件夹，请先创建并放入mp4视频。")
        return

    # 获取所有mp4文件
    video_files = [f for f in os.listdir(RAW_VIDEO_DIR) if f.lower().endswith('.mp4')]
    if not video_files:
        print("错误：raw_videos 文件夹中没有找到 .mp4 文件。")
        return

    for video_file in video_files:
        # 手势标签 = 文件名去掉扩展名
        gesture = os.path.splitext(video_file)[0]
        video_path = os.path.join(RAW_VIDEO_DIR, video_file)

        print(f"正在处理: {video_file} (标签: {gesture})")

        # 截取帧
        frames = extract_frames(video_path, FRAME_INTERVAL_SEC, START_OFFSET_SEC, END_OFFSET_SEC)
        if not frames:
            print(f"  警告：{video_file} 没有截取到帧，跳过")
            continue

        # 为该手势创建输出文件夹
        gesture_out_dir = os.path.join(OUTPUT_DIR, gesture)
        os.makedirs(gesture_out_dir, exist_ok=True)

        # 对每一帧进行增强并保存
        for i, frame in enumerate(frames):
            base = os.path.join(gesture_out_dir, f"{gesture}_frame{i:02d}")
            augment_image(frame, base)

        print(f"  完成：共 {len(frames)} 帧，增强后图片保存在 {gesture_out_dir}")

    print("\n全部处理完成！增强图片位于:", OUTPUT_DIR)

if __name__ == "__main__":
    main()