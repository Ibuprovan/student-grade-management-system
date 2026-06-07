/// <reference types="vite/client" />

declare module '*.vue' {
  import type { DefineComponent } from 'vue'
  const component: DefineComponent<{}, {}, any>
  export default component
}

declare module 'element-plus/dist/locale/zh-cn.mjs' {
  const zhCn: {
    name: string
    el: Record<string, any>
  }
  export default zhCn
}

/** 用户角色类型 */
type UserRole = 'admin' | 'teacher' | 'student'

/** Vue 自定义指令声明 */
declare module 'vue' {
  interface ComponentCustomProperties {
    /** 权限指令：根据用户角色控制元素显示 */
    'v-permission': UserRole | UserRole[]
  }
}
