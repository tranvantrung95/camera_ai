# 📖 Hướng Dẫn Sử Dụng Camera AI

## 🎯 Tổng Quan

Camera AI hỗ trợ 2 chế độ:
- **Video Mode**: Xử lý file video (MP4, AVI, ...)
- **RTSP Mode**: Kết nối camera IP qua RTSP stream

---

## ⚙️ Cấu Hình

### File: `config.yaml`

```yaml
camera:
  # Chọn nguồn đầu vào:
  
  # 1. Video file:
  source: "videos/11933881_2160_3840_30fps.mp4"
  
  # 2. RTSP camera:
  source: "rtsp://admin:L223C2D3@192.168.1.53:554/cam/realmonitor?channel=1&subtype=1"
  
  # 3. Webcam:
  source: 0  # 0 = webcam mặc định
  
  buffer_size: 1  # Chỉ cho RTSP, giảm độ trễ
```

---

## 🚀 Chạy Chương Trình

### **Cách 1: Dùng Script Chính (Khuyến nghị)**

```bash
# Kích hoạt virtual environment
source .venv/bin/activate

# Chạy
python run_camera.py
```

### **Cách 2: Chạy Dashboard Trực Tiếp**

```bash
python dashboard.py
```

### **Cách 3: Chỉ Chạy AI Engine (Không Dashboard)**

```bash
python camera_ai.py
```

---

## 🔄 Chuyển Đổi Giữa Video và Camera

### **Chuyển sang Video Mode:**

1. Mở `config.yaml`
2. Sửa dòng `source`:
   ```yaml
   camera:
     source: "videos/11933881_2160_3840_30fps.mp4"
   ```
3. Lưu file
4. Chạy lại: `python run_camera.py`

### **Chuyển sang RTSP Mode:**

1. Mở `config.yaml`
2. Sửa dòng `source`:
   ```yaml
   camera:
     source: "rtsp://admin:password@192.168.1.53:554/cam/realmonitor?channel=1&subtype=1"
   ```
3. Lưu file
4. Chạy lại: `python run_camera.py`

---

## 🧪 Test Camera RTSP

Trước khi chạy chương trình chính, nên test camera trước:

### **Test Nhanh (Tự động):**

```bash
python test_camera_quick.py
```

**Kết quả mong đợi:**
```
✅ KẾT NỐI THÀNH CÔNG!
📊 THÔNG TIN CAMERA:
   • Độ phân giải: 640x480
   • FPS: 15
   • Backend: FFMPEG
```

### **Test Video Live:**

```bash
python test_camera_live.py
```

Hiển thị video từ camera, nhấn:
- `q` - Thoát
- `s` - Chụp ảnh

---

## 🌐 Dashboard

Sau khi chạy, mở trình duyệt:

```
http://localhost:5000
```

### **Tính năng Dashboard:**

- 📹 **Video Feed**: Xem video real-time
- 🚗 **Detections**: Danh sách phát hiện
- 🔢 **License Plates**: Biển số xe đã nhận dạng
- 📊 **Statistics**: Thống kê tổng quan
- 📈 **Charts**: Biểu đồ theo giờ/ngày
- 🖼️ **Snapshots**: Ảnh đã lưu

---

## 🎛️ Tùy Chỉnh

### **Điều chỉnh độ nhạy:**

```yaml
detection:
  person_confidence: 0.5    # 0.0 - 1.0 (cao = ít phát hiện, chính xác hơn)
  vehicle_confidence: 0.4
  plate_confidence: 0.2
```

### **Bật/Tắt tính năng:**

```yaml
license_plate:
  enabled: true              # false = tắt nhận dạng biển số

recording:
  save_snapshots: true       # false = không lưu ảnh
  save_video: false          # true = lưu video

ocr:
  enabled: true              # false = tắt OCR
```

### **Chọn OCR engine:**

```yaml
ocr:
  engine: "easyocr"          # hoặc "paddleocr"
  languages: ['en']          # Ngôn ngữ
```

### **Hiệu suất:**

```yaml
performance:
  use_gpu: false             # true nếu có NVIDIA GPU
  device: "cpu"              # "0" cho GPU
  skip_frames: 0             # Bỏ qua frames (tăng tốc)
  resize_frame: false        # Giảm độ phân giải
```

---

## 🐛 Xử Lý Lỗi

### **❌ Không kết nối được camera RTSP**

**Nguyên nhân:** macOS Firewall chặn

**Giải pháp:**
1. Tắt Firewall tạm thời (System Settings → Network → Firewall)
2. Test lại: `python test_camera_quick.py`
3. Nếu OK, bật lại Firewall và thêm Python vào whitelist

**Xem chi tiết:** `cat FIX_MACOS_FIREWALL.md`

### **❌ Port 5000 đã bị chiếm**

**Giải pháp:**

```bash
# Giải phóng port
lsof -ti:5000 | xargs kill -9

# Hoặc đổi port trong config.yaml
dashboard:
  port: 8080  # Thay vì 5000
```

