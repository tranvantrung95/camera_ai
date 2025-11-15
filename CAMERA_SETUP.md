# 📹 Hướng dẫn Kết nối Camera

## 🎯 Các loại camera được hỗ trợ:

1. **Webcam/USB Camera** - Camera gắn trực tiếp vào máy
2. **IP Camera** - Camera mạng qua RTSP/HTTP
3. **Video File** - Test bằng file video có sẵn

---

## 🚀 Bước 1: Test camera

Chạy script test tự động:

```bash
python test_camera.py
```

Script sẽ:
- ✅ Tự động tìm tất cả webcam/USB camera
- ✅ Hiển thị preview từ mỗi camera
- ✅ Test kết nối RTSP camera
- ✅ Tự động cập nhật config.yaml

---

## 📹 Option 1: Webcam/USB Camera

### Cách đơn giản nhất:

1. Cắm camera USB vào máy
2. Chạy test:
```bash
python test_camera.py
```

3. Cập nhật `config.yaml`:
```yaml
camera:
  source: 0  # 0 = camera đầu tiên, 1 = camera thứ 2, etc.
```

### Cấp quyền camera (macOS):

1. **System Settings** → **Privacy & Security** → **Camera**
2. Bật quyền cho **Terminal** hoặc **Python**
3. Khởi động lại terminal

---

## 📡 Option 2: IP Camera (RTSP)

### Tìm thông tin camera:

Bạn cần:
- ✅ **IP address** của camera (vd: `192.168.1.100`)
- ✅ **Username** (thường là `admin`)
- ✅ **Password** (mật khẩu camera)
- ✅ **Port** (thường là `554` hoặc `8554` cho V360 Pro)
- ✅ **Stream path** (phụ thuộc hãng camera)

### **Camera V360 Pro (Model: FH8626V100):**

Camera V360 Pro có **2 bộ credentials**:

1. **Default credentials (hardcoded):**
   - Username: `admin`
   - Password: `admin123456`
   - Port: `8554`

2. **App credentials (user-set):**
   - Username: (số điện thoại hoặc username bạn đặt trong app)
   - Password: (mật khẩu bạn đặt trong app V360 Pro)
   - Port: `8554`

**RTSP URLs:**

Luồng HD: `rtsp://admin:admin123456@[CAMERA-IP]:8554/profile0`

Luồng SD: `rtsp://admin:admin123456@[CAMERA-IP]:8554/profile1`

Profile 100: `rtsp://admin:admin123456@[CAMERA-IP]:8554/profile100`

**Ví dụ với IP 192.168.1.56:**
- Luồng HD: `rtsp://admin:admin123456@192.168.1.56:8554/profile0`
- Luồng SD: `rtsp://admin:admin123456@192.168.1.56:8554/profile1`

**Lưu ý:**
- Nếu default credentials không hoạt động, thử app credentials
- Password trong app có thể chứa ký tự đặc biệt (cần URL encode)
- Dùng script `test_camera.py` để tự động test cả hai

### Các format RTSP phổ biến:

#### 1. **Hikvision**
```yaml
camera:
  source: "rtsp://admin:password@192.168.1.100:554/Streaming/Channels/101"
```

Thử thêm:
- `/Streaming/Channels/1`
- `/h264/ch1/main/av_stream`

#### 2. **Dahua**
```yaml
camera:
  source: "rtsp://admin:password@192.168.1.100:554/cam/realmonitor?channel=1&subtype=0"
```

Subtype:
- `subtype=0` = Main stream (chất lượng cao)
- `subtype=1` = Sub stream (chất lượng thấp hơn, nhẹ hơn)

#### 3. **V360 Pro (FH8626V100)**

**URL RTSP:**

Luồng HD: `rtsp://admin:admin123456@[CAMERA-IP]:8554/profile0`

Luồng SD: `rtsp://admin:admin123456@[CAMERA-IP]:8554/profile1`

**Cấu hình config.yaml:**

```yaml
# Default credentials - Khuyến nghị dùng SD Stream (profile1) để nhẹ hơn
camera:
  source: "rtsp://admin:admin123456@192.168.1.56:8554/profile1"  # Luồng SD
  # source: "rtsp://admin:admin123456@192.168.1.56:8554/profile0"  # Luồng HD
  width: 1280
  height: 720
  fps: 25
```

