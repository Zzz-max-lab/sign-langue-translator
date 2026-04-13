import { getHistory, clearHistory, deleteRecord } from '../../utils/historyUtil.js';

Page({
  data: {
    historyList: [],
    isEditMode: false
  },

  onShow() {
    this.loadHistory();
  },

  loadHistory() {
    this.setData({
      historyList: getHistory()
    });
  },

  toggleEditMode() {
    this.setData({
      isEditMode: !this.data.isEditMode
    });
  },

  clearAll() {
    wx.showModal({
      title: '确认清空',
      content: '所有历史记录将被删除，无法恢复',
      confirmColor: '#e64340',
      success: (res) => {
        if (res.confirm) {
          clearHistory();
          this.loadHistory();
          this.setData({ isEditMode: false });
          wx.showToast({ title: '已清空', icon: 'success' });
        }
      }
    });
  },

  deleteItem(e) {
    const id = e.currentTarget.dataset.id;
    wx.showModal({
      title: '删除',
      content: '确定删除这条记录吗？',
      success: (res) => {
        if (res.confirm) {
          deleteRecord(id);
          this.loadHistory();
          wx.showToast({ title: '已删除', icon: 'success' });
        }
      }
    });
  },

  viewDetail(e) {
    const item = e.currentTarget.dataset.item;
    wx.navigateTo({
      url: `/pages/result/result?word=${encodeURIComponent(item.word)}&confidence=${item.confidence}`
    });
  },

  goToCamera() {
    wx.switchTab({
      url: '/pages/camera/camera'
    });
  }
});