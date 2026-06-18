"""
统计分析 CLI 命令

提供统计分析的命令行接口：
- stats average          平均分统计
- stats max              最高分统计
- stats min              最低分统计
- stats pass-rate        及格率统计
- stats excellent-rate   优秀率统计
- stats report           综合统计报告
- stats ranking          单科排名
- stats total-ranking    总分排名
"""

from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from src.core.database import SessionLocal
from src.core.exceptions import AppException
from src.services.statistics_service import StatisticsService

# 创建 Typer 应用
app = typer.Typer(
    name="stats",
    help="统计分析命令",
    no_args_is_help=True,
)

# Rich 控制台
console = Console()


def _get_service() -> tuple:
    """
    获取 StatisticsService 实例和数据库会话

    Returns:
        tuple: (StatisticsService, Session) - 服务实例和数据库会话
    """
    db = SessionLocal()
    return StatisticsService(db), db


@app.command()
def average(
    class_name: Optional[str] = typer.Option(None, "--class", help="班级名称"),
    subject: Optional[str] = typer.Option(None, "--subject", help="科目名称"),
    exam_type: Optional[str] = typer.Option(None, "--exam-type", help="考试类型"),
) -> None:
    """
    平均分统计

    示例：
    - python -m src.cli stats average
    - python -m src.cli stats average --class 2026级1班
    - python -m src.cli stats average --subject 数学 --exam-type 期中
    """
    db = None
    try:
        service, db = _get_service()
        result = service.get_average(
            class_name=class_name,
            subject=subject,
            exam_type=exam_type,
        )

        # 构建条件描述
        conditions = []
        if class_name:
            conditions.append(f"班级: {class_name}")
        if subject:
            conditions.append(f"科目: {subject}")
        if exam_type:
            conditions.append(f"考试类型: {exam_type}")
        condition_str = " | ".join(conditions) if conditions else "全部数据"

        console.print(
            Panel(
                f"[green]平均分统计结果[/green]\n\n"
                f"统计条件: {condition_str}\n"
                f"参与人数: {result['count']}\n"
                f"平均分: [bold cyan]{result['average']}[/bold cyan]",
                title="📊 平均分统计",
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


@app.command("pass-rate")
def pass_rate(
    class_name: Optional[str] = typer.Option(None, "--class", help="班级名称"),
    subject: Optional[str] = typer.Option(None, "--subject", help="科目名称"),
    exam_type: Optional[str] = typer.Option(None, "--exam-type", help="考试类型"),
) -> None:
    """
    及格率统计

    示例：
    - python -m src.cli stats pass-rate
    - python -m src.cli stats pass-rate --class 2026级1班 --subject 数学
    """
    db = None
    try:
        service, db = _get_service()
        result = service.get_pass_rate(
            class_name=class_name,
            subject=subject,
            exam_type=exam_type,
        )

        # 构建条件描述
        conditions = []
        if class_name:
            conditions.append(f"班级: {class_name}")
        if subject:
            conditions.append(f"科目: {subject}")
        if exam_type:
            conditions.append(f"考试类型: {exam_type}")
        condition_str = " | ".join(conditions) if conditions else "全部数据"

        console.print(
            Panel(
                f"[green]及格率统计结果[/green]\n\n"
                f"统计条件: {condition_str}\n"
                f"总人数: {result['total_count']}\n"
                f"及格人数: {result['passed_count']}\n"
                f"及格率: [bold cyan]{result['pass_rate']}%[/bold cyan]",
                title="📊 及格率统计",
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


@app.command("excellent-rate")
def excellent_rate(
    class_name: Optional[str] = typer.Option(None, "--class", help="班级名称"),
    subject: Optional[str] = typer.Option(None, "--subject", help="科目名称"),
    exam_type: Optional[str] = typer.Option(None, "--exam-type", help="考试类型"),
) -> None:
    """
    优秀率统计

    示例：
    - python -m src.cli stats excellent-rate
    - python -m src.cli stats excellent-rate --class 2026级1班 --subject 数学
    """
    db = None
    try:
        service, db = _get_service()
        result = service.get_excellent_rate(
            class_name=class_name,
            subject=subject,
            exam_type=exam_type,
        )

        # 构建条件描述
        conditions = []
        if class_name:
            conditions.append(f"班级: {class_name}")
        if subject:
            conditions.append(f"科目: {subject}")
        if exam_type:
            conditions.append(f"考试类型: {exam_type}")
        condition_str = " | ".join(conditions) if conditions else "全部数据"

        console.print(
            Panel(
                f"[green]优秀率统计结果[/green]\n\n"
                f"统计条件: {condition_str}\n"
                f"总人数: {result['total_count']}\n"
                f"优秀人数: {result['excellent_count']}\n"
                f"优秀率: [bold cyan]{result['excellent_rate']}%[/bold cyan]",
                title="📊 优秀率统计",
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
def report(
    class_name: Optional[str] = typer.Option(None, "--class", help="班级名称"),
    subject: Optional[str] = typer.Option(None, "--subject", help="科目名称"),
    exam_type: Optional[str] = typer.Option(None, "--exam-type", help="考试类型"),
    top_n: int = typer.Option(5, "--top", help="优秀学生数量"),
) -> None:
    """
    综合统计报告

    示例：
    - python -m src.cli stats report
    - python -m src.cli stats report --class 2026级1班 --subject 数学
    """
    db = None
    try:
        service, db = _get_service()
        result = service.get_report(
            class_name=class_name,
            subject=subject,
            exam_type=exam_type,
            top_n=top_n,
        )

        stats = result["statistics"]

        # 构建条件描述
        conditions = []
        if class_name:
            conditions.append(f"班级: {class_name}")
        if subject:
            conditions.append(f"科目: {subject}")
        if exam_type:
            conditions.append(f"考试类型: {exam_type}")
        condition_str = " | ".join(conditions) if conditions else "全部数据"

        # 统计概览
        console.print(
            Panel(
                f"统计条件: {condition_str}\n"
                f"参与人数: {stats['count']}\n\n"
                f"[bold]基本统计[/bold]\n"
                f"  平均分: {stats['average']}\n"
                f"  最高分: {stats['max_score']}\n"
                f"  最低分: {stats['min_score']}\n"
                f"  及格率: {stats['pass_rate']}%\n"
                f"  优秀率: {stats['excellent_rate']}%",
                title="📊 综合统计报告",
                border_style="cyan",
            )
        )

        # 分数分布
        dist = stats["score_distribution"]
        dist_table = Table(title="分数分布", show_header=True, header_style="bold magenta")
        dist_table.add_column("分数段", style="cyan")
        dist_table.add_column("人数", justify="right")
        dist_table.add_column("占比", justify="right")

        total = stats["count"]
        for range_name, count in dist.items():
            percentage = f"{round(count / total * 100, 1)}%" if total > 0 else "0%"
            dist_table.add_row(range_name, str(count), percentage)

        console.print(dist_table)

        # 优秀学生
        if result["top_students"]:
            top_table = Table(title=f"优秀学生 TOP {top_n}", show_header=True, header_style="bold green")
            top_table.add_column("排名", justify="center")
            top_table.add_column("学号")
            top_table.add_column("姓名")
            top_table.add_column("分数", justify="right")

            for i, student in enumerate(result["top_students"], 1):
                top_table.add_row(
                    str(i),
                    student["student_id"],
                    student["name"],
                    str(student["score"]),
                )

            console.print(top_table)

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
def ranking(
    subject: str = typer.Option(..., "--subject", help="科目名称"),
    exam_type: str = typer.Option(..., "--exam-type", help="考试类型"),
    class_name: Optional[str] = typer.Option(None, "--class", help="班级名称（不填则为年级排名）"),
    order: str = typer.Option("desc", "--order", help="排序方式（asc/desc）"),
    limit: Optional[int] = typer.Option(None, "--limit", help="返回数量限制"),
) -> None:
    """
    单科排名

    示例：
    - python -m src.cli stats ranking --subject 数学 --exam-type 期中
    - python -m src.cli stats ranking --subject 数学 --exam-type 期中 --class 2026级1班
    - python -m src.cli stats ranking --subject 数学 --exam-type 期中 --limit 10
    """
    db = None
    try:
        service, db = _get_service()
        result = service.get_subject_ranking(
            subject=subject,
            exam_type=exam_type,
            class_name=class_name,
            order=order,
            limit=limit,
        )

        # 构建标题
        scope = f"班级 '{class_name}'" if class_name else "年级"
        title = f"{scope} {subject} ({exam_type}) 排名"

        if not result["rankings"]:
            console.print(f"[yellow]没有找到 {title} 的数据[/yellow]")
            return

        # 创建排名表格
        table = Table(title=title, show_header=True, header_style="bold cyan")
        table.add_column("排名", justify="center", style="bold")
        table.add_column("学号")
        table.add_column("姓名")
        table.add_column("分数", justify="right")

        for item in result["rankings"]:
            # 高亮前三名
            rank_style = ""
            if item["rank"] == 1:
                rank_style = "[bold yellow]"
            elif item["rank"] == 2:
                rank_style = "[bold white]"
            elif item["rank"] == 3:
                rank_style = "[bold red]"

            table.add_row(
                f"{rank_style}{item['rank']}[/]" if rank_style else str(item["rank"]),
                item["student_id"],
                item["student_name"],
                str(item["score"]),
            )

        console.print(table)
        console.print(f"\n[dim]共 {result['total_count']} 人参与排名[/dim]")

    except AppException as e:
        console.print(f"[red]错误: {e.message}[/red]")
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[red]未知错误: {str(e)}[/red]")
        raise typer.Exit(code=1)
    finally:
        if db is not None:
            db.close()


@app.command("total-ranking")
def total_ranking(
    exam_type: str = typer.Option(..., "--exam-type", help="考试类型"),
    class_name: Optional[str] = typer.Option(None, "--class", help="班级名称（不填则为年级排名）"),
    order: str = typer.Option("desc", "--order", help="排序方式（asc/desc）"),
    limit: Optional[int] = typer.Option(None, "--limit", help="返回数量限制"),
) -> None:
    """
    总分排名

    示例：
    - python -m src.cli stats total-ranking --exam-type 期中
    - python -m src.cli stats total-ranking --exam-type 期中 --class 2026级1班
    - python -m src.cli stats total-ranking --exam-type 期中 --limit 10
    """
    db = None
    try:
        service, db = _get_service()
        result = service.get_total_ranking(
            exam_type=exam_type,
            class_name=class_name,
            order=order,
            limit=limit,
        )

        # 构建标题
        scope = f"班级 '{class_name}'" if class_name else "年级"
        title = f"{scope} 总分排名 ({exam_type})"

        if not result["rankings"]:
            console.print(f"[yellow]没有找到 {title} 的数据[/yellow]")
            return

        # 获取所有科目
        all_subjects = set()
        for item in result["rankings"]:
            all_subjects.update(item["subject_scores"].keys())
        subjects = sorted(all_subjects)

        # 创建排名表格
        table = Table(title=title, show_header=True, header_style="bold cyan")
        table.add_column("排名", justify="center", style="bold")
        table.add_column("学号")
        table.add_column("姓名")
        for subj in subjects:
            table.add_column(subj, justify="right")
        table.add_column("总分", justify="right", style="bold")

        for item in result["rankings"]:
            # 高亮前三名
            rank_style = ""
            if item["rank"] == 1:
                rank_style = "[bold yellow]"
            elif item["rank"] == 2:
                rank_style = "[bold white]"
            elif item["rank"] == 3:
                rank_style = "[bold red]"

            row = [
                f"{rank_style}{item['rank']}[/]" if rank_style else str(item["rank"]),
                item["student_id"],
                item["student_name"],
            ]

            # 添加各科成绩
            for subj in subjects:
                score = item["subject_scores"].get(subj, "-")
                row.append(str(score))

            # 添加总分
            row.append(str(item["total_score"]))

            table.add_row(*row)

        console.print(table)
        console.print(f"\n[dim]共 {result['total_count']} 人参与排名[/dim]")

    except AppException as e:
        console.print(f"[red]错误: {e.message}[/red]")
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[red]未知错误: {str(e)}[/red]")
        raise typer.Exit(code=1)
    finally:
        if db is not None:
            db.close()
