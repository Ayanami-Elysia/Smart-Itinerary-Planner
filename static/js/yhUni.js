
// 公共弹窗提示函数
function showMessage(message, type = 'success', duration = 3000) {
  // 移除可能已存在的消息框
  $('.message-box').remove();

  // 根据类型设置样式
  let bgColor, icon;
  switch(type) {
      case 'success':
          bgColor = '#4CAF50';
          icon = '✓';
          break;
      case 'error':
          bgColor = '#F44336';
          icon = '✗';
          break;
      case 'warning':
          bgColor = '#FF9800';
          icon = '⚠';
          break;
      case 'info':
          bgColor = '#2196F3';
          icon = 'ℹ';
          break;
      default:
          bgColor = '#4CAF50';
          icon = '✓';
  }
}