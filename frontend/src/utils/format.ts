/**
 * 格式化工具函数
 * 日期、数字、分数等格式化
 */

/**
 * 格式化日期
 * @param date 日期字符串或 Date 对象
 * @param format 格式模板，默认 'YYYY-MM-DD'
 * @returns 格式化后的日期字符串
 */
export function formatDate(date: string | Date | null | undefined, format = 'YYYY-MM-DD'): string {
  if (!date) return '-'

  const d = typeof date === 'string' ? new Date(date) : date

  if (isNaN(d.getTime())) return '-'

  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  const hours = String(d.getHours()).padStart(2, '0')
  const minutes = String(d.getMinutes()).padStart(2, '0')
  const seconds = String(d.getSeconds()).padStart(2, '0')

  return format
    .replace('YYYY', String(year))
    .replace('MM', month)
    .replace('DD', day)
    .replace('HH', hours)
    .replace('mm', minutes)
    .replace('ss', seconds)
}

/**
 * 格式化日期时间
 * @param date 日期字符串或 Date 对象
 * @returns 格式化后的日期时间字符串
 */
export function formatDateTime(date: string | Date | null | undefined): string {
  return formatDate(date, 'YYYY-MM-DD HH:mm:ss')
}

/**
 * 格式化分数
 * @param score 分数
 * @param decimals 小数位数，默认 1
 * @returns 格式化后的分数字符串
 */
export function formatScore(score: number | null | undefined, decimals = 1): string {
  if (score === null || score === undefined) return '-'
  return score.toFixed(decimals)
}

/**
 * 格式化百分比
 * @param value 百分比值（0-100）
 * @param decimals 小数位数，默认 1
 * @returns 格式化后的百分比字符串
 */
export function formatPercent(value: number | null | undefined, decimals = 1): string {
  if (value === null || value === undefined) return '-'
  return `${value.toFixed(decimals)}%`
}

/**
 * 获取分数等级
 * @param score 分数
 * @returns 等级文本
 */
export function getScoreLevel(score: number): string {
  if (score >= 90) return '优秀'
  if (score >= 80) return '良好'
  if (score >= 70) return '中等'
  if (score >= 60) return '及格'
  return '不及格'
}

/**
 * 获取分数对应的颜色
 * @param score 分数
 * @returns 颜色值
 */
export function getScoreColor(score: number): string {
  if (score >= 90) return '#67C23A'  // 优秀 - 绿色
  if (score >= 80) return '#409EFF'  // 良好 - 蓝色
  if (score >= 70) return '#E6A23C'  // 中等 - 橙色
  if (score >= 60) return '#909399'  // 及格 - 灰色
  return '#F56C6C'                   // 不及格 - 红色
}

/**
 * 格式化文件大小
 * @param bytes 字节数
 * @returns 格式化后的文件大小
 */
export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 B'

  const units = ['B', 'KB', 'MB', 'GB', 'TB']
  const k = 1024
  const i = Math.floor(Math.log(bytes) / Math.log(k))

  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${units[i]}`
}

/**
 * 截断文本
 * @param text 原始文本
 * @param maxLength 最大长度
 * @param suffix 后缀，默认 '...'
 * @returns 截断后的文本
 */
export function truncateText(text: string, maxLength: number, suffix = '...'): string {
  if (!text || text.length <= maxLength) return text
  return text.substring(0, maxLength) + suffix
}

/**
 * 格式化数字（千分位）
 * @param num 数字
 * @returns 格式化后的数字字符串
 */
export function formatNumber(num: number | null | undefined): string {
  if (num === null || num === undefined) return '-'
  return num.toLocaleString('zh-CN')
}
