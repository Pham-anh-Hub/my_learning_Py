# 📸 PhotoBooth Web App

A web-based photobooth application built with Streamlit and WebRTC for browser-based camera access.

## Features

✨ **Web-Based**
- No installation needed - runs in browser
- Camera access via WebRTC
- Responsive design

🎨 **Layout Options**
- 1 × 4 Vertical strip
- 2 × 2 Square grid

🎭 **Sticker Decoration**
- Random sticker selection
- Transparent PNG support
- Auto-positioned stickers

💾 **Multiple Output Options**
- Save to server
- Download directly to device
- jpg format

## Installation

### Local Setup

1. **Clone or navigate to project directory**
   ```bash
   cd P1_BasicInPython
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Add stickers** (optional)
   - Create `stickers/` folder in project directory
   - Add PNG files (with transparency) to the folder
   - Example: `stickers/emoji.png`, `stickers/heart.png`

4. **Run locally**
   ```bash
   streamlit run app.py
   ```
   - Opens at `http://localhost:8501`

## Deployment on Streamlit Cloud

### Step 1: Prepare on GitHub

1. Create a GitHub account (if you don't have one)
2. Create a new repository named `photobooth-web`
3. Clone it:
   ```bash
   git clone https://github.com/YOUR_USERNAME/photobooth-web.git
   cd photobooth-web
   ```

4. Copy these files to the repository:
   - `app.py`
   - `requirements.txt`
   - `.streamlit/config.toml`
   - `stickers/` folder (with your PNG stickers)

5. Commit and push:
   ```bash
   git add .
   git commit -m "Initial PhotoBooth Web App"
   git push origin main
   ```

### Step 2: Deploy on Streamlit Cloud

1. Go to [Streamlit Cloud](https://share.streamlit.io/)
2. Click "**New app**"
3. Select:
   - Repository: `YOUR_USERNAME/photobooth-web`
   - Branch: `main`
   - Main file path: `app.py`
4. Click "**Deploy**"
5. Wait for deployment (2-5 minutes)
6. Get your **public link**: `https://photobooth-web-YOUR_USERNAME.streamlit.app/`

### Step 3: Share Your Link

Your public PhotoBooth link is ready! Share it with:
- Friends and family
- Social media
- QR code (Streamlit Cloud can generate one)

## Using the App

1. **Enable Camera** - Click "Enable camera" in the sidebar
2. **Select Layout** - Choose between 1×4 or 2×2 in the sidebar
3. **Start Capture** - Click "🚀 Start Capture"
4. **View Results** - Photos appear after capture
5. **Save or Download**
   - Click "💾 Save Photo" to save on server
   - Click "⬇️ Download Photo" to get file
6. **Retake** - Click "🔄 Retake" to capture again

## File Structure

```
P1_BasicInPython/
├── app.py                 # Main Streamlit app
├── requirements.txt       # Python dependencies
├── .streamlit/
│   └── config.toml       # Streamlit configuration
├── stickers/             # PNG sticker files (optional)
│   ├── emoji.png
│   ├── heart.png
│   └── ...
└── output/               # Saved photos (local)
    ├── photobooth_20260301_120000.jpg
    └── ...
```

## Sticker Requirements

- **Format**: PNG with transparency (RGBA)
- **Size**: 150×150 pixels or larger
- **Position**: Bottom-right corner of photo
- **Location**: `stickers/` folder

### Creating Stickers

Use any image editor (Photoshop, Gimp, Canva, etc.):
1. Create design on transparent background
2. Export as PNG (ensure transparency is preserved)
3. Save to `stickers/` folder

Example free tools:
- [Canva](https://www.canva.com/) - Design online
- [GIMP](https://www.gimp.org/) - Free image editor
- [Paint.NET](https://www.getpaint.net/) - Simple Windows tool

## Troubleshooting

### Camera not working
- Check browser permissions
- Try a different browser (Chrome/Edge)
- Allow `https://share.streamlit.io` camera access

### Stickers not showing
- Verify PNG files are in `stickers/` folder
- Check file names (no spaces, lowercase)
- Ensure PNG has transparency layer

### Deployment stuck
- Check GitHub repository settings
- Verify all files are committed
- Go to [Streamlit Cloud](https://share.streamlit.io/) and check logs

### Download not working
- Try a different browser
- Check browser download settings
- Use "Save Photo" option instead

## Customization

### Change Colors
Edit `.streamlit/config.toml`:
```toml
[theme]
primaryColor = "#e74c3c"   # Red
backgroundColor = "#f8f9fa" # Light gray
```

### Change Text/Messages
Edit `app.py` and search for `st.markdown()` or `st.info()` calls

### Change Photo Size
In `build_strip()` function, modify:
```python
max_width = 400  # Change this value
```

### Change Countdown Time
In `app.py`, modify:
```python
COUNTDOWN = 3  # seconds
```

## System Requirements

- **Browser**: Chrome, Edge, Firefox (recent version)
- **Internet**: Stable connection for Streamlit Cloud
- **Camera**: Any USB webcam or built-in camera

## Browser Support

✅ **Fully Supported**
- Google Chrome
- Microsoft Edge
- Firefox (recent)

⚠️ **Limited Support**
- Safari (may require permission settings)
- Mobile browsers (touch controls may be needed)

## License

Free to use and modify

## Support

For issues:
1. Check the troubleshooting section
2. Review Streamlit docs: https://docs.streamlit.io/
3. Check webrtc docs: https://github.com/whitphx/streamlit-webrtc

---

**Enjoy your PhotoBooth Web App! 📸**
