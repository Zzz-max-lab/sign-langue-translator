Page({
  data: { result: '', isRecognizing: false },
  onReady() {
    this.ctx = wx.createCameraContext();
    this.timer = setInterval(() => {
      if (this.data.isRecognizing) return;
      this.data.isRecognizing = true;
      this.ctx.takePhoto({
        quality: 'low',
        success: (res) => {
          this.uploadImage(res.tempImagePath);
        },
        fail: () => { this.data.isRecognizing = false; }
      });
    }, 1000);
  },
  uploadImage(filePath) {
    wx.uploadFile({
      url: 'http://你的后端IP:5000/predict',
      filePath: filePath,
      name: 'image',
      success: (res) => {
        const data = JSON.parse(res.data);
        this.setData({ result: data.word });
        this.data.isRecognizing = false;
      },
      fail: () => { this.data.isRecognizing = false; }
    });
  },
  onUnload() {
    clearInterval(this.timer);
  }
})