Page({
  onLoad() {
    console.log('首页加载');
  },

  goToCamera() {
    wx.switchTab({
      url: '/pages/camera/camera'
    });
  },

  goToHistory() {
    wx.switchTab({
      url: '/pages/history/history'
    });
  }
});