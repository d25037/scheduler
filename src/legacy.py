# import random
# import math
# import pandas as pd
# import numpy as np
# import datetime
# import openpyxl


# def legacy():
#     # エクセルファイルを読み込む。
#     original_file = "../templates/scheduler_2022.xlsx"

#     try:
#         wb = openpyxl.load_workbook(f"{original_file}")
#     except FileNotFoundError as e:
#         print(f"{e}")
#         return

#     ws = wb.worksheets[1]

#     weekday = ["月", "火", "水", "木", "金"]
#     hankoma_waku = [
#         "月AM",
#         "月PM",
#         "火AM",
#         "火PM",
#         "水AM",
#         "水PM",
#         "木AM",
#         "木PM",
#         "金AM",
#         "金PM",
#     ]
#     jouken_list = ["CT", "MR", "RI", "昼", "検査番"]
#     staff_flag = hankoma_waku + jouken_list
#     staff_level = ["非専門医", "専門医級", "上1", "上2"]

#     # エクセルファイルpyシートのA列を単語で検索し、その単語が初めて出てくる行を返す関数（最大100行）
#     def excel_search(word):
#         row_of_word = 0
#         # for row in ws.iter_rows(min_row=1, max_row=100, max_col=1):
#         #     if row[0].value == word:
#         #         row_of_word = k + 1
#         #         break
#         for k in range(100):
#             if ws.cell(k + 1, 1).value == word:
#                 row_of_word = k + 1
#                 break
#         return row_of_word

#     # スケジュール表の雛形を作る
#     df = pd.DataFrame(columns=hankoma_waku)
#     ctRow = excel_search("CT")

#     n = 0
#     while ws.cell(ctRow + n, 1).value is not None:
#         from_excel = []
#         for k in range(11):
#             from_excel.append(ws.cell(ctRow + n, 1 + k).value)
#         df.loc[from_excel[0]] = from_excel[1:]
#         n += 1

#     # スタッフ名をエクセルから読み込んでスタッフ予定表を作る。
#     def staffInput(staffLevel):
#         staffRow = excel_search(staffLevel)
#         staffListExcel = []
#         for col in range(10):
#             if ws.cell(staffRow, 2 + col).value is not None:
#                 staffListExcel.append(ws.cell(staffRow, 2 + col).value)
#             else:
#                 break
#         return staffListExcel

#     staff_list = (
#         staffInput(staff_level[0])
#         + staffInput(staff_level[1])
#         + staffInput(staff_level[2])
#         + staffInput(staff_level[3])
#     )
#     df_staff = pd.DataFrame(columns=staff_flag, index=staff_list)

#     for waku1 in hankoma_waku:
#         hito1 = df[waku1].unique()
#         for hito in hito1[1:]:
#             yotei = df[df[waku1] == hito].index
#             df_staff.loc[hito, waku1] = yotei[0]

#     # 週の日付を作り、休日の有無を反映させる。昼番予定表を作る。
#     df_weekday = pd.DataFrame(columns=weekday)

#     y0, m0, d0 = ws["H3"].value, ws["I3"].value, ws["J3"].value
#     d = datetime.date(y0, m0, d0)
#     week = ["日付"]
#     for i in range(5):
#         td_i = datetime.timedelta(days=i)
#         d_td_i = d + td_i
#         week.append(d_td_i)
#     df_weekday.loc[week[0]] = week[1:]

#     weekday_xl = ws["B2:F2"]
#     holiday = np.array(["休日"])
#     for k in range(5):
#         holiday = np.append(holiday, weekday_xl[0][k].value)
#     df_weekday.loc[holiday[0]] = holiday[1:]

#     hiru_a = np.array(["未定", "未定", "未定", "未定", "未定"])
#     df_weekday.loc["CT昼"] = hiru_a
#     df_weekday.loc["MR昼"] = hiru_a

#     for column_name in df_weekday:
#         if df_weekday.loc["休日", column_name] == "休日":
#             df.loc[:, df.columns.str.contains(column_name)] = "休日"
#             df_staff.loc[:, df_staff.columns.str.contains(column_name)] = "休日"
#             df_weekday.loc["CT昼":, column_name] = "休日"

