"""
Dashboard Web - Giao diện theo dõi và quản lý Camera AI
"""
from flask import Flask, render_template, jsonify, Response, request
from flask_cors import CORS
import yaml
import sqlite3
import cv2
import os
import json
from datetime import datetime, timedelta
from threading import Thread, Lock
import base64
from camera_ai import CameraAI

app = Flask(__name__)
CORS(app)

# Global variables
camera_system = None
camera_lock = Lock()
latest_frame = None
is_running = False

def load_config():
    """Load cấu hình"""
    # Kiểm tra biến môi trường CONFIG_FILE (để dùng config khác nếu cần)
    config_file = os.environ.get('CONFIG_FILE', 'config.yaml')
    with open(config_file, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

config = load_config()
print(f"📋 Đã load config từ: {os.environ.get('CONFIG_FILE', 'config.yaml')}")

def get_db_connection():
    """Kết nối database"""
    conn = sqlite3.connect(config['database']['path'])
    conn.row_factory = sqlite3.Row
    return conn

def camera_loop():
    """Vòng lặp chạy camera detection"""
    global camera_system, latest_frame, is_running
    
    camera_system = CameraAI()
    is_running = True
    
    print("📹 Camera loop bắt đầu...")
    camera_system.start_recording()
    
    frame_count = 0
    try:
        while is_running:
            ret, frame = camera_system.cap.read()
            if not ret:
                print("⚠️  Không đọc được frame, quay lại đầu video...")
                # Quay lại đầu video
                camera_system.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue
            
            frame_count += 1
            if frame_count % 30 == 0:  # Log mỗi 30 frames
                print(f"📹 Đã xử lý {frame_count} frames...")
            
            # Phát hiện objects
            detections = camera_system.detect_frame(frame)
            
            # Vẽ kết quả
            frame_display = camera_system.draw_detections(frame.copy(), detections)
            
            # Lưu frame mới nhất
            with camera_lock:
                latest_frame = frame_display.copy()
            
            # Ghi video
            if camera_system.video_writer:
                camera_system.video_writer.write(frame_display)
            
            # Lưu snapshots và log
            if detections['persons'] or detections['vehicles']:
                if frame_count % 30 == 0:  # Log mỗi 30 frames
                    print(f"   → Phát hiện: {len(detections['persons'])} người, {len(detections['vehicles'])} xe, {len(detections['plates'])} biển số")
                
                if config['recording']['save_snapshots']:
                    snapshot_path = camera_system.save_snapshot(
                        frame_display,
                        'detection'
                    )
                    
                    # Log detections
                    for person in detections['persons']:
                        camera_system.log_detection(
                            'person',
                            person['confidence'],
                            person['bbox'],
                            snapshot_path
                        )
                    
                    # Tạo map biển số theo vehicle bbox
                    plate_map = {}
                    for plate in detections['plates']:
                        veh_bbox_str = str(plate['vehicle_bbox'])
                        plate_map[veh_bbox_str] = plate['plate_text']
                        if frame_count % 30 == 0:
                            print(f"   🚗 Biển số: {plate['plate_text']}")
                    
                    for vehicle in detections['vehicles']:
                        # Tìm biển số tương ứng với xe này
                        veh_bbox_str = str(vehicle['bbox'])
                        plate_text = plate_map.get(veh_bbox_str, None)
                        vehicle_type = vehicle.get('vehicle_type', None)
                        
                        camera_system.log_detection(
                            'vehicle',
                            vehicle['confidence'],
                            vehicle['bbox'],
                            snapshot_path,
                            plate_text,
                            vehicle_type
                        )
    
    except Exception as e:
        print(f"❌ Lỗi camera loop: {e}")
    finally:
        if camera_system:
            camera_system.cleanup()
        is_running = False
        print("⏹️  Camera loop đã dừng")

@app.route('/')
def index():
    """Trang chủ dashboard"""
    return render_template('dashboard.html')

@app.route('/api/stats')
def get_stats():
    """API lấy thống kê"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Thống kê hôm nay
        today = datetime.now().date()
        
        cursor.execute('''
            SELECT COUNT(*) as count, type 
            FROM detections 
            WHERE DATE(timestamp) = ? 
            GROUP BY type
        ''', (today,))
        
        today_stats = {}
        for row in cursor.fetchall():
            today_stats[row['type']] = row['count']
        
        # Thống kê tuần này
        week_ago = today - timedelta(days=7)
        cursor.execute('''
            SELECT COUNT(*) as count, type 
            FROM detections 
            WHERE DATE(timestamp) >= ? 
            GROUP BY type
        ''', (week_ago,))
        
        week_stats = {}
        for row in cursor.fetchall():
            week_stats[row['type']] = row['count']
        
        # Thống kê tổng
        cursor.execute('SELECT COUNT(*) as total FROM detections')
        total = cursor.fetchone()['total']
    except sqlite3.OperationalError as e:
        print(f"Error in get_stats: {e}")
        # Trả về dữ liệu rỗng nếu bảng chưa tồn tại
        return jsonify({
            'today': {'person': 0, 'vehicle': 0, 'license_plate': 0},
            'week': {'person': 0, 'vehicle': 0, 'license_plate': 0},
            'total': 0
        })
    except Exception as e:
        print(f"Error in get_stats: {e}")
        return jsonify({'error': str(e)}), 500
    
    # Detections gần nhất
    cursor.execute('''
        SELECT * FROM detections 
        ORDER BY timestamp DESC 
        LIMIT 10
    ''')
    recent = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    
    # Camera status
    camera_stats = camera_system.get_stats() if camera_system else {
        'total_persons': 0,
        'total_vehicles': 0,
        'total_plates': 0,
        'last_detection': None
    }
    
    return jsonify({
        'today': today_stats,
        'week': week_stats,
        'total': total,
        'recent': recent,
        'camera': camera_stats,
        'is_running': is_running
    })

@app.route('/api/detections')
def get_detections():
    """API lấy danh sách detections với filter"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Parameters
    limit = request.args.get('limit', 50, type=int)
    det_type = request.args.get('type', None)
    date_from = request.args.get('from', None)
    date_to = request.args.get('to', None)
    
    query = 'SELECT * FROM detections WHERE 1=1'
    params = []
    
    if det_type:
        query += ' AND type = ?'
        params.append(det_type)
    
    if date_from:
        query += ' AND DATE(timestamp) >= ?'
        params.append(date_from)
    
    if date_to:
        query += ' AND DATE(timestamp) <= ?'
        params.append(date_to)
    
    query += ' ORDER BY timestamp DESC LIMIT ?'
    params.append(limit)
    
    cursor.execute(query, params)
    detections = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    
    return jsonify(detections)

@app.route('/api/plates')
def get_plates():
    """API lấy danh sách biển số đã phát hiện"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT license_plate, vehicle_type, COUNT(*) as count, 
                   MAX(timestamp) as last_seen
            FROM detections 
            WHERE license_plate IS NOT NULL AND license_plate != 'UNKNOWN'
            GROUP BY license_plate, vehicle_type
            ORDER BY last_seen DESC
        ''')
    except sqlite3.OperationalError as e:
        print(f"Error in get_plates: {e}")
        return jsonify([])
    except Exception as e:
        print(f"Error in get_plates: {e}")
        return jsonify({'error': str(e)}), 500
    
    plates = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return jsonify(plates)

@app.route('/api/chart/daily')
def get_daily_chart():
    """API lấy dữ liệu biểu đồ theo ngày"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        days = request.args.get('days', 7, type=int)
        start_date = datetime.now().date() - timedelta(days=days)
        
        cursor.execute('''
            SELECT DATE(timestamp) as date, 
                   type,
                   COUNT(*) as count
            FROM detections
            WHERE DATE(timestamp) >= ?
            GROUP BY DATE(timestamp), type
            ORDER BY date
        ''', (start_date,))
        
        data = {}
        for row in cursor.fetchall():
            date = row['date']
            if date not in data:
                data[date] = {'person': 0, 'vehicle': 0}
            data[date][row['type']] = row['count']
        
        conn.close()
        
        # Format for chart
        labels = []
        persons = []
        vehicles = []
        
        for i in range(days):
            date = (datetime.now().date() - timedelta(days=days-i-1)).isoformat()
            labels.append(date)
            persons.append(data.get(date, {}).get('person', 0))
            vehicles.append(data.get(date, {}).get('vehicle', 0))
        
        return jsonify({
            'labels': labels,
            'persons': persons,
            'vehicles': vehicles
        })
    except Exception as e:
        print(f"Error in get_daily_chart: {e}")
        # Trả về dữ liệu rỗng nếu lỗi
        days = request.args.get('days', 7, type=int)
        labels = []
        for i in range(days):
            date = (datetime.now().date() - timedelta(days=days-i-1)).isoformat()
            labels.append(date)
        return jsonify({
            'labels': labels,
            'persons': [0] * days,
            'vehicles': [0] * days
        })

@app.route('/api/chart/hourly')
def get_hourly_chart():
    """API lấy dữ liệu biểu đồ theo giờ (hôm nay)"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        today = datetime.now().date()
        
        cursor.execute('''
            SELECT strftime('%H', timestamp) as hour,
                   type,
                   COUNT(*) as count
            FROM detections
            WHERE DATE(timestamp) = ?
            GROUP BY hour, type
            ORDER BY hour
        ''', (today,))
        
        data = {}
        for row in cursor.fetchall():
            hour = int(row['hour'])
            if hour not in data:
                data[hour] = {'person': 0, 'vehicle': 0}
            data[hour][row['type']] = row['count']
        
        conn.close()
        
        # Format for chart (24 hours)
        labels = [f"{h:02d}:00" for h in range(24)]
        persons = [data.get(h, {}).get('person', 0) for h in range(24)]
        vehicles = [data.get(h, {}).get('vehicle', 0) for h in range(24)]
        
        return jsonify({
            'labels': labels,
            'persons': persons,
            'vehicles': vehicles
        })
    except Exception as e:
        print(f"Error in get_hourly_chart: {e}")
        # Trả về dữ liệu rỗng nếu lỗi
        labels = [f"{h:02d}:00" for h in range(24)]
        return jsonify({
            'labels': labels,
            'persons': [0] * 24,
            'vehicles': [0] * 24
        })

def gen_frames():
    """Generator để stream video"""
    global latest_frame
    
    while True:
        with camera_lock:
            if latest_frame is None:
                continue
            frame = latest_frame.copy()
        
        # Encode frame to JPEG
        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            continue
        
        frame_bytes = buffer.tobytes()
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/video_feed')
def video_feed():
    """Stream video feed"""
    return Response(
        gen_frames(),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )

@app.route('/api/control/start', methods=['POST'])
def start_camera():
    """Bắt đầu camera"""
    global is_running
    
    if not is_running:
        thread = Thread(target=camera_loop, daemon=True)
        thread.start()
        return jsonify({'status': 'started', 'message': 'Camera đã bắt đầu'})
    else:
        return jsonify({'status': 'already_running', 'message': 'Camera đang chạy'})

@app.route('/api/control/stop', methods=['POST'])
def stop_camera():
    """Dừng camera"""
    global is_running, camera_system
    
    is_running = False
    if camera_system:
        camera_system.cleanup()
    
    return jsonify({'status': 'stopped', 'message': 'Camera đã dừng'})

@app.route('/api/snapshot')
def get_latest_snapshot():
    """Lấy snapshot mới nhất"""
    snapshot_dir = config['recording']['snapshot_path']
    
    if not os.path.exists(snapshot_dir):
        return jsonify({'error': 'No snapshots'}), 404
    
    snapshots = sorted(
        [f for f in os.listdir(snapshot_dir) if f.endswith('.jpg')],
        reverse=True
    )
    
    if not snapshots:
        return jsonify({'error': 'No snapshots'}), 404
    
    latest = os.path.join(snapshot_dir, snapshots[0])
    
    # Read and encode image
    img = cv2.imread(latest)
    _, buffer = cv2.imencode('.jpg', img)
    img_base64 = base64.b64encode(buffer).decode('utf-8')
    
    return jsonify({
        'filename': snapshots[0],
        'image': f'data:image/jpeg;base64,{img_base64}'
    })

@app.route('/api/config', methods=['GET', 'POST'])
def manage_config():
    """Quản lý cấu hình"""
    if request.method == 'GET':
        return jsonify(config)
    
    elif request.method == 'POST':
        # Update config
        new_config = request.json
        
        # Merge với config hiện tại
        config.update(new_config)
        
        # Save to file
        with open('config.yaml', 'w', encoding='utf-8') as f:
            yaml.dump(config, f, allow_unicode=True)
        
        return jsonify({'status': 'updated', 'config': config})

if __name__ == '__main__':
    # Tự động start camera khi chạy dashboard
    print("🚀 Khởi động Camera AI Dashboard...")
    
    # Start camera thread
    camera_thread = Thread(target=camera_loop, daemon=True)
    camera_thread.start()
    
    # Start Flask server
    host = config['dashboard']['host']
    port = config['dashboard']['port']
    
    print(f"🌐 Dashboard đang chạy tại: http://{host}:{port}")
    print(f"📊 Mở trình duyệt và truy cập dashboard")
    
    app.run(
        host=host,
        port=port,
        debug=False,
        threaded=True
    )

