"""
FFMPEG Camera Module
Đọc RTSP stream qua FFMPEG subprocess (hoạt động tốt hơn OpenCV trên macOS)
"""
import cv2
import subprocess
import numpy as np
import threading
import queue
import time

class FFMPEGCamera:
    """Camera RTSP qua FFMPEG"""
    
    def __init__(self, rtsp_url, width=1280, height=720, fps=25):
        """
        Khởi tạo FFMPEG Camera
        
        Args:
            rtsp_url: RTSP URL
            width: Độ rộng (có thể resize)
            height: Độ cao (có thể resize)
            fps: FPS mong muốn
        """
        self.rtsp_url = rtsp_url
        self.width = width
        self.height = height
        self.fps = fps
        
        self.process = None
        self.frame_queue = queue.Queue(maxsize=2)
        self.is_running = False
        self.current_frame = None
        self.frame_lock = threading.Lock()
        
        print(f"📹 FFMPEG Camera: {rtsp_url}")
        print(f"   Resolution: {width}x{height}")
        print(f"   FPS: {fps}")
    
    def start(self):
        """Bắt đầu đọc stream"""
        if self.is_running:
            return True
        
        # FFMPEG command để đọc RTSP và output raw video
        # Dùng command tối ưu để giảm delay và ổn định hơn
        cmd = [
            'ffmpeg',
            '-hide_banner',
            '-loglevel', 'warning',  # Giảm log output
            '-fflags', 'nobuffer',  # Không buffer để giảm delay
            '-flags', 'low_delay',  # Low delay mode
            '-rtsp_transport', 'tcp',  # Dùng TCP thay vì UDP (ổn định hơn)
            '-i', self.rtsp_url,
            '-an',  # Bỏ audio (không cần cho AI detection)
            '-vf', f'scale={self.width}:{self.height}',  # Resize về resolution mong muốn
            '-pix_fmt', 'bgr24',  # OpenCV format
            '-f', 'rawvideo',
            '-r', str(self.fps),  # FPS
            'pipe:1'  # Output to stdout
        ]
        
        try:
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                bufsize=10**8  # Buffer lớn hơn
            )
            
            self.is_running = True
            
            # Start thread đọc stderr để debug
            self.stderr_thread = threading.Thread(target=self._read_stderr, daemon=True)
            self.stderr_thread.start()
            
            # Start thread đọc frames
            self.read_thread = threading.Thread(target=self._read_frames, daemon=True)
            self.read_thread.start()
            
            # Đợi frame đầu tiên (tăng thời gian đợi)
            print("   ⏳ Đang kết nối stream...")
            for i in range(10):  # Đợi tối đa 10 giây
                time.sleep(1)
                if self.current_frame is not None:
                    # Cập nhật resolution thực tế
                    h, w = self.current_frame.shape[:2]
                    self.height = h
                    self.width = w
                    print(f"✅ FFMPEG Camera đã kết nối! Resolution: {w}x{h}")
                    return True
                if i < 9:
                    print(f"   ⏳ Đang đợi... ({i+1}/10)")
            
            print(f"⚠️  Timeout - Không nhận được frame sau 10 giây")
            # In stderr để debug
            if hasattr(self, 'stderr_output'):
                print(f"   FFMPEG stderr: {self.stderr_output[:500]}")
            return False
                
        except Exception as e:
            print(f"❌ Lỗi khởi động FFMPEG: {e}")
            import traceback
            traceback.print_exc()
            self.is_running = False
            return False
    
    def _read_stderr(self):
        """Đọc stderr từ FFMPEG để debug và detect resolution"""
        self.stderr_output = ""
        if self.process and self.process.stderr:
            try:
                for line in iter(self.process.stderr.readline, b''):
                    if not self.is_running:
                        break
                    line_str = line.decode('utf-8', errors='ignore')
                    self.stderr_output += line_str
                    
                    # Detect resolution từ stderr
                    # Format: "Stream #0:0: Video: h264, yuvj420p(pc, bt709, progressive), 1920x1080"
                    if 'Video:' in line_str and 'x' in line_str:
                        import re
                        match = re.search(r'(\d+)x(\d+)', line_str)
                        if match:
                            w, h = int(match.group(1)), int(match.group(2))
                            if w > 0 and h > 0:
                                self.width = w
                                self.height = h
                                print(f"   📐 Detected resolution from stream: {w}x{h}")
                    
                    # In lỗi nếu có
                    if 'error' in line_str.lower() or 'failed' in line_str.lower():
                        print(f"   ⚠️  FFMPEG: {line_str.strip()}")
            except Exception as e:
                pass
    
    def _read_frames(self):
        """Thread đọc frames từ FFMPEG"""
        # Đợi một chút để stderr thread detect resolution
        time.sleep(1)
        
        # Tính frame size từ resolution (đã được scale về width x height)
        frame_size = self.width * self.height * 3
        print(f"   📐 Frame size: {self.width}x{self.height} = {frame_size} bytes")
        
        first_frame = True
        
        while self.is_running and self.process:
            try:
                # Đọc raw frame từ stdout
                raw_frame = self.process.stdout.read(frame_size)
                
                if len(raw_frame) == 0:
                    if self.is_running:
                        time.sleep(0.1)
                    continue
                
                if len(raw_frame) < frame_size:
                    # Frame không đủ, đợi thêm data
                    if first_frame:
                        # Đợi thêm data cho frame đầu tiên
                        remaining = frame_size - len(raw_frame)
                        additional = self.process.stdout.read(remaining)
                        if len(additional) > 0:
                            raw_frame += additional
                        else:
                            time.sleep(0.1)
                            continue
                    else:
                        # Bỏ qua frame không đủ (có thể bị mất một phần)
                        continue
                
                # Convert sang numpy array
                frame_data = raw_frame[:frame_size]
                frame = np.frombuffer(frame_data, dtype=np.uint8)
                frame = frame.reshape((self.height, self.width, 3))
                
                # Kiểm tra frame hợp lệ (không phải toàn 0 hoặc toàn 255)
                if frame.sum() > 0 and frame.sum() < self.width * self.height * 3 * 255 * 0.99:
                    # Lưu frame mới nhất
                    with self.frame_lock:
                        self.current_frame = frame.copy()
                    
                    if first_frame:
                        print(f"   ✅ Đã nhận được frame đầu tiên!")
                        first_frame = False
                else:
                    # Frame không hợp lệ, bỏ qua
                    if first_frame:
                        time.sleep(0.1)
                        continue
                
            except Exception as e:
                if self.is_running:
                    print(f"⚠️  Lỗi đọc frame: {e}")
                    import traceback
                    traceback.print_exc()
                time.sleep(0.1)
    
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
        
        if self.process:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
            self.process = None
        
        if hasattr(self, 'read_thread'):
            self.read_thread.join(timeout=2)
        
        if hasattr(self, 'stderr_thread'):
            self.stderr_thread.join(timeout=2)
        
        print("🧹 FFMPEG Camera released")
    
    def set(self, prop_id, value):
        """Giả lập set property"""
        pass
    
    def get(self, prop_id):
        """Giả lập get property"""
        if prop_id == cv2.CAP_PROP_FRAME_WIDTH:
            return self.width
        elif prop_id == cv2.CAP_PROP_FRAME_HEIGHT:
            return self.height
        elif prop_id == cv2.CAP_PROP_FPS:
            return self.fps
        return 0

def test_ffmpeg_camera(rtsp_url):
    """Test FFMPEG camera"""
    print("=" * 70)
    print("🎥 TEST FFMPEG CAMERA")
    print("=" * 70)
    
    cam = FFMPEGCamera(rtsp_url, width=1280, height=720, fps=20)
    
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
                    
                    cv2.imshow('FFMPEG Camera - Press Q to quit', frame)
                    
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
    url = "rtsp://admin:L223C2D3@192.168.1.53:554/cam/realmonitor?channel=1&subtype=1"
    
    print("Bạn có thể thay đổi URL nếu cần:")
    custom_url = input(f"Nhập URL (Enter để dùng: {url}): ").strip()
    
    if custom_url:
        url = custom_url
    
    test_ffmpeg_camera(url)

