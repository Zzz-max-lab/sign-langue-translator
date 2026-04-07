from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import base64
from werkzeug.utils import secure_filename
from datetime import datetime

# 初始化Flask应用
app = Flask(__name__)
CORS(app)

# 配置上传文件夹
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 历史记录存储
history = []

# 模拟AI模型
def mock_predict(image_path):
    return {"word": "模拟识别结果", "confidence": 0.95}

# 实际预测函数（暂时用mock，等AI同学接入真实模型）
def real_predict(image_path):
    # 这里等待AI同学导入真实模型后替换
    return mock_predict(image_path)

# 尝试导入AI同学的真实模型
try:
    from ai_model import predict as ai_predict
    def real_predict(image_path):
        result = ai_predict(image_path)
        return {"word": result["word"], "confidence": result["confidence"]}
    print("✅ 成功加载AI真实模型")
except Exception as e:
    print(f"⚠️ AI模型加载失败，使用模拟模式: {e}")

# 健康检查接口
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "message": "Flask后端服务运行正常",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

# 测试接口
@app.route('/hello', methods=['GET'])
def hello():
    return "Hello Flask后端启动成功！"

# 预测接口（核心）
@app.route('/predict', methods=['POST'])
def predict():
    # 检查是否有文件上传
    if 'image' not in request.files:
        return jsonify({"error": "No image part"}), 400
    
    file = request.files['image']
    
    # 检查文件名是否为空
    if file.filename == '':
        return jsonify({"error": "Empty filename"}), 400
    
    # 安全处理文件名并保存
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # 调用AI预测
        result = real_predict(filepath)
        
        # 保存历史记录
        history.append({
            "word": result["word"],
            "confidence": result["confidence"],
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        
        return jsonify(result)
    
    return jsonify({"error": "Upload failed"}), 500

# 历史记录接口
@app.route('/history', methods=['GET'])
def get_history():
    return jsonify(history[-20:])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)