#     # スタッフ予定表に検査室シフト条件を反映させる。
#     def flag0(jouken, n):
#         list3 = []
#         for staffLevel in staff_level:
#             staffJouken = excel_search(staffLevel) + 1
#             for k in range(len(staffInput(staffLevel))):
#                 list3.append(ws.cell(staffJouken, 3 + n).value)
#         df_staff[jouken] = list3

#     i = 0
#     for koumoku in jouken_list:
#         flag0(koumoku, i)
#         i += 2

#     hitos = df_staff[df_staff.loc[:, "検査番"].isnull()].index
#     for hito in hitos:
#         df_staff.loc[hito, "検査番"] = math.floor(
#             df_staff.loc[hito][:-1].isnull().sum() * 3 / 4
#         )

#     df_staff = df_staff.fillna("未定")

#     for column_name in hankoma_waku:
#         for k in ["CT", "MR", "RI", "IVR", "その他"]:
#             mask = df_staff[column_name].str.contains(k)
#             if len(df_staff.loc[mask]) > 0:
#                 df_staff.loc[mask, "検査番"] -= 1

#     def pickup_room(yotei, room0):
#         gyaku = yotei[0] + "PM" if "A" in yotei[0] else yotei[0] + "AM"
#         kouho0 = df_staff.index[
#             (df_staff[yotei] == "未定") & (df_staff[room0] > 0) & (df_staff["検査番"] > 0)
#         ].tolist()
#         list01 = []
#         for kouho1 in kouho0:
#             if df_staff.loc[kouho1, gyaku] == "未定":
#                 list01.append(kouho1)
#             elif kouho1 not in "_".join(map(str, df_weekday.loc[:, yotei[0]].tolist())):
#                 list01.append(kouho1)
#         return list01

#     def pickup_hiru(youbi):
#         am, pm = youbi + "AM", youbi + "PM"
#         mask = df_staff.columns.str.contains(youbi)
#         kouhosya = df_staff.loc[:, mask]
#         kouhosya = pd.concat([kouhosya, df_staff["昼"]], axis=1)
#         kouhosya.query("昼 > 0", inplace=True)
#         test4 = ["外勤", "休暇", "センター", "IVR"]
#         for k in test4:
#             kouhosya.query(
#                 'not {0}.str.contains("{2}") & not {1}.str.contains("{2}")'.format(
#                     am, pm, k
#                 ),
#                 inplace=True,
#             )
#         return kouhosya

#     sentakushi = 50
#     while sentakushi > 0:
#         df_room = pd.DataFrame(columns=hankoma_waku)
#         for room in ["CT", "MR", "RI"]:
#             list3 = [room]
#             for yotei in hankoma_waku:
#                 if df.loc[room, yotei] == "休日" or df.loc[room, yotei] is not None:
#                     list3.append(100)
#                 else:
#                     list3.append(len(pickup_room(yotei, room)))
#             df_room.loc[list3[0]] = list3[1:]

#         df_hiroom = pd.DataFrame(columns=weekday)
#         list3 = ["昼"]
#         for youbi in weekday:
#             if df_weekday.loc["CT昼", youbi] == "休日":
#                 list3.append(100)
#             elif df_weekday.loc["CT昼", youbi] == "未定":
#                 df_youbi = pickup_hiru(youbi)
#                 list3.append(
#                     len(
#                         df_youbi.index[
#                             (df_youbi.iloc[:, 0] == "未定")
#                             | (df_youbi.iloc[:, 1] == "未定")
#                         ]
#                     )
#                 )
#             else:
#                 list3.append(100)
#         df_hiroom.loc[list3[0]] = list3[1:]

#         sentakushi = min(
#             df_room.astype("int").min().min(), df_hiroom.astype("int").min().min()
#         )
#         if sentakushi == 100:
#             break

