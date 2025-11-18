"""
Camera AI - Hệ thống phát hiện người và xe với YOLOv11
"""
import cv2
import yaml
import torch
from datetime import datetime
import os
import sqlite3
import numpy as np
from pathlib import Path
from ultralytics import YOLO

# Chọn detector dựa trên config
try:
    with open('config.yaml', 'r', encoding='utf-8') as f:
        _config = yaml.safe_load(f)
    
    if _config.get('license_plate', {}).get('use_yolo', False):
        from license_plate_yolo import YOLOLicensePlateDetector as LicensePlateDetector
        print("🎯 Sử dụng YOLO License Plate Detector")
    else:
        from license_plate import LicensePlateDetector
        print("📝 Sử dụng Contour License Plate Detector")
except Exception as e:
    from license_plate import LicensePlateDetector
    print(f"⚠️  Lỗi khi load config, dùng detector mặc định: {e}")

# Import FFMPEG camera nếu là RTSP
try:
    from ffmpeg_camera import FFMPEGCamera
    FFMPEG_AVAILABLE = True
except ImportError:
    FFMPEG_AVAILABLE = False
    print("⚠️  FFMPEG camera module không có, sẽ dùng OpenCV")

class CameraAI:
    def __init__(self, config_path='config.yaml'):
        """Khởi tạo Camera AI System"""
        # Load config
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        print("🚀 Đang khởi động Camera AI System...")
        
        # Khởi tạo models
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print(f"📱 Sử dụng device: {self.device}")
        
        # Load YOLO models
        model_path = self.config['detection']['person_model']
        if not os.path.exists(model_path):
            print(f"⬇️  Đang tải YOLOv11 model...")
            self.model = YOLO('yolo11n.pt')  # Tự động download
            os.makedirs('models', exist_ok=True)
            # Model sẽ được tải tự động
        else:
            self.model = YOLO(model_path)
        
        # Khởi tạo License Plate Detector
        self.plate_detector = LicensePlateDetector(self.config)
        
        # Khởi tạo camera
        self.cap = None
        self.setup_camera()
        
        # Khởi tạo database
        self.setup_database()
        
        # Recording settings
        self.video_writer = None
        self.current_video_path = None
        
        # Thống kê
        self.stats = {
            'total_persons': 0,
            'total_vehicles': 0,
            'total_plates': 0,
            'last_detection': None
        }
        
        print("✅ Camera AI System đã sẵn sàng!")
    
    def setup_camera(self):
        """Thiết lập kết nối camera"""
        source = self.config['camera']['source']
        
        # Kiểm tra nếu là RTSP URL
        is_rtsp = isinstance(source, str) and source.startswith('rtsp://')
        
        if is_rtsp and FFMPEG_AVAILABLE:
            # Dùng FFMPEG camera cho RTSP (hoạt động tốt hơn trên macOS)
            print(f"📡 Phát hiện RTSP stream, dùng FFMPEG backend...")
            self.cap = FFMPEGCamera(
                source,
                width=self.config['camera']['width'],
                height=self.config['camera']['height'],
                fps=self.config['camera']['fps']
            )
            
            if not self.cap.start():
                raise Exception(f"❌ Không thể kết nối RTSP stream: {source}")
        else:
            # Dùng OpenCV cho webcam hoặc RTSP (nếu FFMPEG không có)
            if is_rtsp:
                # Dùng FFMPEG backend cho RTSP
                self.cap = cv2.VideoCapture(source, cv2.CAP_FFMPEG)
                
                # Set buffer size nếu có trong config (giảm độ trễ)
                if 'buffer_size' in self.config['camera']:
                    self.cap.set(cv2.CAP_PROP_BUFFERSIZE, self.config['camera']['buffer_size'])
                    print(f"📦 Buffer size: {self.config['camera']['buffer_size']}")
            else:
                self.cap = cv2.VideoCapture(source)
            
            if not self.cap.isOpened():
                if is_rtsp:
                    print(f"⚠️  OpenCV không kết nối được RTSP, thử cài FFMPEG camera module")
                raise Exception(f"❌ Không thể mở camera: {source}")
            
            # Set resolution
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.config['camera']['width'])
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config['camera']['height'])
            self.cap.set(cv2.CAP_PROP_FPS, self.config['camera']['fps'])
        
        print(f"📹 Camera đã kết nối: {source}")
    
    def setup_database(self):
        """Tạo database để lưu log"""
        db_path = self.config['database']['path']
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Bảng detections
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS detections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                type TEXT,
                confidence REAL,
                bbox TEXT,
                snapshot_path TEXT,
                license_plate TEXT,
                vehicle_type TEXT,
                notes TEXT
            )
        ''')
        
        # Migration: Thêm cột vehicle_type nếu chưa có
        try:
            cursor.execute("SELECT vehicle_type FROM detections LIMIT 1")
        except sqlite3.OperationalError:
            print("🔧 Đang migrate database: thêm cột vehicle_type...")
            cursor.execute("ALTER TABLE detections ADD COLUMN vehicle_type TEXT")
            conn.commit()
            print("✅ Migration hoàn tất!")
        
        # Bảng statistics
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS statistics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE,
                total_persons INTEGER,
                total_vehicles INTEGER,
                total_plates INTEGER
            )
        ''')
        
        conn.commit()
        conn.close()
        print("💾 Database đã sẵn sàng")
    
    def start_recording(self):
        """Bắt đầu ghi video"""
        if not self.config['recording']['enabled']:
            return
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.current_video_path = os.path.join(
            self.config['recording']['save_path'],
            f"recording_{timestamp}.mp4"
        )
        
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        fps = self.config['camera']['fps']
        size = (self.config['camera']['width'], self.config['camera']['height'])
        
        self.video_writer = cv2.VideoWriter(
            self.current_video_path, fourcc, fps, size
        )
        print(f"🎥 Bắt đầu ghi: {self.current_video_path}")
    
    def save_snapshot(self, frame, detection_type, extra_info=""):
        """Lưu ảnh snapshot"""
        if not self.config['recording']['save_snapshots']:
            return None
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        filename = f"{detection_type}_{timestamp}.jpg"
        filepath = os.path.join(
            self.config['recording']['snapshot_path'],
            filename
        )
        
        cv2.imwrite(filepath, frame)
        return filepath
    
    def get_vehicle_type(self, class_id):
        """Phân loại xe dựa trên YOLO class ID"""
        # COCO dataset classes:
        # 1: bicycle, 2: car, 3: motorcycle, 5: bus, 7: truck
        vehicle_types = {
            1: 'Xe đạp',
            2: 'Ô tô',
            3: 'Xe máy',
            5: 'Xe buýt',
            7: 'Xe tải'
        }
        return vehicle_types.get(class_id, 'Xe khác')
    
    def log_detection(self, det_type, confidence, bbox, snapshot_path=None, plate=None, vehicle_type=None):
        """Ghi log vào database"""
        conn = sqlite3.connect(self.config['database']['path'])
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO detections (type, vehicle_type, confidence, bbox, snapshot_path, license_plate)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (det_type, vehicle_type, confidence, str(bbox), snapshot_path, plate))
        
        conn.commit()
        conn.close()
    
    def detect_frame(self, frame):
        """Phát hiện objects trong frame"""
        results = self.model(frame, verbose=False)
        
        detections = {
            'persons': [],
            'vehicles': [],
            'plates': []
        }
        
        for result in results:
            boxes = result.boxes
            for box in boxes:
                cls = int(box.cls[0])
                conf = float(box.conf[0])
                bbox = box.xyxy[0].cpu().numpy()
                
                # Phát hiện người
                if cls in self.config['detection']['person_classes']:
                    if conf >= self.config['detection']['person_confidence']:
                        detections['persons'].append({
                            'bbox': bbox,
                            'confidence': conf
                        })
                        self.stats['total_persons'] += 1
                
                # Phát hiện xe
                elif cls in self.config['detection']['vehicle_classes']:
                    if conf >= self.config['detection']['vehicle_confidence']:
                        vehicle_type = self.get_vehicle_type(cls)
                        detections['vehicles'].append({
                            'bbox': bbox,
                            'confidence': conf,
                            'class': cls,
                            'vehicle_type': vehicle_type
                        })
                        self.stats['total_vehicles'] += 1
                        
                        # Crop vùng xe để phát hiện biển số (mở rộng thêm 10% để bao gồm biển số)
                        x1, y1, x2, y2 = map(int, bbox)
                        h_frame, w_frame = frame.shape[:2]
                        
                        # Mở rộng vùng crop
                        expand_ratio = 0.1
                        w_box = x2 - x1
                        h_box = y2 - y1
                        x1_exp = max(0, int(x1 - w_box * expand_ratio))
                        y1_exp = max(0, int(y1 - h_box * expand_ratio))
                        x2_exp = min(w_frame, int(x2 + w_box * expand_ratio))
                        y2_exp = min(h_frame, int(y2 + h_box * expand_ratio))
                        
                        vehicle_crop = frame[y1_exp:y2_exp, x1_exp:x2_exp]
                        
                        # Phát hiện biển số
                        plate_result = self.plate_detector.detect(vehicle_crop)
                        if plate_result:
                            # Chuyển đổi tọa độ biển số từ vehicle_crop sang frame gốc
                            plate_bbox_in_frame = None
                            if plate_result.get('bbox'):
                                px, py, pw, ph = plate_result['bbox']
                                # Tọa độ trong frame gốc
                                plate_x1 = x1_exp + px
                                plate_y1 = y1_exp + py
                                plate_x2 = plate_x1 + pw
                                plate_y2 = plate_y1 + ph
                                plate_bbox_in_frame = (plate_x1, plate_y1, plate_x2, plate_y2)
                            
                            detections['plates'].append({
                                'vehicle_bbox': bbox,
                                'plate_bbox': plate_bbox_in_frame,  # Tọa độ biển số trong frame
                                'plate_text': plate_result['text'],
                                'plate_confidence': plate_result['confidence']
                            })
                            self.stats['total_plates'] += 1
                            print(f"   ✅ Phát hiện biển số: {plate_result['text']} ({vehicle_type})")
        
        self.stats['last_detection'] = datetime.now()
        return detections
    
    def draw_detections(self, frame, detections):
        """Vẽ bounding boxes lên frame"""
        # Vẽ người
        for person in detections['persons']:
            x1, y1, x2, y2 = map(int, person['bbox'])
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            label = f"Person: {person['confidence']:.2f}"
            cv2.putText(frame, label, (x1, y1-10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        # Vẽ xe
        for vehicle in detections['vehicles']:
            x1, y1, x2, y2 = map(int, vehicle['bbox'])
            cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
            
            # Hiển thị loại xe và confidence
            vehicle_type = vehicle.get('vehicle_type', 'Xe')
            label = f"{vehicle_type}: {vehicle['confidence']:.2f}"
            
            # Vẽ nền cho text
            (text_w, text_h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
            cv2.rectangle(frame, (x1, y1-text_h-10), (x1+text_w, y1), (255, 0, 0), -1)
            cv2.putText(frame, label, (x1, y1-5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Vẽ biển số
        for plate in detections['plates']:
            # Vẽ khung vàng quanh biển số (nếu có tọa độ)
            if plate.get('plate_bbox'):
                px1, py1, px2, py2 = map(int, plate['plate_bbox'])
                # Khung vàng nổi bật cho biển số
                cv2.rectangle(frame, (px1, py1), (px2, py2), (0, 255, 255), 3)
                
                # Vẽ nền cho text biển số
                text = plate['plate_text']
                font_scale = 0.8
                thickness = 2
                (text_w, text_h), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness)
                
                # Nền đen cho text
                cv2.rectangle(frame, (px1, py1-text_h-10), (px1+text_w+10, py1), (0, 0, 0), -1)
                # Text vàng
                cv2.putText(frame, text, (px1+5, py1-5),
                           cv2.FONT_HERSHEY_SIMPLEX, font_scale, (0, 255, 255), thickness)
            else:
                # Nếu không có bbox biển số, vẽ text dưới xe
                x1, y1, x2, y2 = map(int, plate['vehicle_bbox'])
                text = f"Plate: {plate['plate_text']}"
                cv2.putText(frame, text, (x1, y2+20),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        
        # Thêm thống kê
        stats_text = f"Persons: {len(detections['persons'])} | Vehicles: {len(detections['vehicles'])} | Plates: {len(detections['plates'])}"
        cv2.putText(frame, stats_text, (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        return frame
    
    def run(self, show_preview=True):
        """Chạy hệ thống detection"""
        print("▶️  Bắt đầu phát hiện...")
        self.start_recording()
        
        try:
            while True:
                ret, frame = self.cap.read()
                if not ret:
                    print("⚠️  Không đọc được frame")
                    break
                
                # Phát hiện objects
                detections = self.detect_frame(frame)
                
                # Vẽ kết quả
                frame_display = self.draw_detections(frame.copy(), detections)
                
                # Ghi video
                if self.video_writer:
                    self.video_writer.write(frame_display)
                
                # Lưu snapshots nếu có detection
                if detections['persons'] or detections['vehicles']:
                    if self.config['recording']['save_snapshots']:
                        snapshot_path = self.save_snapshot(
                            frame_display, 
                            'detection'
                        )
                        
                        # Log vào database
                        for person in detections['persons']:
                            self.log_detection(
                                'person',
                                person['confidence'],
                                person['bbox'],
                                snapshot_path
                            )
                        
                        for vehicle in detections['vehicles']:
                            plate_text = None
                            # Tìm biển số tương ứng
                            for plate in detections['plates']:
                                if np.array_equal(plate['vehicle_bbox'], vehicle['bbox']):
                                    plate_text = plate['plate_text']
                                    break
                            
                            self.log_detection(
                                'vehicle',
                                vehicle['confidence'],
                                vehicle['bbox'],
                                snapshot_path,
                                plate_text
                            )
                
                # Hiển thị preview
                if show_preview:
                    cv2.imshow('Camera AI - Press Q to quit', frame_display)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
                
        except KeyboardInterrupt:
            print("\n⏹️  Dừng hệ thống...")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Dọn dẹp tài nguyên"""
        if self.cap:
            if hasattr(self.cap, 'release'):
                self.cap.release()
        if self.video_writer:
            self.video_writer.release()
        cv2.destroyAllWindows()
        print("🧹 Đã dọn dẹp tài nguyên")
    
    def get_stats(self):
        """Lấy thống kê"""
        return self.stats

if __name__ == '__main__':
    # Chạy camera AI
    camera = CameraAI()
    camera.run(show_preview=True)

