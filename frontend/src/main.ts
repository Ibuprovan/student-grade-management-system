import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'
import { permissionDirective } from './directives/permission'

// 导入 Element Plus 基础样式（确保我们的 CSS 变量覆盖生效）
import 'element-plus/dist/index.css'
import './assets/styles/global.scss'

// 创建 Vue 应用实例
const app = createApp(App)

// 注册 Pinia 状态管理
const pinia = createPinia()
app.use(pinia)

// 注册路由
app.use(router)

// 注册全局指令
app.directive('permission', permissionDirective)

// Element Plus 按需导入已通过 unplugin-vue-components 和 unplugin-auto-import 自动配置
// 中文语言包在 App.vue 中通过 ElConfigProvider 使用

// 挂载应用
app.mount('#app')
