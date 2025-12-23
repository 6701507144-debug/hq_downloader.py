import streamlit as st
import yt_dlp
import os
import shutil

# ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="Ultimate Downloader", page_icon="💎")
st.title("💎 ระบบดูดคลิปอัจฉริยะ (เลือกความชัดได้)")

url = st.text_input("🔗 วางลิงก์คลิปที่นี่:", placeholder="https://...")

# --- ส่วนตั้งค่าการดาวน์โหลด (ไฮไลท์ใหม่!) ---
st.write("---")
st.write("📺 **เลือกโหมดความคมชัด:**")
quality_mode = st.radio(
    "เลือกรูปแบบไฟล์ที่ต้องการ:",
    (
        "✅ 1. โหมดปลอดภัย (1080p Max) - เปิดได้ทุกเครื่องแน่นอน 100%",
        "🚀 2. โหมดวัดใจ (4K/2K Original) - ชัดสุดๆ แต่อาจต้องใช้ VLC เปิด"
    )
)

# ส่วนอัปโหลด Cookies
with st.expander("🔐 ตั้งค่า Cookies (สำหรับคลิปส่วนตัว)"):
    uploaded_cookies = st.file_uploader("อัปโหลดไฟล์ cookies.txt", type=['txt'])

def download_video_smart(link, mode, cookie_file):
    output_folder = "downloads_smart"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        
    # ตั้งค่าพื้นฐาน
    ydl_opts = {
        'outtmpl': f'{output_folder}/%(title)s.%(ext)s',
        'noplaylist': True,
        'restrictfilenames': True,
        'merge_output_format': 'mp4', # บังคับปลายทางเป็น mp4 เสมอ
    }

    # --- กำหนดสูตรการโหลดตามโหมดที่เลือก ---
    if "1. โหมดปลอดภัย" in mode:
        # สูตรนี้จะหาไฟล์ที่เป็น H.264 (avc) เท่านั้น ซึ่ง iPhone/Windows รักมาก
        # มักจะได้ความชัดสูงสุดที่ 1080p (เพราะ YouTube ไม่ปล่อย 4K เป็น H.264)
        ydl_opts['format'] = 'bestvideo[ext=mp4][vcodec^=avc]+bestaudio[ext=m4a]/best[ext=mp4]/best'
        st.info("🛡️ กำลังค้นหาไฟล์แบบ H.264 (เปิดง่ายที่สุด)...")
    else:
        # สูตรเดิม: เอาชัดสุดไม่สนลูกใคร (VP9/AV1)
        ydl_opts['format'] = 'bestvideo+bestaudio/best'
        st.info("🚀 กำลังดึงไฟล์ต้นฉบับคุณภาพสูงสุด (อาจเป็น VP9)...")
    
    # จัดการ Cookies
    if cookie_file is not None:
        with open("temp_cookies_smart.txt", "wb") as f:
            f.write(cookie_file.getbuffer())
        ydl_opts['cookiefile'] = "temp_cookies_smart.txt"

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            st.write("⏳ ระบบกำลังประมวลผล... (Cloud กำลังทำงาน)")
            info = ydl.extract_info(link, download=True)
            filename = ydl.prepare_filename(info)
            
            # เช็คและแก้ชื่อไฟล์ให้ถูกต้อง (เผื่อ yt-dlp คืนค่ามาผิด)
            base, ext = os.path.splitext(filename)
            if ext != '.mp4':
                # ถ้าไฟล์จริงไม่ใช่ mp4 เราจะแกล้งๆ เปลี่ยนชื่อมัน (เพราะเราสั่ง merge แล้ว)
                new_filename = base + '.mp4'
                if os.path.exists(filename):
                     # กรณีที่ ffmpeg แปลงให้แล้วแต่ชื่อยังเพี้ยน
                    try:
                        os.rename(filename, new_filename)
                        filename = new_filename
                    except:
                        pass # ถ้าเปลี่ยนไม่ได้ก็ใช้ชื่อเดิม
            
            return filename
    except Exception as e:
        st.error(f"❌ เกิดข้อผิดพลาด: {e}")
        return None

if st.button("🚀 เริ่มดาวน์โหลด", use_container_width=True):
    if url:
        file_path = download_video_smart(url, quality_mode, uploaded_cookies)
        
        if file_path and os.path.exists(file_path):
            st.success("✅ เรียบร้อย! พร้อมส่งเข้ามือถือ")
            
            file_name_only = os.path.basename(file_path)
            file_size = os.path.getsize(file_path) / (1024 * 1024) # ขนาด MB
            
            st.write(f"📦 ขนาดไฟล์: {file_size:.2f} MB")
            
            with open(file_path, "rb") as file:
                st.download_button(
                    label=f"📥 ดาวน์โหลดลงเครื่อง ({file_name_only})",
                    data=file,
                    file_name=file_name_only,
                    mime="video/mp4",
                    use_container_width=True
                )
            
            # ลบขยะ
            if os.path.exists("temp_cookies_smart.txt"):
                os.remove("temp_cookies_smart.txt")
    else:
        st.warning("⚠️ อย่าลืมใส่ลิงก์นะครับ")
