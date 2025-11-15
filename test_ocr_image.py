"""
Script test OCR với ảnh có biển số
"""
import cv2
import sys
from license_plate import LicensePlateDetector
import yaml

# Load config
with open('config.yaml', 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

# Khởi tạo detector
detector = LicensePlateDetector(config)

# Đọc ảnh (bạn cần cung cấp ảnh có biển số)
image_path = sys.argv[1] if len(sys.argv) > 1 else 'test_plate.jpg'

try:
    img = cv2.imread(image_path)
    if img is None:
        print(f"❌ Không đọc được ảnh: {image_path}")
        print("📝 Cách dùng: python test_ocr_image.py <đường_dẫn_ảnh>")
        sys.exit(1)
    
    print(f"✅ Đã đọc ảnh: {image_path}")
    print(f"📐 Kích thước: {img.shape}")
    
    # Phát hiện biển số
    result = detector.detect(img)
    
    if result:
        print(f"\n🎉 PHÁT HIỆN BIỂN SỐ:")
        print(f"   📝 Text: {result['text']}")
        print(f"   📊 Confidence: {result['confidence']}")
        print(f"   📍 BBox: {result['bbox']}")
        
        # Vẽ khung và text
        if result['bbox']:
            x, y, w, h = result['bbox']
            cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 255), 3)
            cv2.putText(img, result['text'], (x, y-10),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
        
        # Lưu kết quả
        output_path = 'test_result.jpg'
        cv2.imwrite(output_path, img)
        print(f"\n💾 Đã lưu kết quả: {output_path}")
    else:
        print("\n❌ KHÔNG PHÁT HIỆN ĐƯỢC BIỂN SỐ")
        print("   Có thể do:")
        print("   - Ảnh không có biển số")
        print("   - Biển số quá nhỏ/mờ")
        print("   - Góc chụp không phù hợp")

except Exception as e:
    print(f"❌ Lỗi: {e}")
    import traceback
    traceback.print_exc()

