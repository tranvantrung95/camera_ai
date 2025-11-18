# 📤 Hướng dẫn đưa project lên GitHub

## Bước 1: Tạo repository trên GitHub

1. Truy cập: https://github.com/new
2. Điền thông tin:
   - **Repository name**: `camera-ai` (hoặc tên bạn muốn)
   - **Description**: `🎥 Hệ thống Camera AI với YOLOv11 - Phát hiện người, xe và biển số`
   - **Public** hoặc **Private**: Tùy chọn
   - ❌ **KHÔNG** chọn "Add a README file"
   - ❌ **KHÔNG** chọn ".gitignore"
   - ❌ **KHÔNG** chọn "license"
3. Click **"Create repository"**

## Bước 2: Kết nối và push

Sau khi tạo repository, GitHub sẽ hiển thị hướng dẫn. Chạy các lệnh sau:

### Option 1: HTTPS (Đơn giản, khuyến nghị)

```bash
# Thêm remote repository
git remote add origin https://github.com/YOUR_USERNAME/camera-ai.git

# Đổi branch sang main (nếu cần)
git branch -M main

# Push code lên GitHub
git push -u origin main
```

### Option 2: SSH (Nếu đã setup SSH key)

```bash
# Thêm remote repository
git remote add origin git@github.com:YOUR_USERNAME/camera-ai.git

# Đổi branch sang main (nếu cần)
git branch -M main

# Push code lên GitHub
git push -u origin main
```

## Bước 3: Xác thực (nếu dùng HTTPS)

GitHub sẽ yêu cầu đăng nhập:
- **Username**: Tên GitHub của bạn
- **Password**: Dùng **Personal Access Token** (KHÔNG phải password)

### Tạo Personal Access Token:

1. Vào: https://github.com/settings/tokens
2. Click **"Generate new token"** → **"Generate new token (classic)"**
3. Điền:
   - **Note**: `camera-ai-upload`
   - **Expiration**: `90 days` (hoặc tùy chọn)
   - **Scopes**: Chọn `repo` (full control)
4. Click **"Generate token"**
5. **COPY TOKEN** (chỉ hiện 1 lần!)
6. Dùng token này làm password khi push

## Bước 4: Kiểm tra

Sau khi push thành công, truy cập:

```
https://github.com/YOUR_USERNAME/camera-ai
```

Bạn sẽ thấy:
- ✅ 23 files
- ✅ README.md hiển thị đẹp
- ✅ Commit message

## 🔄 Cập nhật sau này

Khi có thay đổi:

```bash
# 1. Xem thay đổi
git status

# 2. Thêm files
git add .

# 3. Commit
git commit -m "✨ Thêm tính năng mới"

# 4. Push lên GitHub
git push
```

## 🆘 Xử lý lỗi

### Lỗi: "remote origin already exists"

```bash
git remote remove origin
git remote add origin https://github.com/YOUR_USERNAME/camera-ai.git
```

### Lỗi: "failed to push some refs"

```bash
# Pull trước, sau đó push
git pull origin main --rebase
git push -u origin main
```

### Lỗi: Authentication failed

- Đảm bảo dùng **Personal Access Token**, không phải password
- Token phải có quyền `repo`

## 📝 Lưu ý

- ❌ File video (`.mp4`) KHÔNG được push (đã ignore)
- ❌ Database (`.db`) KHÔNG được push (đã ignore)
- ❌ Models (`.pt`) KHÔNG được push (tải tự động)
- ✅ Code và config ĐÃ được push
- ✅ README và docs ĐÃ được push

## 🎉 Hoàn tất!

Repository của bạn đã sẵn sàng trên GitHub!

Chia sẻ link với người khác:
```
https://github.com/YOUR_USERNAME/camera-ai
```