#         for column_name in df_room:
#             kensashitsu = df_room[column_name][df_room[column_name] == sentakushi].index
#             for kensashitsu01 in kensashitsu:
#                 kouho = pickup_room(column_name, kensashitsu01)
#                 weight = np.zeros(len(kouho))
#                 for k in range(len(kouho)):
#                     weight[0] = len(kouho) - k
#                 kettei = random.choices(kouho, weights=weight)
#                 df.loc[kensashitsu01, column_name] = kettei[0]
#                 df_staff.loc[kettei, column_name] = kensashitsu01
#                 df_staff.loc[kettei, [kensashitsu01, "検査番"]] -= 1

#         mask = df_hiroom.loc["昼"] == sentakushi
#         gaitouWaku = df_hiroom.loc["昼", mask].index.tolist()
#         for youbi in gaitouWaku:
#             df_youbi = pickup_hiru(youbi)
#             kouho = df_youbi.index[
#                 (df_youbi.iloc[:, 0] == "未定") | (df_youbi.iloc[:, 1] == "未定")
#             ].tolist()
#             kettei12 = random.sample(kouho, 2)
#             df_weekday.loc["CT昼", youbi], df_weekday.loc["MR昼", youbi] = (
#                 kettei12[0],
#                 kettei12[1],
#             )
#             df_staff.loc[[kettei12[0], kettei12[1]], "昼"] -= 1

#         sentakushi -= 1

#     df_staff = df_staff.applymap(lambda x: "読影室" if x == "未定" else x)

#     staff_list = (
#         staffInput(staff_level[0])
#         + staffInput(staff_level[1])
#         + staffInput(staff_level[2])
#     )
#     df_test = pd.DataFrame(index=staff_list)

#     for staff in staff_list:
#         test = "_".join(map(str, df_staff.loc[staff, :].tolist()))
#         for k in ["CT", "MR", "RI", "外勤", "休暇", "読影室"]:
#             tt = test.count(k)
#             df_test.loc[staff, k] = tt
#         df_test.loc[staff, "不在"] = df_test.loc[staff, ["外勤", "休暇"]].sum()

#     df_test = df_test.astype(int)

#     for inferior in staff_list:
#         i, j = df_test.loc[inferior, "読影室"], df_test.loc[inferior, "不在"]
#         superior_list = (
#             df_test.loc[
#                 inferior:,
#             ]
#             .query("読影室 < @i & 不在 <= @j")
#             .index.tolist()
#         )
#         for superior in superior_list:
#             flag00 = "変更前"
#             for xx in hankoma_waku:
#                 if (
#                     df_staff.loc[inferior, xx] == "読影室"
#                     and inferior not in df_weekday[xx[0]].tolist()
#                 ):
#                     if (
#                         df_staff.loc[superior, xx] == "CT"
#                         or df_staff.loc[superior, xx] == "MR"
#                         or df_staff.loc[superior, xx] == "RI"
#                     ):
#                         kensashitsu = df_staff.loc[superior, xx]
#                         df_staff.loc[inferior, xx], df_staff.loc[superior, xx] = (
#                             kensashitsu,
#                             "読影室",
#                         )
#                         df.loc[kensashitsu, xx] = inferior
#                         df_test.loc[inferior, "読影室"] -= 1
#                         df_test.loc[superior, kensashitsu] -= 1
#                         df_test.loc[superior, "読影室"] += 1
#                         df_test.loc[inferior, kensashitsu] += 1
#                         flag00 = "変更した"
#                         break
#             if flag00 == "変更した":
#                 break

#     # エクセルへの出力。

#     # 日付と昼番を入力する。
#     def datehiruban(x, koumoku):
#         for k in range(5):
#             hidsuke = df_weekday.loc[koumoku].tolist()[k]
#             ws.cell(3 + x, 2 + k).value = hidsuke

#     datehiruban(0, "日付")
#     datehiruban(1, "CT昼")
#     datehiruban(2, "MR昼")

#     # CT,MRI,RIの検査番を入力する。
#     def kensaban(x, room):
#         for k in range(10):
#             kensashitsu = df.loc[room].tolist()[k]
#             ws.cell(10 + x, 2 + k).value = kensashitsu

#     kensaban(0, "CT")
#     kensaban(1, "MR")
#     kensaban(2, "RI")

#     d_str = str(d)
#     filename = "勤務表" + d_str + ".xlsx"
#     wb.save(filename)


# if __name__ == "__main__":
#     legacy()
