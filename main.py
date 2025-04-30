import sys
import cv2
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QLineEdit,
    QHBoxLayout, QMessageBox, QGroupBox, QScrollArea, QFrame, QSplitter,
    QStatusBar, QProgressBar, QComboBox
)
from PyQt5.QtGui import QImage, QPixmap, QFont, QColor, QPainter, QPen, QIcon
from PyQt5.QtCore import QTimer, Qt, QSize, QPropertyAnimation, QEasingCurve


class FaceDetectionApp(QWidget):
    def __init__(self):
        super().__init__()

        # UI setup
        self.setWindowTitle("Advanced Face Detection Security System")
        self.setGeometry(100, 100, 1000, 800)
        
        # Modern dark theme with accent colors
        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
                color: #f0f0f0;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QGroupBox {
                border: 2px solid #3498db;
                border-radius: 8px;
                margin-top: 12px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 10px;
                background-color: #1e1e1e;
            }
            QLineEdit {
                padding: 10px;
                background-color: #333333;
                border: 1px solid #555555;
                border-radius: 5px;
                color: #f0f0f0;
                font-size: 12px;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
            }
            QScrollArea {
                border: none;
            }
            QComboBox {
                padding: 8px;
                background-color: #333333;
                border: 1px solid #555555;
                border-radius: 5px;
                color: #f0f0f0;
            }
            QProgressBar {
                border: 1px solid #555555;
                border-radius: 5px;
                text-align: center;
                background-color: #333333;
            }
            QProgressBar::chunk {
                background-color: #3498db;
                border-radius: 5px;
            }
            QLabel {
                color: #f0f0f0;
            }
        """)

        # Main layout with splitter
        main_layout = QHBoxLayout(self)
        self.splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(self.splitter)
        
        # Left panel for camera feed
        self.left_panel = QWidget()
        self.left_layout = QVBoxLayout(self.left_panel)
        self.left_layout.setContentsMargins(15, 15, 15, 15)
        
        # Status indicator
        self.status_layout = QHBoxLayout()
        self.status_label = QLabel("System Status:")
        self.status_indicator = QLabel("Ready")
        self.status_indicator.setStyleSheet("color: #3498db; font-weight: bold;")
        self.status_layout.addWidget(self.status_label)
        self.status_layout.addWidget(self.status_indicator)
        self.status_layout.addStretch()
        self.left_layout.addLayout(self.status_layout)
        
        # Camera feed frame with border
        self.camera_frame = QFrame()
        self.camera_frame.setFrameStyle(QFrame.StyledPanel | QFrame.Sunken)
        self.camera_frame.setStyleSheet("background-color: #000000; border: 2px solid #3498db; border-radius: 8px;")
        self.camera_layout = QVBoxLayout(self.camera_frame)
        self.camera_layout.setContentsMargins(1, 1, 1, 1)
        
        # Face display label
        self.label = QLabel()
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setMinimumSize(640, 480)
        self.camera_layout.addWidget(self.label)
        self.left_layout.addWidget(self.camera_frame)
        
        # Detection status bar
        self.status_bar = QStatusBar()
        self.status_bar.setStyleSheet("background-color: #333333; color: #f0f0f0;")
        self.status_bar.showMessage("No faces detected")
        self.left_layout.addWidget(self.status_bar)
        
        # Right panel for controls
        self.right_panel = QWidget()
        self.right_layout = QVBoxLayout(self.right_panel)
        self.right_layout.setContentsMargins(15, 15, 15, 15)
        self.right_layout.setSpacing(20)
        
        # Title
        title_label = QLabel("Security Control Panel")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #3498db; padding: 10px 0;")
        title_label.setAlignment(Qt.AlignCenter)
        self.right_layout.addWidget(title_label)
        
        # Camera selection
        self.camera_group = QGroupBox("Camera Settings")
        camera_layout = QVBoxLayout()
        
        camera_select_layout = QHBoxLayout()
        camera_select_layout.addWidget(QLabel("Camera:"))
        self.camera_selector = QComboBox()
        self.camera_selector.addItem("Default Camera (0)")
        self.camera_selector.addItem("Camera 1")
        self.camera_selector.addItem("Camera 2")
        self.camera_selector.currentIndexChanged.connect(self.change_camera)
        camera_select_layout.addWidget(self.camera_selector)
        camera_layout.addLayout(camera_select_layout)
        
        # Detection sensitivity
        sensitivity_layout = QHBoxLayout()
        sensitivity_layout.addWidget(QLabel("Detection Sensitivity:"))
        self.sensitivity_slider = QProgressBar()
        self.sensitivity_slider.setRange(0, 10)
        self.sensitivity_slider.setValue(5)
        self.sensitivity_slider.setTextVisible(False)
        self.sensitivity_slider.setOrientation(Qt.Horizontal)
        sensitivity_layout.addWidget(self.sensitivity_slider)
        camera_layout.addLayout(sensitivity_layout)
        
        self.camera_group.setLayout(camera_layout)
        self.right_layout.addWidget(self.camera_group)
        
        # User Registration Section
        self.registration_group = QGroupBox("User Registration")
        self.registration_layout = QVBoxLayout()

        # Name input with icon
        name_layout = QHBoxLayout()
        name_label = QLabel("Name:")
        name_label.setMinimumWidth(60)
        self.nameInput = QLineEdit()
        self.nameInput.setPlaceholderText("Enter Full Name")
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.nameInput)
        self.registration_layout.addLayout(name_layout)

        # ID input with icon
        id_layout = QHBoxLayout()
        id_label = QLabel("ID:")
        id_label.setMinimumWidth(60)
        self.idInput = QLineEdit()
        self.idInput.setPlaceholderText("Enter Unique ID")
        id_layout.addWidget(id_label)
        id_layout.addWidget(self.idInput)
        self.registration_layout.addLayout(id_layout)

        # Take photo button
        self.takePhotoButton = QPushButton("Capture Face")
        self.takePhotoButton.clicked.connect(self.take_photo)
        self.takePhotoButton.setMinimumHeight(40)
        self.takePhotoButton.setCursor(Qt.PointingHandCursor)
        self.takePhotoButton.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border-radius: 5px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
            QPushButton:pressed {
                background-color: #219653;
            }
        """)
        self.registration_layout.addWidget(self.takePhotoButton)
        self.registration_group.setLayout(self.registration_layout)
        self.right_layout.addWidget(self.registration_group)

        # Unlock Door Section
        self.unlock_group = QGroupBox("Access Control")
        self.unlock_layout = QVBoxLayout()

        # Verification mode
        verify_mode_layout = QHBoxLayout()
        verify_mode_layout.addWidget(QLabel("Mode:"))
        self.verify_mode = QComboBox()
        self.verify_mode.addItem("Face Recognition")
        self.verify_mode.addItem("Face + PIN")
        verify_mode_layout.addWidget(self.verify_mode)
        self.unlock_layout.addLayout(verify_mode_layout)

        # Unlock button
        self.unlockButton = QPushButton("Unlock Door")
        self.unlockButton.clicked.connect(self.start_unlock)
        self.unlockButton.setMinimumHeight(40)
        self.unlockButton.setCursor(Qt.PointingHandCursor)
        self.unlockButton.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 5px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #1c6ea4;
            }
        """)
        self.unlock_layout.addWidget(self.unlockButton)
        
        # Emergency unlock
        self.emergency_button = QPushButton("Emergency Override")
        self.emergency_button.setMinimumHeight(40)
        self.emergency_button.setCursor(Qt.PointingHandCursor)
        self.emergency_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border-radius: 5px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:pressed {
                background-color: #a33529;
            }
        """)
        self.unlock_layout.addWidget(self.emergency_button)
        
        self.unlock_group.setLayout(self.unlock_layout)
        self.right_layout.addWidget(self.unlock_group)

        # Add spacer
        self.right_layout.addStretch()
        
        # Add the panels to the splitter
        self.splitter.addWidget(self.left_panel)
        self.splitter.addWidget(self.right_panel)
        self.splitter.setSizes([650, 350])

        # OpenCV and QTimer setup
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.capture = cv2.VideoCapture(0)
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )

        self.is_registering = False
        self.user_data_dir = 'user_data'
        os.makedirs(self.user_data_dir, exist_ok=True)

        # Variables to track access states
        self.access_denied_displayed = False
        self.access_granted_displayed = False
        self.detected_faces = []  # Store detected faces for drawing

        # Start the camera feed
        self.timer.start(30)
        
        # Animation for button feedback
        self.animation = QPropertyAnimation(self.takePhotoButton, b"geometry")
        self.animation.setDuration(100)
        
    def change_camera(self, index):
        self.capture.release()
        self.capture = cv2.VideoCapture(index)
        if not self.capture.isOpened():
            QMessageBox.warning(self, "Camera Error", f"Failed to open camera {index}")
            self.capture = cv2.VideoCapture(0)  # Fallback to default camera
            self.camera_selector.setCurrentIndex(0)

    def start_unlock(self):
        self.is_registering = False
        self.status_indicator.setText("Verifying...")
        self.status_indicator.setStyleSheet("color: #f39c12; font-weight: bold;")
        self.clear_inputs()
        self.access_denied_displayed = False  # Reset access denied state
        self.access_granted_displayed = False  # Reset access granted state

    def clear_inputs(self):
        self.nameInput.clear()
        self.idInput.clear()

    def take_photo(self):
        name = self.nameInput.text().strip()
        unique_id = self.idInput.text().strip()

        if not name or not unique_id:
            QMessageBox.warning(self, "Registration Error", "Please enter both Name and Unique ID")
            return

        # Visual feedback animation
        self.takePhotoButton.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border-radius: 5px;
                font-weight: bold;
                font-size: 13px;
            }
        """)
        QTimer.singleShot(200, self.reset_button_style)

        self.status_indicator.setText("Capturing...")
        self.status_indicator.setStyleSheet("color: #e74c3c; font-weight: bold;")

        ret, frame = self.capture.read()
        if ret:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)

            if len(faces) == 0:
                QMessageBox.warning(self, "Registration Error", "No human face detected. Please position your face in the camera view.")
                self.status_indicator.setText("Ready")
                self.status_indicator.setStyleSheet("color: #3498db; font-weight: bold;")
                return

            # Proceed with photo capture
            user_folder = os.path.join(self.user_data_dir, f"{unique_id}_{name}")
            os.makedirs(user_folder, exist_ok=True)
            img_path = os.path.join(user_folder, 'face.jpg')
            cv2.imwrite(img_path, frame)
            
            self.status_indicator.setText("Registered")
            self.status_indicator.setStyleSheet("color: #2ecc71; font-weight: bold;")
            
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle("Registration Successful")
            msg.setText(f"User {name} with ID {unique_id} has been registered successfully!")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()
            
            # Reset status after delay
            QTimer.singleShot(2000, self.reset_status)

    def reset_button_style(self):
        self.takePhotoButton.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border-radius: 5px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
            QPushButton:pressed {
                background-color: #219653;
            }
        """)

    def reset_status(self):
        self.status_indicator.setText("Ready")
        self.status_indicator.setStyleSheet("color: #3498db; font-weight: bold;")

    def update_frame(self):
        ret, frame = self.capture.read()
        if ret:
            # Create a copy of the frame for drawing
            display_frame = frame.copy()
            
            # Face detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
            
            # Store detected faces for drawing
            self.detected_faces = faces
            
            # Update status bar with face count
            face_count = len(faces)
            if face_count == 0:
                self.status_bar.showMessage("No faces detected")
            elif face_count == 1:
                self.status_bar.showMessage("1 face detected")
            else:
                self.status_bar.showMessage(f"{face_count} faces detected")
            
            # Draw fancy rectangles around faces
            for (x, y, w, h) in faces:
                # Main rectangle
                cv2.rectangle(display_frame, (x, y), (x + w, y + h), (0, 165, 255), 2)
                
                # Corner markers (top-left)
                cv2.line(display_frame, (x, y), (x + 20, y), (0, 255, 0), 3)
                cv2.line(display_frame, (x, y), (x, y + 20), (0, 255, 0), 3)
                
                # Corner markers (top-right)
                cv2.line(display_frame, (x + w, y), (x + w - 20, y), (0, 255, 0), 3)
                cv2.line(display_frame, (x + w, y), (x + w, y + 20), (0, 255, 0), 3)
                
                # Corner markers (bottom-left)
                cv2.line(display_frame, (x, y + h), (x + 20, y + h), (0, 255, 0), 3)
                cv2.line(display_frame, (x, y + h), (x, y + h - 20), (0, 255, 0), 3)
                
                # Corner markers (bottom-right)
                cv2.line(display_frame, (x + w, y + h), (x + w - 20, y + h), (0, 255, 0), 3)
                cv2.line(display_frame, (x + w, y + h), (x + w, y + h - 20), (0, 255, 0), 3)
                
                # Add face ID label
                cv2.rectangle(display_frame, (x, y - 30), (x + w, y), (0, 165, 255), -1)
                cv2.putText(display_frame, "Face Detected", (x + 5, y - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

            if not self.is_registering and face_count > 0:
                self.verify_face(frame)

            # Convert to QImage and display
            rgb_image = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
            scaled_pixmap = QPixmap.fromImage(qt_image).scaled(
                self.label.width(), self.label.height(),
                Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            self.label.setPixmap(scaled_pixmap)

    def verify_face(self, frame):
        user_folders = os.listdir(self.user_data_dir)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        face_found = False

        for folder in user_folders:
            face_path = os.path.join(self.user_data_dir, folder, 'face.jpg')
            if not os.path.exists(face_path):
                continue
                
            stored_img = cv2.imread(face_path, cv2.IMREAD_GRAYSCALE)
            if stored_img is not None:
                # Simple template matching (in a real application, use a more robust method)
                res = cv2.matchTemplate(gray, stored_img, cv2.TM_CCOEFF_NORMED)
                threshold = 0.5  # Lowered threshold for demo purposes
                loc = (res >= threshold).any()
                
                if loc:
                    if not self.access_granted_displayed:
                        user_name = folder.split('_', 1)[1] if '_' in folder else folder
                        
                        self.status_indicator.setText("Access Granted")
                        self.status_indicator.setStyleSheet("color: #2ecc71; font-weight: bold;")
                        
                        msg = QMessageBox()
                        msg.setIcon(QMessageBox.Information)
                        msg.setWindowTitle("Access Granted")
                        msg.setText(f"Welcome {user_name}!\nDoor unlocked.")
                        msg.setStandardButtons(QMessageBox.Ok)
                        msg.exec_()
                        
                        self.access_granted_displayed = True
                        
                        # Reset status after delay
                        QTimer.singleShot(3000, self.reset_status)
                    
                    face_found = True
                    break

        if not face_found and not self.access_denied_displayed:
            self.status_indicator.setText("Access Denied")
            self.status_indicator.setStyleSheet("color: #e74c3c; font-weight: bold;")
            
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("Access Denied")
            msg.setText("Unrecognized face detected.\nPlease register or try again.")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()
            
            self.access_denied_displayed = True
            
            # Reset status after delay
            QTimer.singleShot(3000, self.reset_status)

    def closeEvent(self, event):
        self.capture.release()
        cv2.destroyAllWindows()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FaceDetectionApp()
    window.show()
    sys.exit(app.exec_())