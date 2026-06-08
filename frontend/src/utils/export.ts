/**
 * 通用导出工具函数
 * 提供 CSV 导出等通用数据导出能力
 */

/**
 * 转义 CSV 字段
 * 处理包含逗号、双引号、换行符的字段
 * @param field 字段值
 * @returns 转义后的字段字符串
 */
function escapeCSVField(field: string | number): string {
  const str = String(field)
  if (str.includes(',') || str.includes('"') || str.includes('\n')) {
    return `"${str.replace(/"/g, '""')}"`
  }
  return str
}

/**
 * 下载 CSV 文件
 * @param headers 表头数组
 * @param rows 数据行（每行为字段值数组）
 * @param filename 文件名（不含日期后缀和扩展名）
 */
export function downloadCSV(
  headers: string[],
  rows: (string | number)[][],
  filename: string,
): void {
  const csvContent = [
    headers.join(','),
    ...rows.map((row) => row.map(escapeCSVField).join(',')),
  ].join('\n')

  const blob = new Blob(['\ufeff' + csvContent], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = `${filename}_${new Date().toISOString().slice(0, 10)}.csv`
  link.click()
  URL.revokeObjectURL(link.href)
}
