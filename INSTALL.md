# 📖 Hướng dẫn Cài đặt Chi tiết

## 🎯 Mục lục
1. [Cài đặt Python](#1-cài-đặt-python)
2. [Cài đặt Dependencies](#2-cài-đặt-dependencies)
3. [Cấu hình Camera](#3-cấu-hình-camera)
4. [Cấu hình OCR](#4-cấu-hình-ocr)
5. [Chạy hệ thống](#5-chạy-hệ-thống)
6. [Tùy chọn nâng cao](#6-tùy-chọn-nâng-cao)

---

## 1. Cài đặt Python

### Windows

1. Tải Python 3.8+ từ: https://www.python.org/downloads/
2. Chạy installer, **QUAN TRỌNG**: Tick vào "Add Python to PATH"
3. Kiểm tra cài đặt:
```cmd
python --version
```

### macOS

```bash
# Dùng Homebrew (khuyến nghị)
brew install python@3.11

# Hoặc tải từ python.org
```

### Linux (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

## 2. Cài đặt Dependencies

### Cách 1: Tự động (Khuyến nghị)

**Windows:**
```cmd
start.bat
```

**macOS/Linux:**
```bash
./start.sh
```

### Cách 2: Thủ công

```bash
# Tạo virtual environment
python -m venv venv

# Kích hoạt
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Cài đặt packages
pip install -r requirements.txt
```

### 2.1. Cài đặt với GPU (NVIDIA)

Nếu có card đồ họa NVIDIA:

```bash
# Gỡ PyTorch CPU
pip uninstall torch torchvision

# Cài PyTorch GPU (CUDA 11.8)
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118

# Hoặc CUDA 12.1
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
```

Kiểm tra GPU:
```python
import torch
print(torch.cuda.is_available())  # Phải là True
print(torch.cuda.get_device_name(0))
```

## 3. Cấu hình Camera

### 3.1. Webcam USB

Mặc định sử dụng webcam có sẵn:

```yaml
# config.yaml
camera:
  source: 0  # 0 = camera đầu tiên
```

Nếu có nhiều camera, thử: `1`, `2`, etc.

### 3.2. IP Camera / RTSP

```yaml
camera:
  source: "rtsp://admin:password@192.168.1.100:554/stream1"
```

**Các định dạng RTSP phổ biến:**

- **Hikvision**: `rtsp://admin:password@IP:554/Streaming/Channels/101`
- **Dahua**: `rtsp://admin:password@IP:554/cam/realmonitor?channel=1&subtype=0`
- **TP-Link**: `rtsp://admin:password@IP:554/stream1`
- **Generic**: `rtsp://username:password@IP:port/stream`

**Test RTSP stream:**
```bash
# Dùng ffplay (từ ffmpeg)
ffplay "rtsp://admin:password@192.168.1.100:554/stream1"
```

### 3.3. Video File (test)

```yaml
camera:
  source: "path/to/video.mp4"
```

## 4. Cấu hình OCR

### 4.1. PaddleOCR (Khuyến nghị)

Đã bao gồm trong `requirements.txt`. Tốt cho tiếng Việt.

```bash
pip install paddleocr paddlepaddle
```

**Lưu ý**: PaddleOCR sẽ tự động tải model khi chạy lần đầu (~100MB).

### 4.2. EasyOCR (Thay thế)

```bash
pip install easyocr
```

Sau đó sửa `config.yaml`:
```yaml
ocr:
  enabled: true
  engine: "easyocr"  # Thay vì "paddleocr"
```

### 4.3. Tắt OCR

Nếu chỉ muốn phát hiện xe mà không đọc biển số:

```yaml
ocr:
  enabled: false
```

## 5. Chạy hệ thống

### 5.1. Chạy Dashboard (Full features)

**Windows:**
```cmd
start.bat
```

**macOS/Linux:**
```bash
./start.sh
```

**Hoặc thủ công:**
```bash
python dashboard.py
```

Mở trình duyệt: http://localhost:5000

### 5.2. Chạy chỉ Detection (không dashboard)

```bash
python camera_ai.py
```

Nhấn `Q` để thoát.

### 5.3. Chạy nền (background)

**Linux/macOS:**
```bash
nohup python dashboard.py > output.log 2>&1 &
```

**Windows (PowerShell):**
```powershell
Start-Process python -ArgumentList "dashboard.py" -WindowStyle Hidden
```

## 6. Tùy chọn Nâng cao

### 6.1. Tối ưu hiệu suất

**Giảm độ phân giải:**
```yaml
camera:
  width: 640
  height: 480
```

**Sử dụng model nhẹ:**
```yaml
detection:
  person_model: "models/yolo11n.pt"  # nano (nhanh nhất)
```

**Tăng confidence threshold:**
```yaml
detection:
  person_confidence: 0.6
  vehicle_confidence: 0.6
```

### 6.2. Tăng độ chính xác

**Tăng độ phân giải:**
```yaml
camera:
  width: 1920
  height: 1080
```

**Dùng model lớn:**
```yaml
detection:
  person_model: "models/yolo11l.pt"  # large (chính xác nhất)
```

**Giảm threshold:**
```yaml
detection:
  person_confidence: 0.3
  vehicle_confidence: 0.3
```

### 6.3. Cấu hình lưu trữ

**Tắt recording (tiết kiệm dung lượng):**
```yaml
recording:
  enabled: false
```

**Chỉ lưu snapshot:**
```yaml
recording:
  enabled: false
  save_snapshots: true
```

**Thay đổi thời gian lưu trữ:**
```yaml
recording:
  video_retention_days: 3  # Xóa video cũ hơn 3 ngày
```

### 6.4. Truy cập từ xa

**Trong mạng LAN:**

Sửa `config.yaml`:
```yaml
dashboard:
  host: "0.0.0.0"  # Cho phép kết nối từ mạng LAN
  port: 5000
```

Tìm IP máy:
- Windows: `ipconfig`
- Linux/macOS: `ifconfig` hoặc `ip addr`

Truy cập từ máy khác: `http://192.168.1.xxx:5000`

**Qua Internet (cẩn thận!):**

Không khuyến khích vì vấn đề bảo mật. Nếu cần:

1. **Dùng VPN** (ZeroTier, Tailscale)
2. **Reverse Proxy với Auth** (Nginx + Basic Auth)
3. **Port forward** trên router (+ firewall rules)

### 6.5. Chạy khi khởi động

**Windows (Task Scheduler):**

1. Mở Task Scheduler
2. Create Basic Task
3. Trigger: When computer starts
4. Action: Start a program
5. Program: `C:\path\to\camera_ai\start.bat`

**Linux (systemd service):**

Tạo file `/etc/systemd/system/camera-ai.service`:

```ini
[Unit]
Description=Camera AI Service
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/camera_ai
ExecStart=/path/to/camera_ai/venv/bin/python dashboard.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable service:
```bash
sudo systemctl enable camera-ai
sudo systemctl start camera-ai
```

**macOS (launchd):**

Tạo file `~/Library/LaunchAgents/com.camera-ai.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.camera-ai</string>
    <key>ProgramArguments</key>
    <array>
        <string>/path/to/camera_ai/venv/bin/python</string>
        <string>/path/to/camera_ai/dashboard.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>WorkingDirectory</key>
    <string>/path/to/camera_ai</string>
</dict>
</plist>
```

Load service:
```bash
launchctl load ~/Library/LaunchAgents/com.camera-ai.plist
```

## 🆘 Xử lý sự cố

### Lỗi "Camera not found"

```bash
# Test camera
python -c "import cv2; cap = cv2.VideoCapture(0); print(cap.isOpened())"

# Thử các index khác
source: 1
source: 2
```

### Lỗi "Module not found"

```bash
# Đảm bảo virtual environment được kích hoạt
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Cài lại dependencies
pip install -r requirements.txt
```

### Lỗi PaddleOCR

```bash
# Gỡ và cài lại
pip uninstall paddleocr paddlepaddle -y
pip install paddleocr paddlepaddle --no-cache-dir

# Hoặc dùng EasyOCR
pip install easyocr
# Sửa config.yaml: engine: "easyocr"
```

### Dashboard không load

```bash
# Kiểm tra port
netstat -ano | findstr :5000  # Windows
lsof -i :5000                 # Linux/Mac

# Thử port khác
dashboard:
  port: 8080
```

### Chậm, giật lag

1. Giảm resolution camera
2. Dùng model nhỏ hơn (yolo11n)
3. Tăng confidence threshold
4. Tắt recording nếu không cần
5. Kiểm tra CPU/RAM usage

### Out of memory

```bash
# Dùng model nhỏ nhất
detection:
  person_model: "models/yolo11n.pt"

# Giảm resolution
camera:
  width: 640
  height: 480
```

## ✅ Checklist cài đặt

- [ ] Python 3.8+ đã cài đặt
- [ ] Virtual environment đã tạo và kích hoạt
- [ ] Dependencies đã cài đặt (`pip install -r requirements.txt`)
- [ ] YOLOv11 model đã tải (hoặc sẽ tự động tải)
- [ ] Camera đã kết nối và test
- [ ] `config.yaml` đã cấu hình đúng
- [ ] Đã chạy `python dashboard.py` thành công
- [ ] Dashboard truy cập được tại http://localhost:5000
- [ ] Video feed hiển thị bình thường
- [ ] Detection hoạt động (test bằng cách đi qua camera)

## 📞 Hỗ trợ

Nếu vẫn gặp vấn đề:
1. Kiểm tra log trong terminal
2. Đảm bảo đã làm theo đúng các bước
3. Xem phần xử lý sự cố ở trên
4. Kiểm tra cấu hình `config.yaml`

---

**Chúc bạn thành công! 🎉**



