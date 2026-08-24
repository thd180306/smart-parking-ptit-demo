# Hệ Thống Quản Lý Bãi Giữ Xe Thông Minh PTIT (Smart Parking System)

Hệ thống quản lý bãi giữ xe thông minh cho sinh viên trong khuôn viên trường đại học, sử dụng thẻ từ NFC kết hợp Camera AI OCR nhận diện biển số xe để kiểm soát ra/vào và tự động thu phí qua ví điện tử.

---

## 🚀 Tính năng nổi bật
- **Quản lý CSDL quan hệ chuẩn hóa 3NF:** 8 thực thể (`SinhVien`, `TaiKhoan`, `NhanVien`, `Xe`, `TheNFC`, `BangGia`, `LichSu`, `GiaoDichVi`).
- **Bảo mật phân tầng:** Tách biệt tài khoản và mật khẩu mã hóa SHA-256 khỏi thông tin cá nhân sinh viên.
- **Quy tắc nghiệp vụ gộp lượt (< 5 phút):** Tự động hoàn phí khi xe quẹt ra rồi vào lại dưới 300 giây.
- **Cảnh báo an ninh & Kiểm soát bất thường:** Đối chiếu chéo biển số & thẻ NFC, cảnh báo khi phát hiện sai lệch và hỗ trợ bảo vệ xử lý sự cố.
- **Bảng tính đãi ngộ nhân sự:** Tự động tính lương ca + thưởng xử lý sự cố (+50.000đ/lần).
- **Trình thực thi SQL thời gian thực (Live SQL Console):** Tích hợp sẵn 5 mẫu truy vấn môn học phức tạp.

---

## 🛠️ Hướng dẫn cài đặt & Chạy ứng dụng

### 1. Cài đặt thư viện phụ thuộc
```bash
pip install -r requirements.txt
```

### 2. Khởi chạy ứng dụng
```bash
python app.py
```

Ứng dụng sẽ chạy tại địa chỉ: **http://localhost:5000**

---

## 🔑 Tài khoản đăng nhập mẫu
- **Quản trị viên (Admin):** `admin` / `admin123`
- **Sinh viên 1:** `B22DCCN001` / `123456`
- **Sinh viên 2:** `B22DCCN002` / `123456`
- **Sinh viên 3:** `B22DCCN003` / `123456`
