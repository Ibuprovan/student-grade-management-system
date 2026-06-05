"""
学生 CLI 命令

提供学生管理的命令行接口：
- student add      添加学生
- student list     学生列表
- student search   搜索学生
- student update   修改学生
- student delete   删除学生
"""

import sys
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from src.core.database import SessionLocal
from src.core.exceptions import AppException
from src.schemas.student import StudentCreate, StudentUpdate
from src.services.student_service import StudentService

# 创建 Typer 应用
app = typer.Typer(
    name="student",
    help="学生信息管理命令",
    no_args_is_help=True,
)

# Rich 控制台
console = Console()


def _get_service() -> tuple:
    """
    获取 StudentService 实例和数据库会话

    Returns:
        tuple: (StudentService, Session) - 服务实例和数据库会话
    """
    db = SessionLocal()
    return StudentService(db), db


@app.command()
def add(
    student_id: str = typer.Option(..., "--id", help="学号（8位数字）"),
    name: str = typer.Option(..., "--name", help="姓名"),
    gender: str = typer.Option(..., "--gender", help="性别（男/女）"),
    class_name: str = typer.Option(..., "--class", help="班级"),
    year: int = typer.Option(..., "--year", help="入学年份"),
) -> None:
    """
    添加学生

    示例：python -m src.cli student add --id 20260001 --name 张三 --gender 男 --class 三年一班 --year 2026
    """
    db = None
    try:
        # 构建请求数据
        data = StudentCreate(
            student_id=student_id,
            name=name,
            gender=gender,
            class_name=class_name,
            enrollment_year=year,
        )

        # 调用 Service 创建学生
        service, db = _get_service()
        student = service.create_student(data)

        # 输出成功信息
        console.print(
            Panel(
                f"[green]学生添加成功！[/green]\n\n"
                f"学号: {student.student_id}\n"
                f"姓名: {student.name}\n"
                f"性别: {student.gender}\n"
                f"班级: {student.class_name}\n"
                f"入学年份: {student.enrollment_year}",
                title="✅ 操作成功",
                border_style="green",
            )
        )
    except AppException as e:
        console.print(f"[red]错误: {e.message}[/red]")
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[red]未知错误: {str(e)}[/red]")
        raise typer.Exit(code=1)
    finally:
        if db is not None:
            db.close()


@app.command()
def list(
    class_name: Optional[str] = typer.Option(None, "--class", help="按班级筛选"),
    page: int = typer.Option(1, "--page", help="页码"),
    size: int = typer.Option(20, "--size", help="每页数量"),
) -> None:
    """
    学生列表

    示例：python -m src.cli student list --class 三年一班 --page 1 --size 10
    """
    db = None
    try:
        service, db = _get_service()
        students, total = service.get_student_list(
            page=page,
            page_size=size,
            class_name=class_name,
        )

        if not students:
            console.print("[yellow]没有找到学生记录[/yellow]")
            return

        # 创建表格
        table = Table(
            title=f"学生列表 (共 {total} 条记录，第 {page} 页)",
            show_header=True,
            header_style="bold cyan",
        )
        table.add_column("学号", style="dim")
        table.add_column("姓名")
        table.add_column("性别")
        table.add_column("班级")
        table.add_column("入学年份")
        table.add_column("创建时间")

        for student in students:
            table.add_row(
                student.student_id,
                student.name,
                student.gender,
                student.class_name,
                str(student.enrollment_year),
                student.created_at.strftime("%Y-%m-%d %H:%M"),
            )

        console.print(table)

        # 显示分页信息
        import math

        total_pages = math.ceil(total / size) if total > 0 else 0
        console.print(
            f"[dim]共 {total_pages} 页，当前第 {page} 页[/dim]"
        )

    except AppException as e:
        console.print(f"[red]错误: {e.message}[/red]")
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[red]未知错误: {str(e)}[/red]")
        raise typer.Exit(code=1)
    finally:
        if db is not None:
            db.close()


