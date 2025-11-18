#!/usr/bin/env python3
"""
Test Camera RTSP - Debug Mode
Thử nhiều phương pháp kết nối khác nhau
"""

import cv2
import os
import sys

# RTSP URL
RTSP_URL = "rtsp://admin:L223C2D3@192.168.1.53:554/cam/realmonitor?channel=1&subtype=1"

print("=" * 70)
print("🔍 CAMERA RTSP - DEBUG MODE")
print("=" * 70)
print(f"\n📡 URL: rtsp://admin:***@192.168.1.53:554/...")

# Kiểm tra OpenCV version và backends
print(f"\n📦 OpenCV Version: {cv2.__version__}")
print(f"📦 Python Version: {sys.version}")

# Liệt kê backends có sẵn
backends = []
for backend_name in dir(cv2):
    if backend_name.startswith('CAP_'):
        backends.append(backend_name)

print(f"\n🔧 Available Backends: {len(backends)}")
print("   " + ", ".join(backends[:10]) + "...")

print("\n" + "=" * 70)
print("🧪 THỬ CÁC PHƯƠNG PHÁP KẾT NỐI")
print("=" * 70)

# Phương pháp 1: FFMPEG (mặc định)
print("\n1️⃣  Thử với CAP_FFMPEG...")
try:
    cap1 = cv2.VideoCapture(RTSP_URL, cv2.CAP_FFMPEG)
    if cap1.isOpened():
        ret, frame = cap1.read()
        if ret:
            print("   ✅ THÀNH CÔNG với CAP_FFMPEG!")
            print(f"   📊 Frame: {frame.shape[1]}x{frame.shape[0]}")
            cv2.imwrite("test_ffmpeg.jpg", frame)
            print("   📸 Đã lưu: test_ffmpeg.jpg")
            cap1.release()
        else:
            print("   ⚠️  Mở được nhưng không đọc được frame")
            cap1.release()
    else:
        print("   ❌ Không mở được với CAP_FFMPEG")
except Exception as e:
    print(f"   ❌ Lỗi: {e}")

# Phương pháp 2: GStreamer
print("\n2️⃣  Thử với CAP_GSTREAMER...")
try:
    cap2 = cv2.VideoCapture(RTSP_URL, cv2.CAP_GSTREAMER)
    if cap2.isOpened():
        ret, frame = cap2.read()
        if ret:
            print("   ✅ THÀNH CÔNG với CAP_GSTREAMER!")
            print(f"   📊 Frame: {frame.shape[1]}x{frame.shape[0]}")
            cv2.imwrite("test_gstreamer.jpg", frame)
            print("   📸 Đã lưu: test_gstreamer.jpg")
            cap2.release()
        else:
            print("   ⚠️  Mở được nhưng không đọc được frame")
            cap2.release()
    else:
        print("   ❌ Không mở được với CAP_GSTREAMER")
except Exception as e:
    print(f"   ❌ Lỗi: {e}")

# Phương pháp 3: Không chỉ định backend
print("\n3️⃣  Thử không chỉ định backend (auto)...")
try:
    cap3 = cv2.VideoCapture(RTSP_URL)
    if cap3.isOpened():
        ret, frame = cap3.read()
        if ret:
            print("   ✅ THÀNH CÔNG với AUTO backend!")
            print(f"   📊 Frame: {frame.shape[1]}x{frame.shape[0]}")
            print(f"   🔧 Backend: {cap3.getBackendName()}")
            cv2.imwrite("test_auto.jpg", frame)
            print("   📸 Đã lưu: test_auto.jpg")
            cap3.release()
        else:
            print("   ⚠️  Mở được nhưng không đọc được frame")
            cap3.release()
    else:
        print("   ❌ Không mở được với AUTO backend")
except Exception as e:
    print(f"   ❌ Lỗi: {e}")

# Phương pháp 4: Thử với TCP transport
print("\n4️⃣  Thử với TCP transport (thay vì UDP)...")
rtsp_tcp = RTSP_URL + "&tcp"
try:
    cap4 = cv2.VideoCapture(rtsp_tcp, cv2.CAP_FFMPEG)
    if cap4.isOpened():
        ret, frame = cap4.read()
        if ret:
            print("   ✅ THÀNH CÔNG với TCP transport!")
            print(f"   📊 Frame: {frame.shape[1]}x{frame.shape[0]}")
            cv2.imwrite("test_tcp.jpg", frame)
            print("   📸 Đã lưu: test_tcp.jpg")
            cap4.release()
        else:
            print("   ⚠️  Mở được nhưng không đọc được frame")
            cap4.release()
    else:
        print("   ❌ Không mở được với TCP transport")
