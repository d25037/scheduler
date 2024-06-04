import json

import streamlit as st


def streamlit():
    st.title("Hello Streamlit!")

    data = read_json()

    st.write(data)

    # セッションステートの初期化
    if "inputs" not in st.session_state:
        st.session_state.inputs = {
            staff["id"]: staff["name"] for staff in data["staffs"]
        }

    # フォームの表示
    with st.form("my_form"):
        for staff_id, name in st.session_state.inputs.items():
            st.write(f"ID: {staff_id}")
            st.session_state.inputs[staff_id] = st.text_input(
                "名前", value=name, key=staff_id
            )

        submit_button = st.form_submit_button(label="Submit")

    # 送信ボタンがクリックされた場合の処理
    if submit_button:
        # JSONデータの更新
        for staff in data["staffs"]:
            if staff["id"] in st.session_state.inputs:
                staff["name"] = st.session_state.inputs[staff["id"]]

        # JSONファイルへの保存
        write_json(data)
        print("Submitted!")

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
