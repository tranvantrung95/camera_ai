# 🚀 Hướng Dẫn Test Nhanh - YOLOv8 + EasyOCR

## ✅ Đã Hoàn Thành

1. ✅ Cài đặt `ultralytics` và `easyocr`
2. ✅ Tải model YOLOv8n
3. ✅ Cập nhật `config.yaml`
4. ✅ Tích hợp YOLOLicensePlateDetector
5. ✅ Xóa database cũ

---

## 🎯 Cách Test

### **Option 1: Test với ảnh có biển số** (Khuyến nghị)

```bash
# 1. Tải ảnh có biển số xe (Google: "vietnam license plate")
# Hoặc chụp màn hình từ video có biển số

# 2. Chạy script test
python test_ocr_image.py anh_bien_so.jpg
```

**Kết quả mong đợi:**
```
✅ Đã đọc ảnh: anh_bien_so.jpg
📐 Kích thước: (height, width, 3)
🎉 PHÁT HIỆN BIỂN SỐ:
   📝 Text: 29A-12345
   📊 Confidence: 0.85
   📍 BBox: (x, y, w, h)
💾 Đã lưu kết quả: test_result.jpg
```

---

### **Option 2: Test với video có biển số**

```bash
# 1. Đặt video có biển số vào thư mục videos/
# Ví dụ: videos/xe_co_bien_so.mp4

# 2. Cập nhật config.yaml
# camera:
#   source: "videos/xe_co_bien_so.mp4"

# 3. Chạy dashboard
python dashboard.py
```

---

### **Option 3: Chạy với video hiện tại** (Sẽ không có biển số)

```bash
# Video hiện tại không có biển số rõ ràng
# Nhưng có thể test xem hệ thống hoạt động

python dashboard.py
```

**Kết quả mong đợi:**
- ✅ Phát hiện người và xe
- ✅ Hệ thống chạy mượt mà
- ❌ Không có biển số (vì video không có)

---

## 📊 So Sánh: Trước vs Sau

### **Trước (PaddleOCR + Contour):**
```
🚗 Phát hiện xe, đang quét biển số...
🔍 OCR không đọc được text nào
→ Kết quả: None
```

### **Sau (YOLOv8 + EasyOCR):**
```
🎯 Sử dụng YOLO License Plate Detector
✅ EasyOCR đã sẵn sàng cho đọc text
🎯 YOLO phát hiện biển số: '29A-12345' (confidence: 0.85)
→ Kết quả: {'text': '29A-12345', 'confidence': 0.85, 'bbox': (x, y, w, h)}
```

---

## 🔧 Cấu Hình Hiện Tại

### `config.yaml`:
```yaml
ocr:
  enabled: true
  engine: "easyocr"  # Đã chuyển từ paddleocr
  languages: ['en']

license_plate:
  use_yolo: true  # Sử dụng YOLO
  yolo_model: "yolov8n.pt"  # Model YOLOv8
```

### Detector được chọn:
- ✅ `YOLOLicensePlateDetector` (license_plate_yolo.py)
- ✅ EasyOCR cho đọc text

---

## 📝 Lưu Ý

### **1. Model hiện tại:**
- Đang dùng YOLOv8n (base model)
- **Chưa được train cho license plate**
- Sẽ cải thiện khi có model chuyên dụng

### **2. Để có kết quả tốt nhất:**
- Dùng ảnh/video có biển số **rõ ràng**
- Biển số **không bị che khuất**
- Góc chụp **thẳng** (không quá nghiêng)

### **3. Nâng cấp sau:**
- Tải model license plate chuyên dụng từ Roboflow
- Train model riêng với dataset biển số VN
- Tối ưu hóa OCR cho biển số Việt Nam

---

## 🎓 Model License Plate Chuyên Dụng (Tùy chọn)

Để có độ chính xác cao hơn, tải model chuyên dụng:

### **Roboflow License Plate Model:**
```bash
# 1. Truy cập: https://universe.roboflow.com/roboflow-universe-projects/license-plate-recognition-rxg4e
# 2. Download model (YOLOv8 format)
# 3. Đặt vào thư mục dự án
# 4. Cập nhật config.yaml:
#    license_plate:
#      yolo_model: "license_plate_model.pt"
```

---

## ✅ Kiểm Tra Hệ Thống

```bash
# Kiểm tra các thư viện đã cài
python -c "
import ultralytics
import easyocr
import cv2
print('✅ Ultralytics:', ultralytics.__version__)
print('✅ EasyOCR: Installed')
print('✅ OpenCV:', cv2.__version__)
"
```

---

## 🚀 Chạy Ngay

```bash
# Test nhanh với ảnh
python test_ocr_image.py anh_bien_so.jpg

# Hoặc chạy dashboard
python dashboard.py
```

**Mở trình duyệt**: http://localhost:8080

---

## 📞 Hỗ Trợ

Nếu gặp lỗi:
1. Kiểm tra log trong terminal
2. Xem file `SOLUTIONS.md` để biết thêm chi tiết
3. Đảm bảo ảnh/video có biển số rõ ràng

