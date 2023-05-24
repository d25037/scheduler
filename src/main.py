import datetime
import os
from time import perf_counter
from typing import cast

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
from read_excel import (
    get_excel_column_number,
    get_excel_row,
    read_original_excel,
    read_schedule,
)
from read_toml import read_toml
from write_excel import read_template, write_cells


def main():
    settings = read_toml()
    if not isinstance(settings, AppSettings):
        print(settings)
        return

    wb = read_original_excel(settings.all_schedule_file_path)
    if isinstance(wb, FileNotFoundError):
        return print(wb)

    try:
        excel_rows_or_error = [
            get_excel_row(wb=wb, date_and_weekday=settings.monday()),
            get_excel_row(wb=wb, date_and_weekday=settings.tuesday()),
            get_excel_row(wb=wb, date_and_weekday=settings.wednesday()),
            get_excel_row(wb=wb, date_and_weekday=settings.thursday()),
            get_excel_row(wb=wb, date_and_weekday=settings.friday()),
        ]
        print(excel_rows_or_error)
    except (SheetNotFoundError, CellError, RowNotFoundError) as e:
        return print(e)

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
        return print("oops")

    wb_created = write_cells(
        wb=output_template,
        staffs=staffs,
        columns=columns,
        noon_room=noon_room,
        settings=settings,
    )

    dt_now = datetime.datetime.now()
    dt_now_str = dt_now.strftime("%Y%m%d%H%M%S")
    monday = settings.get_date().strftime("%Y%m%d")

    output_file_path = os.path.join(
        settings.output_directory_path, f"schedule_{monday}_{dt_now_str}.xlsx"
    )
    wb_created.save(output_file_path)

    print(output_file_path)

    return


if __name__ == "__main__":
    t0 = perf_counter()

    main()

    print(f"処理時間: {round(perf_counter() - t0, 2)} 秒")
