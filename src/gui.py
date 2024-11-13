import datetime
import json

import streamlit as st
from loguru import logger
from typer import Typer

app = Typer(no_args_is_help=True)


@app.command()
def run():
    # logger = make_logger(name=__name__, level=LogLevel.INFO)

    st.title("Hello Streamlit!")

    data = read_json()

    st.write(data)

    monday = st.date_input("月曜日の日付", datetime.datetime.now())
    # if isinstance(d, datetime.date):
    #     st.write(d.year)
    #     st.write(d.month)
    #     st.write(d.day)

    # セッションステートの初期化
    if "inputs" not in st.session_state:
        st.session_state.inputs = data.copy()

    # フォームの表示
    with st.form("my_form"):
        st.header("Staffs")
        for i, staff in enumerate(st.session_state.inputs["staffs"]):
            st.write(f"ID: {staff['id']}")
            st.session_state.inputs["staffs"][i]["name"] = st.text_input(
                "名前", value=staff["name"], key=staff["name"]
            )

        st.header("Columns")
        for i, column in enumerate(st.session_state.inputs["columns"]):
            st.session_state.inputs["columns"][i] = st.text_input(
                "列名", value=column, key=column
            )

        submit_button = st.form_submit_button(label="Submit")

    # 送信ボタンがクリックされた場合の処理
    if submit_button:
        # JSONファイルへの保存
        write_json(st.session_state.inputs)
        logger.info("Submitted!")

        st.write("Submitted!")
        st.write(st.session_state.inputs)  # 変更後のデータを表示
        del st.session_state.inputs


def read_json():
    with open("dummy.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


def write_json(data):
    with open("dummy.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
