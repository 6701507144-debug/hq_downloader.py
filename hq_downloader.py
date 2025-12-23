import streamlit as st
import yt_dlp
import os
import time

# ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="Universal Downloader", page_icon="🌎")
st.title("🌎 ระบบดูดคลิปจักรวาล (All-in-One)")
st.write("เลือกรูปแบบที่ต้องการได้เลยครับ รองรับทั้งมือถือและ PC")

# 1. รับลิงก์
url = st.text_input("🔗 วางลิงก์คลิปที่นี่:", placeholder="https://...")

# 2. ตัวเลือกการดาวน์โหลด (หัวใจสำคัญ)
st.write("---")
st.subheader("⚙️ ตั้งค่าก่อนโหลด")

col1, col2 = st.columns(2)

with col1:
    download_type = st.radio(
        "เลือกประเภทไฟล์:",
        ("🎬 วิดีโอ (Video)", "🎵 เพลง/เสียงอย่างเดียว (MP3)")
    )

with col2:
    if download_type == "🎬 วิดีโอ (Video)":
        quality_mode = st.selectbox(
            "เลือกความคมชัด:",
            (
                "📱 โหมดมือถือ/ทั่วไป (1080p - H.264) [แนะนำ! เปิดได้ชัวร์]",
                "💎 โหมดชัดสูงสุด (4K/2K) [ภาพสวยสุด แต่อาจต้องใช้ VLC เปิด]",
                "📉 โหมดประหยัดเน็ต (480p/360p)"
            )
        )
    else:
        st.info("🎵 ระบบจะแปลงเป็น MP3 คุณภาพสูงให้ครับ")
        quality_mode = "Audio"

# ส่วนอัปโหลด Cookies
with st.expander("🔐 ตั้งค่า Cookies (สำหรับคลิปส่วนตัว/Member)"):
    uploaded_cookies = st.file_uploader("อัปโหลดไฟล์ cookies.txt", type=['txt'])

# --- ฟังก์ชันดาวน์โหลดระดับเทพ ---
def download_master(link, type_mode, q_mode, cookie_file):
    output_folder = "downloads_master"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        
    # ตั้งค่าพื้นฐาน
    ydl_opts = {
        'outtmpl': f'{output_folder}/%(title)s.%(ext)s',
        'noplaylist': True,
        'restrictfilenames': True,
    }

    # --- Logic การเลือกสูตร ---
    if type_mode == "🎵 เพลง/เสียงอย่างเดียว (MP3)":
        # สูตรโหลดเพลง: ดึงเฉพาะเสียงแล้วแปลงเป็น mp3
        ydl_opts.update({
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        })
        target_ext = '.mp3'
        
    elif "📱 โหมดมือถือ" in q_mode:
        # สูตรมือถือ: บังคับ H.264 (avc) + MP4 (สำคัญมากสำหรับ iPhone)
        ydl_opts.update({
            'format': 'bestvideo[ext=mp4][vcodec^=avc]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'merge_output_format': 'mp4'
        })
        target_ext = '.mp4'

    elif "💎 โหมดชัดสูงสุด" in q_mode:
        # สูตรชัดสุด: ไม่สน Codec ขอชัดไว้ก่อน (เหมาะกับ PC + VLC)
        ydl_opts.update({
            'format': 'bestvideo+bestaudio/best',
            'merge_output_format': 'mp4'
        })
        target_ext = '.mp4'
        
    elif "📉 โหมดประหยัด" in q_mode:
        # สูตรประหยัด: จำกัดความสูงภาพไม่เกิน 480p
        ydl_opts.update({
            'format': 'bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/best[height<=480][ext=mp4]',
            'merge_output_format': 'mp4'
        })
        target_ext = '.mp4'

    # จัดการ Cookies
    if cookie_file is not None:
        with open("temp_cookies.txt", "wb") as f:
            f.write(cookie_file.getbuffer())
        ydl_opts['cookiefile'] = "temp_cookies.txt"

    # เริ่มปฏิบัติการ
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            status_text = st.empty() # สร้างกล่องข้อความสถานะ
            status_text.info(f"⏳ กำลังดำเนินการ... ({q_mode})")
            
            info = ydl.extract_info(link, download=True)
            filename = ydl.prepare_filename(info)
            
            # ปรับนามสกุลไฟล์ให้ตรงกับความเป็นจริง (โดยเฉพาะ MP3)
            base, ext = os.path.splitext(filename)
            final_filename = base + target_ext
            
            # กรณีที่เป็น MP3 ชื่อไฟล์จาก prepare_filename อาจยังไม่เปลี่ยน เราต้องเดาชื่อใหม่
            if type_mode == "🎵 เพลง/เสียงอย่างเดียว (MP3)":
                if os.path.exists(final_filename):
                    return final_filename
                else:
                    # บางที ffmpeg ยังทำงานไม่เสร็จ รอแป๊บนึง
                    time.sleep(1)
                    return final_filename if os.path.exists(final_filename) else filename
            
            # กรณี Video
            if ext != target_ext and target_ext == '.mp4':
                 return base + '.mp4'
                 
            return filename
            
    except Exception as e:
        st.error(f"❌ เกิดข้อผิดพลาด: {e}")
        return None

# --- ปุ่มกดสั่งงาน ---
if st.button("🚀 เริ่มดาวน์โหลดเดี๋ยวนี้", use_container_width=True):
    if url:
        file_path = download_master(url, download_type, quality_mode, uploaded_cookies)
        
        if file_path and os.path.exists(file_path):
            st.success("✅ สำเร็จ! ไฟล์มารอแล้วครับ")
            
            file_name_only = os.path.basename(file_path)
            file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
            
            st.info(f"📦 ไฟล์: {file_name_only} | ขนาด: {file_size_mb:.2f} MB")
            
            # กำหนด MIME Type ให้ถูกต้อง เพื่อให้มือถือไม่งง
            mime_type = "audio/mpeg" if download_type == "🎵 เพลง/เสียงอย่างเดียว (MP3)" else "video/mp4"
            
            with open(file_path, "rb") as file:
                btn = st.download_button(
                    label=f"📥 แตะเพื่อบันทึก ({file_name_only})",
                    data=file,
                    file_name=file_name_only,
                    mime=mime_type,
                    use_container_width=True
                )
            
            # เคลียร์ขยะ
            if os.path.exists("temp_cookies.txt"):
                os.remove("temp_cookies.txt")
    else:
        st.warning("⚠️ กรุณาวางลิงก์ก่อนครับ")
