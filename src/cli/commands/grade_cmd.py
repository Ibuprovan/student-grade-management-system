"""
成绩 CLI 命令

提供成绩管理的命令行接口：
- grade input    单条成绩录入
- grade batch    批量成绩录入（从 CSV 文件）
- grade query    成绩查询（按学生/班级/科目/组合条件）
- grade update   修改成绩
- grade delete   删除成绩
"""

import csv
import sys
from datetime import date
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from src.core.database import SessionLocal
from src.core.exceptions import AppException
from src.schemas.grade import GradeCreate, GradeUpdate, GradeBatchCreate, GradeBatchItem
from src.services.grade_service import GradeService

# 创建 Typer 应用
app = typer.Typer(
    name="grade",
    help="成绩管理命令",
    no_args_is_help=True,
)

# Rich 控制台
console = Console()


def _get_service() -> tuple:
    """
    获取 GradeService 实例和数据库会话

    Returns:
        tuple: (GradeService, Session) - 服务实例和数据库会话
    """
    db = SessionLocal()
    return GradeService(db), db


@app.command()
def input(
    student_id: str = typer.Option(..., "--student-id", help="学号"),
    subject: str = typer.Option(..., "--subject", help="科目"),
    score: float = typer.Option(..., "--score", help="分数（0-100）"),
    exam_type: str = typer.Option(..., "--exam-type", help="考试类型（期中/期末/月考/单元测试）"),
    exam_date: str = typer.Option(..., "--date", help="考试日期（YYYY-MM-DD）"),
) -> None:
    """
    单条成绩录入

    示例：python -m src.cli grade input --student-id 20260001 --subject 数学 --score 95.5 --exam-type 期中 --date 2026-06-01
    """
    db = None
    try:
        # 解析日期
        parsed_date = date.fromisoformat(exam_date)

        # 构建请求数据
        data = GradeCreate(
            student_id=student_id,
            subject=subject,
            score=score,
            exam_type=exam_type,
            exam_date=parsed_date,
        )

        # 调用 Service 创建成绩
        service, db = _get_service()
        grade = service.create_grade(data)

        # 输出成功信息
        console.print(
            Panel(
                f"[green]成绩录入成功！[/green]\n\n"
                f"成绩ID: {grade.grade_id}\n"
                f"学号: {grade.student_id}\n"
                f"科目: {grade.subject}\n"
                f"分数: {grade.score}\n"
                f"考试类型: {grade.exam_type}\n"
                f"考试日期: {grade.exam_date}",
                title="✅ 操作成功",
                border_style="green",
            )
        )
    except AppException as e:
        console.print(f"[red]错误: {e.message}[/red]")
        raise typer.Exit(code=1)
    except ValueError as e:
        console.print(f"[red]参数错误: {str(e)}[/red]")
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[red]未知错误: {str(e)}[/red]")
        raise typer.Exit(code=1)
    finally:
        if db is not None:
            db.close()


