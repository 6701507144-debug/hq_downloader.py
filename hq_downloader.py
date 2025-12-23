import streamlit as st
import yt_dlp
import os
import shutil

# ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="4K Video Downloader", page_icon="💎")
st.title("💎 ระบบดูดคลิป 4K (ชัดสุด + iPhone รองรับ)")

url = st.text_input("🔗 วางลิงก์คลิปที่นี่:", placeholder="https://...")

# ส่วนอัปโหลด Cookies (เผื่อใช้กับคลิปส่วนตัวแบบชัดๆ)
with st.expander("🔐 ตั้งค่า Cookies (สำหรับคลิปส่วนตัว)"):
    uploaded_cookies = st.file_uploader("อัปโหลดไฟล์ cookies.txt", type=['txt'])

def download_video_hq(link, cookie_file):
    output_folder = "downloads_hq"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        
    # สูตรลับ: ชัดสุด + แปลงเป็น MP4
    ydl_opts = {
        # เลือก Video ชัดสุด + Audio ชัดสุด
        'format': 'bestvideo+bestaudio/best',
        
        # สั่งรวมร่างแล้วแปลงเป็น MP4 (เพื่อให้ iPhone อ่านออก)
        'merge_output_format': 'mp4',
        
        'outtmpl': f'{output_folder}/%(title)s.%(ext)s',
        'noplaylist': True,
        'restrictfilenames': True,
    }
    
    if cookie_file is not None:
        with open("temp_cookies_hq.txt", "wb") as f:
            f.write(cookie_file.getbuffer())
        ydl_opts['cookiefile'] = "temp_cookies_hq.txt"

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            st.info("⏳ กำลังดูดและแปลงไฟล์คุณภาพสูง... (ขั้นตอนนี้จะนานกว่าปกตินะครับ)")
            info = ydl.extract_info(link, download=True)
            filename = ydl.prepare_filename(info)
            # แก้บั๊กนามสกุลไฟล์นิดหน่อยเผื่อ yt-dlp คืนค่ามาผิด
            base, ext = os.path.splitext(filename)
            if ext != '.mp4':
                filename = base + '.mp4'
            return filename
    except Exception as e:
        st.error(f"❌ เกิดข้อผิดพลาด: {e}")
        return None

if st.button("🚀 ดาวน์โหลดแบบ HQ", use_container_width=True):
    if url:
        file_path = download_video_hq(url, uploaded_cookies)
        
        if file_path and os.path.exists(file_path):
            st.success("✅ สำเร็จ! ได้ไฟล์ชัดเปรี้ยะ")
            
            file_name_only = os.path.basename(file_path)
            with open(file_path, "rb") as file:
                st.download_button(
                    label=f"📥 เซฟลงมือถือ ({file_name_only})",
                    data=file,
                    file_name=file_name_only,
                    mime="video/mp4",
                    use_container_width=True
                )
            
            if os.path.exists("temp_cookies_hq.txt"):
                os.remove("temp_cookies_hq.txt")