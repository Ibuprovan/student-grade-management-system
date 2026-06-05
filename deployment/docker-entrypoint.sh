#!/bin/bash
# 后端容器入口脚本
# 负责初始化数据库和启动应用

set -e

echo "=========================================="
echo "  学生成绩管理系统 - 后端服务启动中..."
echo "=========================================="

# 等待数据库就绪（如果使用外部数据库）
# 如果使用 SQLite，此步骤可跳过
# while ! nc -z db 5432; do
#   echo "等待数据库就绪..."
#   sleep 1
# done

# 确保数据目录存在
mkdir -p /app/data

# 初始化数据库
echo "正在初始化数据库..."
python -c "from src.core.database import init_db; init_db()" || {
    echo "数据库初始化失败，尝试使用 Alembic 迁移..."
    # 如果有 Alembic，使用迁移
    # alembic upgrade head
}

# 检查环境变量
APP_NAME=${APP_NAME:-"学生成绩管理系统"}
DEBUG=${DEBUG:-"false"}
BACKEND_HOST=${BACKEND_HOST:-"0.0.0.0"}
BACKEND_PORT=${BACKEND_PORT:-8000}

echo "应用名称: $APP_NAME"
echo "调试模式: $DEBUG"
echo "监听地址: $BACKEND_HOST:$BACKEND_PORT"
echo "=========================================="

# 启动应用
# 使用 exec 替换当前进程，确保信号正确传递
exec uvicorn src.main:app \
    --host "$BACKEND_HOST" \
    --port "$BACKEND_PORT" \
    --workers 1 \
    --log-level info