except Exception as e:
    print(f"   ❌ Lỗi: {e}")

# Phương pháp 5: Thử với environment variables
print("\n5️⃣  Thử với OPENCV_FFMPEG_CAPTURE_OPTIONS...")
try:
    os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;tcp|timeout;5000000"
    cap5 = cv2.VideoCapture(RTSP_URL, cv2.CAP_FFMPEG)
    if cap5.isOpened():
        ret, frame = cap5.read()
        if ret:
            print("   ✅ THÀNH CÔNG với FFMPEG options!")
            print(f"   📊 Frame: {frame.shape[1]}x{frame.shape[0]}")
            cv2.imwrite("test_ffmpeg_opts.jpg", frame)
            print("   📸 Đã lưu: test_ffmpeg_opts.jpg")
            cap5.release()
        else:
            print("   ⚠️  Mở được nhưng không đọc được frame")
            cap5.release()
    else:
        print("   ❌ Không mở được với FFMPEG options")
except Exception as e:
    print(f"   ❌ Lỗi: {e}")

# Phương pháp 6: Thử URL đơn giản hơn
print("\n6️⃣  Thử URL đơn giản hơn...")
simple_url = "rtsp://admin:L223C2D3@192.168.1.53:554"
try:
    cap6 = cv2.VideoCapture(simple_url, cv2.CAP_FFMPEG)
    if cap6.isOpened():
        ret, frame = cap6.read()
        if ret:
            print("   ✅ THÀNH CÔNG với URL đơn giản!")
            print(f"   📊 Frame: {frame.shape[1]}x{frame.shape[0]}")
            cv2.imwrite("test_simple.jpg", frame)
            print("   📸 Đã lưu: test_simple.jpg")
            cap6.release()
        else:
            print("   ⚠️  Mở được nhưng không đọc được frame")
            cap6.release()
    else:
        print("   ❌ Không mở được với URL đơn giản")
except Exception as e:
    print(f"   ❌ Lỗi: {e}")

print("\n" + "=" * 70)
print("📊 KẾT LUẬN")
print("=" * 70)

# Kiểm tra file nào được tạo
test_files = ["test_ffmpeg.jpg", "test_gstreamer.jpg", "test_auto.jpg", 
              "test_tcp.jpg", "test_ffmpeg_opts.jpg", "test_simple.jpg"]
success_files = [f for f in test_files if os.path.exists(f)]

if success_files:
    print(f"\n✅ CÓ {len(success_files)} PHƯƠNG PHÁP THÀNH CÔNG!")
    print("\n📸 Các file đã tạo:")
    for f in success_files:
        size = os.path.getsize(f)
        print(f"   • {f} ({size:,} bytes)")
    
    print("\n🎯 KHUYẾN NGHỊ:")
    print("   Sử dụng phương pháp đã thành công để cập nhật code!")
else:
    print("\n❌ TẤT CẢ PHƯƠNG PHÁP ĐỀU THẤT BẠI!")
    print("\n🔍 NGUYÊN NHÂN CÓ THỂ:")
    print("   1. OpenCV không được build với FFMPEG support")
    print("   2. Firewall/Security software chặn Python")
    print("   3. VLC dùng codec/transport khác")
    print("   4. Camera chỉ cho phép 1 kết nối RTSP")
    
    print("\n💡 GIẢI PHÁP:")
    print("   1. Cài đặt lại opencv-python:")
    print("      pip uninstall opencv-python")
    print("      pip install opencv-python")
    
    print("\n   2. Hoặc dùng opencv-contrib:")
    print("      pip install opencv-contrib-python")
    
    print("\n   3. Cài đặt ffmpeg:")
    print("      brew install ffmpeg")
    
    print("\n   4. Thử dùng GStreamer:")
    print("      brew install gstreamer gst-plugins-base gst-plugins-good")

print("\n" + "=" * 70)

