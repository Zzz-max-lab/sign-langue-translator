from flask import Flask, request, jsonify
from flask_cors import CORS  # 引入CORS
import os
import base64
from werkzeug.utils import secure_filename
from datetime import datetime

# 初始化Flask应用
app = Flask(__name__)

# 允许跨域
CORS(app)

# 配置上传文件夹
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 历史记录存储
history = []

# 模拟AI模型 (初期返回固定结果)
# def mock_predict(image_path):
#     return {"word": "你好", "confidence": 0.95}

# 等待AI同学导入真实模型
try:
    # 这里会在AI同学提交代码后生效
    from ai_model import predict as ai_predict
    
    def real_predict(image_path):
        """调用AI模型预测"""
        result = ai_predict(image_path)
        return {"word": result, "confidence": 0.9}
except ImportError:
    # 如果AI模型还没准备好，使用mock
    def real_predict(image_path):
        return {"word": "AI模型加载中...", "confidence": 0.0}

@app.route('/hello')
def hello():
    return "Hello Flask 后端启动成功！"

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
        
        # 调用AI预测接口
        result = real_predict(filepath)
        
        # 保存历史记录
        history.append({
            "word": result["word"],
            "confidence": result["confidence"],
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        
        return jsonify(result)
    
    return jsonify({"error": "Upload failed"}), 500

@app.route('/history', methods=['GET'])
def get_history():
    # 返回最近20条记录
    return jsonify(history[-20:])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)