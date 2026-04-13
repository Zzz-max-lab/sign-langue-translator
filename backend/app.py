import os
import pickle
import numpy as np
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import cv2
import mediapipe as mp

app = Flask(__name__)
CORS(app)  # 允许跨域请求

# ==================== 配置 ====================
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 限制10MB
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# ==================== 全局变量 ====================
model = None          # AI分类模型
scaler = None         # 数据标准化器
label_map = None      # 标签映射 {0: '你好', 1: '谢谢', ...}

# 初始化MediaPipe（手部关键点检测）
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=True,      # 图片模式（非视频流）
    max_num_hands=1,             # 只检测一只手
    min_detection_confidence=0.5 # 检测置信度阈值
)

# ==================== 辅助函数 ====================
def extract_features(image_path):
    """
    从图片提取手部关键点特征（42维）
    21个关键点 × (x, y) = 42个特征
    """
    # 读取图片
    img = cv2.imread(image_path)
    if img is None:
        return None
    
    # 转换为RGB（MediaPipe需要RGB格式）
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    result = hands.process(img_rgb)
    
    # 未检测到手部
    if not result.multi_hand_landmarks:
        return None
    
    # 提取第一只手的21个关键点坐标（只取x,y，不要z）
    landmarks = result.multi_hand_landmarks[0]
    features = []
    for lm in landmarks.landmark:
        features.append(lm.x)  # X坐标
        features.append(lm.y)  # Y坐标
        # 不添加lm.z，保持42维特征
    
    return features  # 返回长度为42的列表

def compress_image(image_path, max_size=640):
    """
    压缩图片，加快处理速度
    """
    img = cv2.imread(image_path)
    if img is None:
        return
    
    h, w = img.shape[:2]
    if max(w, h) > max_size:
        scale = max_size / max(w, h)
        new_w = int(w * scale)
        new_h = int(h * scale)
        img = cv2.resize(img, (new_w, new_h))
        cv2.imwrite(image_path, img)

# ==================== API接口 ====================
import base64  # 顶部导入这个库

@app.route('/predict', methods=['POST'])
def predict():
    """
    手势识别接口（适配前端JSON/base64格式）
    接收JSON格式的base64图片，返回识别结果
    """
    try:
        # 1. 接收前端发来的JSON数据
        data = request.get_json()
        if not data or 'image' not in data:
            return jsonify({'error': '请上传图片'}), 400
        
        base64_image = data['image']
        
        # 2. base64解码为图片
        try:
            # 去掉base64头（如果有的话）
            if ',' in base64_image:
                base64_image = base64_image.split(',')[1]
            img_data = base64.b64decode(base64_image)
            img_array = np.frombuffer(img_data, np.uint8)
            img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        except Exception as e:
            return jsonify({'error': f'图片解码失败: {str(e)}'}), 400
        
        if img is None:
            return jsonify({'error': '图片读取失败'}), 400
        
        # 3. 保存临时图片（适配原extract_features函数）
        filename = 'temp.jpg'
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        cv2.imwrite(filepath, img)
        
        # 4. 压缩图片（可选，加快速度）
        compress_image(filepath)
        
        # 5. 提取手部特征
        features = extract_features(filepath)
        os.remove(filepath)  # 删除临时文件
        
        if features is None:
            return jsonify({'error': '未检测到手部，请确保手部清晰可见'}), 400
        
        # 6. 特征数量检查（必须是42维）
        if len(features) != 42:
            return jsonify({'error': f'特征提取异常，期望42维，实际{len(features)}维'}), 500
        
        # 7. AI预测
        if model and scaler and label_map:
            # 标准化特征
            features_scaled = scaler.transform([features])
            # 预测标签
            pred_label = model.predict(features_scaled)[0]
            # 获取置信度
            proba = model.predict_proba(features_scaled)[0]
            confidence = float(max(proba))
            # 转换为文字
            result = label_map.get(int(pred_label), '未知')
        else:
            # 降级方案：返回默认结果
            result = '你好'
            confidence = 0.5
        
        # 8. 返回结果
        return jsonify({
            'word': result,
            'confidence': round(confidence, 2)
        })
    
    except Exception as e:
        return jsonify({'error': f'服务器错误: {str(e)}'}), 500


@app.route('/health', methods=['GET'])
def health():
    """健康检查接口"""
    return jsonify({
        'status': 'ok',
        'model_loaded': model is not None
    })


@app.route('/', methods=['GET'])
def index():
    """根路径接口"""
    return jsonify({
        'name': '手语识别API',
        'version': '2.0',
        'endpoints': ['/predict (POST)', '/health (GET)']
    })


# ==================== 启动服务 ====================
if __name__ == '__main__':
    # 加载AI模型
    try:
        with open('gesture_model.pkl', 'rb') as f:
            model = pickle.load(f)
        with open('scaler.pkl', 'rb') as f:
            scaler = pickle.load(f)
        with open('label_to_word.pkl', 'rb') as f:
            label_map = pickle.load(f)
        print('✅ AI模型加载成功')
    except FileNotFoundError as e:
        print(f'⚠️ 模型文件不存在: {e.filename}，将使用模拟模式')
    except Exception as e:
        print(f'❌ 模型加载失败: {e}，将使用模拟模式')
    
    # 启动Flask服务
    print('🚀 服务启动: http://0.0.0.0:5000')
    app.run(host='0.0.0.0', port=5000, debug=True)