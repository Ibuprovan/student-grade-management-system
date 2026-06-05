# 前端 Dockerfile - 学生成绩管理系统
# 多阶段构建：构建阶段 + 生产阶段

# ============================================
# 构建阶段 - 编译前端资源
# ============================================
FROM node:18-alpine as builder

# 设置工作目录
WORKDIR /app

# 设置 pnpm 镜像源（可选，国内加速）
# RUN npm config set registry https://registry.npmmirror.com

# 安装 pnpm
RUN npm install -g pnpm

# 复制依赖文件（利用缓存层）
COPY package.json pnpm-lock.yaml* ./

# 安装依赖
RUN pnpm install --frozen-lockfile || pnpm install

# 复制源代码
COPY . .

# 构建应用
RUN pnpm build

# ============================================
# 生产阶段 - Nginx 服务
# ============================================
FROM nginx:alpine

# 安装 curl 用于健康检查
RUN apk add --no-cache curl

# 删除默认配置
RUN rm /etc/nginx/conf.d/default.conf

# 复制 Nginx 配置
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 复制构建产物
COPY --from=builder /app/dist /usr/share/nginx/html

# 创建缓存目录
RUN mkdir -p /var/cache/nginx/client_temp && \
    chown -R nginx:nginx /var/cache/nginx

# 暴露端口
EXPOSE 80

# 健康检查
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:80/health || exit 1

# 启动 Nginx
CMD ["nginx", "-g", "daemon off;"]
