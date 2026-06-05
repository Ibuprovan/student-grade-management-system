/**
 * 表单验证工具
 * 通用验证规则和自定义校验函数
 */

import type { FormItemRule } from 'element-plus'

/** 学号格式：8位数字（4位年份 + 4位序号） */
const STUDENT_ID_PATTERN = /^\d{8}$/

/** 手机号格式 */
const PHONE_PATTERN = /^1[3-9]\d{9}$/

/** 邮箱格式 */
const EMAIL_PATTERN = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/

/**
 * 必填验证规则
 * @param message 提示信息
 * @param trigger 触发方式
 */
export function requiredRule(message: string, trigger: 'blur' | 'change' = 'blur'): FormItemRule {
  return { required: true, message, trigger }
}

/**
 * 学号验证规则
 */
export const studentIdRules: FormItemRule[] = [
  requiredRule('请输入学号'),
  {
    pattern: STUDENT_ID_PATTERN,
    message: '学号格式错误，应为8位数字（如：20260001）',
    trigger: 'blur',
  },
]

/**
 * 姓名验证规则
 */
export const nameRules: FormItemRule[] = [
  requiredRule('请输入姓名'),
  {
    min: 2,
    max: 20,
    message: '姓名长度应在 2 到 20 个字符之间',
    trigger: 'blur',
  },
]

/**
 * 班级验证规则
 */
export const classNameRules: FormItemRule[] = [
  requiredRule('请输入班级'),
  {
    min: 2,
    max: 20,
    message: '班级名称长度应在 2 到 20 个字符之间',
    trigger: 'blur',
  },
]

/**
 * 分数验证规则
 */
export const scoreRules: FormItemRule[] = [
  requiredRule('请输入分数'),
  {
    type: 'number',
    min: 0,
    max: 100,
    message: '分数应在 0 到 100 之间',
    trigger: 'blur',
  },
]

/**
 * 入学年份验证规则
 */
export const enrollmentYearRules: FormItemRule[] = [
  requiredRule('请选择入学年份'),
  {
    type: 'number',
    min: 2000,
    max: 2100,
    message: '入学年份应在 2000 到 2100 之间',
    trigger: 'change',
  },
]

/**
 * 验证学号格式
 * @param value 学号值
 * @returns 是否有效
 */
export function isValidStudentId(value: string): boolean {
  return STUDENT_ID_PATTERN.test(value)
}

/**
 * 验证手机号格式
 * @param value 手机号值
 * @returns 是否有效
 */
export function isValidPhone(value: string): boolean {
  return PHONE_PATTERN.test(value)
}

/**
 * 验证邮箱格式
 * @param value 邮箱值
 * @returns 是否有效
 */
export function isValidEmail(value: string): boolean {
  return EMAIL_PATTERN.test(value)
}

/**
 * 验证分数范围
 * @param score 分数
 * @returns 是否在有效范围内
 */
export function isValidScore(score: number): boolean {
  return score >= 0 && score <= 100
}

/**
 * 自定义学号校验器
 * @param _rule 规则（未使用）
 * @param value 值
 * @param callback 回调
 */
export function validateStudentId(
  _rule: unknown,
  value: string,
  callback: (error?: Error) => void,
): void {
  if (!value) {
    callback(new Error('请输入学号'))
    return
  }
  if (!STUDENT_ID_PATTERN.test(value)) {
    callback(new Error('学号格式错误，应为8位数字（如：20260001）'))
    return
  }
  const year = parseInt(value.substring(0, 4))
  if (year < 2000 || year > 2100) {
    callback(new Error('学号年份部分应在2000-2100之间'))
    return
  }
  callback()
}

/**
 * 自定义分数校验器
 * @param _rule 规则（未使用）
 * @param value 值
 * @param callback 回调
 */
export function validateScore(
  _rule: unknown,
  value: number | string,
  callback: (error?: Error) => void,
): void {
  const score = typeof value === 'string' ? parseFloat(value) : value
  if (isNaN(score)) {
    callback(new Error('请输入有效的分数'))
    return
  }
  if (score < 0 || score > 100) {
    callback(new Error('分数应在 0 到 100 之间'))
    return
  }
  callback()
}
