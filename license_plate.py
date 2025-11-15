"""
Module phát hiện và đọc biển số xe
"""
import cv2
import numpy as np
import re
from typing import Optional, Dict

class LicensePlateDetector:
    def __init__(self, config):
        """Khởi tạo License Plate Detector"""
        self.config = config
        self.ocr_enabled = config['ocr']['enabled']
        
        # Khởi tạo OCR engine
        if self.ocr_enabled:
            engine = config['ocr']['engine']
            if engine == 'paddleocr':
                try:
                    from paddleocr import PaddleOCR
                    self.ocr = PaddleOCR(
                        use_angle_cls=True,
                        lang='en'
                    )
                    self.ocr_engine = 'paddle'
                    print("✅ PaddleOCR đã sẵn sàng")
                except ImportError:
                    print("⚠️  PaddleOCR chưa cài đặt, dùng xử lý cơ bản")
                    self.ocr_engine = None
            elif engine == 'easyocr':
                try:
                    import easyocr
                    self.ocr = easyocr.Reader(['en'], gpu=False)
                    self.ocr_engine = 'easy'
                    print("✅ EasyOCR đã sẵn sàng")
                except ImportError:
                    print("⚠️  EasyOCR chưa cài đặt, dùng xử lý cơ bản")
                    self.ocr_engine = None
            else:
                self.ocr_engine = None
        else:
            self.ocr_engine = None
    
    def preprocess_plate(self, img):
        """Tiền xử lý ảnh biển số"""
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Áp dụng bilateral filter để giảm noise nhưng giữ edges
        blur = cv2.bilateralFilter(gray, 11, 17, 17)
        
        # Tăng contrast
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        enhanced = clahe.apply(blur)
        
        # Edge detection
        edges = cv2.Canny(enhanced, 30, 200)
        
        return gray, edges
    
    def find_plate_contours(self, edges):
        """Tìm contours có thể là biển số"""
        contours, _ = cv2.findContours(
            edges.copy(),
            cv2.RETR_TREE,
            cv2.CHAIN_APPROX_SIMPLE
        )
        
        # Sort theo diện tích
        contours = sorted(contours, key=cv2.contourArea, reverse=True)[:15]
        
        plate_candidates = []
        
        for contour in contours:
            # Tính perimeter
            peri = cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, 0.02 * peri, True)
            
            # Biển số có thể có 4 cạnh hoặc hình chữ nhật
            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = w / float(h)
            area = w * h
            
            # Biển số VN: tỷ lệ 2-5, diện tích tối thiểu 400 pixels
            if 1.5 <= aspect_ratio <= 5.5 and area >= 200:
                # Kiểm tra độ đầy của contour (solidity)
                hull = cv2.convexHull(contour)
                hull_area = cv2.contourArea(hull)
                if hull_area > 0:
                    solidity = float(area) / hull_area
                    # Biển số thường có solidity cao (hình chữ nhật đầy)
                    if solidity > 0.5:
                        plate_candidates.append((x, y, w, h))
        
        return plate_candidates
    
    def extract_text_ocr(self, img):
        """Trích xuất text từ ảnh bằng OCR"""
        if self.ocr_engine == 'paddle':
            try:
                result = self.ocr.ocr(img)
                if result and result[0]:
                    texts = [line[1][0] for line in result[0]]
                    full_text = ' '.join(texts)
                    return self.clean_plate_text(full_text)
            except Exception as e:
                print(f"Lỗi PaddleOCR: {e}")
                return None
        
        elif self.ocr_engine == 'easy':
            try:
                result = self.ocr.readtext(img)
                if result:
                    texts = [item[1] for item in result]
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
        
        # Chuyển về chữ hoa
        text = text.upper()
        
        # Loại bỏ ký tự đặc biệt, giữ chữ, số, dấu gạch ngang, dấu chấm, khoảng trắng
        text = re.sub(r'[^A-Z0-9\-\.\s]', '', text)
        
        # Sửa các lỗi OCR phổ biến
        # O -> 0, I -> 1, S -> 5, B -> 8, Z -> 2, Q -> 0
        text = text.replace('O', '0').replace('I', '1').replace('S', '5')
        text = text.replace('B', '8').replace('Z', '2').replace('Q', '0')
        
        # Loại bỏ khoảng trắng đầu/cuối
        text = text.strip()
        
        # Chuẩn hóa khoảng trắng (nhiều khoảng trắng -> 1 khoảng trắng)
        text = ' '.join(text.split())
        
        # Kiểm tra độ dài hợp lệ (biển số VN: 6-15 ký tự kể cả dấu)
        if len(text) < 6 or len(text) > 15:
            return None
        
        # Kiểm tra có ít nhất 1 chữ cái và 5 số
        text_clean = text.replace('-', '').replace('.', '').replace(' ', '')
        has_letter = any(c.isalpha() for c in text_clean)
        num_digits = sum(c.isdigit() for c in text_clean)
        
        if not (has_letter and num_digits >= 5):
            return None
            
        return text
    
    def detect(self, vehicle_img) -> Optional[Dict]:
        """
        Phát hiện và đọc biển số xe
        
        Args:
            vehicle_img: Ảnh vùng xe đã crop
            
        Returns:
            Dict chứa thông tin biển số hoặc None
        """
        if vehicle_img is None or vehicle_img.size == 0:
            return None
        
        h, w = vehicle_img.shape[:2]
        if h < 30 or w < 30:
            return None
        
        # CHIẾN LƯỢC MỚI: Thử OCR trực tiếp TRƯỚC (hiệu quả hơn cho video thực tế)
        if self.ocr_engine:
            # Resize để OCR tốt hơn
            if h < 100:
                scale = 100 / h
                vehicle_img_resized = cv2.resize(vehicle_img, None, fx=scale, fy=scale)
            else:
                vehicle_img_resized = vehicle_img
            
            # OCR trực tiếp trên toàn bộ vùng xe
            text = self.extract_text_ocr(vehicle_img_resized)
            
            # Kiểm tra text hợp lệ
            if text and self.validate_plate(text):
                # Tìm vị trí chính xác bằng contour
                gray, edges = self.preprocess_plate(vehicle_img)
                plate_candidates = self.find_plate_contours(edges)
                
                if plate_candidates:
                    x, y, w, h = plate_candidates[0]
                    return {
                        'text': text,
                        'confidence': 0.85,
                        'bbox': (x, y, w, h)
                    }
                else:
                    # Ước lượng vị trí biển số (thường ở phần dưới xe)
                    h_img, w_img = vehicle_img.shape[:2]
                    est_x = int(w_img * 0.1)
                    est_y = int(h_img * 0.6)
                    est_w = int(w_img * 0.8)
                    est_h = int(h_img * 0.25)
                    return {
                        'text': text,
                        'confidence': 0.75,
                        'bbox': (est_x, est_y, est_w, est_h)
                    }
        
        # FALLBACK: Phương pháp contour cũ (nếu OCR không hoạt động)
        gray, edges = self.preprocess_plate(vehicle_img)
        plate_candidates = self.find_plate_contours(edges)
        
        if not plate_candidates:
            return None
        
        # Lấy candidate tốt nhất (đầu tiên)
        x, y, w, h = plate_candidates[0]
        plate_roi = gray[y:y+h, x:x+w]
        
        # Resize để OCR tốt hơn
        if plate_roi.shape[0] < 50:
            scale = 50 / plate_roi.shape[0]
            new_w = int(plate_roi.shape[1] * scale)
            plate_roi = cv2.resize(plate_roi, (new_w, 50))
        
        # Threshold
        _, plate_thresh = cv2.threshold(
            plate_roi,
            0,
            255,
            cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )
        
        # OCR
        if self.ocr_engine:
            plate_color = cv2.cvtColor(plate_thresh, cv2.COLOR_GRAY2BGR)
            text = self.extract_text_ocr(plate_color)
            
            if text:
                # Validate biển số Việt Nam
                if self.validate_plate(text):
                    return {
                        'text': text,
                        'confidence': 0.8,
                        'bbox': (x, y, w, h)
                    }
                else:
                    # Biển số không hợp lệ, bỏ qua
                    return None
        
        # Không phát hiện được biển số hợp lệ
        return None
    
    def validate_plate(self, text):
        """
        Kiểm tra tính hợp lệ của biển số Việt Nam
        Format: 
        - Xe máy mới: 49-E1222.22 hoặc 49E122222 (2 số + [gạch] + 1 chữ + 1 số + 3 số + [chấm] + 2 số)
        - Xe máy cũ: 29Y5-59009 (2 số + 1-2 chữ + 1 số + gạch + 5 số)
        - Ô tô: 29A-12345 (2 số + 1 chữ + gạch + 5 số)
        - Ô tô cũ: 29A-123.45 (2 số + 1 chữ + gạch + 3 số + chấm + 2 số)
        """
        if not text or len(text) < 6:
            return False
        
        # Loại bỏ dấu gạch ngang và khoảng trắng để kiểm tra
        text_clean = text.replace('-', '').replace(' ', '').replace('.', '')
        
        # Patterns biển số VN (linh hoạt với dấu gạch, chấm, khoảng trắng)
        patterns = [
            # Xe máy mới: 49-E1 222.22 hoặc 49E122222
            r'^\d{2}-?[A-Z]\d[\s\.]?\d{3}\.?\d{2}$',
            # Xe máy cũ: 29Y5-59009 hoặc 29YZ5-59009
            r'^\d{2}[A-Z]{1,2}\d-?\d{5}$',
            # Ô tô: 29A-12345 hoặc 29A12345
            r'^\d{2}-?[A-Z]-?\d{4,5}$',
            # Ô tô cũ: 29A-123.45
            r'^\d{2}-?[A-Z]-?\d{3}\.?\d{2}$',
        ]
        
        for pattern in patterns:
            if re.match(pattern, text):
                # Kiểm tra thêm: phải có đủ chữ và số
                num_digits = sum(c.isdigit() for c in text_clean)
                num_letters = sum(c.isalpha() for c in text_clean)
                
                # Biển số VN: ít nhất 5 số và 1 chữ
                if num_digits >= 5 and num_letters >= 1:
                    return True
        
        return False

if __name__ == '__main__':
    # Test module
    import yaml
    
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    detector = LicensePlateDetector(config)
    
    # Test với ảnh mẫu
    test_img = cv2.imread('test_car.jpg')
    if test_img is not None:
        result = detector.detect(test_img)
        print(f"Kết quả: {result}")
    else:
        print("Không tìm thấy ảnh test")

