/**
 * 格式化工具函数
 */

/**
 * 格式化数字
 */
export const formatNumber = (num: number, options?: {
  precision?: number;
  unit?: string;
  separator?: string;
}): string => {
  const { precision = 2, unit = '', separator = ',' } = options || {};

  if (num === 0) return `0${unit}`;

  let value = num;
  let suffix = '';

  // 大数字简化
  if (Math.abs(num) >= 1e8) {
    value = num / 1e8;
    suffix = '亿';
  } else if (Math.abs(num) >= 1e4) {
    value = num / 1e4;
    suffix = '万';
  }

  const formatted = value.toFixed(precision).replace(/\B(?=(\d{3})+(?!\d))/g, separator);
  return `${formatted}${suffix}${unit}`;
};

/**
 * 格式化货币
 */
export const formatCurrency = (
  amount: number,
  options?: {
    currency?: string;
    precision?: number;
    showSymbol?: boolean;
  }
): string => {
  const { currency = '¥', precision = 2, showSymbol = true } = options || {};

  const formatted = amount.toFixed(precision).replace(/\B(?=(\d{3})+(?!\d))/g, ',');
  return showSymbol ? `${currency}${formatted}` : formatted;
};

/**
 * 格式化百分比
 */
export const formatPercent = (
  value: number,
  options?: {
    precision?: number;
    showSign?: boolean;
    multiplyBy?: number;
  }
): string => {
  const { precision = 2, showSign = true, multiplyBy = 100 } = options || {};

  const percentValue = value * multiplyBy;
  const formatted = percentValue.toFixed(precision);

  if (showSign && percentValue > 0) {
    return `+${formatted}%`;
  } else if (showSign && percentValue < 0) {
    return `${formatted}%`;
  } else {
    return `${formatted}%`;
  }
};

/**
 * 格式化日期时间
 */
export const formatDateTime = (
  date: Date | string,
  options?: {
    format?: string;
    locale?: string;
  }
): string => {
  const { format = 'YYYY-MM-DD HH:mm:ss', locale = 'zh-CN' } = options || {};

  const dateObj = typeof date === 'string' ? new Date(date) : date;

  // 简单的格式化实现
  const year = dateObj.getFullYear();
  const month = String(dateObj.getMonth() + 1).padStart(2, '0');
  const day = String(dateObj.getDate()).padStart(2, '0');
  const hours = String(dateObj.getHours()).padStart(2, '0');
  const minutes = String(dateObj.getMinutes()).padStart(2, '0');
  const seconds = String(dateObj.getSeconds()).padStart(2, '0');

  return format
    .replace('YYYY', year.toString())
    .replace('MM', month)
    .replace('DD', day)
    .replace('HH', hours)
    .replace('mm', minutes)
    .replace('ss', seconds);
};

/**
 * 格式化日期
 */
export const formatDate = (date: Date | string): string => {
  return formatDateTime(date, { format: 'YYYY-MM-DD' });
};

/**
 * 格式化时间
 */
export const formatTime = (date: Date | string): string => {
  return formatDateTime(date, { format: 'HH:mm:ss' });
};

/**
 * 格式化相对时间
 */
export const formatRelativeTime = (date: Date | string): string => {
  const dateObj = typeof date === 'string' ? new Date(date) : date;
  const now = new Date();
  const diffMs = now.getTime() - dateObj.getTime();
  const diffSeconds = Math.floor(diffMs / 1000);
  const diffMinutes = Math.floor(diffSeconds / 60);
  const diffHours = Math.floor(diffMinutes / 60);
  const diffDays = Math.floor(diffHours / 24);

  if (diffDays > 0) {
    return `${diffDays}天前`;
  } else if (diffHours > 0) {
    return `${diffHours}小时前`;
  } else if (diffMinutes > 0) {
    return `${diffMinutes}分钟前`;
  } else if (diffSeconds > 0) {
    return `${diffSeconds}秒前`;
  } else {
    return '刚刚';
  }
};

/**
 * 格式化文件大小
 */
