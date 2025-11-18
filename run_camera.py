#!/usr/bin/env python3
"""
Run Camera AI với RTSP Camera
Sử dụng: python run_camera.py
"""

import sys
import os
from pathlib import Path

# Thêm thư mục hiện tại vào Python path
sys.path.insert(0, str(Path(__file__).parent))

def main():
    """Chạy Camera AI với cấu hình từ config.yaml"""
    
    # Load config để xem nguồn camera
    import yaml
    with open('config.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    source = config['camera']['source']
    is_rtsp = isinstance(source, str) and source.startswith('rtsp://')
    
    print("\n" + "=" * 70)
    if is_rtsp:
        print("🎥 CAMERA AI - RTSP MODE")
        print("=" * 70)
        print(f"\n📡 Camera: {source[:30]}***")
    else:
        print("🎥 CAMERA AI - VIDEO MODE")
        print("=" * 70)
        print(f"\n📹 Video: {source}")
    
    print("🤖 AI Models: YOLOv11 + YOLOv8 + EasyOCR")
    print(f"🌐 Dashboard: http://localhost:{config['dashboard']['port']}")
    print("\n" + "=" * 70)
    
    try:
        from dashboard import app, camera_loop
        import threading
        
        print("\n🚀 Đang khởi động...")
        print("   • Loading AI models...")
        print("   • Connecting to camera...")
        print("   • Starting dashboard...")
        
        # Chạy camera loop trong thread riêng
        camera_thread = threading.Thread(target=camera_loop, daemon=True)
        camera_thread.start()
        
        print("\n✅ Sẵn sàng!")
        print(f"\n📱 Mở trình duyệt: http://localhost:{config['dashboard']['port']}")
        print("\n⌨️  Nhấn Ctrl+C để dừng\n")
        
        # Chạy Flask app
        app.run(
            host=config['dashboard']['host'],
            port=config['dashboard']['port'],
            debug=False,
            use_reloader=False
        )
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Đang dừng...")
        print("✅ Đã dừng!")
        
    except Exception as e:
        print(f"\n❌ LỖI: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

