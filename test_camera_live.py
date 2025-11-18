#!/usr/bin/env python3
"""
Test Camera RTSP - Live Video (Hiển thị video)
Sử dụng: python test_camera_live.py
Nhấn 'q' để thoát, 's' để chụp ảnh
"""

import cv2
import time
from datetime import datetime

# RTSP URL của camera
RTSP_URL = "rtsp://admin:L223C2D3@192.168.1.53:554/cam/realmonitor?channel=1&subtype=1"

def main():
    """Hiển thị video live từ camera"""
    
    print("=" * 70)
    print("🎥 TEST CAMERA RTSP - LIVE VIDEO")
    print("=" * 70)
    print(f"\n📡 Đang kết nối đến camera...")
    
    # Tạo VideoCapture
    cap = cv2.VideoCapture(RTSP_URL, cv2.CAP_FFMPEG)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    
    if not cap.isOpened():
        print("❌ Không thể kết nối đến camera!")
        print("\n🔍 Hãy chạy test nhanh trước:")
        print("   python test_camera_quick.py")
        return False
    
    print("✅ Kết nối thành công!")
    
    # Lấy thông tin
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    
    print(f"\n📊 Camera: {width}x{height} @ {fps}fps")
    print("\n⌨️  ĐIỀU KHIỂN:")
    print("   • Nhấn 'q' hoặc ESC để thoát")
    print("   • Nhấn 's' để chụp ảnh")
    print("\n🎬 Đang hiển thị video...\n")
    
    frame_count = 0
    start_time = time.time()
    last_fps_time = start_time
    fps_counter = 0
    current_fps = 0
    
    try:
        while True:
            ret, frame = cap.read()
            
            if not ret:
                print("⚠️  Mất kết nối! Đang thử lại...")
                time.sleep(1)
                continue
            
            frame_count += 1
            fps_counter += 1
            
            # Tính FPS
            current_time = time.time()
            if current_time - last_fps_time >= 1.0:
                current_fps = fps_counter
                fps_counter = 0
                last_fps_time = current_time
            
            # Vẽ thông tin
            cv2.putText(frame, f"Camera RTSP - Live", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                       0.7, (0, 255, 0), 2)
            
            cv2.putText(frame, f"FPS: {current_fps}", 
                       (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 
                       0.6, (0, 255, 255), 2)
            
            cv2.putText(frame, f"Frame: {frame_count}", 
                       (10, 85), cv2.FONT_HERSHEY_SIMPLEX, 
                       0.5, (255, 255, 255), 1)
            
            timestamp = datetime.now().strftime('%H:%M:%S')
            cv2.putText(frame, timestamp, 
                       (width - 120, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                       0.6, (255, 255, 255), 2)
            
            # Hiển thị
            cv2.imshow('Camera RTSP - Live Video', frame)
            
            # Xử lý phím
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q') or key == 27:
                print("👋 Đang thoát...")
                break
                
            elif key == ord('s'):
                filename = f"snapshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                cv2.imwrite(filename, frame)
                print(f"📸 Đã lưu: {filename}")
    
    except KeyboardInterrupt:
        print("\n⚠️  Đã dừng bởi người dùng")
    
    finally:
        elapsed = time.time() - start_time
        print("\n" + "=" * 70)
        print("📊 THỐNG KÊ")
        print("=" * 70)
        print(f"   • Tổng frames: {frame_count}")
        print(f"   • Thời gian: {elapsed:.1f}s")
        if elapsed > 0:
            print(f"   • FPS trung bình: {frame_count/elapsed:.1f}")
        print("\n✅ Hoàn tất!")
        
        cap.release()
        cv2.destroyAllWindows()
    
    return True


if __name__ == "__main__":
    main()

