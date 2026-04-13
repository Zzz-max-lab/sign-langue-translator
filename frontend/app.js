App({
  onLaunch: function () {
    console.log('App启动 - 使用后端API模式');
    // 不需要 wx.cloud.init 了
  },
  
  globalData: {
    userInfo: null,
    recognizeResult: null,
    apiBaseUrl: 'http://192.168.40.233:5000'  // 改成后端给的地址
  }
});