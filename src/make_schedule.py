from pprint import pprint

from models import Room, StaffList, Weekday


def make_schedule(staffs: StaffList, holiday: list[Weekday] | None):
    room_names: list[Room] = ["RI", "CT", "MR"]
    examination_room: dict[str, dict[str, str]] = {"RI": {}, "CT": {}, "MR": {}}

    for room_name in room_names:
        for i in range(10):
            shifts = staffs.make_shift(room=room_name, holiday=holiday)
            if len(shifts) == 0:
                break

            target = shifts.random_fetch_one_by_fewest_residents()
            time = target.time
            selected_staff = target.candidates.random_fetch_one_by_lower_rank()

            staffs.update_staff(
                name=selected_staff.name, time=time, room_name=room_name
            )
            examination_room[room_name].update({time: selected_staff.name})

            pprint(f"i={i}, {selected_staff}")
            pprint(f"i={i}, examination_room: {examination_room}")

    return (examination_room, staffs)


def make_noon(staffs: StaffList, holiday: list[Weekday] | None):
    room_names: list[Room] = ["CT", "MR"]
    noon_room: dict[str, dict[str, str]] = {"CT": {}, "MR": {}}
    weekday: list[Weekday] = ["monday", "tuesday", "wednesday", "thursday", "friday"]

    if isinstance(holiday, list):
        for day in holiday:
            weekday.remove(day)

    selected_staffs: list[str] = []
    for room_name in room_names:
        for day in weekday:
            candidates = staffs.filter_noon_candidates(
                weekday=day, selected_staffs=selected_staffs
            )
            selected_staff = candidates.random_fetch_one_by_lower_rank()
            time = f"{day}"

            staffs.update_staff(
                name=selected_staff.name, time=time, room_name=room_name
            )
            noon_room[room_name].update({time: selected_staff.name})

            selected_staffs.append(selected_staff.name)

    pprint(noon_room)
    pprint(staffs)

    return (noon_room, staffs)
