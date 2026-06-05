"""
CLI 命令模块

包含所有 Typer CLI 命令定义
"""

from src.cli.commands.student_cmd import app as student_app

__all__ = ["student_app"]
