from collections import UserList
from datetime import date, timedelta
from enum import Enum, auto
from random import choice
from typing import Any, Callable, Literal, TypeAlias

from pydantic import BaseModel, DirectoryPath, FilePath, field_validator
from pydantic.dataclasses import dataclass

Weekday: TypeAlias = Literal["monday", "tuesday", "wednesday", "thursday", "friday"]


Room: TypeAlias = Literal["RI", "CT", "MR"]
AmPm: TypeAlias = Literal["am", "pm"]


class WeekdayEnum(Enum):
    MONDAY = auto()
    TUESDAY = auto()
    WEDNESDAY = auto()
    THURSDAY = auto()
    FRIDAY = auto()


class RoomEnum(Enum):
    RI = auto()
    CT = auto()
    MR = auto()


class AmPmNoon(Enum):
    AM = auto()
    PM = auto()
    NOON = auto()


class DateAndWeekday(BaseModel):
    date: date
    weekday: Weekday


class Schedule(BaseModel):
    weekday: WeekdayEnum
    am_pm_noon: AmPmNoon
    body: str


class Staff(BaseModel):
    name: str
    rank: int
    col_number: int | None = None
    schedule: dict[str, str] = {}
    schedule_list: list[Schedule] | None = None
    interpreting_cases: int = 0
    pregnant: bool = False
    maternity_leave: bool = False
    sick_leave: bool = False
    rotate_oncology: bool = False
    center_hospital: bool = True
    resident_check: bool = True


@dataclass
class StaffList(UserList):
    data: list[Staff]

    def filter(self, func: Callable) -> list[Staff]:
        return list(filter(func, self.data))

    def filter_one_by_name(self, name: str) -> Staff:
        filtered = self.filter(lambda staff: staff.name == name)
        return filtered[0]

    def matched_examination_room(self, shift: str, examination_room: Room) -> bool:
        if (
            len(
                self.filter(lambda staff: staff.schedule.get(shift) == examination_room)
            )
            > 0
        ):
            return True
        return False

    def filter_available_staffs(self, examination_room: Room):
        filtered = self.filter(
            lambda staff: len(staff.schedule) < 7
            and staff.rotate_oncology is False
            and staff.maternity_leave is False
            and staff.sick_leave is False
        )
        re_filtered: list[Staff] = []
        for staff in filtered:
            if examination_room == "RI" and staff.pregnant:
                continue

            summed = sum(shift == examination_room for shift in staff.schedule.values())
            if summed < 2:
                re_filtered.append(staff)
        return StaffList(re_filtered)

    def filter_residents(self):
        return StaffList(self.filter(lambda staff: staff.rank <= 3))

    def filter_diagnostician(self, diagnostician_rank: bool):
        return StaffList(self.filter(lambda staff: staff.rank >= diagnostician_rank))

    def filter_candidates(self, weekday: Weekday, am_pm: AmPm, examination_room: Room):
        match am_pm:
            case "am":
                shift = f"{weekday}_am"
                opposite = f"{weekday}_pm"
            case "pm":
                shift = f"{weekday}_pm"
                opposite = f"{weekday}_am"

        exclude_words = ("①", "②", "③", "外勤", examination_room)

        return StaffList(
            list(
                filter(
                    lambda staff: staff.schedule.get(shift) is None
                    and staff.schedule.get(opposite) not in exclude_words,
                    self.filter_available_staffs(examination_room=examination_room),
                )
            )
        )

    def make_shift(self, examination_room: Room, holiday: list[Weekday] | None = None):
        weekday: list[Weekday] = [
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
        ]

        if isinstance(holiday, list):
            for day in holiday:
                weekday.remove(day)

        list_of_each_staffs: list[ShiftAmPm] = []
        for day in weekday:
            am = f"{day}_am"
            if (
                self.matched_examination_room(
                    shift=am, examination_room=examination_room
                )
                is False
            ):
                candidates_am = self.filter_candidates(
                    weekday=day, am_pm="am", examination_room=examination_room
                )
                list_of_each_staffs.append(
                    ShiftAmPm(
                        time=am,
                        resident_numbers=len(candidates_am.filter_residents()),
                        candidates=candidates_am,
                    )
                )

            pm = f"{day}_pm"
            if (
                self.matched_examination_room(
                    shift=pm, examination_room=examination_room
                )
                is False
            ):
                candidates_pm = self.filter_candidates(
                    weekday=day, am_pm="pm", examination_room=examination_room
                )
                list_of_each_staffs.append(
                    ShiftAmPm(
                        time=pm,
                        resident_numbers=len(candidates_pm.filter_residents()),
                        candidates=candidates_pm,
                    )
                )

        return ShiftAmPmList(list_of_each_staffs)

    def filter_by_lower_rank(self):
        lowest_rank = min(list(map(lambda staff: staff.rank, self.data)))
        return StaffList(
            list(filter(lambda staff: staff.rank <= lowest_rank + 2, self.data))
        )

    def random_fetch_one_by_lower_rank(self) -> Staff:
        return choice(self.filter_by_lower_rank())

    def filter_by_schedule(self, schedule: str, work: str):
        return StaffList(
            self.filter(lambda staff: staff.schedule.get(schedule) == work)
        )

    def filter_by_schedule_list(self, schedule: str, works: list[str]):
        return StaffList(
            self.filter(lambda staff: staff.schedule.get(schedule) in works)
        )

    def filter_by_schedule_exclude_list(self, schedule: str, excludes: list[str]):
        filtered = self.filter(lambda staff: staff.schedule.get(schedule))
        re_filtered = [
            staff for staff in filtered if staff.schedule.get(schedule) not in excludes
        ]
        return StaffList(re_filtered)

    def update_staff(self, name: str, time: str, room_name: Room):
        for staff in self.data:
            if staff.name == name:
                staff.schedule.update({time: room_name})
                break
        return

    def filter_noon_candidates(
        self, weekday: Weekday, selected_staffs: list[str] | None = None
    ):
        am = f"{weekday}_am"
        pm = f"{weekday}_pm"
        noon = f"{weekday}_noon"
        exclude_words = ("①", "②", "③", "外勤", "IVR", "センター", "みなとみらい")

        filtered = list(
            filter(
                lambda staff: staff.schedule.get(noon) is None
                and staff.schedule.get(am) not in exclude_words
                and staff.schedule.get(pm) not in exclude_words
                and not (staff.schedule.get(am) and staff.schedule.get(pm))
                and staff.rotate_oncology is False
                and staff.maternity_leave is False
                and staff.sick_leave is False,
                self.data,
            )
        )

        if selected_staffs and filtered:
            re_filtered = [
                staff for staff in filtered if staff.name not in selected_staffs
            ]
            return StaffList(re_filtered)

        return StaffList(filtered)