@app.command()
def search(
    keyword: str = typer.Option(..., "--keyword", help="搜索关键词"),
    class_name: Optional[str] = typer.Option(None, "--class", help="按班级筛选"),
) -> None:
    """
    搜索学生

    示例：python -m src.cli student search --keyword 张三
    """
    db = None
    try:
        service, db = _get_service()
        students, total = service.search_students(
            keyword=keyword,
            class_name=class_name,
        )

        if not students:
            console.print(f"[yellow]没有找到匹配 '{keyword}' 的学生[/yellow]")
            return

        # 创建表格
        table = Table(
            title=f"搜索结果: '{keyword}' (共 {total} 条)",
            show_header=True,
            header_style="bold cyan",
        )
        table.add_column("学号", style="dim")
        table.add_column("姓名")
        table.add_column("性别")
        table.add_column("班级")
        table.add_column("入学年份")

        for student in students:
            table.add_row(
                student.student_id,
                student.name,
                student.gender,
                student.class_name,
                str(student.enrollment_year),
            )

        console.print(table)

    except AppException as e:
        console.print(f"[red]错误: {e.message}[/red]")
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[red]未知错误: {str(e)}[/red]")
        raise typer.Exit(code=1)
    finally:
        if db is not None:
            db.close()


@app.command()
def update(
    student_id: str = typer.Option(..., "--id", help="学号"),
    name: Optional[str] = typer.Option(None, "--name", help="姓名"),
    gender: Optional[str] = typer.Option(None, "--gender", help="性别"),
    class_name: Optional[str] = typer.Option(None, "--class", help="班级"),
    year: Optional[int] = typer.Option(None, "--year", help="入学年份"),
) -> None:
    """
    修改学生信息

    示例：python -m src.cli student update --id 20260001 --name 李四
    """
    db = None
    try:
        # 构建更新数据（只包含非 None 的字段）
        update_data = {}
        if name is not None:
            update_data["name"] = name
        if gender is not None:
            update_data["gender"] = gender
        if class_name is not None:
            update_data["class_name"] = class_name
        if year is not None:
            update_data["enrollment_year"] = year

        if not update_data:
            console.print("[yellow]请至少提供一个需要更新的字段[/yellow]")
            raise typer.Exit(code=1)

        data = StudentUpdate(**update_data)

        # 调用 Service 更新学生
        service, db = _get_service()
        student = service.update_student(student_id, data)

        # 输出成功信息
        console.print(
            Panel(
                f"[green]学生信息更新成功！[/green]\n\n"
                f"学号: {student.student_id}\n"
                f"姓名: {student.name}\n"
                f"性别: {student.gender}\n"
                f"班级: {student.class_name}\n"
                f"入学年份: {student.enrollment_year}",
                title="✅ 操作成功",
                border_style="green",
            )
        )

    except AppException as e:
        console.print(f"[red]错误: {e.message}[/red]")
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[red]未知错误: {str(e)}[/red]")
        raise typer.Exit(code=1)
    finally:
        if db is not None:
            db.close()


@app.command()
def delete(
    student_id: str = typer.Option(..., "--id", help="学号"),
    force: bool = typer.Option(False, "--force", "-f", help="强制删除（跳过确认）"),
) -> None:
    """
    删除学生

    示例：python -m src.cli student delete --id 20260001
    """
    db = None
    try:
        # 确认删除
        if not force:
            confirm = typer.confirm(
                f"确定要删除学生 '{student_id}' 及其所有成绩吗？"
            )
            if not confirm:
                console.print("[yellow]已取消删除[/yellow]")
                return

        # 调用 Service 删除学生
        service, db = _get_service()
        service.delete_student(student_id)

        console.print(
            Panel(
                f"[green]学生 '{student_id}' 删除成功！[/green]\n"
                f"[dim]（已级联删除相关成绩记录）[/dim]",
                title="✅ 操作成功",
                border_style="green",
            )
        )

    except AppException as e:
        console.print(f"[red]错误: {e.message}[/red]")
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[red]未知错误: {str(e)}[/red]")
        raise typer.Exit(code=1)
    finally:
        if db is not None:
            db.close()
