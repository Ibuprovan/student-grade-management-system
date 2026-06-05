"""
CLI 应用入口

提供命令行界面的主入口，注册所有子命令
"""

import typer

from src.cli.commands.student_cmd import app as student_app
from src.cli.commands.grade_cmd import app as grade_app
from src.cli.commands.statistics_cmd import app as stats_app

# 创建主 CLI 应用
app = typer.Typer(
    name="student-grade-system",
    help="学生成绩管理系统 CLI",
    no_args_is_help=True,
)

# 注册子命令
app.add_typer(student_app, name="student")
app.add_typer(grade_app, name="grade")
app.add_typer(stats_app, name="stats")


@app.callback()
def main(
    version: bool = typer.Option(False, "--version", "-v", help="显示版本信息"),
) -> None:
    """
    学生成绩管理系统命令行工具
    """
    if version:
        from src import __version__

        typer.echo(f"学生成绩管理系统 v{__version__}")
        raise typer.Exit()


if __name__ == "__main__":
    app()
