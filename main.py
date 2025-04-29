import sys
import cv2
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QLineEdit, QScrollArea, QMessageBox, QGroupBox, QMainWindow, QStatusBar,
    QFrame, QSizePolicy
)
from PyQt5.QtGui import QImage, QPixmap, QFont, QIcon, QColor
from PyQt5.QtCore import QTimer, Qt, QSize, QDateTime


class FaceDetectionApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # UI setup
        self.setWindowTitle("Face Detection Security System")
        self.setGeometry(100, 100, 1000, 800)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #22252D;
                color: #F0F0F0;
            }
            QLabel {
                color: #F0F0F0;
                font-size: 14px;
            }
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                color: #F0F0F0;
                border: 2px solid #3498db;
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 10px;
                background-color: #22252D;
            }
        """)

        # Create scroll area and central widget
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setCentralWidget(self.scroll_area)
        
        # Create widget for scroll area
        self.central_widget = QWidget()
        self.scroll_area.setWidget(self.central_widget)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.setStyleSheet("background-color: #1A1D24; color: #F0F0F0; padding: 5px;")
        self.status_bar.showMessage("System ready. Camera activated.")

        # Main layout
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(15)

        # Create header
        self.header_frame = QFrame()
        self.header_frame.setStyleSheet("background-color: #1A1D24; border-radius: 10px; padding: 5px;")
        self.header_layout = QHBoxLayout(self.header_frame)
        
        self.header_label = QLabel("FACIAL RECOGNITION SECURITY")
        self.header_label.setFont(QFont("Arial", 16, QFont.Bold))
        self.header_label.setStyleSheet("color: #3498db;")
        self.header_label.setAlignment(Qt.AlignCenter)
        
        self.header_layout.addWidget(self.header_label)
        self.main_layout.addWidget(self.header_frame)

        # Camera feed (Face display)
        self.camera_frame = QFrame()
        self.camera_frame.setStyleSheet("""
            background-color: #1A1D24;
            border: 2px solid #3498db;
            border-radius: 10px;
            padding: 10px;
        """)
        self.camera_layout = QVBoxLayout(self.camera_frame)
        
        # Title for camera section
        self.camera_title = QLabel("CAMERA FEED")
        self.camera_title.setAlignment(Qt.AlignCenter)
        self.camera_title.setFont(QFont("Arial", 12, QFont.Bold))
        self.camera_title.setStyleSheet("color: #3498db; background: none; border: none;")
        
        # Container for camera feed with fixed size
        self.camera_container = QWidget()
        self.camera_container.setFixedSize(640, 480)  # Standard camera size
        self.camera_container_layout = QVBoxLayout(self.camera_container)
        self.camera_container_layout.setContentsMargins(0, 0, 0, 0)
        
        # Label for camera feed
        self.label = QLabel()
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("border: none; background: transparent;")
        self.camera_container_layout.addWidget(self.label)
        
        # Add camera container to a wrapper layout to center it
        self.camera_wrapper = QHBoxLayout()
        self.camera_wrapper.addStretch()
        self.camera_wrapper.addWidget(self.camera_container)
        self.camera_wrapper.addStretch()
        
        self.camera_layout.addWidget(self.camera_title)
        self.camera_layout.addLayout(self.camera_wrapper)
        
        self.main_layout.addWidget(self.camera_frame)
        
        # Lower section with controls - make it responsive with QHBoxLayout
        self.controls_frame = QFrame()
        self.controls_layout = QHBoxLayout(self.controls_frame)
        self.controls_layout.setSpacing(20)
        
        # User Registration Section
        self.registration_group = QGroupBox("USER REGISTRATION")
        self.registration_group.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.registration_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid #28a745;
                border-radius: 10px;
            }
        """)
        self.registration_layout = QVBoxLayout()
        self.registration_layout.setContentsMargins(20, 20, 20, 20)
        self.registration_layout.setSpacing(15)

        self.name_label = QLabel("Full Name:")
        self.name_label.setStyleSheet("font-weight: bold;")
        
        self.nameInput = QLineEdit()
        self.nameInput.setPlaceholderText("Enter Your Full Name")
        self.nameInput.setFont(QFont("Arial", 12))
        self.nameInput.setMinimumHeight(40)
        self.nameInput.setStyleSheet("""
            padding: 8px 15px;
            background-color: #2C303A;
            color: #F0F0F0;
            border: 1px solid #555555;
            border-radius: 6px;
        """)

        self.id_label = QLabel("Unique ID:")
        self.id_label.setStyleSheet("font-weight: bold;")
        
        self.idInput = QLineEdit()
        self.idInput.setPlaceholderText("Enter Unique ID")
        self.idInput.setFont(QFont("Arial", 12))
        self.idInput.setMinimumHeight(40)
        self.idInput.setStyleSheet("""
            padding: 8px 15px;
            background-color: #2C303A;
            color: #F0F0F0;
            border: 1px solid #555555;
            border-radius: 6px;
        """)

        self.takePhotoButton = QPushButton("REGISTER FACE")
        self.takePhotoButton.clicked.connect(self.take_photo)
        self.takePhotoButton.setFont(QFont("Arial", 12, QFont.Bold))
        self.takePhotoButton.setMinimumHeight(50)
        self.takePhotoButton.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                padding: 12px;
                border-radius: 8px;
                border: none;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:pressed {
                background-color: #1e7e34;
            }
        """)

        self.registration_layout.addWidget(self.name_label)
        self.registration_layout.addWidget(self.nameInput)
        self.registration_layout.addWidget(self.id_label)
        self.registration_layout.addWidget(self.idInput)
        self.registration_layout.addWidget(self.takePhotoButton)
        self.registration_group.setLayout(self.registration_layout)

        # Unlock Door Section
        self.unlock_group = QGroupBox("ACCESS CONTROL")
        self.unlock_group.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.unlock_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid #3498db;
                border-radius: 10px;
            }
        """)
        self.unlock_layout = QVBoxLayout()
        self.unlock_layout.setContentsMargins(20, 20, 20, 20)
        self.unlock_layout.setSpacing(15)

        self.unlock_info = QLabel("Scan your face to unlock the door")
        self.unlock_info.setAlignment(Qt.AlignCenter)
        self.unlock_info.setWordWrap(True)
        self.unlock_info.setStyleSheet("color: #F0F0F0;")

        self.unlockButton = QPushButton("SCAN TO UNLOCK")
        self.unlockButton.clicked.connect(self.start_unlock)
        self.unlockButton.setFont(QFont("Arial", 12, QFont.Bold))
        self.unlockButton.setMinimumHeight(50)
        self.unlockButton.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 12px;
                border-radius: 8px;
                border: none;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #2471a3;
            }
        """)

        self.status_label = QLabel("Ready to scan")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #F0F0F0; font-size: 12px;")

        self.unlock_layout.addWidget(self.unlock_info)
        self.unlock_layout.addWidget(self.unlockButton)
        self.unlock_layout.addWidget(self.status_label)
        self.unlock_group.setLayout(self.unlock_layout)

        # Add both groups to controls layout
        self.controls_layout.addWidget(self.registration_group)
        self.controls_layout.addWidget(self.unlock_group)
        
        # Add controls to main layout
        self.main_layout.addWidget(self.controls_frame)

        # Add a spacer at the bottom for better scrolling experience
        self.main_layout.addStretch()

        # OpenCV and QTimer setup
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.capture = cv2.VideoCapture(0)
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )

        # Set the camera resolution
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        # Flags and directories
        self.is_registering = False
        self.user_data_dir = 'user_data'
        os.makedirs(self.user_data_dir, exist_ok=True)

        # Flags to control notifications
        self.access_denied_time = QDateTime.currentDateTime().addSecs(-10)  # Initialize to past time
        self.access_granted_time = QDateTime.currentDateTime().addSecs(-10)  # Initialize to past time
        self.cooldown_seconds = 5  # Seconds to wait between notifications

        # Start camera feed
        self.timer.start(30)
        
        # Fixed camera display dimensions
        self.display_width = 640
        self.display_height = 480

    def on_resize_event(self, event):
        # Make controls vertical on small width
        if self.width() < 800:
            # Check if layout is already horizontal
            if isinstance(self.controls_layout, QHBoxLayout):
                # Remove widgets from horizontal layout
                self.registration_group.setParent(None)
                self.unlock_group.setParent(None)
                
                # Create new vertical layout
                new_layout = QVBoxLayout()
                new_layout.addWidget(self.registration_group)
                new_layout.addWidget(self.unlock_group)
                
                # Delete old layout and set new one
                old_layout = self.controls_layout
                self.controls_layout = new_layout
                self.controls_frame.setLayout(self.controls_layout)
                if old_layout:
                    old_layout.deleteLater()
        else:
            # Check if layout is already vertical
            if isinstance(self.controls_layout, QVBoxLayout):
                # Remove widgets from vertical layout
                self.registration_group.setParent(None)
                self.unlock_group.setParent(None)
                
                # Create new horizontal layout
                new_layout = QHBoxLayout()
                new_layout.addWidget(self.registration_group)
                new_layout.addWidget(self.unlock_group)
                
                # Delete old layout and set new one
                old_layout = self.controls_layout
                self.controls_layout = new_layout
                self.controls_frame.setLayout(self.controls_layout)
                if old_layout:
                    old_layout.deleteLater()
                    
        super().resizeEvent(event)

    def start_unlock(self):
        self.is_registering = False
        self.clear_inputs()
        self.status_label.setText("Scanning face...")
        self.status_label.setStyleSheet("color: #3498db; font-size: 12px;")
        self.status_bar.showMessage("Scanning for facial recognition...")
        
        # Reset access notification times to allow new notifications
        self.access_denied_time = QDateTime.currentDateTime().addSecs(-10)
        self.access_granted_time = QDateTime.currentDateTime().addSecs(-10)
        
        # Change button appearance to show active state
        self.unlockButton.setStyleSheet("""
            QPushButton {
                background-color: #2980b9;
                color: white;
                padding: 12px;
                border-radius: 8px;
                border: none;
            }
        """)
        QTimer.singleShot(2000, self.reset_unlock_button)

    def reset_unlock_button(self):
        self.unlockButton.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 12px;
                border-radius: 8px;
                border: none;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #2471a3;
            }
        """)

    def clear_inputs(self):
        self.nameInput.clear()
        self.idInput.clear()

    def take_photo(self):
        name = self.nameInput.text().strip()
        unique_id = self.idInput.text().strip()

        if not name or not unique_id:
            self.show_warning("Missing Information", "Please enter both Name and Unique ID to register.")
            return

        self.status_bar.showMessage("Capturing face for registration...")
        
        # Visual feedback
        self.takePhotoButton.setStyleSheet("""
            QPushButton {
                background-color: #1e7e34;
                color: white;
                padding: 12px;
                border-radius: 8px;
                border: none;
            }
        """)
        QTimer.singleShot(500, self.process_registration_photo)

    def process_registration_photo(self):
        name = self.nameInput.text().strip()
        unique_id = self.idInput.text().strip()
        
        ret, frame = self.capture.read()
        if ret:
            # Flip the frame horizontally for a more natural view
            frame = cv2.flip(frame, 1)
            
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)

            if len(faces) == 0:
                self.show_warning("Face Detection Error", "No human face detected. Please position yourself properly in front of the camera.")
                self.reset_register_button()
                return

            # Check if user ID already exists
            for folder in os.listdir(self.user_data_dir):
                if folder.startswith(unique_id + "_"):
                    self.show_warning("ID Already Exists", f"The ID '{unique_id}' is already registered. Please use a different ID.")
                    self.reset_register_button()
                    return

            user_folder = os.path.join(self.user_data_dir, f"{unique_id}_{name}")
            os.makedirs(user_folder, exist_ok=True)
            img_path = os.path.join(user_folder, 'face.jpg')
            cv2.imwrite(img_path, frame)
            
            self.show_success("Registration Successful", f"User '{name}' has been registered successfully with ID: {unique_id}")
            self.clear_inputs()
            self.status_bar.showMessage(f"User {name} registered successfully with ID: {unique_id}")
        
        self.reset_register_button()

    def reset_register_button(self):
        self.takePhotoButton.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                padding: 12px;
                border-radius: 8px;
                border: none;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:pressed {
                background-color: #1e7e34;
            }
        """)

    def update_frame(self):
        ret, frame = self.capture.read()
        if ret:
            # Flip the frame horizontally for a more natural view
            frame = cv2.flip(frame, 1)
            
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)

            # Draw detection rectangle and indication
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(frame, "Face Detected", (x, y-10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

            # Only attempt face verification if there are faces detected
            if len(faces) > 0:
                self.verify_face(frame)

            # Convert to QImage and display - with fixed size
            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
            
            # Create a scaled pixmap with fixed size
            fixed_pixmap = QPixmap.fromImage(qt_image).scaled(
                self.display_width, self.display_height,
                Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            self.label.setPixmap(fixed_pixmap)

    def verify_face(self, frame):
        user_folders = os.listdir(self.user_data_dir)
        if not user_folders:
            # Only show notification if cooldown period has passed
            current_time = QDateTime.currentDateTime()
            if current_time.secsTo(self.access_denied_time) <= -self.cooldown_seconds:
                self.update_status_only("No registered users found. Please register first.", "denied")
                self.access_denied_time = current_time
            return
            
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        face_found = False

        for folder in user_folders:
            face_path = os.path.join(self.user_data_dir, folder, 'face.jpg')
            if not os.path.exists(face_path):
                continue
                
            stored_img = cv2.imread(face_path, cv2.IMREAD_GRAYSCALE)
            if stored_img is not None:
                res = cv2.matchTemplate(gray, stored_img, cv2.TM_CCOEFF_NORMED)
                threshold = 0.6
                if (res >= threshold).any():
                    user_name = folder.split('_', 1)[1] if '_' in folder else "Unknown"
                    
                    # Only show access granted if cooldown period has passed
                    current_time = QDateTime.currentDateTime()
                    if current_time.secsTo(self.access_granted_time) <= -self.cooldown_seconds:
                        self.show_access_granted(f"Welcome, {user_name}! Access Granted.")
                        self.access_granted_time = current_time
                    else:
                        # Just update status without popup
                        self.update_status_only(f"Welcome, {user_name}! Access Granted.", "granted")
                        
                    face_found = True
                    break

        if not face_found:
            # Only show access denied if cooldown period has passed
            current_time = QDateTime.currentDateTime()
            if current_time.secsTo(self.access_denied_time) <= -self.cooldown_seconds:
                self.update_status_only("Unrecognized face. Access denied.", "denied")
                self.access_denied_time = current_time

    def update_status_only(self, message, status_type):
        """Update status without showing popup"""
        if status_type == "granted":
            self.status_label.setText("Access Granted")
            self.status_label.setStyleSheet("color: #28a745; font-weight: bold; font-size: 14px;")
            self.status_bar.showMessage(message)
        else:  # denied
            self.status_label.setText("Access Denied")
            self.status_label.setStyleSheet("color: #dc3545; font-weight: bold; font-size: 14px;")
            self.status_bar.showMessage(message)
            
        # Reset after delay
        QTimer.singleShot(3000, self.reset_status)

    def show_warning(self, title, message):
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #22252D;
                color: #F0F0F0;
            }
            QLabel {
                color: #F0F0F0;
                font-size: 14px;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                min-width: 100px;
            }
        """)
        msg.exec_()

    def show_success(self, title, message):
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #22252D;
                color: #F0F0F0;
            }
            QLabel {
                color: #F0F0F0;
                font-size: 14px;
            }
            QPushButton {
                background-color: #28a745;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                min-width: 100px;
            }
        """)
        msg.exec_()

    def show_access_granted(self, message):
        self.status_label.setText("Access Granted")
        self.status_label.setStyleSheet("color: #28a745; font-weight: bold; font-size: 14px;")
        self.status_bar.showMessage("Access Granted! Door unlocked.")
        
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Access Granted")
        msg.setText(message)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #22252D;
                color: #F0F0F0;
            }
            QLabel {
                color: #F0F0F0;
                font-size: 14px;
            }
            QPushButton {
                background-color: #28a745;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                min-width: 100px;
            }
        """)
        msg.exec_()
        
        # Reset after delay
        QTimer.singleShot(3000, self.reset_status)

    def reset_status(self):
        self.status_label.setText("Ready to scan")
        self.status_label.setStyleSheet("color: #F0F0F0; font-size: 12px;")
        self.status_bar.showMessage("System ready. Camera activated.")

    def closeEvent(self, event):
        reply = QMessageBox.question(
            self, "Exit Confirmation",
            "Are you sure you want to exit the application?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.capture.release()
            cv2.destroyAllWindows()
            event.accept()
        else:
            event.ignore()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")  # More consistent cross-platform look
    window = FaceDetectionApp()
    window.show()
    sys.exit(app.exec_())