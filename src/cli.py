import os
from datetime import datetime
from time import perf_counter
from typing import cast

from loguru import logger
from typer import Option, Typer
from typing_extensions import Annotated

from make_schedule import make_noon, make_schedule
from models import (
    AppSettings,
    CellError,
    ColumnList,
    ExcelRow,
    RowNotFoundError,
    SheetNotFoundError,
    StaffList,
)
from modify import modify_examination_room
from my_logger import LogLevel
from read_excel import (
    get_excel_column_number,
    get_excel_row,
    read_all_schedule,
    read_schedule,
)
from read_toml import read_toml
from write_excel import read_template, write_cells

app = Typer()


@app.command()
def run(
    log_level: Annotated[
        LogLevel,
        Option("--log-level", "-l", help="Set log level", case_sensitive=False),
    ] = LogLevel.INFO,
    dry_run: Annotated[
        bool, Option("--dry-run", "-d", help="Dry run", case_sensitive=False)
    ] = False,
):
    t0 = perf_counter()

    if log_level == LogLevel.DEBUG:
        os.environ["LOG_LEVEL"] = "DEBUG"

    logger.info("app starts.")

    settings = read_toml()
    if not isinstance(settings, AppSettings):
        return logger.critical(settings)

    wb = read_all_schedule(settings.all_schedule_file_path)
    if isinstance(wb, FileNotFoundError):
        return logger.critical(wb)

    try:
        excel_rows_or_error = [
            get_excel_row(wb=wb, date_and_weekday=settings.monday()),
            get_excel_row(wb=wb, date_and_weekday=settings.tuesday()),
            get_excel_row(wb=wb, date_and_weekday=settings.wednesday()),
            get_excel_row(wb=wb, date_and_weekday=settings.thursday()),
            get_excel_row(wb=wb, date_and_weekday=settings.friday()),
        ]
        logger.debug(excel_rows_or_error)
    except (SheetNotFoundError, CellError, RowNotFoundError, ValueError) as e:
        return logger.critical(e)

    excel_rows = cast(list[ExcelRow], excel_rows_or_error)

    result = get_excel_column_number(
        wb=wb,
        columns=settings.get_columns_list(),
        staffs=settings.get_staff_list(),
        date_and_weekday=settings.monday(),
    )

    columns, staffs = cast(tuple[ColumnList, StaffList], result)

    columns, staffs = read_schedule(
        excel_rows=excel_rows, staffs=staffs, columns=columns
    )

    examination_room, staffs = make_schedule(staffs=staffs, holiday=settings.holiday)

    noon_room, staffs = make_noon(staffs=staffs, holiday=settings.holiday)

    examination_room, staffs = modify_examination_room(
        examination_room=examination_room, staffs=staffs, holiday=settings.holiday
    )

    output_template = read_template(settings.output_template_file_path)
    if isinstance(output_template, FileNotFoundError):
        return logger.critical(f"{settings.output_template_file_path} not found.")

    wb_created = write_cells(
        wb=output_template,
        staffs=staffs,
        columns=columns,
        noon_room=noon_room,
        settings=settings,
    )

    dt_now = datetime.now()
    dt_now_str = dt_now.strftime("%Y%m%d_%H%M%S")
    monday = settings.get_date().strftime("%Y%m%d")

    output_file_path = os.path.join(
        settings.output_directory_path, f"schedule_{monday}_{dt_now_str}.xlsx"
    )
    match dry_run:
        case True:
            logger.info(f"{output_file_path} will be created. (dry-run)")
        case False:
            wb_created.save(output_file_path)
            logger.info(f"{output_file_path} have been created.")

    logger.info(f"処理時間: {round(perf_counter() - t0, 2)} 秒")

    return
