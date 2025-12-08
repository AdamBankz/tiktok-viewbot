import sys
import re
import requests
import urllib.parse
from bs4 import BeautifulSoup
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton,
    QLabel, QScrollArea, QHBoxLayout, QFrame, QFileDialog
)
from PyQt6.QtGui import QPixmap, QImage, QClipboard
from PyQt6.QtCore import Qt

class Section(QFrame):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
            QFrame {
                background-color: #1b1b1b;
                border-radius: 14px;
                padding: 12px;
                border: 1px solid #292929;
            }
        """)
        self.layout = QVBoxLayout(self)

class TikTokGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TikTok Account Lookup")
        self.setGeometry(200, 200, 900, 550)
        self.setStyleSheet(self.theme())

        main_layout = QVBoxLayout(self)

        top_row = QHBoxLayout()
        self.input_box = QLineEdit()
        self.input_box.setPlaceholderText("Enter TikTok username")
        self.input_box.setFixedHeight(42)
        self.input_box.setStyleSheet(self.input_style())

        self.fetch_btn = QPushButton("Lookup")
        self.fetch_btn.setFixedHeight(42)
        self.fetch_btn.setFixedWidth(150)
        self.fetch_btn.setStyleSheet(self.button_style())
        self.fetch_btn.clicked.connect(self.fetch_user)

        top_row.addWidget(self.input_box)
        top_row.addWidget(self.fetch_btn)
        main_layout.addLayout(top_row)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(self.scroll_style())

        container = QWidget()
        scroll_layout = QVBoxLayout(container)

        self.avatar_section = Section()
        self.avatar_label = QLabel()
        self.avatar_label.setFixedSize(150, 150)
        self.avatar_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.avatar_label.setStyleSheet("""
            background-color: #000000;
            border-radius: 12px;
        """)
        self.avatar_section.layout.addWidget(self.avatar_label)

        self.download_btn = QPushButton("Download Profile Picture")
        self.download_btn.setStyleSheet(self.small_button_style())
        self.download_btn.clicked.connect(self.download_picture)
        self.avatar_section.layout.addWidget(self.download_btn)

        scroll_layout.addWidget(self.avatar_section)

        self.account_section = Section()
        self.account_section.layout.addWidget(QLabel("<b>ACCOUNT DETAILS</b>"))
        self.account_label = QLabel("")
        self.account_label.setWordWrap(True)
        self.account_label.setStyleSheet("font-size: 15px;")
        self.account_section.layout.addWidget(self.account_label)
        scroll_layout.addWidget(self.account_section)

        self.bio_section = Section()
        self.bio_section.layout.addWidget(QLabel("<b>BIOGRAPHY</b>"))
        self.bio_label = QLabel("")
        self.bio_label.setWordWrap(True)
        self.bio_section.layout.addWidget(self.bio_label)

        self.copy_bio_btn = QPushButton("Copy Biography")
        self.copy_bio_btn.setStyleSheet(self.small_button_style())
        self.copy_bio_btn.clicked.connect(self.copy_bio)
        self.bio_section.layout.addWidget(self.copy_bio_btn)

        scroll_layout.addWidget(self.bio_section)

        self.links_section = Section()
        self.links_section.layout.addWidget(QLabel("<b>BIOGRAPHY LINKS</b>"))
        self.links_label = QLabel("")
        self.links_label.setWordWrap(True)
        self.links_label.setOpenExternalLinks(True)
        self.links_label.setStyleSheet(self.link_style())
        self.links_section.layout.addWidget(self.links_label)
        scroll_layout.addWidget(self.links_section)

        self.profile_section = Section()
        self.profile_section.layout.addWidget(QLabel("<b>TIKTOK PROFILE URL</b>"))
        self.profile_label = QLabel("")
        self.profile_label.setOpenExternalLinks(True)
        self.profile_label.setStyleSheet(self.link_style())
        self.profile_section.layout.addWidget(self.profile_label)
        scroll_layout.addWidget(self.profile_section)

        scroll_layout.addSpacing(20)
        scroll.setWidget(container)
        main_layout.addWidget(scroll)

        self.current_profile_pic = None

    def fetch_user(self):
        username = self.input_box.text().strip()
        if username.startswith("@"):
            username = username[1:]

        info = self.get_user_info(username)
        if not info:
            self.account_label.setText("There was an error retrieving profile information.")
            return

        def up(v):
            s = str(v).lower()
            return "True" if s == "true" else "False" if s == "false" else v

        details = [
            f"User ID: {info['user_id']}",
            f"Unique ID: {info['unique_id']}",
            f"Nickname: {info['nickname']}",
            f"Verified: {up(info['verified'])}",
            f"Private Account: {up(info['privateAccount'])}",
            f"Region: {info['region']}",
            f"Followers: {info['followers']}",
            f"Following: {info['following']}",
            f"Likes: {info['likes']}",
            f"Videos: {info['videos']}",
            f"Friend Count: {info['friendCount']}",
            f"Dig Count: {info['diggCount']}",
        ]

        self.account_label.setText("<br>".join(details))
        self.bio_label.setText(info.get("signature", ""))

        purple = "#6d3de8"

        links = info.get("social_links", [])
        if links:
            self.links_label.setText("<br>".join(
                f'<a style="color:{purple}; text-decoration:none;" href="{l}">{l}</a>'
                for l in links
            ))
        else:
            self.links_label.setText("No social links found.")

        profile_url = f"https://www.tiktok.com/@{info['unique_id']}"
        self.profile_label.setText(
            f'<a style="color:{purple}; text-decoration:none;" href="{profile_url}">{profile_url}</a>'
        )

        pic_url = info.get("profile_pic", "")
        if pic_url.startswith("http"):
            self.current_profile_pic = pic_url
            img_data = requests.get(pic_url).content
            image = QImage.fromData(img_data)

            pix = QPixmap.fromImage(image).scaled(
                150, 150,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )

            self.avatar_label.setPixmap(pix)

        else:
            self.avatar_label.setText("No Image")

    def download_picture(self):
        if not self.current_profile_pic:
            return
        save_path, _ = QFileDialog.getSaveFileName(
            self, "Save Profile Picture", "profile.jpg", "Images (*.jpg *.png)"
        )
        if save_path:
            img_data = requests.get(self.current_profile_pic).content
            with open(save_path, "wb") as f:
                f.write(img_data)

    def copy_bio(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.bio_label.text())

    def get_user_info(self, identifier):
        url = f"https://www.tiktok.com/@{identifier}"
        headers = {"User-Agent": "Mozilla/5.0"}

        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return None

        html = response.text

        patterns = {
            'user_id': r'"id":"(\d+)"',
            'unique_id': r'"uniqueId":"(.*?)"',
            'nickname': r'"nickname":"(.*?)"',
            'followers': r'"followerCount":(\d+)',
            'following': r'"followingCount":(\d+)',
            'likes': r'"heartCount":(\d+)',
            'videos': r'"videoCount":(\d+)',
            'signature': r'"signature":"(.*?)"',
            'verified': r'"verified":(true|false)',
            'privateAccount': r'"privateAccount":(true|false)',
            'region': r'"region":"(.*?)"',
            'diggCount': r'"diggCount":(\d+)',
            'friendCount': r'"friendCount":(\d+)',
            'profile_pic': r'"avatarLarger":"(.*?)"'
        }

        info = {}
        for key, pattern in patterns.items():
            m = re.search(pattern, html)
            info[key] = m.group(1).replace("\\u002F", "/") if m else "N/A"

        info["signature"] = info["signature"].replace("\\n", "\n")

        social_links = []

        link_pats = [
            r'scene=bio_url[^"]*?target=([^"&]+)',
            r'"bioLink":{"link":"([^"]+)"'
        ]

        for pat in link_pats:
            for match in re.findall(pat, html):
                clean = urllib.parse.unquote(match).replace("\\u002F", "/")
                if clean not in social_links:
                    social_links.append(clean)

        bio = info["signature"]
        social_text = {
            "Instagram": r'[iI][gG]:\s*@?([a-zA-Z0-9._]+)',
            "Snapchat": r'[sS][cC]:\s*@?([a-zA-Z0-9._]+)',
            "Twitter/X": r'[tT]witter|[xX]:\s*@?([a-zA-Z0-9._]+)'
        }

        for label, pattern in social_text.items():
            m = re.search(pattern, bio)
            if m:
                social_links.append(f"{label}: @{m.group(1)}")

        info["social_links"] = social_links
        return info

    def theme(self):
        return """
            QWidget { background-color: #121212; color: #f2f2f2; }
        """

    def input_style(self):
        return """
            background-color: #1e1e1e;
            border-radius: 14px;
            padding: 10px;
            border: 1px solid #333;
            font-size: 15px;
            color: white;
        """

    def button_style(self):
        return """
            QPushButton {
                background-color: #6d3de8;
                border-radius: 14px;
                font-size: 16px;
                color: white;
            }
            QPushButton:hover { background-color: #8353ff; }
        """

    def small_button_style(self):
        return """
            QPushButton {
                background-color: #6d3de8;
                border-radius: 10px;
                padding: 6px;
                font-size: 14px;
                color: white;
            }
            QPushButton:hover { background-color: #8353ff; }
        """

    def link_style(self):
        return """
            QLabel {
                color: #6d3de8;
                font-size: 15px;
            }
            QLabel:hover { color: #8353ff; }
        """

    def scroll_style(self):
        return """
            QScrollArea { border: none; }

            QScrollBar:vertical {
                background: #121212;
                width: 14px;
                margin: 3px;
                border-radius: 7px;
            }

            QScrollBar::handle:vertical {
                background: #6d3de8;
                border-radius: 7px;
                min-height: 40px;
            }

            QScrollBar::handle:vertical:hover {
                background: #8353ff;
            }

            QScrollBar::add-line,
            QScrollBar::sub-line {
                height: 0px;
            }
        """
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TikTokGUI()
    window.show()
    sys.exit(app.exec())