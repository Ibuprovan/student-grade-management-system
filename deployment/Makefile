# ============================================
# 学生成绩管理系统 - Makefile
# 封装常用 Docker 和部署命令
# ============================================

.PHONY: help build up down restart logs clean dev dev-build dev-down \
        backend-shell frontend-shell ps stats backup restore update deploy health

# 默认目标
help: ## 显示帮助信息
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ============================================
# 生产环境命令
# ============================================

build: ## 构建所有镜像
	docker-compose build

up: ## 启动所有服务（后台运行）
	docker-compose up -d

down: ## 停止所有服务
	docker-compose down

restart: ## 重启所有服务
	docker-compose restart

logs: ## 查看所有服务日志（实时）
	docker-compose logs -f

logs-backend: ## 查看后端服务日志
	docker-compose logs -f backend

logs-frontend: ## 查看前端服务日志
	docker-compose logs -f frontend

clean: ## 清理所有容器、镜像和数据卷
	docker-compose down -v --rmi all

deploy: ## 完整部署（构建 + 启动）
	docker-compose build
	docker-compose up -d
	@echo ""
	@echo "=========================================="
	@echo "  部署完成！"
	@echo "  前端: http://localhost"
	@echo "  后端: http://localhost:8000"
	@echo "  API 文档: http://localhost:8000/docs"
	@echo "=========================================="

# ============================================
# 开发环境命令
# ============================================

dev: ## 启动开发环境（支持热更新）
	docker-compose -f docker-compose.dev.yml up -d

dev-build: ## 构建开发环境镜像
	docker-compose -f docker-compose.dev.yml build

dev-down: ## 停止开发环境
	docker-compose -f docker-compose.dev.yml down

dev-logs: ## 查看开发环境日志
	docker-compose -f docker-compose.dev.yml logs -f

# ============================================
# 容器操作命令
# ============================================

backend-shell: ## 进入后端容器 Shell
	docker-compose exec backend bash

frontend-shell: ## 进入前端容器 Shell
	docker-compose exec frontend sh

ps: ## 查看容器状态
	docker-compose ps

stats: ## 查看资源使用情况
	docker stats --no-stream

# ============================================
# 数据库命令
# ============================================

backup: ## 备份数据库
	@echo "正在备份数据库..."
	@docker-compose exec backend cp /app/data/grades.db /app/data/grades.db.backup.$(shell date +%Y%m%d%H%M%S)
	@echo "备份完成！"

restore: ## 恢复数据库（需要指定备份文件: make restore FILE=grades.db.backup.20260101120000）
	@if [ -z "$(FILE)" ]; then \
		echo "请指定备份文件: make restore FILE=grades.db.backup.20260101120000"; \
		exit 1; \
	fi
	@echo "正在恢复数据库..."
	@docker-compose exec backend cp /app/data/$(FILE) /app/data/grades.db
	@echo "恢复完成！请重启服务: make restart"

# ============================================
# 维护命令
# ============================================

update: ## 更新部署（拉取代码 + 重新构建）
	git pull
	docker-compose build
	docker-compose up -d
	@echo "更新完成！"

health: ## 健康检查
	@echo "=========================================="
	@echo "  健康检查"
	@echo "=========================================="
	@echo ""
	@echo "检查后端服务..."
	@curl -f http://localhost:8000/health && echo " ✓ 后端服务正常" || echo " ✗ 后端服务异常"
	@echo ""
	@echo "检查前端服务..."
	@curl -f http://localhost:80/health && echo " ✓ 前端服务正常" || echo " ✗ 前端服务异常"
	@echo ""
	@echo "=========================================="
	@echo "  容器状态"
	@echo "=========================================="
	@docker-compose ps

# ============================================
# 清理命令
# ============================================

prune: ## 清理未使用的 Docker 资源
	docker system prune -f
	docker volume prune -f

nuke: ## 彻底清理（包括数据卷！谨慎使用！）
	@echo "警告: 此操作将删除所有数据！"
	@read -p "确认继续? (y/N): " confirm; \
	if [ "$$confirm" = "y" ] || [ "$$confirm" = "Y" ]; then \
		docker-compose down -v --rmi all --remove-orphans; \
		echo "清理完成！"; \
	else \
		echo "已取消"; \
	fi
