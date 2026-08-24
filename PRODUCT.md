# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

- **Sinh viên PTIT (Primary Users):** Sinh viên theo học tại Học viện Công nghệ Bưu chính Viễn thông, sử dụng thẻ từ NFC tích hợp thẻ sinh viên để gửi xe máy/xe đạp điện trong khuôn viên, nạp tiền và theo dõi số dư ví điện tử gửi xe.
- **Nhân viên Bảo vệ & Vận hành bãi xe (Operators):** Trực ca tại cổng kiểm soát, giám sát luồng xe vào/ra qua Camera AI OCR nhận diện biển số, giải quyết các cảnh báo sai lệch biển số và nhận phụ cấp thưởng xử lý sự cố (+50.000đ/lần).
- **Giảng viên & Hội đồng Đánh giá BTL CSDL (Evaluators):** Kiểm tra thiết kế mô hình dữ liệu quan hệ 6 bảng, các ràng buộc toàn vẹn, quy tắc nghiệp vụ gộp lượt < 5 phút và thực thi các câu lệnh SQL trực tiếp (JOIN, GROUP BY).

## Product Purpose

Hệ thống quản lý bãi giữ xe thông minh khép kín cho trường đại học: kết hợp phần cứng mô phỏng (Camera AI OCR + Đầu đọc thẻ NFC + Cổng Barrier tự động) với phần mềm quản trị CSDL quan hệ chuẩn hóa và ví điện tử sinh viên.

## Positioning

Hệ thống quản lý bãi xe chuyên nghiệp đầu tiên tích hợp cơ chế tự động gộp lượt thông minh (quẹt ra rồi vào lại < 5 phút sẽ tự động gộp lượt và hoàn trả cước phí) kết hợp chính sách đãi ngộ nhân viên tự động hóa và bảng điều khiển CSDL thời gian thực cho giảng viên.

## Operating Context

- Trạm gác bảo vệ cổng trường: Màn hình điều khiển trạm kiểm soát (Gate Monitor) chạy liên tục trên trình duyệt, kết nối hệ thống camera và đầu đọc thẻ.
- Thiết bị di động / Laptop của sinh viên: Giao diện tra cứu số dư ví, nạp tiền nhanh qua VietQR và xem lịch sử các lượt ra vào.
- Phòng bảo vệ đồ án: Giảng viên tra cứu trực tiếp cấu trúc CSDL và chạy các kịch bản kiểm thử.

## Capabilities and Constraints

- **CSDL Quan hệ 6 Bảng:** `SinhVien`, `Xe`, `TheNFC`, `NhanVien`, `BangGia`, `LichSu`.
- **Ràng buộc nghiệp vụ 5 phút:** Quẹt ra và vào lại trong vòng dưới 300 giây được tự động gộp thành 1 lượt và hoàn lại 3.000 VNĐ.
- **Cảnh báo an ninh:** Xe trong bãi bị quẹt bởi thẻ khác sẽ kích hoạt còi báo động, hạ barrier và chuyển trạng thái "Bị giữ lại" chờ bảo vệ can thiệp.
- **Tính lương bảo vệ:** Lương cơ bản theo ca trực (Hành chính 3tr / Ca đêm 4tr) + 50.000đ/sự cố đã giải quyết trong tháng.

## Evidence on Hand

- Dữ liệu mẫu sinh viên: B22DCCN001 (Nguyễn Văn A, 29L1-12345, NFC001), B22DCCN002 (Trần Thị Bích, 29M2-67890, NFC002), B22DCCN003 (Lê Hoàng Long, 30V3-11223, NFC003).
- Dữ liệu nhân viên: NV001 (Trần Văn Bảo), NV002 (Lê Thị Hoa), NV003 (Phạm Minh Tuấn).
- Bảng giá cước: Xe máy 3.000đ, Xe đạp điện 2.000đ.

## Product Principles

1. **Minh bạch & Tức thời:** Mọi biến động số dư, quét thẻ, trừ phí đều phản hồi ngay lập tức với lý do rõ ràng.
2. **An toàn phương tiện:** Cổng Barrier chỉ mở khi cả 2 điều kiện (Thẻ NFC + Biển số Camera) hoàn toàn trùng khớp.
3. **Trải nghiệm thực thụ:** Giao diện trực quan, đậm chất kỹ thuật số của một trường đại học công nghệ hàng đầu, không dùng các pattern AI rẻ tiền.
