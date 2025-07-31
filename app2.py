import streamlit as st
import pandas as pd
import os
import qrcode
from io import BytesIO
from PIL import Image
from streamlit_autorefresh import st_autorefresh

# Cấu hình trang
st.set_page_config(page_title="Khảo sát kỹ năng từ chối",
                   page_icon="🧠", layout="centered")

# Tự động làm mới sau mỗi 5 giây
st_autorefresh(interval=5000, key="refresh")

# File dữ liệu
VOTE_FILE = "votes.csv"

questions = [
    "1. Em cảm thấy khó xử khi từ chối lời rủ rê của bạn bè?",
    "2. Em từng làm điều mình không muốn chỉ vì sợ bạn giận?",
    "3. Em nghĩ nói “Không” sẽ khiến người khác ghét em?",
    "4. Em biết phân biệt đúng – sai trong những tình huống bạn bè rủ rê?",
    "5. Em biết cách từ chối lịch sự nhưng vẫn giữ được mối quan hệ?",
    "6. Em từng gặp tình huống khiến em hối hận vì đã không nói “Không” kịp thời?",
    "7. Em dễ bị áp lực khi người khác nài nỉ nhiều lần, dù em không muốn?",
    "8. Em có thể nói “Không” khi bị người lạ trên mạng xin thông tin cá nhân?",
    "9. Em từng chứng kiến một bạn khác bị ép buộc mà không dám từ chối?",
    "10. Em muốn học cách nói “Không” mạnh mẽ, rõ ràng nhưng không làm tổn thương người khác?"
]

# Khởi tạo file nếu chưa có
if not os.path.exists(VOTE_FILE):
    df_init = pd.DataFrame(columns=[f"Q{i+1}" for i in range(len(questions))])
    df_init.to_csv(VOTE_FILE, index=False)

st.title("🧠 Khảo sát: Kỹ năng nói 'Không'")

# QR Code truy cập
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    url = "https://surveyssss.streamlit.app/"
    qr = qrcode.make(url)
    buf = BytesIO()
    qr.save(buf)
    buf.seek(0)
    st.image(Image.open(buf),
             caption="📱 Quét mã QR để truy cập khảo sát", width=180)

st.divider()

# FORM phản hồi
if "submitted" not in st.session_state:
    st.session_state.submitted = False

if not st.session_state.submitted:
    with st.form("survey_form"):
        st.header("📝 Trả lời khảo sát")
        st.write("Hãy chọn ✅ Có hoặc ❌ Không cho từng câu hỏi:")
        user_votes = []
        for i, q in enumerate(questions):
            vote = st.radio(q, ["✅ Có", "❌ Không"], key=f"q{i}")
            user_votes.append("Yes" if vote == "✅ Có" else "No")
        submitted = st.form_submit_button("📤 Gửi phản hồi")
        if submitted:
            df = pd.read_csv(VOTE_FILE)
            new_row = pd.DataFrame([user_votes], columns=df.columns)
            df = pd.concat([df, new_row], ignore_index=True)
            df.to_csv(VOTE_FILE, index=False)
            st.success("🎉 Cảm ơn bạn đã hoàn thành khảo sát!")
            st.session_state.submitted = True
else:
    st.info("✅ Bạn đã gửi phản hồi trong phiên hiện tại.")

st.divider()
st.subheader("📊 Kết quả khảo sát")

# Hiển thị thống kê
try:
    df = pd.read_csv(VOTE_FILE)
    if len(df) > 0:
        for i, q in enumerate(questions):
            yes_count = (df[f"Q{i+1}"] == "Yes").sum()
            no_count = (df[f"Q{i+1}"] == "No").sum()
            total = yes_count + no_count

            if total > 0:
                yes_percent = round(yes_count / total * 100, 1)
                no_percent = round(no_count / total * 100, 1)
                st.markdown(f"**{q}**")
                st.progress(yes_percent / 100, text=f"✅ Có: {yes_percent}%")
                st.progress(no_percent / 100, text=f"❌ Không: {no_percent}%")
            else:
                st.info(f"Chưa có phản hồi cho: {q}")
    else:
        st.info("⏳ Chưa có dữ liệu khảo sát.")
except Exception as e:
    st.error(f"Lỗi khi đọc dữ liệu: {e}")

st.divider()
st.subheader("⚙️ Quản lý dữ liệu")

# Nút xóa dữ liệu có mật khẩu
with st.expander("🔐 Xóa toàn bộ dữ liệu khảo sát"):
    password = st.text_input("Nhập mật khẩu để xác nhận xóa", type="password")
    if st.button("🗑️ Xóa dữ liệu"):
        if password == "112233":
            os.remove(VOTE_FILE)
            df_init = pd.DataFrame(
                columns=[f"Q{i+1}" for i in range(len(questions))])
            df_init.to_csv(VOTE_FILE, index=False)
            st.success("✅ Đã xóa toàn bộ dữ liệu khảo sát.")
            st.session_state.submitted = False
        else:
            st.error("❌ Mật khẩu không chính xác.")
