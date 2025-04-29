import sys
import cv2
import os
import numpy as np
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QLineEdit, QScrollArea, QMessageBox, QGroupBox, QMainWindow, QStatusBar,
    QFrame, QSizePolicy, QProgressBar
)
from PyQt5.QtGui import QImage, QPixmap, QFont, QIcon, QColor
from PyQt5.QtCore import QTimer, Qt, QSize, QDateTime
import face_recognition  


class FaceDetectionApp(QMainWindow):
    def __init__(self):
        super().__init__()

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

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setCentralWidget(self.scroll_area)
        
        self.central_widget = QWidget()
        self.scroll_area.setWidget(self.central_widget)
        
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.setStyleSheet("background-color: #1A1D24; color: #F0F0F0; padding: 5px;")
        self.status_bar.showMessage("System ready. Camera activated.")

        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(15)

        self.header_frame = QFrame()
        self.header_frame.setStyleSheet("background-color: #1A1D24; border-radius: 10px; padding: 5px;")
        self.header_layout = QHBoxLayout(self.header_frame)
        
        self.header_label = QLabel("FACIAL RECOGNITION SECURITY")
        self.header_label.setFont(QFont("Arial", 16, QFont.Bold))
        self.header_label.setStyleSheet("color: #3498db;")
        self.header_label.setAlignment(Qt.AlignCenter)
        
        self.header_layout.addWidget(self.header_label)
        self.main_layout.addWidget(self.header_frame)

        self.camera_frame = QFrame()
        self.camera_frame.setStyleSheet("""
            background-color: #1A1D24;
            border: 2px solid #3498db;
            border-radius: 10px;
            padding: 10px;
        """)
        self.camera_layout = QVBoxLayout(self.camera_frame)
        
        self.camera_title = QLabel("CAMERA FEED")
        self.camera_title.setAlignment(Qt.AlignCenter)
        self.camera_title.setFont(QFont("Arial", 12, QFont.Bold))
        self.camera_title.setStyleSheet("color: #3498db; background: none; border: none;")
        
        self.camera_container = QWidget()
        self.camera_container.setFixedSize(640, 480) 
        self.camera_container_layout = QVBoxLayout(self.camera_container)
        self.camera_container_layout.setContentsMargins(0, 0, 0, 0)
        
        self.label = QLabel()
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("border: none; background: transparent;")
        self.camera_container_layout.addWidget(self.label)
        
        self.camera_wrapper = QHBoxLayout()
        self.camera_wrapper.addStretch()
        self.camera_wrapper.addWidget(self.camera_container)
        self.camera_wrapper.addStretch()
        
        self.camera_layout.addWidget(self.camera_title)
        self.camera_layout.addLayout(self.camera_wrapper)
        
        self.main_layout.addWidget(self.camera_frame)
        
        self.confidence_frame = QFrame()
        self.confidence_frame.setStyleSheet("""
            background-color: #1A1D24;
            border-radius: 10px;
            padding: 5px;
        """)
        self.confidence_layout = QHBoxLayout(self.confidence_frame)
        
        self.confidence_label = QLabel("Match Confidence: ")
        self.confidence_label.setStyleSheet("color: #F0F0F0;")
        
        self.confidence_bar = QProgressBar()
        self.confidence_bar.setRange(0, 100)
        self.confidence_bar.setValue(0)
        self.confidence_bar.setTextVisible(True)
        self.confidence_bar.setFormat("%p%")
        self.confidence_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #555;
                border-radius: 5px;
                text-align: center;
                background-color: #2C303A;
                height: 20px;
                color: white;
            }
            QProgressBar::chunk {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, 
                                              stop:0 #dc3545, stop:0.5 #ffc107, stop:1 #28a745);
                border-radius: 5px;
            }
        """)
        
        self.confidence_layout.addWidget(self.confidence_label)
        self.confidence_layout.addWidget(self.confidence_bar)
        
        self.main_layout.addWidget(self.confidence_frame)
        
        self.controls_frame = QFrame()
        self.controls_layout = QHBoxLayout(self.controls_frame)
        self.controls_layout.setSpacing(20)
        
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

        self.controls_layout.addWidget(self.registration_group)
        self.controls_layout.addWidget(self.unlock_group)
        
        self.main_layout.addWidget(self.controls_frame)

        self.main_layout.addStretch()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.capture = cv2.VideoCapture(0)
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )

        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        self.is_registering = False
        self.user_data_dir = 'user_data'
        self.embeddings_dir = 'face_embeddings'
        os.makedirs(self.user_data_dir, exist_ok=True)
        os.makedirs(self.embeddings_dir, exist_ok=True)

        self.access_denied_time = QDateTime.currentDateTime().addSecs(-10)  # Initialize to past time
        self.access_granted_time = QDateTime.currentDateTime().addSecs(-10)  # Initialize to past time
        self.cooldown_seconds = 5  

        self.face_locations = []
        self.face_encodings = []
        self.match_threshold = 0.6  
        self.process_every_n_frames = 3
        self.frame_count = 0
        self.current_recognition_confidence = 0
        self.recognition_mode = False
        self.current_frame = None
        
        self.known_face_encodings = []
        self.known_face_names = []
        self.known_face_ids = []
        
        self.load_face_encodings()
        
        self.timer.start(30)
        
        self.display_width = 640
        self.display_height = 480

    def load_face_encodings(self):
        """Load all saved face encodings from the embeddings directory"""
        self.known_face_encodings = []
        self.known_face_names = []
        self.known_face_ids = []
        
        if not os.path.exists(self.embeddings_dir):
            return
            
        for filename in os.listdir(self.embeddings_dir):
            if filename.endswith('.npy'):
                try:
                    user_id, name = os.path.splitext(filename)[0].split('_', 1)
                    encoding_path = os.path.join(self.embeddings_dir, filename)
                    
                    face_encoding = np.load(encoding_path)
                    self.known_face_encodings.append(face_encoding)
                    self.known_face_names.append(name)
                    self.known_face_ids.append(user_id)
                    
                    print(f"Loaded face encoding for {name} (ID: {user_id})")
                except Exception as e:
                    print(f"Error loading encoding {filename}: {e}")
        
        print(f"Loaded {len(self.known_face_encodings)} face encodings")

    def on_resize_event(self, event):
        if self.width() < 800:
            if isinstance(self.controls_layout, QHBoxLayout):
                self.registration_group.setParent(None)
                self.unlock_group.setParent(None)
                
                new_layout = QVBoxLayout()
                new_layout.addWidget(self.registration_group)
                new_layout.addWidget(self.unlock_group)
                
                old_layout = self.controls_layout
                self.controls_layout = new_layout
                self.controls_frame.setLayout(self.controls_layout)
                if old_layout:
                    old_layout.deleteLater()
        else:
            if isinstance(self.controls_layout, QVBoxLayout):
                self.registration_group.setParent(None)
                self.unlock_group.setParent(None)
                
                new_layout = QHBoxLayout()
                new_layout.addWidget(self.registration_group)
                new_layout.addWidget(self.unlock_group)
                
                old_layout = self.controls_layout
                self.controls_layout = new_layout
                self.controls_frame.setLayout(self.controls_layout)
                if old_layout:
                    old_layout.deleteLater()
                    
        super().resizeEvent(event)

    def start_unlock(self):
        self.is_registering = False
        self.recognition_mode = True
        self.clear_inputs()
        self.status_label.setText("Scanning face...")
        self.status_label.setStyleSheet("color: #3498db; font-size: 12px;")
        self.status_bar.showMessage("Scanning for facial recognition...")
        
        self.access_denied_time = QDateTime.currentDateTime().addSecs(-10)
        self.access_granted_time = QDateTime.currentDateTime().addSecs(-10)
        
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
        self.is_registering = True
        
        self.takePhotoButton.setStyleSheet("""
            QPushButton {
                background-color: #1e7e34;
                color: white;
                padding: 12px;
                border-radius: 8px;
                border: none;
            }
        """)
        QTimer.singleShot(500, lambda: self.process_registration_photo(name, unique_id))

    def process_registration_photo(self, name, unique_id):
        """Process and register a face with improved face recognition"""
        try:
            ret, frame = self.capture.read()
            if not ret:
                self.show_warning("Camera Error", "Failed to capture image from camera.")
                self.reset_register_button()
                return
                
            frame = cv2.flip(frame, 1)
            
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            face_locations = face_recognition.face_locations(rgb_frame)
            
            if not face_locations:
                self.show_warning("Face Detection Error", "No face detected. Please position yourself properly in front of the camera.")
                self.reset_register_button()
                return
                
            if len(face_locations) > 1:
                self.show_warning("Multiple Faces", "Multiple faces detected. Please ensure only one person is in frame.")
                self.reset_register_button()
                return
                
            embedding_path = os.path.join(self.embeddings_dir, f"{unique_id}_{name}.npy")
            if os.path.exists(embedding_path):
                self.show_warning("ID Already Exists", f"The ID '{unique_id}' is already registered. Please use a different ID.")
                self.reset_register_button()
                return
                
            face_encoding = face_recognition.face_encodings(rgb_frame, face_locations)[0]
            
            user_folder = os.path.join(self.user_data_dir, f"{unique_id}_{name}")
            os.makedirs(user_folder, exist_ok=True)
            
            img_path = os.path.join(user_folder, f'face_{datetime.now().strftime("%Y%m%d_%H%M%S")}.jpg')
            cv2.imwrite(img_path, frame)
            
            np.save(embedding_path, face_encoding)
            
            self.known_face_encodings.append(face_encoding)
            self.known_face_names.append(name)
            self.known_face_ids.append(unique_id)
            
            self.show_success("Registration Successful", 
                              f"User '{name}' has been registered successfully with ID: {unique_id}\n\n"
                              f"The system now has {len(self.known_face_encodings)} registered users.")
                              
            self.clear_inputs()
            self.status_bar.showMessage(f"User {name} registered successfully with ID: {unique_id}")
            
        except Exception as e:
            self.show_warning("Registration Error", f"An error occurred during registration: {str(e)}")
            print(f"Registration error: {e}")
            
        self.is_registering = False
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
        if not ret:
            return
            
        frame = cv2.flip(frame, 1)
        self.current_frame = frame.copy()
        
        self.frame_count = (self.frame_count + 1) % self.process_every_n_frames
        
        self.display_frame(frame)
        
        if self.frame_count != 0 and not self.is_registering and not self.recognition_mode:
            return
            
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        if self.is_registering or self.recognition_mode:
            self.face_locations = face_recognition.face_locations(rgb_frame)
            
            for (top, right, bottom, left) in self.face_locations:
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                
                label = "Face Detected"
                y_pos = max(top - 10, 0)
                cv2.putText(frame, label, (left, y_pos), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            if self.recognition_mode and self.face_locations:
                self.face_encodings = face_recognition.face_encodings(rgb_frame, self.face_locations)
                
                if not self.known_face_encodings:
                    self.update_status_only("No registered users found. Please register first.", "denied")
                    self.recognition_mode = False
                    return
                
                self.verify_face()
            
            self.display_frame(frame)

    def display_frame(self, frame):
        """Convert an OpenCV frame to QPixmap and display it"""
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        
        fixed_pixmap = QPixmap.fromImage(qt_image).scaled(
            self.display_width, self.display_height,
            Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        self.label.setPixmap(fixed_pixmap)

    def verify_face(self):
        """Improved face verification using face_recognition"""
        if not self.face_encodings or not self.known_face_encodings:
            return
            
        best_match_name = None
        best_match_id = None
        best_match_confidence = 0
        
        for face_encoding in self.face_encodings:
            face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
            
            if len(face_distances) > 0:
                best_match_index = np.argmin(face_distances)
                min_distance = face_distances[best_match_index]
                
                confidence = max(0, min(100, (1 - min_distance) * 100))
                
                self.confidence_bar.setValue(int(confidence))
                self.current_recognition_confidence = confidence
                
                if min_distance <= self.match_threshold:
                    best_match_name = self.known_face_names[best_match_index]
                    best_match_id = self.known_face_ids[best_match_index]
                    best_match_confidence = confidence
        
        current_time = QDateTime.currentDateTime()
        
        if best_match_name and best_match_confidence >= (1 - self.match_threshold) * 100:
            # Check cooldown timer for access granted message
            if current_time.secsTo(self.access_granted_time) <= -self.cooldown_seconds:
                access_message = f"Welcome, {best_match_name}! Access Granted. (Confidence: {best_match_confidence:.1f}%)"
                self.show_access_granted(access_message)
                self.access_granted_time = current_time
                self.recognition_mode = False  # Turn off recognition mode after successful authentication
            else:
                self.update_status_only(f"Welcome, {best_match_name}! Access Granted.", "granted")
        else:
            if current_time.secsTo(self.access_denied_time) <= -self.cooldown_seconds:
                if self.face_locations:  
                    confidence_msg = ""
                    if self.current_recognition_confidence > 0:
                        confidence_msg = f" (Confidence: {self.current_recognition_confidence:.1f}% - Below threshold)"
                    
                    self.update_status_only(f"Unrecognized face. Access denied.{confidence_msg}", "denied")
                    self.access_denied_time = current_time

    def update_status_only(self, message, status_type):
        """Update status without showing popup"""
        if status_type == "granted":
            self.status_label.setText("Access Granted")
            self.status_label.setStyleSheet("color: #28a745; font-weight: bold; font-size: 14px;")
            self.status_bar.showMessage(message)
        else:  
            self.status_label.setText("Access Denied")
            self.status_label.setStyleSheet("color: #dc3545; font-weight: bold; font-size: 14px;")
            self.status_bar.showMessage(message)
            
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
        
        QTimer.singleShot(3000, self.reset_status)

    def reset_status(self):
        self.status_label.setText("Ready to scan")
        self.status_label.setStyleSheet("color: #F0F0F0; font-size: 12px;")
        self.status_bar.showMessage("System ready. Camera activated.")
        self.recognition_mode = False
        self.confidence_bar.setValue(0)

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
    app.setStyle("Fusion")  
    window = FaceDetectionApp()
    window.show()
    sys.exit(app.exec_())