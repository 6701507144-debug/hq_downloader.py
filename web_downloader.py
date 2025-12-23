import streamlit as st
import yt_dlp
import os
import shutil

# ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="My Cloud Downloader", page_icon="☁️")
st.title("☁️ ระบบดูดคลิปเวอร์ชัน Cloud (ปิดคอมก็ใช้ได้)")

# 1. รับลิงก์
url = st.text_input("🔗 วางลิงก์คลิปที่นี่:", placeholder="https://...")

# 2. ส่วนเสริมสำหรับคลิปส่วนตัว (Private Video)
with st.expander("🔐 ตั้งค่าสำหรับคลิปส่วนตัว (ต้องใช้ Cookies)"):
    st.write("ถ้าเป็นคลิปทั่วไป (YouTube/TikTok) ไม่ต้องใช้อันนี้ครับ")
    st.write("แต่ถ้าเป็นคลิปกลุ่มปิด Facebook หรือ Member YouTube ต้องอัปโหลดไฟล์ cookies.txt")
    uploaded_cookies = st.file_uploader("อัปโหลดไฟล์ cookies.txt ที่นี่", type=['txt'])

# 3. ฟังก์ชันดาวน์โหลด
def download_video(link, cookie_file):
    # สร้างโฟลเดอร์ชั่วคราว
    output_folder = "downloads_cloud"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # เคลียร์ไฟล์เก่าทิ้งก่อน (เพื่อไม่ให้ Server เต็ม)
    # for f in os.listdir(output_folder):
    #     os.remove(os.path.join(output_folder, f))

    # ตั้งค่า yt-dlp
    ydl_opts = {
        'format': 'best',
        'outtmpl': f'{output_folder}/%(title)s.%(ext)s',
        'noplaylist': True,
        'restrictfilenames': True,
    }
    
    # ถ้ามีการอัปโหลด Cookies ให้เอาไปใช้
    if cookie_file is not None:
        # บันทึกไฟล์ cookies ชั่วคราวเพื่อให้ yt-dlp อ่าน
        with open("temp_cookies.txt", "wb") as f:
            f.write(cookie_file.getbuffer())
        ydl_opts['cookiefile'] = "temp_cookies.txt"

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            st.info("⏳ Cloud กำลังทำงาน... (ดึงไฟล์จากเว็บต้นทาง)")
            info = ydl.extract_info(link, download=True)
            filename = ydl.prepare_filename(info)
            return filename
    except Exception as e:
        st.error(f"❌ เกิดข้อผิดพลาด: {e}")
        return None

# 4. ปุ่มสั่งงาน
if st.button("🚀 เริ่มดาวน์โหลดบน Cloud", use_container_width=True):
    if url:
        file_path = download_video(url, uploaded_cookies)
        
        if file_path and os.path.exists(file_path):
            st.success("✅ สำเร็จ! ไฟล์มารอที่ Cloud แล้ว")
            
            # ปุ่มให้ user โหลดจาก Cloud เข้ามือถือ
            file_name_only = os.path.basename(file_path)
            with open(file_path, "rb") as file:
                st.download_button(
                    label=f"📥 ดึงไฟล์เข้ามือถือ ({file_name_only})",
                    data=file,
                    file_name=file_name_only,
                    mime="video/mp4",
                    use_container_width=True
                )
            
            # ลบไฟล์ cookies ชั่วคราวทิ้ง (เพื่อความปลอดภัย)
            if os.path.exists("temp_cookies.txt"):
                os.remove("temp_cookies.txt")
    else:
        st.warning("⚠️ อย่าลืมใส่ลิงก์นะคร้าบ")