**App credentials (nếu default không hoạt động):**

```yaml
camera:
  source: "rtsp://0344572201:Trung123456a%40@192.168.1.56:8554/profile1"
  width: 1280
  height: 720
  fps: 25
```

**Giải thích Profiles:**
- `profile0` - Luồng HD (chất lượng cao, nặng hơn)
- `profile1` - Luồng SD (chất lượng thấp hơn, nhẹ hơn, **khuyến nghị** cho AI detection)
- `profile100` - Profile 100 (stream thứ 3, ít dùng)

#### 4. **TP-Link / Tapo**
```yaml
camera:
  source: "rtsp://admin:password@192.168.1.100:554/stream1"
```

Thử:
- `/stream1` = Main stream
- `/stream2` = Sub stream

#### 5. **Xiaomi / Mi Home**
```yaml
camera:
  source: "rtsp://username:password@192.168.1.100:8554/unicast"
```

#### 4. **Imou Camera**
```yaml
# Camera Imou với port 554 (RTSP standard) - Khuyến nghị
camera:
  source: "rtsp://admin:L223C2D3@192.168.1.53:554/cam/realmonitor?channel=1&subtype=1"  # Sub Stream (SD) - Port 554
  # source: "rtsp://admin:L223C2D3@192.168.1.53:554/cam/realmonitor?channel=1&subtype=0"  # Main Stream (HD) - Port 554
  # source: "rtsp://admin:L223C2D3@192.168.1.53:37777/cam/realmonitor?channel=1&subtype=1"  # Sub Stream (SD) - Port 37777
  # source: "rtsp://admin:L223C2D3@192.168.1.53:37777/cam/realmonitor?channel=1&subtype=0"  # Main Stream (HD) - Port 37777
  width: 1280
  height: 720
  fps: 25
```

**URL RTSP:**

**Port 554 (RTSP standard) - Khuyến nghị:**
- Luồng HD (Main): `rtsp://admin:L223C2D3@192.168.1.53:554/cam/realmonitor?channel=1&subtype=0`
- Luồng SD (Sub): `rtsp://admin:L223C2D3@192.168.1.53:554/cam/realmonitor?channel=1&subtype=1`

**Port 37777 (RTSP custom):**
- Luồng HD (Main): `rtsp://admin:L223C2D3@192.168.1.53:37777/cam/realmonitor?channel=1&subtype=0`
- Luồng SD (Sub): `rtsp://admin:L223C2D3@192.168.1.53:37777/cam/realmonitor?channel=1&subtype=1`

**Lưu ý:**
- Camera Imou có 2 ports RTSP: **554** (RTSP standard) và **37777** (RTSP custom)
- **Khuyến nghị dùng port 554** (RTSP standard) vì ổn định hơn
- Format: `/cam/realmonitor?channel=1&subtype=0` (Dahua format)
- `subtype=0` = Main stream (HD - chất lượng cao)
- `subtype=1` = Sub stream (SD - chất lượng thấp, nhẹ hơn)
- **Khuyến nghị dùng `subtype=1` (SD) với port 554** cho AI detection

#### 5. **Generic / ONVIF**
```yaml
camera:
  source: "rtsp://admin:password@192.168.1.100:554/stream"
```

Hoặc:
- `/live`
- `/media/video1`
- `/ch01/0`

### Cách tìm IP camera:

#### Method 1: Qua router
1. Login vào router (thường `192.168.1.1`)
2. Xem **Connected Devices**
3. Tìm camera trong danh sách

#### Method 2: Scan network
```bash
# macOS/Linux
sudo arp-scan --localnet

# Hoặc
nmap -sn 192.168.1.0/24
```

#### Method 3: App camera
- Hầu hết camera có app di động
- App thường hiển thị IP trong settings

### Test RTSP stream thủ công:

#### Dùng VLC:
1. Mở VLC
2. **Media** → **Open Network Stream**
3. Nhập: `rtsp://admin:password@192.168.1.100:554/stream`
4. Click Play

