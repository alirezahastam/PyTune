#!/usr/bin/env python3
# Author: Alireza
# Github Repository : https://github.com/alirezahastam

import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QListWidget, QFileDialog, QLabel, QSlider, QFrame, QListWidgetItem
)
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QPixmap, QFont, QColor, QIcon
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent

from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC


# 🔥 برای سازگاری با exe
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


class MusicPlayer(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("PyTune")
        self.setFixedSize(900, 600)
        self.setWindowIcon(QIcon(resource_path("logo.ico")))

        self.center_window()

        self.player = QMediaPlayer()
        self.tracks = []
        self.current_index = 0

        self.init_ui()
        self.apply_style()

    def center_window(self):
        screen = QApplication.primaryScreen().geometry()
        self.move(
            (screen.width() - self.width()) // 2,
            (screen.height() - self.height()) // 2
        )

    def apply_style(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #0D1117;
                color: #E6EDF3;
                font-family: 'Segoe UI';
            }
        """)

    def init_ui(self):
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)

        # ===== LEFT PANEL =====
        left_panel = QFrame()
        left_panel.setFixedWidth(300)
        left_panel.setStyleSheet("""
            QFrame {
                background-color: #161B22;
                border-radius: 15px;
                border: 1px solid #30363D;
            }
        """)

        left_layout = QVBoxLayout(left_panel)

        title = QLabel("🎵 Playlist")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Segoe UI", 13, QFont.Bold))
        title.setStyleSheet("color: #58A6FF;")
        left_layout.addWidget(title)

        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet("""
            QListWidget {
                background-color: #0D1117;
                border: none;
                border-radius: 10px;
                padding: 5px;
                color: #E6EDF3;
            }
            QListWidget::item {
                background-color: transparent;
                color: #E6EDF3;
                padding: 10px;
                border-radius: 6px;
            }
            QListWidget::item:selected {
                background-color: #58A6FF;
                color: #0D1117;
            }
            QListWidget::item:hover {
                background-color: #1F6FEB;
                color: white;
            }
        """)
        left_layout.addWidget(self.list_widget)

        self.btn_load = QPushButton("📁 Load Folder")
        self.btn_load.setMinimumHeight(40)
        left_layout.addWidget(self.btn_load)

        # ===== RIGHT PANEL =====
        right_panel = QFrame()
        right_panel.setStyleSheet("""
            QFrame {
                background-color: #161B22;
                border-radius: 15px;
                border: 1px solid #30363D;
            }
        """)

        right_layout = QVBoxLayout(right_panel)

        # 🎨 LOGO
        self.logo = QLabel()
        self.logo.setAlignment(Qt.AlignCenter)
        logo_pixmap = QPixmap(resource_path("logo.png"))
        self.logo.setPixmap(logo_pixmap.scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        right_layout.addWidget(self.logo)

        # Copytight
        self.credit = QLabel()
        self.credit.setAlignment(Qt.AlignCenter)

        self.credit.setText(
            '<a href="https://github.com/alirezahastam" '
            'style="color:#58A6FF; text-decoration:none;">'
            'Alireza | GitHub</a>'
        )

        self.credit.setOpenExternalLinks(True)

        self.credit.setStyleSheet("""
            QLabel {
                color: #8B949E;
                font-size: 11px;
                margin-top: 5px;
            }
            QLabel:hover {
                color: #58A6FF;
            }
        """)

        right_layout.addWidget(self.credit)
        
        # Cover
        cover_frame = QFrame()
        cover_frame.setFixedHeight(260)
        cover_frame.setStyleSheet("""
            background-color: #0D1117;
            border-radius: 12px;
            border: 1px solid #30363D;
        """)

        cover_layout = QVBoxLayout(cover_frame)
        cover_layout.setAlignment(Qt.AlignCenter)

        self.cover = QLabel()
        self.cover.setFixedSize(220, 220)
        self.cover.setAlignment(Qt.AlignCenter)

        default = QPixmap(220, 220)
        default.fill(QColor(13, 17, 23))
        self.cover.setPixmap(default)

        cover_layout.addWidget(self.cover)
        right_layout.addWidget(cover_frame)

        # Title
        self.title = QLabel("No Track")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        self.title.setStyleSheet("color: #E6EDF3;")
        right_layout.addWidget(self.title)

        # Slider
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setStyleSheet("""
            QSlider::groove:horizontal {
                height: 4px;
                background: #30363D;
            }
            QSlider::handle:horizontal {
                background: #58A6FF;
                width: 12px;
                margin: -4px 0;
                border-radius: 6px;
            }
            QSlider::sub-page:horizontal {
                background: #58A6FF;
            }
        """)
        right_layout.addWidget(self.slider)

        self.time_label = QLabel("00:00 / 00:00")
        self.time_label.setAlignment(Qt.AlignCenter)
        self.time_label.setStyleSheet("color: #8B949E;")
        right_layout.addWidget(self.time_label)

        # Buttons
        btn_layout = QHBoxLayout()

        button_style = """
            QPushButton {
                background-color: #21262D;
                border: 1px solid #30363D;
                border-radius: 20px;
                padding: 10px;
                font-size: 16px;
                color: #E6EDF3;
            }
            QPushButton:hover {
                background-color: #58A6FF;
                color: #0D1117;
            }
        """

        self.btn_prev = QPushButton("⏮")
        self.btn_play = QPushButton("▶")
        self.btn_next = QPushButton("⏭")

        for b in [self.btn_prev, self.btn_play, self.btn_next]:
            b.setStyleSheet(button_style)
            btn_layout.addWidget(b)

        right_layout.addLayout(btn_layout)

        # Volume
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setValue(70)
        self.player.setVolume(70)
        right_layout.addWidget(self.volume_slider)

        main_layout.addWidget(left_panel)
        main_layout.addWidget(right_panel)
        self.setLayout(main_layout)

        # Signals
        self.btn_load.clicked.connect(self.load_folder)
        self.btn_play.clicked.connect(self.play_pause)
        self.btn_next.clicked.connect(self.next_track)
        self.btn_prev.clicked.connect(self.prev_track)
        self.list_widget.itemClicked.connect(self.select_track)

        self.player.positionChanged.connect(self.update_position)
        self.player.durationChanged.connect(self.update_duration)

        self.slider.sliderMoved.connect(self.set_position)
        self.volume_slider.valueChanged.connect(self.player.setVolume)

    def get_cover_art(self, filepath):
        try:
            audio = MP3(filepath, ID3=ID3)
            if audio.tags:
                for tag in audio.tags.values():
                    if isinstance(tag, APIC):
                        pixmap = QPixmap()
                        pixmap.loadFromData(tag.data)
                        return pixmap.scaled(220, 220, Qt.KeepAspectRatio)
        except:
            pass
        return None

    def load_folder(self):
        folder = QFileDialog.getExistingDirectory(self)
        if not folder:
            return

        self.tracks = [
            os.path.join(folder, f)
            for f in os.listdir(folder)
            if f.lower().endswith(".mp3")
        ]

        self.list_widget.clear()

        for track in self.tracks:
            item = QListWidgetItem(os.path.basename(track))
            item.setForeground(QColor("#E6EDF3"))
            self.list_widget.addItem(item)

        if self.tracks:
            self.current_index = 0
            self.load_track()

    def load_track(self):
        track = self.tracks[self.current_index]
        self.player.setMedia(QMediaContent(QUrl.fromLocalFile(track)))

        self.title.setText(os.path.basename(track))

        cover = self.get_cover_art(track)
        if cover:
            self.cover.setPixmap(cover)

        self.list_widget.setCurrentRow(self.current_index)

    def play_pause(self):
        if self.player.state() == QMediaPlayer.PlayingState:
            self.player.pause()
            self.btn_play.setText("▶")
        else:
            self.player.play()
            self.btn_play.setText("⏸")

    def next_track(self):
        if not self.tracks:
            return
        self.current_index = (self.current_index + 1) % len(self.tracks)
        self.load_track()
        self.player.play()

    def prev_track(self):
        if not self.tracks:
            return
        self.current_index = (self.current_index - 1) % len(self.tracks)
        self.load_track()
        self.player.play()

    def select_track(self, item):
        self.current_index = self.list_widget.row(item)
        self.load_track()
        self.player.play()

    def update_position(self, pos):
        self.slider.setValue(pos)
        self.update_time_label(pos, self.player.duration())

    def update_duration(self, dur):
        self.slider.setRange(0, dur)

    def set_position(self, pos):
        self.player.setPosition(pos)

    def update_time_label(self, current, total):
        def fmt(ms):
            s = ms // 1000
            return f"{s//60:02}:{s%60:02}"
        self.time_label.setText(f"{fmt(current)} / {fmt(total)}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    player = MusicPlayer()
    player.show()
    sys.exit(app.exec_())