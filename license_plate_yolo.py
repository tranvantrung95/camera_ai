"""
Module phát hiện biển số xe bằng YOLOv8
Sử dụng model pre-trained cho license plate detection
"""
import cv2
import numpy as np
from typing import Optional, Dict

class YOLOLicensePlateDetector:
    def __init__(self, config):
        """Khởi tạo YOLO License Plate Detector"""
        self.config = config
        
        try:
            from ultralytics import YOLO
            
            # Tải model YOLO cho license plate
            # Option 1: Model từ Roboflow (rất tốt cho biển số)
            model_path = config.get('license_plate', {}).get('yolo_model', 'license_plate_detector.pt')
            
            print("⬇️  Đang tải YOLO License Plate model...")
            self.model = YOLO(model_path)
            print("✅ YOLO License Plate Detector đã sẵn sàng")
            
            # Khởi tạo OCR cho đọc text
            self.ocr_engine = None
            if config.get('ocr', {}).get('enabled', False):
                engine = config['ocr'].get('engine', 'paddleocr')
                if engine == 'paddleocr':
                    try:
                        from paddleocr import PaddleOCR
                        self.ocr = PaddleOCR(use_angle_cls=True, lang='en')
                        self.ocr_engine = 'paddle'
                        print("✅ PaddleOCR đã sẵn sàng cho đọc text")
                    except ImportError:
                        print("⚠️  PaddleOCR chưa cài đặt")
                        self.ocr_engine = None
                elif engine == 'easyocr':
                    try:
                        import easyocr
                        self.ocr = easyocr.Reader(['en'], gpu=False)
                        self.ocr_engine = 'easy'
                        print("✅ EasyOCR đã sẵn sàng cho đọc text")
                    except ImportError:
                        print("⚠️  EasyOCR chưa cài đặt")
                        self.ocr_engine = None
                        
        except ImportError:
            print("❌ Ultralytics YOLO chưa cài đặt. Chạy: pip install ultralytics")
            raise
    
    def detect(self, vehicle_img):
        """
        Phát hiện biển số trong ảnh xe bằng YOLO
        Returns: dict with 'text', 'confidence', 'bbox'
        """
        if vehicle_img is None or vehicle_img.size == 0:
            return None
        
        h, w = vehicle_img.shape[:2]
        if h < 30 or w < 30:
            return None
        
        # Phát hiện xe/object bằng YOLO (tạm thời dùng base model)
        # TODO: Thay bằng model license plate chuyên dụng
        results = self.model(vehicle_img, verbose=False, classes=[2, 3, 5, 7])  # car, motorcycle, bus, truck
        
        if len(results) == 0 or len(results[0].boxes) == 0:
            # Nếu không phát hiện được, thử OCR trực tiếp trên toàn bộ ảnh
            if self.ocr_engine:
                text = self.extract_text_ocr(vehicle_img)
                if text:
                    print(f"🔍 OCR đọc được (không có YOLO detection): '{text}'")
                    # Ước lượng vị trí biển số (thường ở 60% từ trên)
                    h_img, w_img = vehicle_img.shape[:2]
                    est_bbox = (int(w_img * 0.1), int(h_img * 0.6), int(w_img * 0.8), int(h_img * 0.25))
                    return {
                        'text': text,
                        'confidence': 0.7,
                        'bbox': est_bbox
                    }
            return None
        
        # Lấy detection có confidence cao nhất (giả định là vùng có biển số)
        boxes = results[0].boxes
        confidences = boxes.conf.cpu().numpy()
        best_idx = np.argmax(confidences)
        
        box = boxes.xyxy[best_idx].cpu().numpy()
        confidence = float(confidences[best_idx])
        
        # Chuyển đổi tọa độ
        x1, y1, x2, y2 = map(int, box)
        plate_bbox = (x1, y1, x2 - x1, y2 - y1)
        
        # Crop vùng biển số
        plate_img = vehicle_img[y1:y2, x1:x2]
        
        # Đọc text bằng OCR
        plate_text = None
        if self.ocr_engine and plate_img.shape[0] > 10 and plate_img.shape[1] > 10:
            plate_text = self.extract_text_ocr(plate_img)
        
        if plate_text:
            print(f"🎯 YOLO phát hiện biển số: '{plate_text}' (confidence: {confidence:.2f})")
            return {
                'text': plate_text,
                'confidence': confidence,
                'bbox': plate_bbox
            }
        else:
            # Nếu không đọc được text, vẫn trả về bbox
            print(f"🎯 YOLO phát hiện biển số nhưng không đọc được text (confidence: {confidence:.2f})")
            return {
                'text': 'DETECTED',
                'confidence': confidence,
                'bbox': plate_bbox
            }
    
    def extract_text_ocr(self, plate_img):
        """Trích xuất text từ ảnh biển số bằng OCR"""
        if self.ocr_engine == 'paddle':
            try:
                result = self.ocr.ocr(plate_img)
                if result and result[0]:
                    texts = [line[1][0] for line in result[0]]
                    full_text = ' '.join(texts)
                    return self.clean_plate_text(full_text)
            except Exception as e:
                print(f"Lỗi PaddleOCR: {e}")
                return None
        elif self.ocr_engine == 'easy':
            try:
                result = self.ocr.readtext(plate_img)
                if result:
                    texts = [text[1] for text in result]
                    full_text = ' '.join(texts)
                    return self.clean_plate_text(full_text)
            except Exception as e:
                print(f"Lỗi EasyOCR: {e}")
                return None
        return None
    
    def clean_plate_text(self, text):
        """Làm sạch text biển số"""
        if not text:
            return None
        
        import re
        # Loại bỏ ký tự đặc biệt, giữ chữ, số, dấu gạch ngang, chấm, khoảng trắng
        text = re.sub(r'[^A-Z0-9\-\.\s]', '', text.upper())
        
        # Sửa lỗi OCR phổ biến
        text = text.replace('O', '0').replace('I', '1').replace('S', '5')
        text = text.replace('B', '8').replace('Z', '2').replace('Q', '0')
        
        text = text.strip()
        
        # Kiểm tra độ dài hợp lệ
        if len(text) < 5 or len(text) > 15:
            return None
        
        # Phải có ít nhất 1 chữ và 3 số
        has_letter = any(c.isalpha() for c in text)
        digit_count = sum(c.isdigit() for c in text)
        
        if not (has_letter and digit_count >= 3):
            return None
        
        return text

