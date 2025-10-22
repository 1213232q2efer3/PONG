import sys
import random
import string
import math
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLineEdit, QPushButton, QLabel, QMessageBox, QDialog, QGraphicsDropShadowEffect)
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QPoint, QRect, pyqtProperty
from PyQt5.QtGui import (QPainter, QPen, QBrush, QColor, QFont, QImage, QPixmap, 
                         QTransform, QLinearGradient, QRadialGradient, QConicalGradient,
                         QPainterPath, QFontDatabase, QPalette)

class GlowEffect(QGraphicsDropShadowEffect):
    def __init__(self, color):
        super().__init__()
        self.setColor(color)
        self.setBlurRadius(20)
        self.setOffset(0, 0)

class AnimatedLabel(QLabel):
    def __init__(self, text=""):
        super().__init__(text)
        self._glow_intensity = 0
        self.glow_animation = QPropertyAnimation(self, b"glow_intensity")
        self.glow_animation.setDuration(2000)
        self.glow_animation.setLoopCount(-1)
        self.glow_animation.setKeyValueAt(0, 0)
        self.glow_animation.setKeyValueAt(0.5, 1)
        self.glow_animation.setKeyValueAt(1, 0)
        self.glow_animation.start()

    @pyqtProperty(float)
    def glow_intensity(self):
        return self._glow_intensity

    @glow_intensity.setter
    def glow_intensity(self, value):
        self._glow_intensity = value
        self.setStyleSheet(f"""
            color: rgba(0, 255, 255, {255});
            text-shadow: 0 0 {10 + value * 20}px rgba(255, 0, 255, {200 * value});
        """)

class ParticleSystem:
    def __init__(self):
        self.particles = []
        
    def add_particle(self, x, y, color, lifetime=60):
        self.particles.append({
            'x': x, 'y': y,
            'vx': random.uniform(-2, 2),
            'vy': random.uniform(-2, 2),
            'color': color,
            'lifetime': lifetime,
            'max_lifetime': lifetime,
            'size': random.uniform(2, 6)
        })
        
    def update(self):
        for particle in self.particles[:]:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['lifetime'] -= 1
            particle['vy'] += 0.1  # гравитация
            
            if particle['lifetime'] <= 0:
                self.particles.remove(particle)
                
    def draw(self, painter):
        for particle in self.particles:
            alpha = int(255 * (particle['lifetime'] / particle['max_lifetime']))
            size = particle['size'] * (particle['lifetime'] / particle['max_lifetime'])
            
            color = QColor(particle['color'])
            color.setAlpha(alpha)
            
            painter.setBrush(QBrush(color))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(int(particle['x']), int(particle['y']), int(size), int(size))

class SynthwaveCaptchaDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("⚡ SYNTHWAVE VERIFICATION ⚡")
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #000033, stop: 0.3 #330033, stop: 0.7 #660066, stop: 1 #000033);
                border: 3px solid;
                border-image: linear-gradient(45deg, #ff00ff, #00ffff, #ff00ff) 1;
            }
            QLabel {
                color: #00ffff;
                font-family: 'Courier New';
                font-weight: bold;
                font-size: 16px;
                background: transparent;
            }
            QLineEdit {
                background: rgba(0, 0, 0, 150);
                border: 2px solid;
                border-image: linear-gradient(45deg, #00ffff, #ff00ff) 1;
                color: #00ffff;
                font-family: 'Courier New';
                font-size: 16px;
                padding: 12px;
                selection-background-color: #ff00ff;
            }
            QLineEdit:focus {
                background: rgba(0, 0, 0, 200);
                border: 2px solid #ff00ff;
            }
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #ff00ff, stop: 0.5 #00ffff, stop: 1 #ff00ff);
                color: #000;
                border: none;
                font-family: 'Courier New';
                font-weight: bold;
                font-size: 14px;
                padding: 12px;
                min-height: 30px;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #00ffff, stop: 0.5 #ff00ff, stop: 1 #00ffff);
            }
            QPushButton:pressed {
                background: #000;
                color: #ff00ff;
                border: 1px solid #00ffff;
            }
        """)
        self.captcha_text = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        self.particles = ParticleSystem()
        self.init_ui()
        self.setup_animations()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Анимированный заголовок
        title = AnimatedLabel("🔐 SYNTHWAVE VERIFICATION")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Courier New", 18, QFont.Bold))
        layout.addWidget(title)
        
        label = QLabel("▼ ENTER THE CODE BELOW ▼")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("color: #ff00ff; font-size: 14px;")
        layout.addWidget(label)
        
        self.captcha_label = QLabel()
        self.captcha_label.setFixedSize(300, 100)
        self.captcha_label.setStyleSheet("""
            background: rgba(0, 0, 0, 150);
            border: 2px solid;
            border-image: linear-gradient(45deg, #ff00ff, #00ffff) 1;
        """)
        self.generate_synthwave_captcha()
        layout.addWidget(self.captcha_label, alignment=Qt.AlignCenter)
        
        self.input = QLineEdit()
        self.input.setAlignment(Qt.AlignCenter)
        self.input.setMaxLength(6)
        self.input.setFont(QFont("Courier New", 14))
        layout.addWidget(self.input)
        
        buttons_layout = QHBoxLayout()
        self.submit_button = QPushButton("🚀 VERIFY")
        self.refresh_button = QPushButton("🔄 REFRESH")
        
        # Добавляем свечение к кнопкам
        glow_effect = GlowEffect(QColor(255, 0, 255))
        self.submit_button.setGraphicsEffect(glow_effect)
        
        self.submit_button.clicked.connect(self.verify_captcha)
        self.refresh_button.clicked.connect(self.refresh_captcha)
        
        buttons_layout.addWidget(self.submit_button)
        buttons_layout.addWidget(self.refresh_button)
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)
        self.setFixedSize(400, 400)

    def setup_animations(self):
        # Анимация частиц
        self.particle_timer = QTimer()
        self.particle_timer.timeout.connect(self.update_particles)
        self.particle_timer.start(50)

    def update_particles(self):
        # Добавляем частицы по краям диалога
        if random.random() > 0.7:
            side = random.choice(['top', 'bottom', 'left', 'right'])
            if side == 'top':
                self.particles.add_particle(random.randint(0, 400), 0, 
                                          random.choice([QColor(255, 0, 255), QColor(0, 255, 255)]))
            elif side == 'bottom':
                self.particles.add_particle(random.randint(0, 400), 400, 
                                          random.choice([QColor(255, 0, 255), QColor(0, 255, 255)]))
        
        self.particles.update()
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        self.particles.draw(painter)

    def generate_synthwave_captcha(self):
        image = QImage(300, 100, QImage.Format_ARGB32)
        image.fill(Qt.transparent)
        
        painter = QPainter(image)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Фон с сеткой
        for x in range(0, 300, 10):
            for y in range(0, 100, 10):
                if (x + y) % 20 == 0:
                    painter.setPen(QPen(QColor(255, 0, 255, 30), 1))
                    painter.drawPoint(x, y)
        
        # Анимированный градиентный фон
        time = QTimer().remainingTime() / 1000.0
        gradient = QLinearGradient(0, 0, 300, 100)
        gradient.setColorAt(0, QColor(255, 0, 255, 50))
        gradient.setColorAt(0.5, QColor(0, 255, 255, 50))
        gradient.setColorAt(1, QColor(255, 0, 255, 50))
        painter.fillRect(0, 0, 300, 100, gradient)
        
        # Текст с множественным свечением
        font = QFont("Courier New", 32, QFont.Bold)
        painter.setFont(font)
        
        for i, char in enumerate(self.captcha_text):
            # Внешнее свечение
            for glow_size in range(10, 0, -2):
                alpha = 20 + glow_size * 5
                painter.setPen(QPen(QColor(255, 0, 255, alpha), glow_size))
                painter.drawText(30 + i * 40, 60, char)
            
            # Основной текст с градиентом
            char_gradient = QLinearGradient(30 + i * 40, 40, 30 + i * 40, 70)
            char_gradient.setColorAt(0, QColor(255, 255, 255))
            char_gradient.setColorAt(0.5, QColor(0, 255, 255))
            char_gradient.setColorAt(1, QColor(255, 0, 255))
            painter.setPen(QPen(char_gradient, 3))
            painter.drawText(30 + i * 40, 60, char)
            
            # Эффект сканирования
            scan_y = (QTimer().remainingTime() // 10) % 100
            painter.setPen(QPen(QColor(0, 255, 255, 100), 2))
            painter.drawLine(25 + i * 40, scan_y, 55 + i * 40, scan_y)

        painter.end()
        pixmap = QPixmap.fromImage(image)
        self.captcha_label.setPixmap(pixmap)

    def refresh_captcha(self):
        self.captcha_text = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        self.generate_synthwave_captcha()
        self.input.clear()
        # Эффект частиц при обновлении
        for _ in range(20):
            self.particles.add_particle(150, 50, QColor(0, 255, 255), 30)

    def verify_captcha(self):
        if self.input.text().upper() == self.captcha_text:
            # Эффект успеха
            for _ in range(50):
                self.particles.add_particle(200, 200, QColor(0, 255, 0), 60)
            QTimer.singleShot(500, self.accept)
        else:
            # Эффект ошибки
            for _ in range(50):
                self.particles.add_particle(200, 200, QColor(255, 0, 0), 60)
            QMessageBox.warning(self, "⛔ ACCESS DENIED", "❌ INVALID CAPTCHA CODE!")
            self.refresh_captcha()

class SynthwaveLoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("💾 SYNTHWAVE TERMINAL v3.0")
        self.users = {"admin": "password123", "user": "123456", "player": "pong2024"}
        self.particles = ParticleSystem()
        self.init_ui()
        self.setup_animations()

    def init_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #000011, stop: 0.2 #220022, stop: 0.5 #440044, stop: 0.8 #220022, stop: 1 #000011);
            }
            QLabel {
                color: #00ffff;
                font-family: 'Courier New';
                font-weight: bold;
                font-size: 14px;
                background: transparent;
            }
            QLineEdit {
                background: rgba(0, 0, 0, 180);
                border: 2px solid;
                border-image: linear-gradient(45deg, #00ffff, #ff00ff) 1;
                color: #00ffff;
                font-family: 'Courier New';
                font-size: 14px;
                padding: 15px;
                border-radius: 2px;
            }
            QLineEdit:focus {
                background: rgba(0, 0, 0, 220);
                border: 2px solid #ff00ff;
            }
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #ff00ff, stop: 0.5 #00ffff, stop: 1 #ff00ff);
                color: #000;
                border: none;
                font-family: 'Courier New';
                font-weight: bold;
                font-size: 14px;
                padding: 15px;
                min-width: 140px;
                border-radius: 2px;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #00ffff, stop: 0.5 #ff00ff, stop: 1 #00ffff);
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(25)
        layout.setContentsMargins(50, 50, 50, 50)
        
        # Анимированный заголовок терминала
        title_label = AnimatedLabel("""
╔══════════════════════════════════════╗
║           🌌 SYNTHWAVE TERMINAL      ║
║             v3.0 - 2084              ║
║         ACCESS AUTHORIZATION         ║
╚══════════════════════════════════════╝
        """)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Courier New", 12))
        layout.addWidget(title_label)
        
        # Поля ввода с иконками
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("🔑 ENTER USERNAME...")
        self.username_input.setFont(QFont("Courier New", 12))
        layout.addWidget(QLabel("👤 USERNAME:"))
        layout.addWidget(self.username_input)
        
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("🔒 ENTER PASSWORD...")
        self.password_input.setFont(QFont("Courier New", 12))
        layout.addWidget(QLabel("🗝️ PASSWORD:"))
        layout.addWidget(self.password_input)
        
        # Кнопки с иконками
        buttons_layout = QHBoxLayout()
        self.login_button = QPushButton("🚀 LOGIN")
        self.register_button = QPushButton("📝 REGISTER")
        
        # Эффекты свечения для кнопок
        login_glow = GlowEffect(QColor(0, 255, 255))
        self.login_button.setGraphicsEffect(login_glow)
        
        register_glow = GlowEffect(QColor(255, 0, 255))
        self.register_button.setGraphicsEffect(register_glow)
        
        self.login_button.clicked.connect(self.login)
        self.register_button.clicked.connect(self.register)
        
        buttons_layout.addWidget(self.login_button)
        buttons_layout.addWidget(self.register_button)
        layout.addLayout(buttons_layout)
        
        # Анимированный статус бар
        self.status_label = AnimatedLabel(">>> SYSTEM READY <<<")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setFont(QFont("Courier New", 10))
        layout.addWidget(self.status_label)
        
        self.central_widget.setLayout(layout)
        self.setFixedSize(600, 550)

    def setup_animations(self):
        # Таймер для частиц
        self.particle_timer = QTimer()
        self.particle_timer.timeout.connect(self.update_particles)
        self.particle_timer.start(30)

    def update_particles(self):
        # Создаем частицы по краям окна
        if random.random() > 0.8:
            x = random.choice([0, 600])
            y = random.randint(0, 550)
            color = random.choice([QColor(255, 0, 255), QColor(0, 255, 255)])
            self.particles.add_particle(x, y, color, 100)
        
        self.particles.update()
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        self.particles.draw(painter)

    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        if username in self.users and self.users[username] == password:
            self.status_label.setText(">>> ACCESS GRANTED <<<")
            # Эффект успешного входа
            for _ in range(100):
                self.particles.add_particle(300, 275, QColor(0, 255, 0), 80)
            QTimer.singleShot(1000, self.start_game)
        else:
            self.status_label.setText(">>> ACCESS DENIED - CAPTCHA REQUIRED <<<")
            # Эффект ошибки
            for _ in range(50):
                self.particles.add_particle(300, 275, QColor(255, 0, 0), 60)
            captcha_dialog = SynthwaveCaptchaDialog(self)
            if captcha_dialog.exec_():
                self.status_label.setText(">>> INVALID CREDENTIALS <<<")

    def register(self):
        username = self.username_input.text()
        password = self.password_input.text()
        if username and password:
            if username not in self.users:
                self.users[username] = password
                self.status_label.setText(">>> USER REGISTERED <<<")
                # Эффект регистрации
                for _ in range(80):
                    self.particles.add_particle(300, 275, QColor(255, 255, 0), 70)
                QMessageBox.information(self, "✅ SUCCESS", "🎉 USER REGISTRATION COMPLETE!")
            else:
                self.status_label.setText(">>> USER ALREADY EXISTS <<<")
                QMessageBox.warning(self, "❌ ERROR", "⚠️ USER ALREADY EXISTS IN DATABASE!")
        else:
            self.status_label.setText(">>> FILL ALL FIELDS <<<")
            QMessageBox.warning(self, "❌ ERROR", "📝 PLEASE FILL ALL FIELDS!")

    def start_game(self):
        self.game_window = SynthwavePongGame()
        self.game_window.show()
        self.close()

class SynthwaveMenuWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🎮 SYNTHWAVE PONG - MAINFRAME")
        self.particles = ParticleSystem()
        self.init_ui()
        self.setup_animations()

    def init_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #000033, stop: 0.3 #330033, stop: 0.7 #660066, stop: 1 #000033);
            }
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #ff00ff, stop: 0.5 #00ffff, stop: 1 #ff00ff);
                color: black;
                border: 2px solid #00ffff;
                font-family: 'Courier New';
                font-weight: bold;
                font-size: 18px;
                padding: 20px;
                min-width: 200px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #00ffff, stop: 0.5 #ff00ff, stop: 1 #00ffff);
                border: 2px solid #ff00ff;
                font-size: 20px;
            }
            QLabel {
                background: transparent;
                font-family: 'Courier New';
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(40)
        layout.setContentsMargins(60, 60, 60, 60)
        layout.setAlignment(Qt.AlignCenter)

        # Главный заголовок в стиле терминала
        title_label = AnimatedLabel("""
╔══════════════════════════════════╗
║      🌌 SYNTHWAVE PONG 2077     ║
║         RETRO TERMINAL           ║
╚══════════════════════════════════╝
        """)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Courier New", 20, QFont.Bold))
        layout.addWidget(title_label)

        # Кнопки меню
        start_button = QPushButton("🎮 START GAME")
        start_button.clicked.connect(self.start_auth)
        
        exit_button = QPushButton("🚪 EXIT TERMINAL")
        exit_button.clicked.connect(self.close)
        
        # Добавляем свечение к кнопкам
        start_glow = GlowEffect(QColor(0, 255, 255))
        start_button.setGraphicsEffect(start_glow)
        
        exit_glow = GlowEffect(QColor(255, 0, 255))
        exit_button.setGraphicsEffect(exit_glow)
        
        layout.addWidget(start_button)
        layout.addWidget(exit_button)

        # Нижний статус
        footer_label = AnimatedLabel(">>> SYSTEM ONLINE <<<")
        footer_label.setAlignment(Qt.AlignCenter)
        footer_label.setFont(QFont("Courier New", 12))
        layout.addWidget(footer_label)

        self.central_widget.setLayout(layout)
        self.setFixedSize(700, 600)

    def setup_animations(self):
        # Анимация частиц
        self.particle_timer = QTimer()
        self.particle_timer.timeout.connect(self.update_particles)
        self.particle_timer.start(40)
        
        # Анимация мигания заголовка
        self.blink_animation = QPropertyAnimation(self, b"windowTitle")
        self.blink_animation.setDuration(2000)
        self.blink_animation.setLoopCount(-1)
        self.blink_animation.setKeyValueAt(0, "🎮 SYNTHWAVE PONG - MAINFRAME")
        self.blink_animation.setKeyValueAt(0.5, "🎮 SYNTHWAVE PONG - MAINFRAME _")
        self.blink_animation.setKeyValueAt(1, "🎮 SYNTHWAVE PONG - MAINFRAME")
        self.blink_animation.start()

    def update_particles(self):
        # Создаем частицы по всему экрану
        if random.random() > 0.6:
            x = random.randint(0, 700)
            y = random.randint(0, 600)
            color = random.choice([QColor(255, 0, 255), QColor(0, 255, 255), QColor(255, 255, 0)])
            self.particles.add_particle(x, y, color, random.randint(50, 150))
        
        self.particles.update()
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        self.particles.draw(painter)

    def start_auth(self):
        self.auth_window = SynthwaveLoginWindow()
        self.auth_window.show()
        self.close()

class SynthwavePongGame(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🎮 SYNTHWAVE PONG - GAME ACTIVE")
        self.setFixedSize(800, 600)
        self.game_widget = SynthwaveGameWidget(self)
        self.setCentralWidget(self.game_widget)
        self.game_widget.setFocus()
        
        self.setStyleSheet("""
            QMainWindow {
                background: black;
            }
        """)

    def keyPressEvent(self, event):
        self.game_widget.keyPressEvent(event)

    def keyReleaseEvent(self, event):
        self.game_widget.keyReleaseEvent(event)

class SynthwaveGameWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._ball_x, self._ball_y = 400, 300
        self._ball_dx, self._ball_dy = 6, 6
        self._paddle1_y, self._paddle2_y = 250, 250
        self.paddle_height, self.paddle_width = 100, 15
        self._score1, self._score2 = 0, 0
        self.move_up1 = False
        self.move_down1 = False
        self.move_up2 = False
        self.move_down2 = False
        
        self.particles = ParticleSystem()
        self.trail_positions = []
        self.horizontal_lines = [(i * 25, random.randint(50, 150)) for i in range(32)]
        self.mountain_points = self.generate_mountains()
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_game)
        self.timer.start(16)
        self.setFocusPolicy(Qt.StrongFocus)

    def generate_mountains(self):
        points = []
        for x in range(0, 800, 10):
            y = 400 + math.sin(x / 50) * 30 + math.cos(x / 25) * 15
            points.append((x, y))
        return points

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Рисуем сложный синтвейв фон
        self.draw_advanced_background(painter)
        
        # Горы
        self.draw_mountains(painter)
        
        # Солнце и лучи
        self.draw_sun(painter)
        
        # След от мяча
        self.draw_ball_trail(painter)
        
        # Ракетки
        self.draw_paddles(painter)
        
        # Мяч
        self.draw_ball(painter)
        
        # Счет
        self.draw_score(painter)
        
        # Частицы
        self.particles.draw(painter)

    def draw_advanced_background(self, painter):
        # Основной градиент
        gradient = QLinearGradient(0, 0, 0, 600)
        gradient.setColorAt(0, QColor(10, 0, 30))
        gradient.setColorAt(0.3, QColor(30, 0, 50))
        gradient.setColorAt(0.6, QColor(50, 0, 70))
        gradient.setColorAt(1, QColor(0, 0, 0))
        painter.fillRect(0, 0, 800, 600, gradient)
        
        # Звезды
        painter.setPen(QPen(Qt.white, 1))
        for _ in range(100):
            x = random.randint(0, 800)
            y = random.randint(0, 300)
            size = random.randint(1, 3)
            painter.drawEllipse(x, y, size, size)

    def draw_mountains(self, painter):
        path = QPainterPath()
        path.moveTo(0, 600)
        for x, y in self.mountain_points:
            path.lineTo(x, y)
        path.lineTo(800, 600)
        path.closeSubpath()
        
        gradient = QLinearGradient(0, 400, 0, 600)
        gradient.setColorAt(0, QColor(255, 0, 255, 100))
        gradient.setColorAt(1, QColor(0, 0, 0, 0))
        painter.fillPath(path, gradient)

    def draw_sun(self, painter):
        # Солнце
        sun_gradient = QRadialGradient(400, 800, 400)
        sun_gradient.setColorAt(0, QColor(255, 0, 255, 80))
        sun_gradient.setColorAt(1, QColor(0, 0, 0, 0))
        painter.setBrush(QBrush(sun_gradient))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(0, 400, 800, 800)
        
        # # Лучи
        # painter.setPen(QPen(QColor(0, 255, 255, 60), 2))
        # for x, alpha in self.horizontal_lines:
        #     painter.setPen(QPen(QColor(0, 255, 255, alpha), 2))
        #     painter.drawLine(x, 600, x, 200)

    def draw_ball_trail(self, painter):
        for i, (x, y) in enumerate(self.trail_positions):
            alpha = 200 * (i / len(self.trail_positions))
            size = 12 * (i / len(self.trail_positions))
            gradient = QRadialGradient(x, y, size)
            gradient.setColorAt(0, QColor(0, 255, 255, int(alpha)))
            gradient.setColorAt(1, QColor(255, 0, 255, 0))
            painter.setBrush(QBrush(gradient))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(int(x - size/2), int(y - size/2), int(size), int(size))

    def draw_paddles(self, painter):
        # Левая ракетка с свечением
        for i in range(3, 0, -1):
            alpha = 100 - i * 30
            painter.setBrush(QBrush(QColor(255, 0, 255, alpha)))
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(50 - i, int(self._paddle1_y) - i, 
                                  self.paddle_width + i*2, self.paddle_height + i*2, 5, 5)
        
        paddle_gradient = QLinearGradient(50, self._paddle1_y, 50, self._paddle1_y + self.paddle_height)
        paddle_gradient.setColorAt(0, QColor(255, 0, 255))
        paddle_gradient.setColorAt(1, QColor(128, 0, 255))
        painter.setBrush(QBrush(paddle_gradient))
        painter.setPen(QPen(QColor(255, 100, 255), 2))
        painter.drawRoundedRect(50, int(self._paddle1_y), self.paddle_width, self.paddle_height, 5, 5)
        
        # Правая ракетка с свечением
        for i in range(3, 0, -1):
            alpha = 100 - i * 30
            painter.setBrush(QBrush(QColor(0, 255, 255, alpha)))
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(740 - i, int(self._paddle2_y) - i, 
                                  self.paddle_width + i*2, self.paddle_height + i*2, 5, 5)
        
        paddle_gradient2 = QLinearGradient(740, self._paddle2_y, 740, self._paddle2_y + self.paddle_height)
        paddle_gradient2.setColorAt(0, QColor(0, 255, 255))
        paddle_gradient2.setColorAt(1, QColor(0, 128, 255))
        painter.setBrush(QBrush(paddle_gradient2))
        painter.setPen(QPen(QColor(100, 255, 255), 2))
        painter.drawRoundedRect(740, int(self._paddle2_y), self.paddle_width, self.paddle_height, 5, 5)

    def draw_ball(self, painter):
        # Неоновое свечение мяча
        for i in range(3, 0, -1):
            alpha = 100 - i * 30
            painter.setBrush(QBrush(QColor(255, 255, 255, alpha)))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(int(self._ball_x) - i, int(self._ball_y) - i, 10 + i*2, 10 + i*2)
        
        # Основной мяч
        ball_gradient = QRadialGradient(self._ball_x + 5, self._ball_y + 5, 5)
        ball_gradient.setColorAt(0, QColor(255, 255, 255))
        ball_gradient.setColorAt(1, QColor(200, 200, 255))
        painter.setBrush(QBrush(ball_gradient))
        painter.setPen(QPen(QColor(0, 255, 255), 2))
        painter.drawEllipse(int(self._ball_x), int(self._ball_y), 10, 10)

    def draw_score(self, painter):
        painter.setFont(QFont("Courier New", 24, QFont.Bold))
        
        # Тень
        painter.setPen(QPen(QColor(0, 0, 0, 150), 4))
        painter.drawText(195, 47, f"P1: {self._score1}")
        painter.drawText(545, 47, f"P2: {self._score2}")
        
        # Основной текст
        painter.setPen(QPen(QColor(255, 0, 255), 2))
        painter.drawText(200, 50, f"P1: {self._score1}")
        painter.setPen(QPen(QColor(0, 255, 255), 2))
        painter.drawText(550, 50, f"P2: {self._score2}")

    def update_game(self):
        # Обновляем анимации
        self.horizontal_lines = [(pos, (alpha + random.randint(-3, 3)) % 150) 
                               for pos, alpha in self.horizontal_lines]
        
        # След мяча
        self.trail_positions.insert(0, (self._ball_x + 5, self._ball_y + 5))
        if len(self.trail_positions) > 10:
            self.trail_positions.pop()
        
        # Добавляем частицы при движении
        if random.random() > 0.5:
            self.particles.add_particle(self._ball_x + 5, self._ball_y + 5, 
                                      random.choice([QColor(255, 0, 255), QColor(0, 255, 255)]), 20)
        
        # Движение мяча
        self._ball_x += self._ball_dx
        self._ball_y += self._ball_dy

        # Отскок от границ
        if self._ball_y <= 0 or self._ball_y >= 590:
            self._ball_dy *= -1
            # Эффект отскока
            for _ in range(10):
                self.particles.add_particle(self._ball_x, self._ball_y, QColor(255, 255, 0), 30)

        # Отскок от ракеток
        if (self._ball_x <= 65 and self._paddle1_y <= self._ball_y <= self._paddle1_y + self.paddle_height) or \
           (self._ball_x >= 725 and self._paddle2_y <= self._ball_y <= self._paddle2_y + self.paddle_height):
            self._ball_dx *= -1.05  # Ускорение после отскока
            # Эффект отскока от ракетки
            for _ in range(15):
                self.particles.add_particle(self._ball_x, self._ball_y, 
                                          QColor(255, 0, 255) if self._ball_x <= 65 else QColor(0, 255, 255), 40)

        # Гол
        if self._ball_x <= 0:
            self._score2 += 1
            self.reset_ball()
        elif self._ball_x >= 790:
            self._score1 += 1
            self.reset_ball()

        # Движение ракеток
        paddle_speed = 10
        if self.move_up1 and self._paddle1_y > 0:
            self._paddle1_y -= paddle_speed
        if self.move_down1 and self._paddle1_y < 500:
            self._paddle1_y += paddle_speed
        if self.move_up2 and self._paddle2_y > 0:
            self._paddle2_y -= paddle_speed
        if self.move_down2 and self._paddle2_y < 500:
            self._paddle2_y += paddle_speed

        self.particles.update()
        self.update()

    def reset_ball(self):
        self._ball_x, self._ball_y = 400, 300
        self._ball_dx = random.choice([6, -6])
        self._ball_dy = random.choice([4, -4, 5, -5, 6, -6])
        self.trail_positions = []
        # Эффект при сбросе мяча
        for _ in range(30):
            self.particles.add_particle(400, 300, QColor(255, 255, 0), 50)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_W:
            self.move_up1 = True
        elif event.key() == Qt.Key_S:
            self.move_down1 = True
        elif event.key() == Qt.Key_Up:
            self.move_up2 = True
        elif event.key() == Qt.Key_Down:
            self.move_down2 = True

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key_W:
            self.move_up1 = False
        elif event.key() == Qt.Key_S:
            self.move_down1 = False
        elif event.key() == Qt.Key_Up:
            self.move_up2 = False
        elif event.key() == Qt.Key_Down:
            self.move_down2 = False

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # Устанавливаем высококачественный стиль
    app.setStyle('Fusion')
    
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(0, 0, 0))
    palette.setColor(QPalette.WindowText, QColor(0, 255, 255))
    app.setPalette(palette)
    
    app.setStyleSheet("""
        QMessageBox {
            background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                stop: 0 #000033, stop: 0.5 #330033, stop: 1 #000033);
            color: #00ffff;
            font-family: 'Courier New';
            border: 3px solid #ff00ff;
        }
        QMessageBox QPushButton {
            background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                stop: 0 #ff00ff, stop: 0.5 #00ffff, stop: 1 #ff00ff);
            color: #000;
            border: none;
            font-family: 'Courier New';
            font-weight: bold;
            padding: 10px 20px;
            min-width: 100px;
        }
    """)
    
    menu_window = SynthwaveMenuWindow()
    menu_window.show()
    sys.exit(app.exec_())