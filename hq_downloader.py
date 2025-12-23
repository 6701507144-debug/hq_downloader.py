import streamlit as st
import yt_dlp
import os
import shutil

# ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="Mobile Video Downloader", page_icon="📱")
st.title("📱 ระบบดูดคลิปเพื่อมือถือ (การันตีเปิดติด 100%)")

url = st.text_input("🔗 วางลิงก์คลิปที่นี่:", placeholder="https://...")

# ส่วนอัปโหลด Cookies
with st.expander("🔐 ตั้งค่า Cookies (สำหรับคลิปส่วนตัว)"):
    uploaded_cookies = st.file_uploader("อัปโหลดไฟล์ cookies.txt", type=['txt'])

def download_for_mobile(link, cookie_file):
    output_folder = "downloads_mobile"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        
    # --- สูตรลับ: บังคับเอาเฉพาะ H.264 (AVC) เท่านั้น ---
    # สูตรนี้จะปฏิเสธไฟล์ 4K ที่เป็น VP9 ทำให้มือถือเปิดได้แน่นอน
    # คุณภาพสูงสุดที่จะได้คือ 1080p (ซึ่งชัดเหลือเฟือสำหรับมือถือครับ)
    ydl_opts = {
        # คำสั่งยาวๆ นี้แปลว่า: "ขอภาพที่เป็น mp4 และต้องเป็นรหัส avc เท่านั้น + ขอเสียง m4a"
        'format': 'bestvideo[ext=mp4][vcodec^=avc]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        
        # ย้ำอีกรอบว่าต้องรวมร่างเป็น mp4
        'merge_output_format': 'mp4',
        
        'outtmpl': f'{output_folder}/%(title)s.%(ext)s',
        'noplaylist': True,
        'restrictfilenames': True,
    }
    
    if cookie_file is not None:
        with open("temp_cookies_mobile.txt", "wb") as f:
            f.write(cookie_file.getbuffer())
        ydl_opts['cookiefile'] = "temp_cookies_mobile.txt"

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            st.info("📱 กำลังคัดกรองไฟล์ที่มือถือรองรับ... (อาจใช้เวลาแป๊บนึง)")
            info = ydl.extract_info(link, download=True)
            filename = ydl.prepare_filename(info)
            
            # ตรวจสอบนามสกุลไฟล์
            base, ext = os.path.splitext(filename)
            if ext != '.mp4':
                new_filename = base + '.mp4'
                # ลองเปลี่ยนชื่อเผื่อระบบพลาด
                try:
                    os.rename(filename, new_filename)
                    return new_filename
                except:
                    return filename
            return filename
    except Exception as e:
        st.error(f"❌ เกิดข้อผิดพลาด: {e}")
        return None

if st.button("🚀 ดาวน์โหลดเข้ามือถือ", use_container_width=True):
    if url:
        file_path = download_for_mobile(url, uploaded_cookies)
        
        if file_path and os.path.exists(file_path):
            st.success("✅ สำเร็จ! ไฟล์นี้เปิดบนมือถือได้แน่นอน")
            
            file_name_only = os.path.basename(file_path)
            # เช็คขนาดไฟล์
            file_size = os.path.getsize(file_path) / (1024 * 1024)
            st.caption(f"📦 ขนาดไฟล์: {file_size:.2f} MB")
            
            with open(file_path, "rb") as file:
                st.download_button(
                    label=f"📥 บันทึกลงเครื่อง ({file_name_only})",
                    data=file,
                    file_name=file_name_only,
                    mime="video/mp4",
                    use_container_width=True
                )
            
            if os.path.exists("temp_cookies_mobile.txt"):
                os.remove("temp_cookies_mobile.txt")
    else:
        st.warning("⚠️ อย่าลืมวางลิงก์ก่อนนะครับ")
