# 🎥 Camera AI - Hệ thống giám sát thông minh

Hệ thống Camera AI sử dụng YOLOv11 và YOLOv8 để phát hiện người, xe và biển số xe tự động. Hỗ trợ phân loại xe (ô tô, xe máy, xe tải, xe buýt) và nhận diện biển số xe Việt Nam.

## ✨ Tính năng

- 🚗 **Phát hiện xe**: Ô tô, xe máy, xe tải, xe buýt, xe đạp
- 👤 **Phát hiện người**: Theo dõi người ra vào
- 🔢 **Nhận diện biển số**: Hỗ trợ định dạng biển số Việt Nam
- 📊 **Dashboard web**: Theo dõi real-time với biểu đồ
- 💾 **Lưu trữ**: Ghi video, snapshot và database
- 🎯 **Phân loại xe**: Tự động phân loại loại xe

## 🛠️ Công nghệ

- **YOLOv11**: Phát hiện người và xe
- **YOLOv8**: Phát hiện biển số xe
- **EasyOCR**: Đọc text từ biển số
- **Flask**: Web dashboard
- **OpenCV**: Xử lý video
- **SQLite**: Lưu trữ dữ liệu

## 📋 Yêu cầu

- Python 3.11+ (khuyến nghị Python 3.11, tránh 3.13)
- macOS / Linux / Windows
- Camera IP hoặc file video

## 🚀 Cài đặt

### 1. Clone repository

```bash
git clone <repository-url>
cd camera_ai
```

### 2. Tạo virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate  # macOS/Linux
# hoặc
.venv\Scripts\activate  # Windows
```

### 3. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### 4. Cấu hình

Chỉnh sửa `config.yaml`:

```yaml
camera:
  source: "videos/input.mp4"  # Hoặc RTSP URL
  width: 1920
  height: 1080
  fps: 30

detection:
  person_confidence: 0.5
  vehicle_confidence: 0.5

license_plate:
  use_yolo: true
  yolo_model: "yolov8n.pt"

ocr:
  enabled: true
  engine: "easyocr"
  confidence: 0.5

dashboard:
  port: 8080
```

## 🎬 Sử dụng

### Chạy Dashboard

```bash
python dashboard.py
```

Mở trình duyệt: http://localhost:8080

### Tính năng Dashboard

- **Live Feed**: Xem video real-time với detection
- **Fullscreen**: Click icon 🔍 để xem toàn màn hình
- **Thống kê**: Số người, xe, biển số phát hiện
- **Biểu đồ**: Thống kê theo ngày và theo giờ
- **Bảng biển số**: Danh sách biển số đã phát hiện với loại xe

## 📁 Cấu trúc Project

```
camera_ai/
├── camera_ai.py              # Core detection engine
├── license_plate_yolo.py     # YOLO-based plate detection
├── dashboard.py              # Flask web dashboard
├── config.yaml               # Cấu hình hệ thống
├── requirements.txt          # Python dependencies
├── templates/
│   └── dashboard.html        # Dashboard UI
├── detections/               # Video recordings & database
├── snapshots/                # Detection snapshots
└── videos/                   # Input videos
```

## 🎯 Định dạng biển số hỗ trợ

### Xe máy
- Mới: `29A-12345`, `51F-67890`
- Cũ: `29Y5-59009`, `49-E1 222.22`

### Ô tô
- Mới: `30A-123.45`, `51G-678.90`
- Cũ: `30A-12345`, `51F-67890`

## 🔧 Troubleshooting

### Lỗi: "no such column: vehicle_type"

Database cũ không tương thích. Xóa và tạo lại:

```bash
rm -f detections/detections.db
python dashboard.py
```

### Video không chạy

Kiểm tra:
1. File video tồn tại trong `videos/`
2. Đường dẫn trong `config.yaml` đúng
3. Codec video được hỗ trợ (MP4, AVI)

### OCR không đọc được biển số

- Đảm bảo biển số rõ ràng trong video
- Tăng độ phân giải video
- Điều chỉnh `ocr.confidence` trong config
- Thử chuyển sang `engine: "paddleocr"`

### Port 8080 đã được sử dụng

Đổi port trong `config.yaml`:

```yaml
dashboard:
  port: 8888
```

## 📊 Database Schema

### Table: detections

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| timestamp | DATETIME | Thời gian phát hiện |
| type | TEXT | person/vehicle |
| vehicle_type | TEXT | Ô tô/Xe máy/... |
| confidence | REAL | Độ tin cậy (0-1) |
| bbox | TEXT | Bounding box |
| snapshot_path | TEXT | Đường dẫn ảnh |
| license_plate | TEXT | Biển số xe |

## 🎨 Screenshots

### Dashboard
- Live camera feed với detection boxes
- Thống kê real-time
- Biểu đồ phát hiện theo thời gian
- Bảng biển số với phân loại xe

## 🤝 Đóng góp

Mọi đóng góp đều được chào đón! Hãy tạo issue hoặc pull request.

## 📝 License

MIT License - Tự do sử dụng cho mục đích cá nhân và thương mại.

## 👨‍💻 Tác giả

Phát triển bởi AI Assistant & Tran Trung

## 🙏 Credits

- [Ultralytics YOLO](https://github.com/ultralytics/ultralytics)
- [EasyOCR](https://github.com/JaidedAI/EasyOCR)
- [Flask](https://flask.palletsprojects.com/)
- [OpenCV](https://opencv.org/)

---

**⭐ Nếu project hữu ích, hãy cho một star!**
