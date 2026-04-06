import streamlit as st
import google.generativeai as genai
from PIL import Image
import PyPDF2
import streamlit.components.v1 as components

# ==========================================
# CẤU HÌNH GIAO DIỆN STREAMLIT (NÂNG CẤP CHUYÊN NGHIỆP)
# ==========================================
st.set_page_config(page_title="Đại Sứ Di Sản Quảng Ninh", page_icon="🌊", layout="centered")

# CUSTOM CSS: Tối ưu UI/UX, bo góc, tạo bóng đổ, giao diện chat
st.markdown("""
<style>
    /* Ẩn menu và footer mặc định của Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Style cho header chính */
    .main-header {
        background: linear-gradient(135deg, #005c97, #363795);
        padding: 2.5rem 1rem;
        border-radius: 16px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.2);
    }
    .main-header h1 {
        color: white !important;
        font-size: 2.5rem;
        font-weight: 900;
        margin-bottom: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .main-header p {
        font-size: 1.1rem;
        opacity: 0.9;
        margin-bottom: 0;
        font-weight: 300;
    }
    
    /* Style cho các Nút bấm (Buttons) */
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        background: linear-gradient(to right, #005c97, #363795);
        color: white;
        font-weight: bold;
        border: none;
        padding: 0.7rem 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .stButton>button:hover {
        transform: translateY(-3px);
        box-shadow: 0 7px 14px rgba(0,0,0,0.2);
        color: #f1f5f9;
    }
    
    /* Style cho các Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        justify-content: center;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px 10px 0 0;
        padding: 12px 20px;
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-bottom: none;
    }
    .stTabs [aria-selected="true"] {
        background-color: #ffffff;
        border-bottom: 3px solid #005c97;
        color: #005c97;
        font-weight: 800;
    }
    
    /* Tùy chỉnh khung Chat */
    .stChatMessage {
        background-color: #f8fafc;
        border-radius: 15px;
        padding: 15px;
        margin-bottom: 15px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 2px 5px rgba(0,0,0,0.02);
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# HÀM XỬ LÝ RAG - HỖ TRỢ NHIỀU FILE
# ==========================================
@st.cache_data(show_spinner=False)
def extract_text_from_pdfs(uploaded_files):
    """Trích xuất văn bản từ NHIỀU file PDF"""
    text = ""
    for file in uploaded_files:
        try:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
        except Exception as e:
            st.sidebar.error(f"Lỗi đọc file {file.name}: {e}")
    return text

# ==========================================
# HÀM KẾT NỐI AI SIÊU BỀN (CHỐNG LỖI 404)
# ==========================================
def robust_ai_generate(prompt, image):
    """Tự động thử nhiều model khác nhau nếu gặp lỗi 404"""
    # Danh sách các model để thử dự phòng
    models_to_try = ['gemini-1.5-flash', 'gemini-1.5-flash-latest', 'gemini-1.5-pro', 'gemini-1.5-pro-latest']
    last_error = None
    
    for model_name in models_to_try:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content([prompt, image])
            return response
        except Exception as e:
            last_error = e
            # Bỏ qua và thử model tiếp theo trong danh sách
            continue
            
    # Nếu tất cả đều lỗi, trả về lỗi cuối cùng
    raise Exception(f"Đã thử tất cả các model nhưng vẫn lỗi. Lỗi cuối: {last_error}")

# ==========================================
# GIAO DIỆN CHÍNH
# ==========================================
st.markdown("""
<div class="main-header">
    <h1>Đại Sứ Di Sản Quảng Ninh</h1>
    <p>Trí tuệ Nhân tạo kết nối Thế hệ trẻ & Lịch sử quê hương</p>
</div>
""", unsafe_allow_html=True)

# ==========================================
# SIDEBAR: CÀI ĐẶT & KHO TRI THỨC
# ==========================================
with st.sidebar:
    st.markdown("### 🛡️ TRUNG TÂM ĐIỀU KHIỂN")
    
    # XỬ LÝ BẢO MẬT API KEY (Ẩn hoàn toàn nếu đã có trong Secrets)
    api_key = ""
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
        st.success("✅ Đã kết nối API an toàn từ máy chủ!")
    except Exception:
        st.warning("⚠️ Chưa cấu hình API Key trên máy chủ.")
        api_key = st.text_input("🔑 Nhập Gemini API Key của bạn:", type="password", help="Chỉ dùng tạm thời. Hãy cài đặt trong Streamlit Secrets để ẩn hoàn toàn ô này.")

    st.markdown("---")
    st.markdown("### 📚 KHO TRI THỨC ĐỊA PHƯƠNG")
    st.caption("Tải lên các tài liệu GDĐP Quảng Ninh để AI tham chiếu thông tin chính xác.")
    
    # HỖ TRỢ UPLOAD NHIỀU FILE
    pdf_files = st.file_uploader("Chọn một hoặc nhiều file PDF", type=["pdf"], accept_multiple_files=True)
    
    context_text = ""
    if pdf_files:
        with st.spinner("Đang đọc và phân tích tài liệu..."):
            context_text = extract_text_from_pdfs(pdf_files)
        if context_text:
            st.success(f"🎉 Đã nạp thành công {len(pdf_files)} tài liệu!")

# ==========================================
# XỬ LÝ LÕI ỨNG DỤNG AI
# ==========================================
if api_key:
    genai.configure(api_key=api_key)
    
    st.markdown("### 📸 Tải Ảnh Di Sản / Ẩm Thực")
    
    col1, col2 = st.columns(2)
    with col1:
        img_file = st.file_uploader("📂 Tải ảnh từ máy", type=['png', 'jpg', 'jpeg'])
    with col2:
        camera_file = st.camera_input("📷 Chụp ảnh trực tiếp")
    
    target_image = img_file if img_file else camera_file
    
    if target_image is not None:
        img = Image.open(target_image)
        # Hiển thị ảnh một cách gọn gàng, bo góc
        st.image(img, caption="Tác phẩm của bạn đã sẵn sàng phân tích", use_column_width=True)
        
        st.markdown("<br>", unsafe_allow_html=True) # Khoảng trắng
        
        # CHIA TABS TÍNH NĂNG
        tab1, tab2, tab3 = st.tabs(["🗣️ Hỏi Đáp Tri Thức", "🌀 Xuyên Không", "🪪 Thẻ Đại Sứ"])
        
        with tab1:
            st.markdown("#### 🔍 Khám phá câu chuyện đằng sau bức ảnh")
            if st.button("Phân tích & Kể chuyện ngay", key="btn_story"):
                story_prompt = f"""
                Bạn là 'Trợ lý ảo Di sản Quảng Ninh'. Hãy nhìn bức ảnh và thực hiện:
                1. Nhận diện bức ảnh này là danh thắng hay món ăn nào của Quảng Ninh.
                2. Viết một đoạn hội thoại ngắn, sống động giữa "Trợ lý ảo" (giọng điệu uyên bác, tự hào) và "Đại sứ học sinh" (giọng điệu Gen Z, năng động, dùng từ lóng vui vẻ như 'flex', 'đỉnh chóp', 'chuẩn không cần chỉnh').
                3. Đảm bảo cung cấp thông tin lịch sử/địa lý/văn hóa chính xác.

                Dữ liệu tham khảo bắt buộc (Trích từ Tài liệu GDĐP Quảng Ninh):
                ---
                {context_text if context_text else "Không có tài liệu tham khảo nào được cung cấp. Hãy dùng kiến thức mặc định chuẩn xác nhất của bạn về Quảng Ninh."}
                ---
                """
                with st.spinner("Đang kết nối hệ thống AI và rà soát kho tri thức..."):
                    try:
                        # Sử dụng hàm siêu bền chống lỗi 404
                        response = robust_ai_generate(story_prompt, img)
                        
                        # Hiển thị giao diện Chatbot chuyên nghiệp
                        with st.chat_message("assistant", avatar="🤖"):
                            st.markdown("**Trợ lý Di sản Số trả lời:**")
                            st.write(response.text)
                    except Exception as e:
                        st.error(f"Đã xảy ra sự cố kết nối AI. Chi tiết lỗi: {e}")
                        
        with tab2:
            st.markdown("#### ⏳ Du hành vượt thời gian")
            st.caption("AI sẽ phân tích hình ảnh và tạo ra một mô tả cực kỳ hùng tráng về địa danh này trong quá khứ.")
            if st.button("Kích hoạt Vòng Xoáy Thời Gian 🚀", key="btn_time"):
                time_travel_prompt = f"""
                Dựa vào bức ảnh này và tài liệu sau đây (nếu có), hãy tạo một đoạn mô tả (prompt) cực kỳ chi tiết, hùng tráng và sống động về bối cảnh lịch sử hoặc địa chất của địa danh này hàng trăm hoặc hàng triệu năm trước. 
                Văn phong điện ảnh, tập trung vào ánh sáng, không khí, hoạt động quân sự hoặc sự biến đổi của thiên nhiên kỳ vĩ.
                
                Tài liệu tham khảo: {context_text[:5000] if context_text else "Không có."}
                """
                with st.spinner("Đang tính toán tọa độ không - thời gian..."):
                    try:
                        tt_response = robust_ai_generate(time_travel_prompt, img)
                        
                        with st.chat_message("assistant", avatar="🌀"):
                            st.success("✨ Cánh cổng thời gian đã mở!")
                            st.write(tt_response.text)
                    except Exception as e:
                        st.error(f"Đã xảy ra sự cố kết nối AI. Chi tiết lỗi: {e}")
                        
        with tab3:
            st.markdown("#### 🌟 Khẳng định niềm tự hào quê hương")
            user_name = st.text_input("Tên Đại sứ của bạn:", "Học sinh yêu Quảng Ninh")
            message = st.text_area("Thông điệp lan tỏa:", "Di sản quê hương mình đỉnh chóp! Cùng nhau bảo vệ và phát huy nhé mọi người! ❤️")
            
            if st.button("Tạo thẻ Kỹ thuật số 💳", key="btn_card"):
                # Giao diện thẻ được thiết kế lại sang trọng hơn
                card_html = f"""
                <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
                <div class="flex justify-center items-center py-4">
                    <div class="relative bg-white w-full max-w-lg rounded-2xl shadow-2xl overflow-hidden border-2 border-gray-100">
                        <div class="absolute top-0 w-full h-3 bg-gradient-to-r from-blue-700 via-blue-500 to-indigo-600"></div>
                        <div class="p-7">
                            <div class="flex items-center space-x-5 mb-6">
                                <div class="w-16 h-16 rounded-full bg-gradient-to-br from-blue-700 to-indigo-500 flex items-center justify-center text-white font-extrabold text-2xl shadow-lg ring-4 ring-blue-50">
                                    QN
                                </div>
                                <div>
                                    <div class="uppercase tracking-widest text-xs text-blue-600 font-bold mb-1">Đại sứ Di sản Kỹ thuật số</div>
                                    <p class="text-gray-900 font-bold text-xl leading-tight">{user_name}</p>
                                </div>
                            </div>
                            
                            <div class="relative bg-gray-50 p-6 rounded-xl border border-gray-200 mb-6">
                                <svg class="absolute top-3 left-3 w-8 h-8 text-blue-200 opacity-50" fill="currentColor" viewBox="0 0 24 24"><path d="M14.017 21v-7.391c0-5.704 3.731-9.57 8.983-10.609l.995 2.151c-2.432.917-3.995 3.638-3.995 5.849h4v10h-9.983zm-14.017 0v-7.391c0-5.704 3.748-9.57 9-10.609l.996 2.151c-2.433.917-3.996 3.638-3.996 5.849h3.983v10h-9.983z"/></svg>
                                <p class="text-gray-800 font-medium italic text-center px-4 leading-relaxed z-10 relative">
                                    {message}
                                </p>
                            </div>
                            
                            <div class="flex justify-between items-center border-t border-gray-100 pt-5">
                                <div class="flex items-center space-x-2">
                                    <span class="relative flex h-3 w-3">
                                      <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                                      <span class="relative inline-flex rounded-full h-3 w-3 bg-green-500"></span>
                                    </span>
                                    <span class="text-xs text-gray-500 font-bold tracking-wider">AI VERIFIED</span>
                                </div>
                                <div class="text-xs text-indigo-500 font-bold bg-indigo-50 px-4 py-1.5 rounded-full border border-indigo-100">
                                    Proudly from Quang Ninh
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                """
                components.html(card_html, height=400)
                st.success("Tạo thẻ thành công! Bạn có thể dùng điện thoại chụp ảnh màn hình để chia sẻ nhé! 📸")

else:
    st.info("👈 Bắt đầu bằng cách kiểm tra hệ thống API ở thanh bên trái.")
