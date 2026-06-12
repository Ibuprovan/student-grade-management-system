/**
 * 批量导入相关 API
 */

import { upload, get } from '@/utils/request'

/**
 * 批量导入学生
 * @param formData 包含文件的 FormData 对象
 * @returns 导入结果
 */
export function importStudents(formData: FormData) {
  return upload<any>('/import/students', formData)
}

/**
 * 预览导入数据
 * @param formData 包含文件的 FormData 对象
 * @returns 预览结果
 */
export function previewImport(formData: FormData) {
  return upload<any>('/import/students/preview', formData)
}

/**
 * 下载导入模板
 * @param format 模板格式：'xlsx' 或 'csv'
 * @returns 模板文件 Blob
 */
export function downloadTemplate(format: 'xlsx' | 'csv' = 'xlsx') {
  return get<Blob>('/import/students/template', {
    params: { format },
    responseType: 'blob'
  })
}