#### Dùng ffplay:
```bash
ffplay "rtsp://admin:password@192.168.1.100:554/stream"
```

---

## 🎬 Option 3: Video File (Test)

Nếu chưa có camera, test bằng video:

1. Tải video mẫu hoặc dùng video có sẵn

2. Cập nhật `config.yaml`:
```yaml
camera:
  source: "/path/to/video.mp4"
```

Hoặc dùng video mẫu online:
```yaml
camera:
  source: "https://sample-videos.com/video123/mp4/720/big_buck_bunny_720p_1mb.mp4"
```

---

## 🔧 Troubleshooting

### ❌ "Camera not found" / Cannot open camera

**Giải pháp:**

1. **Kiểm tra camera có online không:**
```bash
ping 192.168.1.100
```

2. **Test qua browser:**
- Mở browser, vào: `http://192.168.1.100`
- Login vào web interface camera
- Tìm RTSP URL trong settings

3. **Kiểm tra firewall:**
- Tắt firewall tạm thời để test
- Nếu OK, thêm rule cho port 554

4. **Thử các port khác:**
- Port 554 (RTSP standard)
- Port 8554 (alternative)
- Port 88 (một số camera Trung Quốc)

5. **Kiểm tra username/password:**
- Thử login qua web interface
- Reset password nếu quên

6. **Thử sub stream thay vì main stream:**
```yaml
# Thay vì Channels/101, thử Channels/102
camera:
  source: "rtsp://admin:password@192.168.1.100:554/Streaming/Channels/102"
```

### ❌ Stream mở được nhưng không có frame

**Giải pháp:**

1. **Giảm resolution:**
```yaml
camera:
  width: 640
  height: 480
```

2. **Tăng timeout:**
```python
# Thêm vào camera_ai.py
cap = cv2.VideoCapture(source)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
```

3. **Dùng sub stream:**
- Sub stream ít tải hơn, ổn định hơn
- Chất lượng thấp hơn nhưng đủ cho detection

### ❌ Lag, giật, chậm

**Giải pháp:**

1. **Dùng sub stream thay vì main stream**

2. **Giảm FPS:**
```yaml
camera:
  fps: 15  # Thay vì 30
```

3. **Giảm resolution:**
```yaml
camera:
  width: 640
  height: 480
```

4. **Check network:**
- Camera và máy tính cùng mạng LAN
- Dùng dây mạng thay vì WiFi (nếu được)

---

## 📝 Template config.yaml

### Webcam:
```yaml
camera:
  source: 0
  width: 1280
  height: 720
  fps: 30
```

### IP Camera (Main stream - chất lượng cao):
```yaml
camera:
  source: "rtsp://admin:password123@192.168.1.100:554/Streaming/Channels/101"
  width: 1920
  height: 1080
  fps: 30
```

### IP Camera (Sub stream - nhẹ hơn):
```yaml
camera:
  source: "rtsp://admin:password123@192.168.1.100:554/Streaming/Channels/102"
  width: 640
  height: 480
  fps: 15
```

### Video File:
```yaml
camera:
  source: "/Users/trantrung/Videos/test.mp4"
  width: 1280
  height: 720
  fps: 30
```

---

## ✅ Checklist

- [ ] Đã biết IP camera
- [ ] Đã biết username/password
- [ ] Đã test ping được camera
- [ ] Đã test mở web interface camera
- [ ] Đã tìm được RTSP URL
- [ ] Đã chạy `python test_camera.py`
- [ ] Thấy preview camera thành công
- [ ] Đã cập nhật `config.yaml`
- [ ] Đã chạy `python dashboard.py` thành công

---

## 🆘 Vẫn không được?

Cung cấp thông tin sau để được hỗ trợ:

1. **Hãng camera:** (Hikvision, Dahua, TP-Link, etc.)
2. **Model camera:** (vd: Hikvision DS-2CD2143G0-I)
3. **Kết nối:** (WiFi hay dây mạng)
4. **Lỗi gặp phải:** (copy log lỗi)
5. **Đã test gì:** (VLC, browser, etc.)

---

**Chúc bạn thành công! 🎉**

