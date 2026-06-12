/**
 * 批量导入相关 API
 */

import request from './index'

/**
 * 批量导入学生
 * @param formData 包含文件的 FormData 对象
 * @returns 导入结果
 */
export function importStudents(formData: FormData) {
  return request.post<any, any>('/import/students', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

/**
 * 预览导入数据
 * @param formData 包含文件的 FormData 对象
 * @returns 预览结果
 */
export function previewImport(formData: FormData) {
  return request.post<any, any>('/import/students/preview', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

/**
 * 下载导入模板
 * @param format 模板格式：'xlsx' 或 'csv'
 * @returns 模板文件 Blob
 */
export function downloadTemplate(format: 'xlsx' | 'csv' = 'xlsx') {
  return request.get<any, Blob>('/import/students/template', {
    params: { format },
    responseType: 'blob'
  })
}
