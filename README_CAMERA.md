# 🎥 Camera AI - RTSP Mode

Hướng dẫn sử dụng Camera AI với camera RTSP thực tế.

---

## 📡 Thông Tin Camera

- **Model**: Camera IP (Dahua/Hikvision compatible)
- **IP**: 192.168.1.53
- **Port**: 554 (RTSP)
- **Username**: admin
- **Password**: L223C2D3
- **RTSP URL**: `rtsp://admin:L223C2D3@192.168.1.53:554/cam/realmonitor?channel=1&subtype=1`

---

## 🚀 Cách Sử Dụng

### 1️⃣ Test Kết Nối Camera (Khuyến nghị làm trước)

```bash
# Test đầy đủ - hiển thị video live
python test_camera_rtsp.py
# Chọn option 1

# Hoặc test nhanh - chỉ chụp 1 frame
python test_camera_rtsp.py
# Chọn option 2
```

**Điều khiển trong test mode:**
- `q` hoặc `ESC` - Thoát
- `s` - Chụp ảnh snapshot
- `i` - Xem thông tin frame

### 2️⃣ Chạy Camera AI Đầy Đủ

```bash
# Cách 1: Sử dụng script chuyên dụng
python run_camera.py

# Cách 2: Chạy dashboard với config camera
CONFIG_FILE=config_camera.yaml python dashboard.py
```

### 3️⃣ Mở Dashboard

Mở trình duyệt và truy cập:

```
http://localhost:5000
```

---

## 📊 Chức Năng

### ✅ Đã Bật

- 🚗 **Phát hiện xe**: Ô tô, xe máy, xe buýt, xe tải
- 👤 **Phát hiện người**: Người đi bộ
- 🔢 **Nhận dạng biển số**: YOLOv8 + EasyOCR
- 📸 **Lưu snapshot**: Tự động lưu khi phát hiện
- 💾 **Database**: Lưu lịch sử phát hiện
- 📊 **Dashboard**: Hiển thị real-time + thống kê

### 🎯 Độ Chính Xác

- **Phát hiện người**: ≥ 50% confidence
- **Phát hiện xe**: ≥ 40% confidence
- **Biển số xe**: ≥ 20% confidence
- **OCR**: ≥ 30% confidence

---

## 🔧 Cấu Hình

File cấu hình: `config_camera.yaml`

### Thay Đổi Camera

```yaml
camera:
  source: "rtsp://admin:L223C2D3@192.168.1.53:554/cam/realmonitor?channel=1&subtype=1"
  width: 1920
  height: 1080
  fps: 25
```

### Điều Chỉnh Độ Nhạy

```yaml
detection:
  person_confidence: 0.5    # Giảm xuống 0.3 để phát hiện nhiều hơn
  vehicle_confidence: 0.4   # Giảm xuống 0.3
  plate_confidence: 0.2     # Giảm xuống 0.15
```

### Bật/Tắt Tính Năng

```yaml
license_plate:
  enabled: true              # false để tắt nhận dạng biển số
  use_yolo_plate: true       # false để dùng contour detection

recording:
  save_snapshots: true       # false để không lưu ảnh
  save_video: false          # true để lưu video
```

---

## 🐛 Xử Lý Lỗi

### ❌ Không kết nối được camera

**Kiểm tra:**

1. **Camera có bật không?**
   ```bash
   ping 192.168.1.53
   ```

2. **Port 554 có mở không?**
   ```bash
   nc -zv 192.168.1.53 554
   ```

3. **Username/password đúng chưa?**
   - Thử đăng nhập qua VLC
   - Kiểm tra web interface camera

4. **Firewall có chặn không?**
   ```bash
   # macOS
   sudo pfctl -s rules | grep 554
   
   # Linux
   sudo iptables -L | grep 554
   ```

### ⚠️ Video bị giật/lag

**Giải pháp:**

1. **Giảm buffer size** (trong `config_camera.yaml`):
   ```yaml
   camera:
     buffer_size: 1  # Thử giảm xuống 1
   ```

2. **Bỏ qua frames**:
   ```yaml
   performance:
     skip_frames: 2  # Xử lý mỗi 3 frames
   ```

3. **Giảm độ phân giải**:
   ```yaml
   performance:
     resize_frame: true
     resize_width: 1280
     resize_height: 720
   ```

### 🔢 Không nhận dạng được biển số

**Giải pháp:**