@app.command()
def batch(
    subject: str = typer.Option(..., "--subject", help="科目"),
    exam_type: str = typer.Option(..., "--exam-type", help="考试类型"),
    exam_date: str = typer.Option(..., "--date", help="考试日期（YYYY-MM-DD）"),
    file: Path = typer.Option(..., "--file", help="CSV 文件路径"),
) -> None:
    """
    批量成绩录入（从 CSV 文件）

    CSV 文件格式：student_id,score
    示例：python -m src.cli grade batch --subject 数学 --exam-type 期中 --date 2026-06-01 --file grades.csv
    """
    db = None
    try:
        # 检查文件是否存在
        if not file.exists():
            console.print(f"[red]错误: 文件 '{file}' 不存在[/red]")
            raise typer.Exit(code=1)

        # 解析日期
        parsed_date = date.fromisoformat(exam_date)

        # 读取 CSV 文件
        grades = []
        with open(file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                grades.append(GradeBatchItem(
                    student_id=row["student_id"],
                    score=float(row["score"]),
                ))

        if not grades:
            console.print("[yellow]CSV 文件中没有数据[/yellow]")
            raise typer.Exit(code=1)

        # 构建批量请求数据
        data = GradeBatchCreate(
            subject=subject,
            exam_type=exam_type,
            exam_date=parsed_date,
            grades=grades,
        )

        # 调用 Service 批量创建成绩
        service, db = _get_service()
        result = service.batch_create_grades(data)

        # 输出结果
        console.print(
            Panel(
                f"[green]批量录入完成！[/green]\n\n"
                f"总数: {result['total']}\n"
                f"成功: {result['success_count']}\n"
                f"失败: {result['fail_count']}",
                title="📊 批量录入结果",
                border_style="green" if result['fail_count'] == 0 else "yellow",
            )
        )

        # 显示失败详情
        if result['fail_count'] > 0:
            console.print("\n[yellow]失败详情:[/yellow]")
            for r in result['results']:
                if r['status'] == 'fail':
                    console.print(f"  - {r['student_id']}: {r['error']}")

    except AppException as e:
        console.print(f"[red]错误: {e.message}[/red]")
        raise typer.Exit(code=1)
    except ValueError as e:
        console.print(f"[red]参数错误: {str(e)}[/red]")
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[red]未知错误: {str(e)}[/red]")
        raise typer.Exit(code=1)
    finally:
        if db is not None:
            db.close()


@app.command()
def query(
    student_id: Optional[str] = typer.Option(None, "--student-id", help="按学号查询"),
    class_name: Optional[str] = typer.Option(None, "--class", help="按班级查询"),
    subject: Optional[str] = typer.Option(None, "--subject", help="按科目查询"),
    exam_type: Optional[str] = typer.Option(None, "--exam-type", help="按考试类型筛选"),
    page: int = typer.Option(1, "--page", help="页码"),
    size: int = typer.Option(20, "--size", help="每页数量"),
) -> None:
    """
    成绩查询

    示例：
    - 按学生查询：python -m src.cli grade query --student-id 20260001
    - 按班级查询：python -m src.cli grade query --class 三年一班 [--subject 数学] [--exam-type 期中]
    - 按科目查询：python -m src.cli grade query --subject 数学 [--exam-type 期中]
    """
    db = None
    try:
        service, db = _get_service()

        # 根据查询参数选择查询方式
        if student_id:
            # 按学生查询
            grades = service.get_grades_by_student(
                student_id=student_id,
                skip=(page - 1) * size,
                limit=size,
            )
            title = f"学生 '{student_id}' 的成绩"
        elif class_name:
            # 按班级查询
            grades = service.get_grades_by_class(
                class_name=class_name,
                subject=subject,
                exam_type=exam_type,
                skip=(page - 1) * size,
                limit=size,
            )
            title = f"班级 '{class_name}' 的成绩"
        elif subject:
            # 按科目查询
            grades = service.get_grades_by_subject(
                subject=subject,
                exam_type=exam_type,
                skip=(page - 1) * size,
                limit=size,
            )
            title = f"科目 '{subject}' 的成绩"
        else:
            # 组合查询（无筛选条件）
            grades_list, total = service.search_grades(
                exam_type=exam_type,
                page=page,
                page_size=size,
            )
            grades = grades_list
            title = f"所有成绩 (共 {total} 条)"

        if not grades:
            console.print("[yellow]没有找到成绩记录[/yellow]")
            return

        # 创建表格
        table = Table(
            title=title,
            show_header=True,
            header_style="bold cyan",
        )
        table.add_column("成绩ID", style="dim")
        table.add_column("学号")
        table.add_column("学生姓名")
        table.add_column("班级")
        table.add_column("科目")
        table.add_column("分数")
        table.add_column("考试类型")
        table.add_column("考试日期")

        for grade in grades:
            # 获取学生信息（如果已加载）
            student_name = grade.student.name if grade.student else "-"
            class_name_display = grade.student.class_name if grade.student else "-"

            table.add_row(
                str(grade.grade_id),
                grade.student_id,
                student_name,
                class_name_display,
                grade.subject,
                str(grade.score),
                grade.exam_type,
                str(grade.exam_date),
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
    grade_id: int = typer.Option(..., "--grade-id", help="成绩ID"),
    score: float = typer.Option(..., "--score", help="新分数（0-100）"),
) -> None:
    """
    修改成绩

    示例：python -m src.cli grade update --grade-id 1 --score 98.0
    """
    db = None
    try:
        # 构建更新数据
        data = GradeUpdate(score=score)

        # 调用 Service 更新成绩
        service, db = _get_service()
        grade = service.update_grade(grade_id, data)

        # 输出成功信息
        console.print(
            Panel(
                f"[green]成绩更新成功！[/green]\n\n"
                f"成绩ID: {grade.grade_id}\n"
                f"学号: {grade.student_id}\n"
                f"科目: {grade.subject}\n"
                f"分数: {grade.score}\n"
                f"考试类型: {grade.exam_type}",
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
    grade_id: int = typer.Option(..., "--grade-id", help="成绩ID"),
    force: bool = typer.Option(False, "--force", "-f", help="强制删除（跳过确认）"),
) -> None:
    """
    删除成绩

    示例：python -m src.cli grade delete --grade-id 1
    """
    db = None
    try:
        # 确认删除
        if not force:
            confirm = typer.confirm(f"确定要删除成绩记录 '{grade_id}' 吗？")
            if not confirm:
                console.print("[yellow]已取消删除[/yellow]")
                return

        # 调用 Service 删除成绩
        service, db = _get_service()
        service.delete_grade(grade_id)

        console.print(
            Panel(
                f"[green]成绩记录 '{grade_id}' 删除成功！[/green]",
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
