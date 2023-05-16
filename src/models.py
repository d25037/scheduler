from collections import UserList
from datetime import date, timedelta
from random import choice
from typing import Any, Literal, TypeAlias

from pydantic import BaseModel, FilePath, validator
from pydantic.dataclasses import dataclass

Weekday: TypeAlias = Literal["monday", "tuesday", "wednesday", "thursday", "friday"]
Room: TypeAlias = Literal["RI", "CT", "MR"]
AmPm: TypeAlias = Literal["am", "pm"]


class DateAndWeekday(BaseModel):
    date: date
    weekday: Weekday


class Staff(BaseModel):
    name: str
    rank: int
    col_number: int | None
    schedule: dict[str, str] = {}


@dataclass
class StaffList(UserList):
    data: list[Staff]

    def filter_one_by_name(self, value: str) -> Staff:
        filtered = list(filter(lambda x: x.name == value, self.data))
        return filtered[0]

    def already_matched(self, shift: str, room: Room):
        if len(list(filter(lambda x: x.schedule.get(shift) == room, self.data))) > 0:
            return True
        return False

    def filter_available_staffs(self):
        return StaffList(list(filter(lambda x: len(x.schedule) < 7, self.data)))

    def filter_residents(self):
        return StaffList(list(filter(lambda x: x.rank <= 3, self.data)))

    def filter_candidates(self, weekday: Weekday, am_pm: AmPm):
        match am_pm:
            case "am":
                shift = f"{weekday}_am"
                opposite = f"{weekday}_pm"
            case "pm":
                shift = f"{weekday}_pm"
                opposite = f"{weekday}_am"

        exclude_words = ("①", "②", "③", "外勤")

        return StaffList(
            list(
                filter(
                    lambda x: x.schedule.get(shift) is None
                    and x.schedule.get(opposite) not in exclude_words,
                    self.filter_available_staffs(),
                )
            )
        )

    def make_shift(self, room: Room, holiday: list[Weekday] | None = None):
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
            if self.already_matched(shift=am, room=room) is False:
                candidates_am = self.filter_candidates(weekday=day, am_pm="am")
                list_of_each_staffs.append(
                    ShiftAmPm(
                        time=am,
                        resident_numbers=len(candidates_am.filter_residents()),
                        candidates=candidates_am,
                    )
                )

            pm = f"{day}_pm"
            if self.already_matched(shift=pm, room=room) is False:
                candidates_pm = self.filter_candidates(weekday=day, am_pm="pm")
                list_of_each_staffs.append(
                    ShiftAmPm(
                        time=pm,
                        resident_numbers=len(candidates_pm.filter_residents()),
                        candidates=candidates_pm,
                    )
                )

        return ShiftAmPmList(list_of_each_staffs)

    def filter_by_lower_rank(self):
        lowest_rank = min(list(map(lambda x: x.rank, self.data)))
        return StaffList(list(filter(lambda x: x.rank <= lowest_rank + 2, self.data)))

    def random_fetch_one_by_lower_rank(self) -> Staff:
        return choice(self.filter_by_lower_rank())

    def filter_by_schedule(self, schedule: str, work: str):
        return StaffList(
            list(filter(lambda x: x.schedule.get(schedule) == work, self.data))
        )

    def filter_by_schedule_list(self, schedule: str, works: list[str]):
        return StaffList(
            list(filter(lambda x: x.schedule.get(schedule) in works, self.data))
        )

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
        exclude_words = ("①", "②", "③", "外勤", "IVR")

        filtered = list(
            filter(
                lambda x: x.schedule.get(noon) is None
                and x.schedule.get(am) not in exclude_words
                and x.schedule.get(pm) not in exclude_words
                and not (x.schedule.get(am) and x.schedule.get(pm)),
                self.data,
            )
        )

        if selected_staffs and filtered:
            return StaffList(
                list(
                    filter(
                        lambda x: x.name not in selected_staffs,
                        filtered,
                    )
                )
            )

        return StaffList(filtered)


class Column(BaseModel):
    name: str
    col_number: int | None = None
    schedule: dict[str, str] = {}


@dataclass
class ColumnList(UserList):
    data: list[Column]

    def filter_one_by_name(self, value) -> Column:
        filtered = list(filter(lambda x: x.name == value, self.data))
        return filtered[0]


class AppSettings(BaseModel):
    file_path: FilePath
    year: int
    month: int
    day: int
    holiday: list[Weekday] | None = None
    column_list: list[str]
    staffs: list[Staff]

    @validator("month")
    def month_validator(cls, v: int):
        if v < 1 or v > 12:
            raise ValueError("monthの値が不正です(1=<month=<12にしてください)")
        return v

    @validator("day")
    def day_validator(cls, v: int):
        if v < 1 or v > 31:
            raise ValueError("dayの値が不正です(1=<day=<31にしてください)")
        return v

    @validator("column_list")
    def column_validator(cls, v: list):
        unique_count = len(set(v))
        if len(v) != unique_count:
            raise ValueError("column_listに重複があります")
        return v

    @validator("staffs")
    def staffs_validator(cls, v: list):
        staff_name_list = list(map(lambda x: x.name, v))
        unique_count = len(set(staff_name_list))
        if len(staff_name_list) != unique_count:
            raise ValueError("staffsの名前に重複があります")
        return v

    def get_staff_list(self) -> StaffList:
        return StaffList(self.staffs)

    def get_columns_list(self) -> ColumnList:
        return ColumnList(list(map(lambda x: Column(name=x), self.column_list)))

    def month_to_str(self) -> str:
        return str(self.month) + "月"

    def get_date(self) -> date:
        monday = date(self.year, self.month, self.day)
        if monday.weekday() != 0:
            raise ValueError("設定された日付が月曜日ではありません")
        return monday

    def monday(self) -> DateAndWeekday:
        monday = date(self.year, self.month, self.day)
        if monday.weekday() != 0:
            raise ValueError("設定された日付が月曜日ではありません")
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
