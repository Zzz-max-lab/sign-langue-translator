let historyList = [];

export function getHistory() {
  return historyList;
}

export function clearHistory() {
  historyList = [];
}

export function deleteRecord(id) {
  historyList = historyList.filter(item => item.id !== id);
}

export function addHistory(item) {
  historyList.unshift(item);
}