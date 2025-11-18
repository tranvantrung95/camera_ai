#!/usr/bin/env python3
"""
Test Camera RTSP - Quick Test (Tự động)
Sử dụng: python test_camera_quick.py
"""

import cv2
import time
from datetime import datetime

# RTSP URL của camera
RTSP_URL = "rtsp://admin:L223C2D3@192.168.1.53:554/cam/realmonitor?channel=1&subtype=1"

def main():
    """Test nhanh camera RTSP"""
    
    print("=" * 70)
    print("🎥 TEST CAMERA RTSP - QUICK MODE")
    print("=" * 70)
    print(f"\n📡 RTSP URL: rtsp://admin:***@192.168.1.53:554/...")
    print(f"⏰ Thời gian: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n🔄 Đang kết nối...")
    
    # Tạo VideoCapture với RTSP
    cap = cv2.VideoCapture(RTSP_URL, cv2.CAP_FFMPEG)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    
    if not cap.isOpened():
        print("\n" + "=" * 70)
        print("❌ LỖI: KHÔNG THỂ KẾT NỐI ĐẾN CAMERA!")
        print("=" * 70)
        print("\n🔍 KIỂM TRA:")
        print("   1. ✓ Camera có bật không?")
        print("      → ping 192.168.1.53")
        print("\n   2. ✓ Port 554 có mở không?")
        print("      → nc -zv 192.168.1.53 554")
        print("\n   3. ✓ Username/password đúng chưa?")
        print("      → admin / L223C2D3")
        print("\n   4. ✓ VLC có xem được không?")
        print("      → Mở VLC và paste RTSP URL")
        print("\n   5. ✓ Firewall có chặn không?")
        print("      → Tắt firewall thử")
        print("\n" + "=" * 70)
        return False
    
    print("✅ KẾT NỐI THÀNH CÔNG!")
    
    # Lấy thông tin camera
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    backend = cap.getBackendName()
    
    print("\n" + "=" * 70)
    print("📊 THÔNG TIN CAMERA")
    print("=" * 70)
    print(f"   • Độ phân giải: {width}x{height}")
    print(f"   • FPS: {fps}")
    print(f"   • Backend: {backend}")
    
    print("\n🎬 Đang đọc 10 frames để test...")
    
    success_count = 0
    fail_count = 0
    start_time = time.time()
    
    for i in range(10):
        ret, frame = cap.read()
        
        if ret:
            success_count += 1
            print(f"   ✅ Frame {i+1}/10 - OK ({frame.shape[1]}x{frame.shape[0]})")
            
            # Lưu frame đầu tiên
            if i == 0:
                filename = f"test_snapshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                cv2.imwrite(filename, frame)
                print(f"      📸 Đã lưu: {filename}")
        else:
            fail_count += 1
            print(f"   ❌ Frame {i+1}/10 - FAILED")
        
        time.sleep(0.1)
    
    elapsed = time.time() - start_time
    
    print("\n" + "=" * 70)
    print("📊 KẾT QUẢ TEST")
    print("=" * 70)
    print(f"   • Thành công: {success_count}/10 frames")
    print(f"   • Thất bại: {fail_count}/10 frames")
    print(f"   • Thời gian: {elapsed:.2f}s")
    print(f"   • FPS thực tế: {success_count/elapsed:.1f}")
    
    cap.release()
    
    if success_count >= 8:
        print("\n" + "=" * 70)
        print("✅ CAMERA HOẠT ĐỘNG TỐT!")
        print("=" * 70)
        print("\n🚀 BƯỚC TIẾP THEO:")
        print("   1. Chạy Camera AI đầy đủ:")
        print("      python run_camera.py")
        print("\n   2. Hoặc xem video live:")
        print("      python test_camera_live.py")
        print("\n   3. Mở dashboard:")
        print("      http://localhost:5000")
        print("\n" + "=" * 70)
        return True
    else:
        print("\n" + "=" * 70)
        print("⚠️  CAMERA KHÔNG ỔN ĐỊNH!")
        print("=" * 70)
        print("\n🔧 KHUYẾN NGHỊ:")
        print("   • Kiểm tra kết nối mạng")
        print("   • Thử giảm độ phân giải (subtype=1)")
        print("   • Kiểm tra băng thông mạng")
        print("\n" + "=" * 70)
        return False


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Đã dừng bởi người dùng")
    except Exception as e:
        print(f"\n❌ LỖI: {e}")
        import traceback
        traceback.print_exc()

