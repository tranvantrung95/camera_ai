# 🚀 CHẠY HỆ THỐNG

## ✅ Đã fix: Port conflict với AirPlay

Dashboard đã được đổi từ port **5000** → **8080**

## 🎯 Lệnh chạy:

```bash
cd /Users/trantrung/PycharmProjects/camera_ai
source venv/bin/activate
python dashboard.py
```

## 🌐 Truy cập Dashboard:

Mở trình duyệt và vào:

```
http://localhost:8080
```

Hoặc từ thiết bị khác trong mạng:

```
http://[IP-máy-Mac]:8080
```

## 📺 Xem IP máy Mac:

```bash
ifconfig | grep "inet " | grep -v 127.0.0.1
```

Hoặc: **System Preferences → Network**

## 🛑 Dừng hệ thống:

- Nhấn `Ctrl + C` trong terminal
- Hoặc dùng nút "Tạm dừng" trên dashboard

## 💡 Tips:

### Đầu vào video (offline)

1. Tạo thư mục và copy video:
   ```bash
   mkdir -p videos
   cp /path/to/video.mp4 videos/input.mp4
   ```
2. Hoặc sửa `camera.source` trong `config.yaml` tới file của bạn.

Sau đó chạy `python camera_ai.py` hoặc `python dashboard.py`, hệ thống sẽ đọc video thay vì camera.

### Chỉ test camera (không cần dashboard):

```bash
python camera_ai.py
```

Nhấn `Q` để thoát.

### Chạy nền (background):

```bash
nohup python dashboard.py > output.log 2>&1 &
```

Xem log:
```bash
tail -f output.log
```

Dừng:
```bash
pkill -f dashboard.py
```

## 🔧 Nếu vẫn lỗi port:

### Kiểm tra port nào đang dùng:

```bash
lsof -i :8080
```

### Đổi sang port khác:

Sửa `config.yaml`:
```yaml
dashboard:
  port: 8888  # Hoặc số nào bạn thích (1024-65535)
```

## ⚙️ Tắt AirPlay Receiver (nếu muốn dùng port 5000):

1. **System Settings** (hoặc System Preferences)
2. **General** → **AirDrop & Handoff**
3. Tắt **AirPlay Receiver**

Sau đó đổi lại port 5000 trong `config.yaml`.

## 📸 Test camera:

Nếu camera không hoạt động:

```bash
# Test camera
python -c "import cv2; cap = cv2.VideoCapture(0); print('Camera OK' if cap.isOpened() else 'Camera FAIL')"
```

Nếu FAIL, thử:
- Cấp quyền Camera cho Terminal trong System Settings → Privacy & Security → Camera
- Thử `source: 1` trong config.yaml
- Kiểm tra camera có đang dùng bởi app khác không

## 🎉 Khi thành công:

Bạn sẽ thấy:

```
🚀 Khởi động Camera AI Dashboard...
📱 Sử dụng device: cpu
✅ Camera AI System đã sẵn sàng!
📹 Camera loop bắt đầu...
🌐 Dashboard đang chạy tại: http://0.0.0.0:8080
 * Running on http://0.0.0.0:8080
```

Mở browser → http://localhost:8080 → Thấy camera live! ✅

---

**Chúc may mắn! 🚀**



