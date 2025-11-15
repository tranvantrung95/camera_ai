# 🚀 Quick Start - Bắt đầu nhanh

## ⚠️ LƯU Ý QUAN TRỌNG

Bạn đang dùng **Python 3.13** trên macOS (M1/M2). Một số lưu ý:

## 📝 Các bước cài đặt (macOS)

### Bước 1: Tạo Virtual Environment

```bash
cd /Users/trantrung/PycharmProjects/camera_ai
python3 -m venv venv
```

### Bước 2: Kích hoạt Virtual Environment

**⚠️ QUAN TRỌNG - Phải làm bước này trước khi cài đặt:**

```bash
source venv/bin/activate
```

Sau khi kích hoạt, bạn sẽ thấy `(venv)` ở đầu dòng lệnh.

### Bước 3: Upgrade pip

```bash
pip install --upgrade pip
```

### Bước 4: Cài đặt dependencies

```bash
pip install -r requirements.txt
```

**Nếu gặp lỗi với Python 3.13**, cài từng package:

```bash
# Core packages
pip install ultralytics torch torchvision opencv-python numpy

# Web framework
pip install Flask Flask-CORS PyYAML

# Image processing
pip install Pillow python-dateutil

# OCR (có thể skip nếu lỗi, sẽ cài sau)
pip install paddleocr paddlepaddle
```

### Bước 5: Test cài đặt

```bash
python -c "import cv2, torch, yaml; print('✅ OK')"
```

### Bước 6: Chạy hệ thống

```bash
python dashboard.py
```

Hoặc chỉ camera AI:

```bash
python camera_ai.py
```

## 🔧 Khắc phục sự cố Python 3.13

### Vấn đề: PaddleOCR không tương thích

**Giải pháp 1**: Dùng EasyOCR

```bash
pip install easyocr
```

Sửa `config.yaml`:
```yaml
ocr:
  engine: "easyocr"
```

**Giải pháp 2**: Tắt OCR tạm thời

Sửa `config.yaml`:
```yaml
ocr:
  enabled: false
```

### Vấn đề: Homebrew Python externally-managed

Đừng cài global, luôn dùng venv:

```bash
# Đúng ✅
source venv/bin/activate
pip install package

# SAI ❌ 
pip install package  # Không kích hoạt venv
```

### Vấn đề: Một số package không có wheel cho Python 3.13

**Giải pháp**: Dùng Python 3.11 (ổn định hơn)

```bash
# Cài Python 3.11
brew install python@3.11

# Tạo venv với Python 3.11
python3.11 -m venv venv

# Kích hoạt và cài đặt
source venv/bin/activate
pip install -r requirements.txt
```

## 📋 Checklist

- [ ] Đã vào thư mục dự án
- [ ] Đã tạo venv: `python3 -m venv venv`
- [ ] Đã kích hoạt venv: `source venv/bin/activate` 
- [ ] Thấy `(venv)` ở đầu dòng lệnh
- [ ] Đã upgrade pip: `pip install --upgrade pip`
- [ ] Đã cài requirements: `pip install -r requirements.txt`
- [ ] Test OK: `python -c "import cv2; print('OK')"`

## 🎯 Commands chính

```bash
# Kích hoạt venv (luôn làm trước khi làm việc)
source venv/bin/activate

# Cài đặt/cập nhật packages
pip install -r requirements.txt

# Chạy dashboard (full features)
python dashboard.py

# Chạy chỉ camera (no web)
python camera_ai.py

# Tắt venv khi xong
deactivate
```

## 🆘 Nếu vẫn lỗi

### Option 1: Cài minimal (không OCR)

```bash
pip install ultralytics opencv-python Flask Flask-CORS PyYAML Pillow
```

Tắt OCR trong `config.yaml`:
```yaml
ocr:
  enabled: false
```

### Option 2: Docker (nếu quen Docker)

```bash
# Tạo Dockerfile
docker build -t camera-ai .
docker run -p 5000:5000 --device=/dev/video0 camera-ai
```

### Option 3: Conda environment

```bash
conda create -n camera-ai python=3.11
conda activate camera-ai
pip install -r requirements.txt
```

## ✅ Khi cài đặt thành công

Bạn sẽ thấy:

```bash
(venv) trantrung@MacBook-Pro camera_ai % python dashboard.py
🚀 Đang khởi động Camera AI System...
📱 Sử dụng device: cpu
⬇️  Đang tải YOLOv11 model...
✅ PaddleOCR đã sẵn sàng
📹 Camera đã kết nối: 0
💾 Database đã sẵn sàng
✅ Camera AI System đã sẵn sàng!
📹 Camera loop bắt đầu...
🌐 Dashboard đang chạy tại: http://0.0.0.0:5000
```

Mở browser: http://localhost:5000

---

**Good luck! 🎉**



