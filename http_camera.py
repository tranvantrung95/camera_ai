"""
HTTP Camera Module
Lấy snapshot từ HTTP endpoint (fallback khi RTSP không hoạt động)
"""
import cv2
import requests
import numpy as np
import time
import threading
from urllib.parse import urlparse
from requests.auth import HTTPBasicAuth, HTTPDigestAuth

class HTTPCamera:
    """Camera HTTP Snapshot - Polling để tạo video stream"""
    
    def __init__(self, snapshot_url, fps=5, username=None, password=None, auth_type='basic'):
        """
        Khởi tạo HTTP Camera
        
        Args:
            snapshot_url: URL để lấy snapshot (http://...)
            fps: FPS mong muốn (số snapshot/giây)
            username: Username cho authentication
            password: Password cho authentication
            auth_type: 'basic' hoặc 'digest'
        """
        self.snapshot_url = snapshot_url
        self.fps = fps
        self.interval = 1.0 / fps if fps > 0 else 1.0
        
        # Parse URL để lấy auth info
        parsed = urlparse(snapshot_url)
        if parsed.username:
            self.username = parsed.username
            self.password = parsed.password
            # Remove auth từ URL
            self.snapshot_url = f"{parsed.scheme}://{parsed.hostname}:{parsed.port or 80}{parsed.path}"
        else:
            self.username = username
            self.password = password
        
        # Authentication
        if self.username and self.password:
            if auth_type == 'digest':
                self.auth = HTTPDigestAuth(self.username, self.password)
            else:
                self.auth = HTTPBasicAuth(self.username, self.password)
        else:
            self.auth = None
        
        # Frame buffer
        self.current_frame = None
        self.frame_lock = threading.Lock()
        self.is_running = False
        self.read_thread = None
        
        # Stats
        self.frame_count = 0
        self.last_update = time.time()
        
        print(f"📹 HTTP Camera: {self.snapshot_url}")
        print(f"   FPS: {fps}")
        print(f"   Username: {self.username or 'None'}")
        print(f"   Auth: {auth_type}")
    
    def start(self):
        """Bắt đầu lấy snapshot"""
        if self.is_running:
            return True
        
        # Test kết nối
        print("⏳ Đang test kết nối HTTP snapshot...")
        if not self._fetch_snapshot():
            print("❌ Không thể lấy snapshot từ HTTP endpoint")
            return False
        
        self.is_running = True
        
        # Start thread đọc snapshot
        self.read_thread = threading.Thread(target=self._read_loop, daemon=True)
        self.read_thread.start()
        
        # Đợi frame đầu tiên
        print("⏳ Đang đợi frame đầu tiên...")
        for i in range(10):  # Timeout 10 giây
            time.sleep(1)
            with self.frame_lock:
                if self.current_frame is not None:
                    h, w = self.current_frame.shape[:2]
                    print(f"✅ HTTP Camera đã kết nối! Resolution: {w}x{h}")
                    return True
            if i < 9:
                print(f"   ⏳ Đang đợi... ({i+1}/10)")
        
        print("⚠️  Timeout - Không nhận được snapshot sau 10 giây")
        return False
    
    def _fetch_snapshot(self):
        """Lấy snapshot từ HTTP endpoint"""
        try:
            response = requests.get(
                self.snapshot_url,
                auth=self.auth,
                timeout=5,
                stream=True
            )
            
            if response.status_code == 200:
                # Convert response content to image
                image_array = np.frombuffer(response.content, np.uint8)
                image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
                
                if image is not None:
                    return image
                else:
                    print("⚠️  Không thể decode image từ response")
                    return None
            else:
                print(f"⚠️  HTTP status code: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"⚠️  Lỗi lấy snapshot: {e}")
            return None
    
    def _read_loop(self):
        """Loop đọc snapshot định kỳ"""
        while self.is_running:
            start_time = time.time()
            
            # Lấy snapshot
            frame = self._fetch_snapshot()
            
            if frame is not None:
                with self.frame_lock:
                    self.current_frame = frame.copy()
                self.frame_count += 1
                self.last_update = time.time()
            else:
                # Nếu không lấy được, giữ frame cũ
                pass
            
            # Đợi đến lượt tiếp theo
            elapsed = time.time() - start_time
            sleep_time = max(0, self.interval - elapsed)
            if sleep_time > 0:
                time.sleep(sleep_time)
    
    def read(self):
        """
        Đọc frame hiện tại (tương thích với cv2.VideoCapture)
        
        Returns:
            ret: True nếu có frame
            frame: Frame hiện tại
        """
        with self.frame_lock:
            if self.current_frame is not None:
                return True, self.current_frame.copy()
            else:
                return False, None
    
    def isOpened(self):
        """Kiểm tra camera có mở không"""
        return self.is_running and self.current_frame is not None
    
    def release(self):
        """Giải phóng camera"""
        self.is_running = False
        
        if self.read_thread:
            self.read_thread.join(timeout=2)
        
        print("🧹 HTTP Camera released")
    
    def set(self, prop_id, value):
        """Giả lập set property"""
        if prop_id == cv2.CAP_PROP_FPS:
            self.fps = value
            self.interval = 1.0 / value if value > 0 else 1.0
        pass
    
    def get(self, prop_id):
        """Giả lập get property"""
        with self.frame_lock:
            if self.current_frame is not None:
                h, w = self.current_frame.shape[:2]
                if prop_id == cv2.CAP_PROP_FRAME_WIDTH:
                    return w
                elif prop_id == cv2.CAP_PROP_FRAME_HEIGHT:
                    return h
        if prop_id == cv2.CAP_PROP_FPS:
            return self.fps
        return 0

def test_http_camera(snapshot_url, username=None, password=None):
    """Test HTTP camera"""
    print("=" * 70)
    print("🎥 TEST HTTP CAMERA")
    print("=" * 70)
    
    # Parse URL để lấy auth
    parsed = urlparse(snapshot_url)
    if parsed.username:
        username = parsed.username
        password = parsed.password
        # Remove auth từ URL
        snapshot_url = f"{parsed.scheme}://{parsed.hostname}:{parsed.port or 80}{parsed.path}"
    
    cam = HTTPCamera(snapshot_url, fps=5, username=username, password=password)
    
    if cam.start():
        print("\n✅ Camera đã kết nối!")
        print("👁️  Nhấn Q để thoát\n")
        
        try:
            frame_count = 0
            start_time = time.time()
            
            while True:
                ret, frame = cam.read()
                
                if ret:
                    frame_count += 1
                    elapsed = time.time() - start_time
                    
                    if elapsed > 0:
                        fps = frame_count / elapsed
                        cv2.putText(frame, f"FPS: {fps:.1f} | Frames: {frame_count}", 
                                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    
                    cv2.imshow('HTTP Camera - Press Q to quit', frame)
                    
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
                else:
                    print("⚠️  Không đọc được frame")
                    time.sleep(0.1)
        
        except KeyboardInterrupt:
            print("\n⏹️  Stopped by user")
        finally:
            cam.release()
            cv2.destroyAllWindows()
        
        print("\n✅ Test hoàn tất!")
    else:
        print("\n❌ Không thể kết nối camera")

if __name__ == '__main__':
    # Test với camera Imou
    # Thử các URL snapshot phổ biến
    urls = [
        "http://admin:L223C2D3@192.168.1.53:80/snap.jpg",
        "http://admin:L223C2D3@192.168.1.53:37777/snap.jpg",
        "http://admin:L223C2D3@192.168.1.53/cgi-bin/snapshot.cgi",
        "http://admin:L223C2D3@192.168.1.53/Streaming/channels/1/picture",
    ]
    
    print("Bạn có thể thay đổi URL nếu cần:")
    custom_url = input(f"Nhập URL (Enter để test các URL mặc định): ").strip()
    
    if custom_url:
        test_http_camera(custom_url)
    else:
        # Test từng URL
        for url in urls:
            print(f"\n🔍 Test: {url}")
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200 and response.headers.get('content-type', '').startswith('image'):
                    print(f"✅ URL hoạt động: {url}")
                    test_http_camera(url)
                    break
            except Exception as e:
                print(f"❌ Lỗi: {e}")
                continue



