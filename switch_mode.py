#!/usr/bin/env python3
"""
Script chuyển đổi nhanh giữa Video Mode và Camera Mode
Sử dụng: python switch_mode.py [video|camera]
"""

import sys
import yaml
from pathlib import Path

# Cấu hình mặc định
VIDEO_SOURCE = "videos/11933881_2160_3840_30fps.mp4"
CAMERA_SOURCE = "rtsp://admin:L223C2D3@192.168.1.53:554/cam/realmonitor?channel=1&subtype=1"

CONFIG_FILE = "config.yaml"

def load_config():
    """Load config hiện tại"""
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def save_config(config):
    """Lưu config"""
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

def switch_to_video():
    """Chuyển sang Video Mode"""
    config = load_config()
    config['camera']['source'] = VIDEO_SOURCE
    save_config(config)
    
    print("✅ Đã chuyển sang VIDEO MODE")
    print(f"📹 Source: {VIDEO_SOURCE}")
    print("\n🚀 Chạy: python run_camera.py")

def switch_to_camera():
    """Chuyển sang Camera Mode"""
    config = load_config()
    config['camera']['source'] = CAMERA_SOURCE
    save_config(config)
    
    print("✅ Đã chuyển sang CAMERA MODE (RTSP)")
    print(f"📡 Source: {CAMERA_SOURCE[:50]}...")
    print("\n🚀 Chạy: python run_camera.py")

def show_current():
    """Hiển thị mode hiện tại"""
    config = load_config()
    source = config['camera']['source']
    
    print("=" * 70)
    print("📊 CAMERA AI - MODE HIỆN TẠI")
    print("=" * 70)
    
    if isinstance(source, str) and source.startswith('rtsp://'):
        print("\n✅ Mode: CAMERA (RTSP)")
        print(f"📡 Source: {source[:50]}...")
    elif isinstance(source, str) and source.endswith(('.mp4', '.avi', '.mov', '.mkv')):
        print("\n✅ Mode: VIDEO")
        print(f"📹 Source: {source}")
    else:
        print("\n✅ Mode: WEBCAM")
        print(f"📷 Source: {source}")
    
    print("\n" + "=" * 70)

def show_usage():
    """Hiển thị hướng dẫn"""
    print("""
╔══════════════════════════════════════════════════════════════════╗
║                  CAMERA AI - MODE SWITCHER                       ║
╚══════════════════════════════════════════════════════════════════╝

Sử dụng:
    python switch_mode.py [command]

Commands:
    video      - Chuyển sang Video Mode
    camera     - Chuyển sang Camera Mode (RTSP)
    status     - Xem mode hiện tại
    help       - Hiển thị trợ giúp

Ví dụ:
    python switch_mode.py video
    python switch_mode.py camera
    python switch_mode.py status

Sau khi chuyển mode, chạy:
    python run_camera.py
""")

def main():
    """Main function"""
    
    if len(sys.argv) < 2:
        show_current()
        print("\n💡 Sử dụng: python switch_mode.py [video|camera|status|help]")
        return
    
    command = sys.argv[1].lower()
    
    if command == 'video':
        switch_to_video()
    elif command == 'camera' or command == 'rtsp':
        switch_to_camera()
    elif command == 'status' or command == 'current':
        show_current()
    elif command == 'help' or command == '-h' or command == '--help':
        show_usage()
    else:
        print(f"❌ Lệnh không hợp lệ: {command}")
        print("💡 Sử dụng: python switch_mode.py [video|camera|status|help]")
        sys.exit(1)

if __name__ == "__main__":
    main()

