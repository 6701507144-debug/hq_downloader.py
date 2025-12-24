import streamlit as st
import os
import subprocess
import time
import shutil
import gc  # เพิ่มตัวจัดการหน่วยความจำ (Garbage Collector)

# ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="Stable Video Tool", page_icon="🛡️", layout="centered")
st.title("🛡️ Smart Export: Stable Edition")
st.write("เวอร์ชั่นเสถียร: มีระบบล้างไฟล์ขยะและคืนแรมอัตโนมัติ")

# --- 0. ฟังก์ชันทำความสะอาดระบบ (Auto-Cleanup) ---
def cleanup_system():
    # ลบไฟล์ขยะที่อาจค้างจากการรันครั้งก่อน
    files = os.listdir()
    count = 0
    for f in files:
        if f.startswith("temp_") or f.startswith("out_") or f.startswith("Smart_"):
            try:
                os.remove(f)
                count += 1
            except:
                pass
    if count > 0:
        print(f"🧹 ล้างไฟล์ขยะไป {count} ไฟล์")

# เรียกใช้งานทันทีที่เปิดแอป
cleanup_system()

# --- 1. เช็ค FFmpeg ---
if not shutil.which("ffmpeg"):
    st.error("❌ ไม่พบ FFmpeg! (กรุณา Reboot App)")
    st.stop()

# --- 2. อัปโหลดไฟล์ ---
# จำกัดขนาดไฟล์ไม่เกิน 200MB เพื่อป้องกัน Server น็อค
uploaded_file = st.file_uploader("📂 อัปโหลดไฟล์วิดีโอ (แนะนำ < 200MB)", type=["mp4", "mov", "avi"])

if uploaded_file and uploaded_file.size > 250 * 1024 * 1024:
    st.warning("⚠️ ไฟล์ใหญ่เกิน 250MB อาจทำให้ Server ค้างได้ครับ แนะนำให้ตัดแบ่งเป็นไฟล์ย่อย")

# --- 3. เลือกโหมด ---
st.write("---")
mode = st.radio(
    "เลือกโหมด:",
    (
        "💬 1. ส่งไลน์ (ประหยัดแรม)",
        "⚡ 2. God Speed (แปลงไว)",
        "🎵 3. TikTok (60fps)",
        "🟥 4. YouTube (4K แนวนอน)",
        "📱 5. คลิปสั้น 4K (Shorts/Reels)" 
    )
)

# --- 4. ฟังก์ชันประมวลผล ---
def process_video_stable(input_file, output_file, platform_mode):
    cmd = ['ffmpeg', '-i', input_file]
    cmd.extend(['-c:v', 'libx264', '-profile:v', 'high'])
    filters = []

    # Logic การเลือกโหมด
    if "1. ส่งไลน์" in platform_mode:
        cmd.extend(['-preset', 'veryfast']) # ใช้ veryfast เพื่อประหยัด CPU
        cmd.extend(['-b:v', '3500k', '-maxrate', '4000k', '-bufsize', '8000k'])
        filters.append('scale=1080:-2')
        
    elif "2. God Speed" in platform_mode:
        cmd.extend(['-preset', 'ultrafast', '-tune', 'zerolatency', '-crf', '25'])
        
    elif "3. TikTok" in platform_mode:
        cmd.extend(['-preset', 'superfast']) # ลดความแรงลงนิดนึงกันเครื่องน็อค
        cmd.extend(['-b:v', '10M', '-maxrate', '10M', '-bufsize', '20M'])
        filters.append('scale=1080:-2')
        filters.append('fps=60')
        
    elif "4. YouTube" in platform_mode:
        cmd.extend(['-preset', 'superfast', '-crf', '23']) # ลด load ลงเพื่อให้ render ผ่าน
        filters.append('scale=3840:2160:flags=bicubic') # ใช้ bicubic กินแรงน้อยกว่า lanczos

    elif "5. คลิปสั้น 4K" in platform_mode:
        cmd.extend(['-preset', 'superfast', '-crf', '20'])
        filters.append('scale=-2:2160:flags=bicubic') 
        filters.append('fps=60')

    if filters:
        cmd.extend(['-vf', ','.join(filters)])
        
    cmd.extend(['-c:a', 'aac', '-b:a', '128k', '-movflags', '+faststart', '-pix_fmt', 'yuv420p', '-y', output_file])
    
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    
    if process.returncode != 0:
        raise Exception(f"FFmpeg Error: {stderr.decode()}")

# --- 5. ปุ่มทำงาน ---
if uploaded_file:
    if st.button("🚀 เริ่มแปลงไฟล์"):
        # Clear Memory ก่อนเริ่มงาน
        gc.collect()
        
        temp_in = f"temp_{int(time.time())}.mp4"
        output_name = f"Smart_{int(time.time())}.mp4"
        output_path = f"out_{output_name}"
        
        try:
            with open(temp_in, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            with st.spinner('⏳ กำลังประมวลผล... (ห้ามปิดจอนะครับ)'):
                process_video_stable(temp_in, output_path, mode)
                
                if os.path.exists(output_path):
                    st.success("✅ สำเร็จ!")
                    with open(output_path, "rb") as f:
                        st.download_button("📥 ดาวน์โหลด", f, file_name=output_name)
                    
                    # ลบไฟล์ Output ทันทีหลังโหลดเสร็จ (Clean up logic ย้ายไปทำตอนเริ่ม app แทนเพื่อความชัวร์)
                else:
                    st.error("❌ ไฟล์ปลายทางไม่ถูกสร้าง (อาจเกิดจาก RAM หมด)")

        except Exception as e:
            st.error(f"❌ เกิดข้อผิดพลาด: {e}")
            
        finally:
            # Cleanup ทันทีที่จบการทำงาน
            if os.path.exists(temp_in): 
                os.remove(temp_in)
            if os.path.exists(output_path):
                os.remove(output_path)
            
            # บังคับคืนแรม
            del uploaded_file
            gc.collect()