export const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 B';

  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));

  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`;
};

/**
 * 格式化股票代码
 */
export const formatStockCode = (code: string): string => {
  // 确保股票代码格式正确
  if (!code) return '';

  // 移除可能的后缀，然后重新添加
  const cleanCode = code.replace(/\.(SH|SZ|BJ)$/i, '');

  // 根据代码前缀判断市场
  if (/^(000|001|002|003|300)/.test(cleanCode)) {
    return `${cleanCode}.SZ`;
  } else if (/^(600|601|603|605|688)/.test(cleanCode)) {
    return `${cleanCode}.SH`;
  } else if (/^(8|4)/.test(cleanCode)) {
    return `${cleanCode}.BJ`;
  } else {
    return code; // 保持原样
  }
};

/**
 * 格式化交易量
 */
export const formatVolume = (volume: number): string => {
  return formatNumber(volume, { unit: '股' });
};

/**
 * 格式化成交额
 */
export const formatTurnover = (turnover: number): string => {
  return formatCurrency(turnover, { showSymbol: false, unit: '元' });
};

/**
 * 格式化涨跌
 */
export const formatChange = (change: number, percent: number): {
  amount: string;
  percent: string;
  color: string;
} => {
  const color = change > 0 ? 'red' : change < 0 ? 'green' : 'default';
  const sign = change > 0 ? '+' : '';

  return {
    amount: `${sign}${formatCurrency(change)}`,
    percent: `${sign}${formatPercent(percent)}`,
    color,
  };
};

/**
 * 格式化技术指标值
 */
export const formatIndicatorValue = (
  value: number,
  indicator: string
): string => {
  switch (indicator.toUpperCase()) {
    case 'RSI':
    case 'WR':
    case 'CCI':
      return `${value.toFixed(2)}`;
    case 'MACD':
      return formatCurrency(value, { showSymbol: false, precision: 4 });
    case 'KDJ':
      return `${value.toFixed(2)}`;
    case 'BOLL':
      return formatCurrency(value, { showSymbol: false });
    case 'ATR':
      return formatCurrency(value, { showSymbol: false });
    default:
      return value.toFixed(2);
  }
};

/**
 * 格式化手机号
 */
export const formatPhoneNumber = (phone: string): string => {
  const cleaned = phone.replace(/\D/g, '');

  if (cleaned.length === 11) {
    return `${cleaned.slice(0, 3)}-${cleaned.slice(3, 7)}-${cleaned.slice(7)}`;
  }

  return phone;
};

/**
 * 格式化银行卡号
 */
export const formatBankCard = (cardNumber: string): string => {
  const cleaned = cardNumber.replace(/\D/g, '');
  const masked = cleaned.slice(0, 4) + ' **** **** ' + cleaned.slice(-4);
  return masked;
};

/**
 * 格式化ID卡号
 */
export const formatIdCard = (idCard: string): string => {
  if (idCard.length === 18) {
    return idCard.slice(0, 6) + '********' + idCard.slice(-4);
  } else if (idCard.length === 15) {
    return idCard.slice(0, 6) + '*****' + idCard.slice(-4);
  }
  return idCard;
};

/**
 * 格式化价格区间
 */
export const formatPriceRange = (min: number, max: number): string => {
  if (min === max) {
    return formatCurrency(min);
  }
  return `${formatCurrency(min)} - ${formatCurrency(max)}`;
};

/**
 * 格式化时间区间
 */
export const formatTimeRange = (start: Date | string, end: Date | string): string => {
  const startTime = formatTime(start);
  const endTime = formatTime(end);
  return `${startTime} - ${endTime}`;
};

/**
 * 格式化数字为中文大写
 */
export const formatNumberToChinese = (num: number): string => {
  const digits = ['零', '一', '二', '三', '四', '五', '六', '七', '八', '九'];
  const units = ['', '十', '百', '千', '万', '十', '百', '千', '亿'];

  if (num === 0) return '零';

  let result = '';
  let strNum = Math.abs(num).toString();

  for (let i = 0; i < strNum.length; i++) {
    const digit = parseInt(strNum[i]);
    const unit = units[strNum.length - 1 - i];

    if (digit !== 0) {
      result += digits[digit] + unit;
    } else {
      // 处理零的情况
      const nextDigit = i < strNum.length - 1 ? parseInt(strNum[i + 1]) : 0;
      if (nextDigit !== 0 && !result.endsWith('零')) {
        result += '零';
      }
    }
  }

  return num < 0 ? `负${result}` : result;
};

/**
 * 格式化JSON字符串
 */
export const formatJSON = (obj: any, indent: number = 2): string => {
  try {
    return JSON.stringify(obj, null, indent);
  } catch (error) {
    return String(obj);
  }
};