import streamlit as st
import os
import subprocess
import time
import shutil

# ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="Video Optimizer Ultimate", page_icon="🎥", layout="centered")
st.title("🎥 Smart Export: Ultimate Edition")
st.write("เครื่องมือแปลงไฟล์ครอบจักรวาล: ส่งไลน์ชัด / คลิปสั้น 4K / ทำงานไว")

# --- 1. ระบบตรวจเช็คความพร้อม (System Check) ---
st.write("---")
# เช็ค FFmpeg ก่อนเริ่ม
if not shutil.which("ffmpeg"):
    st.error("❌ ไม่พบโปรแกรม FFmpeg! (กรุณาเช็คไฟล์ packages.txt และกด Reboot App)")
    st.stop()

# --- 2. ส่วนอัปโหลด ---
uploaded_file = st.file_uploader("📂 เลือกไฟล์วิดีโอ", type=["mp4", "mov", "avi"])

# --- 3. ส่วนเลือกสูตร (เพิ่มโหมด 4K Short ให้แล้วครับ) ---
st.write("---")
st.subheader("🎯 เลือกโหมดการใช้งาน")

mode = st.radio(
    "เลือกสูตรที่ต้องการ:",
    (
        "💬 1. ส่งไลน์/Messenger (สูตรลับ: ชัดแต่ไฟล์เล็ก)",
        "⚡ 2. God Speed (แปลงไวสุดขีด สำหรับรีบใช้)",
        "🎵 3. TikTok / Reels (เน้นลื่น 60fps)",
        "🟥 4. YouTube (4K Upscale มาตรฐาน)",
        "✨ 5. คลิปสั้น 4K (สูตรใหม่: ชัดตาแตกสำหรับ Short)" 
    )
)

# --- 4. ฟังก์ชัน FFmpeg (รวมทุกสูตร) ---
def process_video_ultimate(input_file, output_file, platform_mode):
    # สร้างคำสั่งเริ่มต้น
    cmd = ['ffmpeg', '-i', input_file]
    
    # ตั้งค่า Codec พื้นฐาน
    cmd.extend(['-c:v', 'libx264', '-profile:v', 'high'])
    
    # ตัวแปรสำหรับ Filter
    filters = []
    
    # --- LOGIC การเลือกโหมด ---
    if "1. ส่งไลน์" in platform_mode:
        # สูตรไลน์: Medium preset + Bitrate จำกัด
        cmd.extend(['-preset', 'medium'])
        cmd.extend(['-b:v', '3500k', '-maxrate', '4000k', '-bufsize', '8000k'])
        filters.append('scale=1080:-2')
        
    elif "2. God Speed" in platform_mode:
        # สูตรไว: Ultrafast preset
        cmd.extend(['-preset', 'ultrafast', '-tune', 'zerolatency'])
        cmd.extend(['-crf', '25']) 
        
    elif "3. TikTok" in platform_mode:
        # สูตร TikTok: Faster + 60fps
        cmd.extend(['-preset', 'faster'])
        cmd.extend(['-b:v', '15M', '-maxrate', '15M', '-bufsize', '30M'])
        filters.append('scale=1080:-2')
        filters.append('fps=60')
        
    elif "4. YouTube" in platform_mode:
        # สูตร YouTube: 4K มาตรฐาน
        cmd.extend(['-preset', 'faster'])
        cmd.extend(['-crf', '20'])
        filters.append('scale=3840:2160:flags=lanczos')

    elif "5. คลิปสั้น 4K" in platform_mode:
        # สูตรใหม่: คลิปสั้น 4K (เน้นคุณภาพมากกว่าความเร็ว)
        # ใช้ Medium เพื่อให้ภาพเนียนกว่า Faster
        cmd.extend(['-preset', 'medium'])
        # CRF 18 คือชัดมาก (ต่ำกว่านี้ไฟล์จะใหญ่เกินจำเป็น)
        cmd.extend(['-crf', '18'])
        # Upscale เป็น 4K ด้วย Algorithm ที่ดีที่สุด (Lanczos)
        filters.append('scale=3840:2160:flags=lanczos')
        # บังคับ 60fps เพื่อความลื่นไหลแบบงานพรีเมียม
        filters.append('fps=60')

    # --- จบ LOGIC ---

    # ใส่ Filter (ถ้ามี)
    if filters:
        cmd.extend(['-vf', ','.join(filters)])
        
    # ตั้งค่าเสียงและ Output สุดท้าย
    cmd.extend(['-c:a', 'aac', '-b:a', '128k', '-movflags', '+faststart', '-pix_fmt', 'yuv420p', '-y', output_file])
    
    # รันคำสั่ง
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    
    if process.returncode != 0:
        raise Exception(f"FFmpeg Error: {stderr.decode()}")

# --- 5. ปุ่มกดสั่งงาน ---
if uploaded_file:
    file_size_mb = uploaded_file.size / (1024 * 1024)
    st.info(f"📹 ต้นฉบับ: {uploaded_file.name} ({file_size_mb:.2f} MB)")
    
    if st.button("🚀 เริ่มแปลงไฟล์", use_container_width=True):
        
        input_path = f"temp_in_{uploaded_file.name}"
        output_filename = f"Smart_{mode.split(' ')[1]}_{uploaded_file.name}"
        output_path = f"output_{output_filename}"
        
        # Save Input
        with open(input_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        try:
            with st.spinner('⏳ กำลังประมวลผล... (โหมด 4K จะใช้เวลานานหน่อยนะครับ)'):
                start_time = time.time()
                
                # เรียกฟังก์ชันทำงาน
                process_video_ultimate(input_path, output_path, mode)
                
                end_time = time.time()
                
                st.success(f"✅ เสร็จเรียบร้อย! (ใช้เวลา {end_time - start_time:.2f} วินาที)")
                
                if os.path.exists(output_path):
                    new_size = os.path.getsize(output_path) / (1024 * 1024)
                    st.caption(f"📦 ขนาดไฟล์ใหม่: {new_size:.2f} MB")
                    
                    with open(output_path, "rb") as f:
                        st.download_button(
                            label="📥 ดาวน์โหลดไฟล์",
                            data=f,
                            file_name=output_filename,
                            mime="video/mp4",
                            use_container_width=True
                        )
                    # ลบไฟล์ทิ้ง
                    os.remove(output_path)
                    
        except Exception as e:
            st.error(f"❌ เกิดข้อผิดพลาด: {e}")
        finally:
            if os.path.exists(input_path): os.remove(input_path)
