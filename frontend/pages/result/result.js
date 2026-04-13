Page({
  data: {
    word: '',
    confidence: 0
  },

  onLoad() {
    const app = getApp();
    const result = app.globalData.recognizeResult;
    
    if (result) {
      this.setData({
        word: result.word,
        confidence: result.confidence
      });
    }
  },

  continueRecognize() {
    wx.navigateBack({ delta: 1 });
  },

  viewHistory() {
    wx.navigateTo({ url: '/history/history' });
  }
});