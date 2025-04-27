import sys
import os
import requests
import qrcode
import speedtest
import yt_dlp
from PyQt5.QtWidgets import (QApplication, QLabel, QWidget, QPushButton, QVBoxLayout, QHBoxLayout,
                             QLineEdit, QFileDialog, QProgressBar, QMessageBox, QGraphicsOpacityEffect)
from PyQt5.QtGui import QFont, QPixmap, QIcon, QPalette, QColor
from PyQt5.QtCore import Qt, QPropertyAnimation

class SmartDownloader(QWidget):
    def __init__(self):
        super().__init__()
        self.is_dark_mode = True
        self.setWindowTitle("Smart Video Tool ✨")
        self.setGeometry(150, 150, 1100, 700)
        self.setWindowIcon(QIcon(self.resource_path("icon.png")))

        self.bg_label = QLabel(self)
        self.bg_pixmap = QPixmap(self.resource_path('You-Tube-2.png'))
        self.bg_label.setPixmap(self.bg_pixmap)
        self.bg_label.setScaledContents(True)
        self.bg_label.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.bg_label.lower()
        opacity_effect = QGraphicsOpacityEffect()
        opacity_effect.setOpacity(0.9)
        self.bg_label.setGraphicsEffect(opacity_effect)

        self.initUI()
        self.fade_in()
        self.detect_weather()
        self.test_speed()

    def resource_path(self, relative_path):
        """ Get absolute path to resource, works for dev and for PyInstaller """
        if hasattr(sys, '_MEIPASS'):
            return os.path.join(sys._MEIPASS, relative_path)
        return os.path.join(os.path.abspath("."), relative_path)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if not self.bg_pixmap.isNull():
            self.bg_label.setGeometry(0, 0, self.width(), self.height())

    def initUI(self):
        self.set_palette()

        font_big = QFont("Segoe UI", 18, QFont.Bold)
        font_small = QFont("Segoe UI", 10)

        # Weather and Speed Labels
        self.weather_label = QLabel("☁️ Weather: Detecting...", self)
        self.weather_label.setFont(font_small)
        self.speed_label = QLabel("📶 Speed: Testing...", self)
        self.speed_label.setFont(font_small)

        top_layout = QHBoxLayout()
        top_layout.addWidget(self.weather_label)
        top_layout.addStretch()
        top_layout.addWidget(self.speed_label)

        # URL Input
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("🔗 Paste YouTube URL here...")
        self.url_input.setFont(QFont("Segoe UI", 14))
        self.url_input.setFixedHeight(50)

        # Download Button
        self.download_btn = QPushButton("📥 Download Now")
        self.download_btn.setFont(font_big)
        self.download_btn.clicked.connect(self.download_video)

        # QR Button
        self.qr_btn = QPushButton("🔲 Generate QR")
        self.qr_btn.setFont(font_small)
        self.qr_btn.clicked.connect(self.generate_qr)

        # Progress Bar
        self.progress = QProgressBar()
        self.progress.setValue(0)
        self.progress.setTextVisible(False)
        self.progress.setFixedHeight(10)

        # Status Label
        self.status = QLabel("Ready ✅")
        self.status.setFont(font_small)

        # Preview Area
        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setFixedSize(300, 300)
        self.preview_label.setStyleSheet("border: 2px dashed #cccccc;")

        # Theme Toggle
        self.toggle_theme_btn = QPushButton("🌙 Dark Mode")
        self.toggle_theme_btn.clicked.connect(self.toggle_theme)
        self.toggle_theme_btn.setFont(font_small)

        left_layout = QVBoxLayout()
        left_layout.addLayout(top_layout)
        left_layout.addSpacing(20)
        left_layout.addWidget(self.url_input)
        left_layout.addWidget(self.download_btn)
        left_layout.addWidget(self.qr_btn)
        left_layout.addWidget(self.progress)
        left_layout.addWidget(self.status)
        left_layout.addWidget(self.toggle_theme_btn)
        left_layout.addStretch()

        right_layout = QVBoxLayout()
        right_layout.addWidget(self.preview_label)
        right_layout.addStretch()

        main_layout = QHBoxLayout()
        main_layout.addLayout(left_layout, 2)
        main_layout.addLayout(right_layout, 1)

        self.setLayout(main_layout)

    def set_palette(self):
        palette = QPalette()
        if self.is_dark_mode:
            palette.setColor(QPalette.Window, QColor(25, 25, 25))
            palette.setColor(QPalette.WindowText, Qt.white)
        else:
            palette.setColor(QPalette.Window, QColor(250, 250, 250))
            palette.setColor(QPalette.WindowText, Qt.black)
        self.setPalette(palette)
        self.setAutoFillBackground(True)

    def fade_in(self):
        self.setWindowOpacity(0)
        anim = QPropertyAnimation(self, b"windowOpacity")
        anim.setDuration(1500)
        anim.setStartValue(0)
        anim.setEndValue(1)
        anim.start()
        self.anim = anim  # keep reference

    def toggle_theme(self):
        self.is_dark_mode = not self.is_dark_mode
        self.set_palette()
        if self.is_dark_mode:
            self.toggle_theme_btn.setText("🌙 Dark Mode")
        else:
            self.toggle_theme_btn.setText("☀️ Light Mode")

    def download_video(self):
        url = self.url_input.text().strip()
        if not url:
            self.show_error("Please enter a URL!")
            return
        try:
            self.update_status("Downloading...")
            self.progress.setValue(20)
            ydl_opts = {
                'format': 'best',
                'outtmpl': 'downloads/%(title)s.%(ext)s'
            }
            os.makedirs('downloads', exist_ok=True)
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                thumbnail_url = info.get('thumbnail')
                if thumbnail_url:
                    self.show_preview(thumbnail_url)
            self.progress.setValue(100)
            self.update_status("Downloaded Successfully ✅")
        except Exception as e:
            self.show_error(str(e))

    def generate_qr(self):
        url = self.url_input.text().strip()
        if not url:
            self.show_error("Please enter a URL!")
            return
        qr_img = qrcode.make(url)
        qr_path = "qr_temp.png"
        qr_img.save(qr_path)
        self.show_preview(qr_path, is_qr=True)
        self.update_status("QR Code Generated ✅")

    def show_preview(self, path, is_qr=False):
        try:
            if not is_qr:
                response = requests.get(path)
                img_data = response.content
                with open("temp_thumb.jpg", "wb") as f:
                    f.write(img_data)
                pix = QPixmap("temp_thumb.jpg")
            else:
                pix = QPixmap(path)

            pix = pix.scaled(300, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.preview_label.setPixmap(pix)

            opacity_effect = QGraphicsOpacityEffect()
            self.preview_label.setGraphicsEffect(opacity_effect)
            anim = QPropertyAnimation(opacity_effect, b"opacity")
            anim.setDuration(1000)
            anim.setStartValue(0)
            anim.setEndValue(1)
            anim.start()
            self.preview_anim = anim
        except Exception as e:
            self.show_error(f"Failed to load preview: {str(e)}")

    def update_status(self, message):
        self.status.setText(f"{message}")

    def show_error(self, message):
        self.status.setText(f"⚠️ {message}")
        QMessageBox.critical(self, "Error", message)

    def detect_weather(self):
        try:
            ip_info = requests.get("http://ip-api.com/json").json()
            city = ip_info['city']
            api_key = "98b2a86868b235af311d5a6acfe49dcb"
            weather = requests.get(
                f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
            ).json()
            temp = weather['main']['temp']
            icon = weather['weather'][0]['main']
            self.weather_label.setText(f"🌡️ {city}: {temp}°C {icon}")
        except Exception as e:
            self.weather_label.setText("Weather: N/A")

    def test_speed(self):
        try:
            s = speedtest.Speedtest()
            download = round(s.download() / 1_000_000, 2)
            upload = round(s.upload() / 1_000_000, 2)
            self.speed_label.setText(f"📶 {download} Mbps ↓ / {upload} Mbps ↑")
        except Exception as e:
            self.speed_label.setText("📶 Speed: N/A")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SmartDownloader()
    window.show()
    sys.exit(app.exec_())