class Column(BaseModel):
    name: str
    col_number: int | None = None
    schedule: dict[str, str] = {}


# @dataclass
class ColumnList(BaseModel):
    data: list[Column]

    def filter_one_by_name(self, value) -> Column:
        filtered = list(filter(lambda x: x.name == value, self.data))
        return filtered[0]


class AppSettings(BaseModel):
    all_schedule_file_path: FilePath
    output_template_file_path: FilePath
    output_directory_path: DirectoryPath
    year: int
    month: int
    day: int
    holiday: list[Weekday] | None = None
    column_list: list[str]
    diagnostician_rank: int
    staffs: list[Staff]

    @field_validator("month")
    @classmethod
    def month_validator(cls, v: int):
        if v < 1 or v > 12:
            raise ValueError("monthの値が不正です(1=<month=<12にしてください)")
        return v

    @field_validator("day")
    @classmethod
    def day_validator(cls, v: int):
        if v < 1 or v > 31:
            raise ValueError("dayの値が不正です(1=<day=<31にしてください)")
        return v

    @field_validator("column_list")
    @classmethod
    def column_validator(cls, v: list):
        unique_count = len(set(v))
        if len(v) != unique_count:
            raise ValueError("column_listに重複があります")
        return v

    @field_validator("staffs")
    @classmethod
    def staffs_validator(cls, v: list):
        staff_name_list = list(map(lambda x: x.name, v))
        unique_count = len(set(staff_name_list))
        if len(staff_name_list) != unique_count:
            raise ValueError("staffsの名前に重複があります")
        return v

    def get_staff_list(self) -> StaffList:
        return StaffList(self.staffs)

    def get_columns_list(self) -> ColumnList:
        return ColumnList(data=list(map(lambda x: Column(name=x), self.column_list)))

    def month_to_str(self) -> str:
        return str(self.month) + "月"

    def get_date(self) -> date:
        monday = date(self.year, self.month, self.day)
        if monday.weekday() != 0:
            raise ValueError("The set date is not Monday.")
        return monday

    def monday(self) -> DateAndWeekday:
        monday = date(self.year, self.month, self.day)
        if monday.weekday() != 0:
            raise ValueError("The set date is not Monday.")
        return DateAndWeekday(date=monday, weekday="monday")

    def tuesday(self) -> DateAndWeekday:
        return DateAndWeekday(
            date=date(self.year, self.month, self.day) + timedelta(days=1),
            weekday="tuesday",
        )

    def wednesday(self) -> DateAndWeekday:
        return DateAndWeekday(
            date=date(self.year, self.month, self.day) + timedelta(days=2),
            weekday="wednesday",
        )

    def thursday(self) -> DateAndWeekday:
        return DateAndWeekday(
            date=date(self.year, self.month, self.day) + timedelta(days=3),
            weekday="thursday",
        )

    def friday(self) -> DateAndWeekday:
        return DateAndWeekday(
            date=date(self.year, self.month, self.day) + timedelta(days=4),
            weekday="friday",
        )


class ExcelRow(BaseModel):
    weekday: Weekday
    sheet_name: str
    # row
    am_row: list[Any] | None = []
    # row
    pm_row: list[Any] | None = []


class SheetNotFoundError(Exception):
    pass


class CellError(Exception):
    pass


class RowNotFoundError(Exception):
    pass


class ShiftAmPm(BaseModel):
    time: str
    resident_numbers: int
    candidates: StaffList


@dataclass
class ShiftAmPmList(UserList):
    data: list[ShiftAmPm]

    def filter_fewest_residents(self):
        resident_numbers = list(map(lambda x: x.resident_numbers, self.data))
        if resident_numbers:
            minimum_number = min(list(map(lambda x: x.resident_numbers, self.data)))
            filtered = list(
                filter(lambda x: x.resident_numbers == minimum_number, self.data)
            )
            return ShiftAmPmList(filtered)

        return ShiftAmPmList(self.data)

    def random_fetch_one_by_fewest_residents(self) -> ShiftAmPm:
        return choice(self.filter_fewest_residents())
