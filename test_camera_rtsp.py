#!/usr/bin/env python3
"""
Test Camera RTSP - Kiểm tra kết nối camera qua RTSP
Sử dụng: python test_camera_rtsp.py
"""

import cv2
import time
from datetime import datetime

# RTSP URL của camera
RTSP_URL = "rtsp://admin:L223C2D3@192.168.1.53:554/cam/realmonitor?channel=1&subtype=1"

def test_rtsp_connection():
    """Test kết nối RTSP và hiển thị video"""
    
    print("=" * 70)
    print("🎥 TEST CAMERA RTSP")
    print("=" * 70)
    print(f"\n📡 RTSP URL: {RTSP_URL}")
    print(f"⏰ Thời gian: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n🔄 Đang kết nối...")
    
    # Tạo VideoCapture với RTSP
    cap = cv2.VideoCapture(RTSP_URL, cv2.CAP_FFMPEG)
    
    # Cấu hình buffer để giảm độ trễ
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    
    if not cap.isOpened():
        print("\n❌ LỖI: Không thể kết nối đến camera!")
        print("\n🔍 KIỂM TRA:")
        print("   1. Camera có bật không?")
        print("   2. IP address đúng chưa? (192.168.1.53)")
        print("   3. Username/password đúng chưa? (admin/L223C2D3)")
        print("   4. Port 554 có mở không?")
        print("   5. Firewall có chặn không?")
        return False
    
    print("\n✅ KẾT NỐI THÀNH CÔNG!")
    
    # Lấy thông tin camera
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    
    print("\n📊 THÔNG TIN CAMERA:")
    print(f"   • Độ phân giải: {width}x{height}")
    print(f"   • FPS: {fps}")
    print(f"   • Backend: {cap.getBackendName()}")
    
    print("\n" + "=" * 70)
    print("🎬 BẮT ĐẦU HIỂN THỊ VIDEO")
    print("=" * 70)
    print("\n⌨️  ĐIỀU KHIỂN:")
    print("   • Nhấn 'q' hoặc 'ESC' để thoát")
    print("   • Nhấn 's' để chụp ảnh")
    print("   • Nhấn 'i' để xem thông tin frame")
    print("\n")
    
    frame_count = 0
    start_time = time.time()
    last_fps_time = start_time
    fps_counter = 0
    current_fps = 0
    
    try:
        while True:
            ret, frame = cap.read()
            
            if not ret:
                print("\n⚠️  CẢNH BÁO: Không đọc được frame!")
                print("   Đang thử kết nối lại...")
                time.sleep(1)
                continue
            
            frame_count += 1
            fps_counter += 1
            
            # Tính FPS thực tế
            current_time = time.time()
            if current_time - last_fps_time >= 1.0:
                current_fps = fps_counter
                fps_counter = 0
                last_fps_time = current_time
            
            # Vẽ thông tin lên frame
            info_y = 30
            cv2.putText(frame, f"Camera RTSP - Live Feed", 
                       (10, info_y), cv2.FONT_HERSHEY_SIMPLEX, 
                       0.7, (0, 255, 0), 2)
            
            info_y += 30
            cv2.putText(frame, f"FPS: {current_fps}", 
                       (10, info_y), cv2.FONT_HERSHEY_SIMPLEX, 
                       0.6, (0, 255, 255), 2)
            
            info_y += 25
            cv2.putText(frame, f"Frame: {frame_count}", 
                       (10, info_y), cv2.FONT_HERSHEY_SIMPLEX, 
                       0.5, (255, 255, 255), 1)
            
            info_y += 25
            cv2.putText(frame, f"Size: {width}x{height}", 
                       (10, info_y), cv2.FONT_HERSHEY_SIMPLEX, 
                       0.5, (255, 255, 255), 1)
            
            # Hiển thị thời gian
            timestamp = datetime.now().strftime('%H:%M:%S')
            cv2.putText(frame, timestamp, 
                       (width - 120, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                       0.6, (255, 255, 255), 2)
            
            # Hiển thị frame
            cv2.imshow('Camera RTSP Test', frame)
            
            # Xử lý phím bấm
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q') or key == 27:  # 'q' hoặc ESC
                print("\n👋 Đang thoát...")
                break
                
            elif key == ord('s'):  # Chụp ảnh
                filename = f"snapshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                cv2.imwrite(filename, frame)
                print(f"📸 Đã lưu ảnh: {filename}")
                
            elif key == ord('i'):  # Hiển thị info
                elapsed = time.time() - start_time
                print(f"\n📊 Thông tin hiện tại:")
                print(f"   • Frame đã đọc: {frame_count}")
                print(f"   • Thời gian chạy: {elapsed:.1f}s")
                print(f"   • FPS trung bình: {frame_count/elapsed:.1f}")
                print(f"   • FPS hiện tại: {current_fps}")
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Nhận Ctrl+C - Đang dừng...")
    
    except Exception as e:
        print(f"\n❌ LỖI: {e}")
    
    finally:
        # Thống kê cuối cùng
        elapsed = time.time() - start_time
        print("\n" + "=" * 70)
        print("📊 THỐNG KÊ CUỐI CÙNG")
        print("=" * 70)
        print(f"   • Tổng frames: {frame_count}")
        print(f"   • Thời gian chạy: {elapsed:.1f}s")
        if elapsed > 0:
            print(f"   • FPS trung bình: {frame_count/elapsed:.1f}")
        print("\n✅ Đã giải phóng tài nguyên")
        
        cap.release()
        cv2.destroyAllWindows()
    
    return True


def test_quick_capture():
    """Test nhanh - chỉ chụp 1 frame"""
    
    print("\n" + "=" * 70)
    print("⚡ TEST NHANH - Chụp 1 frame")
    print("=" * 70)
    
    cap = cv2.VideoCapture(RTSP_URL, cv2.CAP_FFMPEG)
    
    if not cap.isOpened():
        print("❌ Không thể kết nối!")
        return False
    
    print("✅ Kết nối thành công!")
    print("📸 Đang chụp frame...")
    
    ret, frame = cap.read()
    
    if ret:
        filename = f"test_frame_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        cv2.imwrite(filename, frame)
        print(f"✅ Đã lưu: {filename}")
        print(f"   Kích thước: {frame.shape[1]}x{frame.shape[0]}")
    else:
        print("❌ Không đọc được frame!")
    
    cap.release()
    return ret


def main():
    """Main function"""
    
    print("\n" + "=" * 70)
    print("🎥 CAMERA RTSP TEST TOOL")
    print("=" * 70)
    print("\nChọn chế độ test:")
    print("  1. Test đầy đủ (hiển thị video live)")
    print("  2. Test nhanh (chụp 1 frame)")
    print("  3. Thoát")
    
    try:
        choice = input("\nNhập lựa chọn (1-3): ").strip()
        
        if choice == "1":
            test_rtsp_connection()
        elif choice == "2":
            test_quick_capture()
        elif choice == "3":
            print("\n👋 Tạm biệt!")
        else:
            print("\n❌ Lựa chọn không hợp lệ!")
            
    except KeyboardInterrupt:
        print("\n\n👋 Tạm biệt!")
    
    print("\n")


if __name__ == "__main__":
    main()

