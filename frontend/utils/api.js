// ========== 配置区 =========
const BASE_URL = 'https://egomaniac-gutter-obtuse.ngrok-free.dev'
// ========== 核心函数 ==========

/**
 * 识别手语图片
 * @param {string} filePath 图片临时路径
 * @returns {Promise<{word: string, confidence: number}>}
 */
const recognizeSign = (filePath) => {
  return new Promise((resolve, reject) => {
    // 1. 先压缩图片
    wx.compressImage({
      src: filePath,
      quality: 80,
      success: (compressRes) => {
        doUpload(compressRes.tempImagePath, resolve, reject);
      },
      fail: () => {
        // 压缩失败用原图
        doUpload(filePath, resolve, reject);
      }
    });
  });
};

/**
 * 实际上传
 */
const doUpload = (filePath, resolve, reject) => {
  wx.uploadFile({
    url: BASE_URL +'/predict',
    filePath: filePath,
    name: 'image',
    method:'POST',
    timeout: 30000,
    success: (res) => {
      try {
        const data = res.data; // 不用 JSON.parse
        resolve({
          word: data.gesture || '识别失败',
          confidence: data.confidence || 0
        });
      } catch (e) {
        reject(new Error('解析响应失败'));
      }
    },
    fail: (err) => {
      console.error('上传失败', err);
      reject(new Error('网络请求失败，请检查后端服务'));
    }
  });
};

/**
 * 测试后端连通性
 */
const testConnection = () => {
  return new Promise((resolve, reject) => {
    wx.request({
      url: `${BASE_URL}/health`,
      method: 'GET',
      timeout: 5000,
      success: () => resolve(true),
      fail: () => reject(false)
    });
  });
};

module.exports = { recognizeSign, testConnection, BASE_URL };