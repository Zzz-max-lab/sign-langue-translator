import { addHistory } from '../../utils/historyUtil.js';

Page({
  data: {
    showPreview: false,
    isProcessing: false,
    photoPath: ''
  },

  // 拍照
  takePhoto() {
    if (this.data.showPreview) return;
    
    const ctx = wx.createCameraContext();
    ctx.takePhoto({
      quality: 'high',
      success: (res) => {
        this.setData({
          photoPath: res.tempImagePath,
          showPreview: true
        });
      }
    });
  },

  // 从相册选择
  chooseFromAlbum() {
    wx.chooseImage({
      count: 1,
      sizeType: ['compressed'],
      sourceType: ['album'],
      success: (res) => {
        this.setData({
          photoPath: res.tempFilePaths[0],
          showPreview: true
        });
      }
    });
  },

  // 重新拍摄
  resetCamera() {
    this.setData({
      showPreview: false,
      photoPath: ''
    });
  },

  // 确认使用照片 - 调用后端接口
  confirmPhoto() {
    if (!this.data.photoPath) return;
    
    this.setData({ isProcessing: true });
    
    // 1. 压缩图片
    wx.compressImage({
      src: this.data.photoPath,
      quality: 50,
      success: (compressRes) => {
        // 2. 转 base64
        wx.getFileSystemManager().readFile({
          filePath: compressRes.tempFilePath,
          encoding: 'base64',
          success: (base64Res) => {
            // 3. 调用后端接口
            this.callBackendAPI(base64Res.data);
          },
          fail: (err) => {
            this.setData({ isProcessing: false });
            wx.showToast({ title: '图片处理失败', icon: 'none' });
          }
        });
      },
      fail: () => {
        this.setData({ isProcessing: false });
        wx.showToast({ title: '压缩失败', icon: 'none' });
      }
    });
  },

  // 调用后端接口
  callBackendAPI(base64Image) {
    const app = getApp();
    
    wx.request({
      url: app.globalData.apiBaseUrl + '/predict',  // 后端给的接口地址
      method: 'POST',
      header: {
        'Content-Type': 'application/json'
      },
      data: {
        image: base64Image,
        // 如果需要其他参数，在这里加
      },
      success: (res) => {
        this.setData({ isProcessing: false });
        
        if (res.statusCode === 200 && res.data) {
          // 假设后端返回 { word: '你好', confidence: 0.95 }
          const result = {
            word: res.data.word || '识别成功',
            confidence: res.data.confidence || 0
          };
          
          getApp().globalData.recognizeResult = result;
          wx.navigateTo({ url: '/pages/result/result' });
        } else {
          wx.showToast({ title: '识别失败', icon: 'none' });
        }
      },
      fail: (err) => {
        console.error('请求失败', err);
        this.setData({ isProcessing: false });
        wx.showToast({ title: '网络错误', icon: 'none' });
      }
    });
  },

  onCameraError(err) {
    console.error('相机错误', err);
  }
});