### **❌ Video bị giật/lag**

**Giải pháp:**

```yaml
camera:
  buffer_size: 1           # Giảm buffer

performance:
  skip_frames: 2           # Bỏ qua 2 frames
  resize_frame: true       # Giảm độ phân giải
  resize_width: 1280
  resize_height: 720
```

### **❌ Không nhận dạng được biển số**

**Giải pháp:**

1. **Kiểm tra ánh sáng** - Camera cần đủ sáng
2. **Giảm confidence:**
   ```yaml
   detection:
     plate_confidence: 0.15
   ocr:
     confidence: 0.2
   ```
3. **Thử OCR engine khác:**
   ```yaml
   ocr:
     engine: "paddleocr"  # Thay vì easyocr
   ```

---

## 📊 Database

### **Xem dữ liệu:**

```bash
# Cài sqlite3
brew install sqlite3  # macOS

# Xem 10 phát hiện gần nhất
sqlite3 detections/detections.db "SELECT * FROM detections ORDER BY timestamp DESC LIMIT 10;"

# Đếm tổng số
sqlite3 detections/detections.db "SELECT COUNT(*) FROM detections;"

# Xem biển số xe
sqlite3 detections/detections.db "SELECT license_plate, COUNT(*) as count FROM detections WHERE license_plate IS NOT NULL GROUP BY license_plate ORDER BY count DESC;"
```

### **Reset database:**

```bash
rm detections/detections.db
# Database sẽ tự động tạo lại khi chạy
```

---

## ⌨️ Lệnh Hữu Ích

```bash
# Xem logs real-time
tail -f camera_ai.log

# Xem logs với filter
grep "ERROR" camera_ai.log
grep "biển số" camera_ai.log

# Kiểm tra process đang chạy
ps aux | grep python

# Dừng tất cả process Python
pkill -f "python.*dashboard"

# Xem kết nối mạng
lsof -i :5000
lsof -i :554

# Test kết nối camera
ping 192.168.1.53
nc -zv 192.168.1.53 554
```

---

## 📁 Cấu Trúc Thư Mục

```
camera_ai/
├── config.yaml              # Cấu hình chính ⭐
├── dashboard.py             # Web dashboard
├── camera_ai.py             # AI engine
├── run_camera.py            # Script chạy chính
├── license_plate_yolo.py    # YOLO plate detector
├── license_plate.py         # Contour plate detector
├── test_camera_quick.py     # Test camera nhanh
├── test_camera_live.py      # Test video live
├── templates/
│   └── dashboard.html       # Dashboard UI
├── videos/                  # Video files
├── detections/              # Database + logs
├── snapshots/               # Ảnh đã lưu
└── models/                  # YOLO models
```

---

## 🎯 Workflow Khuyến Nghị

### **Lần Đầu Chạy:**

1. ✅ Cài đặt dependencies: `pip install -r requirements.txt`
2. ✅ Test camera: `python test_camera_quick.py`
3. ✅ Cấu hình `config.yaml`
4. ✅ Chạy: `python run_camera.py`
5. ✅ Mở dashboard: `http://localhost:5000`

### **Sử Dụng Hàng Ngày:**

1. ✅ Kích hoạt venv: `source .venv/bin/activate`
2. ✅ Chạy: `python run_camera.py`
3. ✅ Mở dashboard
4. ✅ Dừng: `Ctrl+C`

### **Khi Có Vấn Đề:**

1. ✅ Xem logs: `tail -f camera_ai.log`
2. ✅ Test camera: `python test_camera_quick.py`
3. ✅ Xem troubleshooting: `cat FIX_MACOS_FIREWALL.md`
4. ✅ Reset database nếu cần

---

## 💡 Tips

### **Tăng Hiệu Suất:**

- Dùng GPU nếu có
- Giảm độ phân giải camera
- Bỏ qua frames (`skip_frames`)
- Dùng substream thay vì mainstream

### **Tăng Độ Chính Xác:**

- Cải thiện ánh sáng
- Góc camera tốt (nhìn thẳng biển số)
- Dùng model lớn hơn (yolo11m.pt thay vì yolo11n.pt)
- Điều chỉnh confidence thresholds

### **Tiết Kiệm Dung Lượng:**

- Tắt `save_video`
- Chỉ lưu snapshot khi cần
- Xóa database cũ định kỳ
- Giảm độ phân giải snapshot

---

## 📞 Hỗ Trợ

### **Files Tài Liệu:**

- `README.md` - Tổng quan project
- `USAGE.md` - Hướng dẫn sử dụng (file này)
- `README_CAMERA.md` - Hướng dẫn camera RTSP
- `FIX_MACOS_FIREWALL.md` - Sửa lỗi Firewall
- `SOLUTIONS.md` - So sánh các giải pháp

### **Scripts Test:**

- `test_camera_quick.py` - Test nhanh
- `test_camera_live.py` - Xem video live
- `test_camera_debug.py` - Debug kết nối

---

**🎊 Chúc bạn sử dụng thành công!** 🚀

