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

# 配置上传文件夹
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB限制
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp'}

# 创建上传文件夹
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# 加载AI模型（全局变量）
model = None
scaler = None
label_to_word = None  # 新增：用于将数字标签映射为文字

# 初始化MediaPipe手部检测
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=True,
    max_num_hands=1,
    min_detection_confidence=0.5
)

def allowed_file(filename):
    """检查文件扩展名是否合法"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_hand_landmarks(image_path):
    """提取手部关键点特征"""
    image = cv2.imread(image_path)
    if image is None:
        return None
    
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = hands.process(image_rgb)
    
    if not results.multi_hand_landmarks:
        return None
    
    hand_landmarks = results.multi_hand_landmarks[0]
    features = []
    for landmark in hand_landmarks.landmark:
        features.extend([landmark.x, landmark.y, landmark.z])
    
    return features

@app.route('/predict', methods=['POST'])
def predict():
    """手势识别接口（最终版）"""
    try:
        # 1. 检查请求是否包含图片
        if 'image' not in request.files:
            return jsonify({'error': '没有上传图片'}), 400
        file = request.files['image']

        # 2. 检查文件名
        if file.filename == '':
            return jsonify({'error': '文件名为空'}), 400

        # 3. 检查文件类型
        if not allowed_file(file.filename):
            return jsonify({'error': '不支持的文件类型'}), 400

        # 4. 保存临时图片
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # 5. 提取特征
        features = extract_hand_landmarks(filepath)
        os.remove(filepath)  # 删除临时文件
        
        if features is None:
            return jsonify({'error': '未检测到手部'}), 400

        # 6. 手势预测
        prediction = None
        confidence = 0.0
        
        if model is not None and scaler is not None:
            # 使用真实AI模型预测
            features_scaled = scaler.transform([features])
            prediction = model.predict(features_scaled)[0]
            confidence = float(np.max(model.predict_proba(features_scaled)[0]))
        else:
            # 模拟预测（降级方案）
            prediction = predict_simple(features)
            confidence = 0.7

        # 7. 转换为文字结果
        result = "未知手势"
        if label_to_word is not None:
            # 使用AI同学提供的映射表
            result = label_to_word.get(int(prediction), f"手势{prediction}")
        else:
            # 备用映射表
            gesture_map = {0: '你好', 1: '谢谢', 2: '再见', 3: '是', 4: '否', 5: '帮助'}
            result = gesture_map.get(int(prediction), f"手势{prediction}")

        # 8. 返回结果
        return jsonify({
            'success': True,
            'gesture': result,
            'confidence': round(confidence, 2),
            'prediction': int(prediction)
        })

    except Exception as e:
        return jsonify({'error': f"服务器错误: {str(e)}"}), 500

def predict_simple(features):
    """简单的手势判断规则（备用）"""
    if len(features) < 2:
        return 0
    wrist_x = features[0]
    if wrist_x < 0.3:
        return 0  # 你好
    elif wrist_x > 0.7:
        return 1  # 谢谢
    else:
        return 2  # 再见

@app.route('/health', methods=['GET'])
def health():
    """健康检查接口"""
    return jsonify({
        'status': 'ok', 
        'model_loaded': model is not None,
        'label_mapping_loaded': label_to_word is not None
    })

@app.route('/', methods=['GET'])
def index():
    """首页接口"""
    return jsonify({
        'name': '手语识别API',
        'version': '2.0',
        'endpoints': {
            'predict': '/predict (POST)',
            'health': '/health (GET)'
        }
    })

if __name__ == '__main__':
    # 加载模型（放在启动前，确保启动时变量已定义）
    try:
        with open('gesture_model.pkl', 'rb') as f:
            model = pickle.load(f)
        with open('scaler.pkl', 'rb') as f:
            scaler = pickle.load(f)
        with open('label_to_word.pkl', 'rb') as f:
            label_to_word = pickle.load(f)
        print("✅ 成功加载真实AI模型及标签映射！")
    except FileNotFoundError as e:
        print(f"⚠️  未找到模型文件: {e.filename}，将使用模拟模式运行")
    except Exception as e:
        print(f"❌ 模型加载失败: {e}，将使用模拟模式运行")
    
    # 启动服务
    print("🚀 启动Flask服务...")
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)