import streamlit as st
import google.generativeai as genai
from PIL import Image
import PyPDF2
import io
import streamlit.components.v1 as components

# ==========================================
# CẤU HÌNH GIAO DIỆN STREAMLIT
# ==========================================
st.set_page_config(page_title="Đại Sứ Di Sản Quảng Ninh", page_icon="🌊", layout="centered")

# ==========================================
# HÀM XỬ LÝ RAG (ĐỌC FILE PDF)
# ==========================================
@st.cache_data
def extract_text_from_pdf(uploaded_file):
    """Trích xuất văn bản từ file PDF Tài liệu GDĐP để làm Knowledge Base"""
    try:
        reader = PyPDF2.PdfReader(uploaded_file)
        text = ""
        for page in reader.pages[:15]: # Đọc 15 trang đầu
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        return f"Lỗi đọc file PDF: {e}"

# ==========================================
# GIAO DIỆN CHÍNH & SIDEBAR
# ==========================================
st.title("🌊 Khám Phá Di Sản Quảng Ninh Cùng AI")
st.markdown("*Ứng dụng nhận diện, kể chuyện và xuyên không lịch sử*")

with st.sidebar:
    st.header("⚙️ Cài đặt (Dành cho Giáo viên)")
    
    # Ưu tiên lấy API Key từ cấu hình bảo mật của Streamlit Cloud (Secrets)
    try:
        secret_api_key = st.secrets["GEMINI_API_KEY"]
    except:
        secret_api_key = ""
        
    api_key = st.text_input("Nhập Google Gemini API Key:", value=secret_api_key, type="password", help="Nếu đã cấu hình trong Secrets, không cần nhập lại.")
    
    st.subheader("📚 Nạp Kiến Thức (RAG)")
    st.info("Tải lên 'Tài liệu GDĐP tỉnh Quảng Ninh' (PDF) để AI trả lời chính xác 100%.")
    pdf_file = st.file_uploader("Tải file PDF", type=["pdf"])
    
    context_text = ""
    if pdf_file is not None:
        with st.spinner("Đang xử lý dữ liệu địa phương..."):
            context_text = extract_text_from_pdf(pdf_file)
        st.success("Đã nạp kiến thức thành công!")

# ==========================================
# XỬ LÝ ẢNH & LOGIC AI
# ==========================================
if api_key:
    genai.configure(api_key=api_key)
    # Sử dụng model public ổn định nhất của Google cho xử lý đa phương thức
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    st.subheader("📸 Chụp hoặc Tải ảnh di sản/món ăn")
    
    img_file = st.file_uploader("Chọn ảnh từ thư viện", type=['png', 'jpg', 'jpeg'])
    camera_file = st.camera_input("Hoặc dùng Camera để chụp trực tiếp")
    
    target_image = img_file if img_file else camera_file
    
    if target_image is not None:
        img = Image.open(target_image)
        st.image(img, caption="Ảnh bạn vừa tải lên", use_column_width=True)
        
        tab1, tab2, tab3 = st.tabs(["🗣️ Kể chuyện & Nhận diện", "🌀 Xuyên Không", "🪪 Thẻ Đại Sứ"])
        
        story_prompt = f"""
        Bạn là 'Trợ lý ảo Di sản Quảng Ninh'. Hãy nhìn bức ảnh và thực hiện:
        1. Nhận diện bức ảnh này là danh thắng hay món ăn nào của Quảng Ninh.
        2. Viết một đoạn hội thoại ngắn giữa "Trợ lý ảo" (giọng điệu uyên bác) và "Đại sứ học sinh" (giọng điệu Gen Z, năng động, dùng từ lóng vui vẻ như 'flex', 'đỉnh chóp').
        Dữ liệu tham khảo bắt buộc (Tài liệu GDĐP Quảng Ninh):
        {context_text[:3000] if context_text else "Hãy dùng kiến thức chuẩn xác nhất của bạn về Quảng Ninh."}
        """
        
        with tab1:
            if st.button("Phân tích & Kể chuyện"):
                with st.spinner("Đang phân tích và sáng tác kịch bản..."):
                    try:
                        response = model.generate_content([story_prompt, img])
                        st.markdown("### 🎙️ Câu chuyện Di sản")
                        st.write(response.text)
                    except Exception as e:
                        st.error(f"Lỗi AI: {e}. Vui lòng kiểm tra lại API Key hoặc mạng.")
                        
        with tab2:
            st.markdown("### 🌀 Mô tả bối cảnh Xuyên Không")
            if st.button("Kích hoạt vòng xoáy thời gian"):
                time_travel_prompt = "Dựa vào bức ảnh này, hãy tạo một đoạn mô tả (prompt) cực kỳ chi tiết, hùng tráng và sống động về bối cảnh lịch sử hoặc địa chất của địa danh này hàng trăm hoặc hàng triệu năm trước bằng tiếng Việt."
                with st.spinner("Đang du hành thời gian..."):
                    try:
                        tt_response = model.generate_content([time_travel_prompt, img])
                        st.success("Mô tả Xuyên không của bạn:")
                        st.write(tt_response.text)
                    except Exception as e:
                        st.error(f"Lỗi AI: {e}")
                        
        with tab3:
            st.markdown("### 🪪 Chia sẻ thông điệp Đại sứ")
            user_name = st.text_input("Nhập tên của bạn (Đại sứ):", "Gen Z Yêu Quảng Ninh")
            message = st.text_area("Thông điệp của bạn:", "Di sản quê hương mình đỉnh chóp! Cùng nhau bảo tồn nhé mọi người!")
            
            if st.button("Tạo thẻ Kỹ thuật số"):
                card_html = f"""
                <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
                <div class="max-w-md mx-auto bg-gradient-to-r from-blue-50 to-blue-100 rounded-xl shadow-lg overflow-hidden md:max-w-2xl m-4 border-l-4 border-blue-500">
                    <div class="p-6">
                        <div class="flex items-center space-x-4 mb-4">
                            <div class="w-12 h-12 rounded-full bg-blue-500 flex items-center justify-center text-white font-bold text-xl">QN</div>
                            <div>
                                <div class="uppercase tracking-wide text-sm text-blue-600 font-bold">Đại sứ Di sản Quảng Ninh</div>
                                <p class="text-gray-800 font-semibold">{user_name}</p>
                            </div>
                        </div>
                        <div class="bg-white p-4 rounded-lg shadow-inner mb-4 italic text-gray-700">"{message}"</div>
                        <div class="mt-4 flex justify-between items-center text-xs text-gray-500 font-medium">
                            <span>📱 Quét & Khám phá</span>
                            <span>Powered by AI & Gen Z</span>
                        </div>
                    </div>
                </div>
                """
                components.html(card_html, height=250)
else:
    st.warning("👈 Vui lòng nhập Google Gemini API Key ở thanh bên trái để bắt đầu!")