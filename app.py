import streamlit as st
import cv2
import numpy as np
import os
import random
import time
from datetime import datetime
from PIL import Image
import io
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration
import av

NUM_PHOTOS = 4
COUNTDOWN = 3
STICKER_FOLDER = "stickers"

# Page config
st.set_page_config(
    page_title="🎉 PhotoBooth",
    page_icon="📸",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
    <style>
        .main { padding: 2rem; }
        h1 { text-align: center; color: #e74c3c; }
        .stButton>button { width: 100%; padding: 10px; font-size: 16px; }
        .info-box { background: #f0f2f6; padding: 15px; border-radius: 8px; margin: 10px 0; }
    </style>
""", unsafe_allow_html=True)

# ===== LOAD STICKERS =====
@st.cache_resource
def load_stickers(folder):
    stickers = []
    if not os.path.exists(folder):
        os.makedirs(folder)
        return stickers
    
    for file in os.listdir(folder):
        if file.endswith(".png"):
            path = os.path.join(folder, file)
            img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
            if img is not None and img.shape[2] == 4:
                stickers.append(img)
    return stickers


# ===== ADD STICKER =====
def add_sticker(frame, sticker, x, y):
    h, w = sticker.shape[:2]
    if y + h > frame.shape[0] or x + w > frame.shape[1]:
        return frame
    alpha = sticker[:, :, 3:4] / 255.0
    frame[y:y+h, x:x+w] = (
        alpha * sticker[:, :, :3] +
        (1 - alpha) * frame[y:y+h, x:x+w]
    )
    return frame


# ===== BUILD STRIP =====
def build_strip(photos, layout="1x4"):
    max_width = 400
    h, w = photos[0].shape[:2]
    scale = max_width / w
    new_h = int(h * scale)
    new_w = max_width
    
    photos = [cv2.resize(p, (new_w, new_h)) for p in photos]

    if layout == "2x2":
        top = np.hstack((photos[0], photos[1]))
        bottom = np.hstack((photos[2], photos[3]))
        strip = np.vstack((top, bottom))
    else:
        strip = np.vstack(photos)

    border_size = 20
    strip = cv2.copyMakeBorder(
        strip, border_size, border_size, border_size, border_size,
        cv2.BORDER_CONSTANT, value=[255, 255, 255]
    )

    header_height = 80
    header = np.ones((header_height, strip.shape[1], 3), dtype=np.uint8) * 255
    cv2.putText(header, "PHOTOBOOTH 2026", (strip.shape[1] // 6, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 0), 2)

    return np.vstack((header, strip))


# ===== MAIN APP =====
st.markdown("<h1>📸 PhotoBooth Web App</h1>", unsafe_allow_html=True)

# Initialize session state
if "photos" not in st.session_state:
    st.session_state.photos = []
if "capture_count" not in st.session_state:
    st.session_state.capture_count = 0
if "show_continue_dialog" not in st.session_state:
    st.session_state.show_continue_dialog = False
if "app_exit" not in st.session_state:
    st.session_state.app_exit = False

# Load stickers
stickers = load_stickers(STICKER_FOLDER)

if len(stickers) == 0:
    st.warning("⚠️ No stickers found in 'stickers' folder. Please add PNG stickers with transparency.")
else:
    st.success(f"✅ Loaded {len(stickers)} stickers")

# Sidebar layout selection
st.sidebar.markdown("<h2>⚙️ Settings</h2>", unsafe_allow_html=True)
layout = st.sidebar.radio("Select Layout:", ["📋 1 × 4 Vertical", "🔲 2 × 2 Square"], index=0)
layout_value = "1x4" if "1 × 4" in layout else "2x2"

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("<div class='info-box'><h3>📷 Camera Preview</h3></div>", unsafe_allow_html=True)
    
    # WebRTC configuration
    RTC_CONFIGURATION = RTCConfiguration(
        {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
    )
    
    webrtc_ctx = webrtc_streamer(
        key="photobooth",
        mode=WebRtcMode.SENDRECV,
        rtc_configuration=RTC_CONFIGURATION,
        media_stream_constraints={"video": True, "audio": False},
        async_processing=True,
        status_indicator="hidden"
    )

with col2:
    st.markdown("<div class='info-box'><h3>📊 Status</h3></div>", unsafe_allow_html=True)
    
    status_placeholder = st.empty()
    
    if st.session_state.capture_count == 0:
        status_placeholder.info(f"🟢 Ready\n\nPhotos: 0/{NUM_PHOTOS}")
    else:
        status_placeholder.warning(f"⏳ Capturing\n\nPhotos: {st.session_state.capture_count}/{NUM_PHOTOS}")

# Control buttons
st.markdown("---")
btn_col1, btn_col2, btn_col3 = st.columns(3)

with btn_col1:
    if st.button("🚀 Start Capture", key="start_btn", use_container_width=True):
        if not webrtc_ctx.state.playing:
            st.warning("Please enable camera first")
        elif len(stickers) == 0:
            st.error("No stickers available")
        else:
            st.session_state.photos = []
            st.session_state.capture_count = 0
            st.session_state.show_continue_dialog = False
            
            countdown_placeholder = st.empty()
            status_info = st.empty()
            
            status_info.info(f"📸 Capturing {NUM_PHOTOS} photos with {COUNTDOWN}s countdown each...")
            
            # Capture frames from webrtc
            if webrtc_ctx.video_processor:
                for i in range(NUM_PHOTOS):
                    status_placeholder.warning(f"⏳ Photo {i+1}/{NUM_PHOTOS}")
                    
                    # Countdown before capture
                    for cd in range(COUNTDOWN, 0, -1):
                        countdown_placeholder.markdown(
                            f"<h2 style='text-align: center; color: #e74c3c;'>📸 {cd}</h2>",
                            unsafe_allow_html=True
                        )
                        time.sleep(1)
                    
                    countdown_placeholder.empty()
                    
                    # Capture frame
                    if hasattr(webrtc_ctx.video_processor, 'recv'):
                        try:
                            frame_data = webrtc_ctx.video_processor.recv()
                            if frame_data is not None:
                                frame = frame_data.to_ndarray(format="bgr24")
                                
                                # Add sticker
                                sticker = random.choice(stickers)
                                sticker_resized = cv2.resize(sticker, (150, 150))
                                frame = add_sticker(frame, sticker_resized,
                                                  frame.shape[1] - 170, frame.shape[0] - 170)
                                
                                st.session_state.photos.append(frame)
                                st.session_state.capture_count += 1
                                status_info.success(f"✅ Photo {i+1} captured!")
                                time.sleep(0.5)
                        except:
                            pass
                
                status_info.empty()
                if len(st.session_state.photos) == NUM_PHOTOS:
                    status_placeholder.success("✅ Capture Complete!")
                    st.session_state.show_continue_dialog = True
                    st.rerun()
                else:
                    status_placeholder.error("❌ Capture failed. Try again.")

with btn_col2:
    if st.button("ℹ️ Info", key="info_btn", use_container_width=True):
        st.info("""
        **📸 How to Use:**
        1. Enable camera
        2. Select layout (sidebar)
        3. Click "Start Capture"
        4. Wait for 3-2-1 countdown
        5. Let pictures be taken automatically
        6. Save or retake
        
        **Features:**
        - 📋 Two layout options (1×4 or 2×2)
        - 🎨 Random sticker decoration
        - 💾 Save to output folder
        - 🔄 Retake anytime
        """)

with btn_col3:
    if st.button("❌ Clear", key="clear_btn", use_container_width=True):
        st.session_state.photos = []
        st.session_state.capture_count = 0
        st.rerun()

# Display captured photos and final result
if len(st.session_state.photos) > 0:
    st.markdown("---")
    st.markdown("<h3>📷 Captured Photos Preview</h3>", unsafe_allow_html=True)
    
    preview_cols = st.columns(len(st.session_state.photos))
    for idx, col in enumerate(preview_cols):
        with col:
            img_rgb = cv2.cvtColor(st.session_state.photos[idx], cv2.COLOR_BGR2RGB)
            st.image(img_rgb, use_column_width=True)
    
    if len(st.session_state.photos) == NUM_PHOTOS:
        st.markdown("---")
        st.markdown("<h3>✨ Final Result</h3>", unsafe_allow_html=True)
        
        final_image = build_strip(st.session_state.photos, layout_value)
        final_image_rgb = cv2.cvtColor(final_image, cv2.COLOR_BGR2RGB)
        
        st.image(final_image_rgb, use_column_width=True, caption="Your PhotoBooth Photo")
        
        # Continue Dialog
        if st.session_state.show_continue_dialog:
            st.markdown("---")
            st.markdown("<h3 style='text-align: center;'>❓ Do you want to take more photos?</h3>", unsafe_allow_html=True)
            
            continue_col1, continue_col2 = st.columns(2)
            
            with continue_col1:
                if st.button("✅ Yes, Take More!", key="continue_yes_btn", use_container_width=True):
                    st.session_state.photos = []
                    st.session_state.capture_count = 0
                    st.session_state.show_continue_dialog = False
                    st.rerun()
            
            with continue_col2:
                if st.button("👋 No, Exit App", key="continue_no_btn", use_container_width=True):
                    st.session_state.app_exit = True
                    st.balloons()
                    st.success("\n\n✨ Thank you for using PhotoBooth! See you next time!")
                    time.sleep(3)
                    import sys
                    st.stop()
        else:
            st.markdown("---")
            # Save options
            save_col1, save_col2, save_col3 = st.columns(3)
            
            with save_col1:
                if st.button("💾 Save Photo", key="save_btn", use_container_width=True):
                    os.makedirs("output", exist_ok=True)
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"output/photobooth_{timestamp}.jpg"
                    cv2.imwrite(filename, final_image)
                    st.success(f"✅ Photo saved as `{filename}`")
            
            with save_col2:
                if st.button("🔄 Retake", key="retake_btn", use_container_width=True):
                    st.session_state.photos = []
                    st.session_state.capture_count = 0
                    st.session_state.show_continue_dialog = False
                    st.rerun()
            
            with save_col3:
                _, buffer = cv2.imencode(".jpg", final_image)
                img_bytes = buffer.tobytes()
                st.download_button(
                    label="⬇️ Download",
                    data=img_bytes,
                    file_name=f"photobooth_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg",
                    mime="image/jpeg",
                    use_container_width=True
                )

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray; font-size: 12px;'>"
    "📸 PhotoBooth Web App v2.0 | Powered by Streamlit"
    "</div>",
    unsafe_allow_html=True
)