1. **Kiểm tra ánh sáng**: Camera cần đủ sáng
2. **Điều chỉnh confidence**:
   ```yaml
   detection:
     plate_confidence: 0.15  # Giảm xuống
   ocr:
     confidence: 0.2         # Giảm xuống
   ```

3. **Thử engine OCR khác**:
   ```yaml
   ocr:
     engine: "paddleocr"  # Thay vì easyocr
   ```

### 🐌 Xử lý chậm

**Giải pháp:**

1. **Bật GPU** (nếu có):
   ```yaml
   performance:
     use_gpu: true
     device: "0"
   ```

2. **Giảm số classes phát hiện**:
   ```yaml
   detection:
     classes: [2, 3]  # Chỉ phát hiện car và motorcycle
   ```

3. **Tắt tracking**:
   ```yaml
   detection:
     enable_tracking: false
   ```

---

## 📸 Test Snapshots

Khi chạy `test_camera_rtsp.py`, các file snapshot sẽ được lưu:

```
snapshot_20250118_143025.jpg
test_frame_20250118_143030.jpg
```

Kiểm tra chất lượng ảnh để đảm bảo:
- ✅ Đủ sáng
- ✅ Rõ nét
- ✅ Biển số xe rõ ràng

---

## 📊 Database

File database: `detections/detections.db`

### Xem dữ liệu

```bash
# Cài đặt sqlite3
brew install sqlite3  # macOS
sudo apt install sqlite3  # Linux

# Xem dữ liệu
sqlite3 detections/detections.db "SELECT * FROM detections ORDER BY timestamp DESC LIMIT 10;"
```

### Reset database

```bash
rm detections/detections.db
# Database sẽ tự động tạo lại khi chạy
```

---

## 🎯 Tips

### Tối Ưu Hiệu Suất

1. **Sử dụng substream** (độ phân giải thấp hơn):
   ```
   rtsp://admin:L223C2D3@192.168.1.53:554/cam/realmonitor?channel=1&subtype=1
   ```
   - `subtype=0` - Mainstream (HD, chậm hơn)
   - `subtype=1` - Substream (SD, nhanh hơn) ✅

2. **Chạy trên máy có GPU**:
   - NVIDIA GPU + CUDA
   - Tăng tốc 5-10 lần

3. **Giảm FPS**:
   ```yaml
   camera:
     fps: 15  # Thay vì 25
   ```

### Tăng Độ Chính Xác

1. **Cải thiện ánh sáng**:
   - Bật đèn hồng ngoại (IR) vào ban đêm
   - Điều chỉnh exposure trên camera

2. **Góc camera tốt**:
   - Nhìn thẳng vào biển số
   - Khoảng cách 3-10m
   - Độ cao 2-3m

3. **Sử dụng model tốt hơn**:
   ```yaml
   detection:
     model: "yolo11m.pt"  # Thay vì yolo11n.pt
   license_plate:
     yolo_model: "yolov8m.pt"  # Thay vì yolov8n.pt
   ```

---

## 📞 Hỗ Trợ

### Logs

```bash
# Xem logs real-time
tail -f camera_ai.log

# Xem logs với filter
grep "ERROR" camera_ai.log
grep "biển số" camera_ai.log
```

### Debug Mode

```bash
# Bật debug trong config
# config_camera.yaml
logging:
  level: "DEBUG"
```

---

## 🔄 So Sánh: Video vs Camera

| Tính năng | Video Mode | Camera Mode |
|-----------|------------|-------------|
| **Nguồn** | File MP4 | RTSP Stream |
| **Độ trễ** | Không có | 1-3 giây |
| **Tốc độ** | Nhanh | Phụ thuộc mạng |
| **Real-time** | ❌ | ✅ |
| **Lưu trữ** | Có sẵn | Cần ghi lại |
| **Ổn định** | Cao | Phụ thuộc mạng |

---

## ✅ Checklist Trước Khi Chạy

- [ ] Camera đã bật và kết nối mạng
- [ ] Đã test kết nối bằng `test_camera_rtsp.py`
- [ ] VLC có thể xem được stream
- [ ] Đã cài đặt dependencies: `pip install -r requirements.txt`
- [ ] Đã tải models: YOLOv11, YOLOv8
- [ ] Đã tạo thư mục: `detections/`, `snapshots/`
- [ ] Port 5000 không bị chiếm dụng

---

**🎊 Chúc bạn sử dụng thành công!** 🚀

