from models import Room, StaffList, Weekday


def modify_examination_room(
    examination_room: dict[str, dict[str, str]],
    staffs: StaffList,
    holiday: list[Weekday] | None,
):
    room_names: list[Room] = ["CT", "MR", "RI"]
    weekday: list[Weekday] = ["monday", "tuesday", "wednesday", "thursday", "friday"]

    if isinstance(holiday, list):
        for day in holiday:
            weekday.remove(day)

    for room_name in room_names:
        for day in weekday:
            am_staff = examination_room[room_name][f"{day}_am"]
            pm_staff = examination_room[room_name][f"{day}_pm"]
            if am_staff != pm_staff:
                continue

            room_list: list[Room] = ["CT", "MR", "RI"]
            room_list.remove(room_name)

            room_a_sum = sum(
                value == am_staff for value in examination_room[room_list[0]].values()
            )
            room_b_sum = sum(
                value == am_staff for value in examination_room[room_list[1]].values()
            )

            if room_a_sum > room_b_sum:
                (
                    examination_room[room_name][f"{day}_am"],
                    examination_room[room_list[1]][f"{day}_am"],
                ) = (
                    examination_room[room_list[1]][f"{day}_am"],
                    examination_room[room_name][f"{day}_am"],
                )

                staffs.update_staff(
                    name=am_staff, time=f"{day}_am", room_name=room_list[1]
                )
                staffs.update_staff(
                    name=examination_room[room_list[1]][f"{day}_am"],
                    time=f"{day}_am",
                    room_name=room_name,
                )

            else:
                (
                    examination_room[room_name][f"{day}_am"],
                    examination_room[room_list[0]][f"{day}_am"],
                ) = (
                    examination_room[room_list[0]][f"{day}_am"],
                    examination_room[room_name][f"{day}_am"],
                )

                staffs.update_staff(
                    name=am_staff, time=f"{day}_am", room_name=room_list[0]
                )
                staffs.update_staff(
                    name=examination_room[room_list[0]][f"{day}_am"],
                    time=f"{day}_am",
                    room_name=room_name,
                )

    return (examination_room, staffs)
