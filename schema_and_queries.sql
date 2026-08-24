-- =====================================================================
-- HỆ THỐNG QUẢN LÝ BÃI GIỮ XE THÔNG MINH PTIT (DEMO CSDL)
-- =====================================================================

-- 1. BẢNG SINH VIÊN
CREATE TABLE IF NOT EXISTS SinhVien (
    mssv TEXT PRIMARY KEY,
    ho_ten TEXT,
    bien_so TEXT,
    ma_nfc TEXT UNIQUE,
    so_du REAL DEFAULT 0,
    trang_thai TEXT DEFAULT 'Ngoài bãi',
    mat_khau TEXT DEFAULT '123456'
);

-- 2. BẢNG LỊCH SỬ GIAO DỊCH / LƯỢT GỬI XE
CREATE TABLE IF NOT EXISTS LichSu (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mssv TEXT,
    bien_so_quet TEXT,
    phuong_thuc TEXT,
    so_tien REAL,
    trang_thai TEXT,
    thoi_gian TEXT,
    FOREIGN KEY(mssv) REFERENCES SinhVien(mssv)
);

-- 3. [BỔ SUNG] BẢNG XE
CREATE TABLE IF NOT EXISTS Xe (
    bien_so TEXT PRIMARY KEY,
    loai_xe TEXT CHECK(loai_xe IN ('Xe máy', 'Xe đạp điện')),
    mssv TEXT,
    FOREIGN KEY(mssv) REFERENCES SinhVien(mssv)
);

-- 4. [BỔ SUNG] BẢNG THẺ NFC
CREATE TABLE IF NOT EXISTS TheNFC (
    ma_the TEXT PRIMARY KEY,
    mssv TEXT,
    trang_thai TEXT DEFAULT 'Đang sử dụng' CHECK(trang_thai IN ('Đang sử dụng', 'Đã báo mất', 'Đã huỷ')),
    ngay_cap TEXT DEFAULT CURRENT_DATE,
    FOREIGN KEY(mssv) REFERENCES SinhVien(mssv)
);

-- 5. [BỔ SUNG] BẢNG NHÂN VIÊN
CREATE TABLE IF NOT EXISTS NhanVien (
    ma_nv TEXT PRIMARY KEY,
    ho_ten TEXT NOT NULL,
    ca_truc TEXT CHECK(ca_truc IN ('Hành chính', 'Ca đêm'))
);

-- 6. [BỔ SUNG] BẢNG GIÁ DỊCH VỤ
CREATE TABLE IF NOT EXISTS BangGia (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    loai_xe TEXT,
    muc_phi REAL,
    hieu_luc_tu TEXT DEFAULT CURRENT_DATE
);

-- =====================================================================
-- DỮ LIỆU MẪU BAN ĐẦU
-- =====================================================================
INSERT OR IGNORE INTO NhanVien (ma_nv, ho_ten, ca_truc) VALUES 
('NV001', 'Trần Văn Bảo', 'Hành chính'),
('NV002', 'Lê Thị Hoa', 'Ca đêm'),
('NV003', 'Phạm Minh Tuấn', 'Hành chính');

INSERT OR IGNORE INTO BangGia (id, loai_xe, muc_phi, hieu_luc_tu) VALUES 
(1, 'Xe máy', 3000, '2026-01-01'),
(2, 'Xe đạp điện', 2000, '2026-01-01');

-- =====================================================================
-- CÁC CÂU TRUY VẤN MINH HOẠ
-- =====================================================================

-- Truy vấn: Tính thu nhập nhân viên bảo vệ theo tháng
-- Lương = Cơ bản (Hành chính 3tr, Ca đêm 4tr) + 50.000đ/lần xử lý cảnh báo
SELECT 
    nv.ma_nv,
    nv.ho_ten,
    nv.ca_truc,
    CASE 
        WHEN nv.ca_truc = 'Hành chính' THEN 3000000 
        ELSE 4000000 
    END AS luong_co_ban,
    COUNT(ls.id) AS so_lan_xu_ly_su_co,
    COUNT(ls.id) * 50000 AS tien_thuong,
    (CASE WHEN nv.ca_truc = 'Hành chính' THEN 3000000 ELSE 4000000 END) + (COUNT(ls.id) * 50000) AS tong_thu_nhap
FROM NhanVien nv
LEFT JOIN LichSu ls ON ls.phuong_thuc LIKE '%' || nv.ma_nv || '%' 
    AND (ls.trang_thai LIKE '%giữ xe%' OR ls.trang_thai LIKE '%Xử lý bởi NV%')
    AND strftime('%m', ls.thoi_gian) = '08' 
    AND strftime('%Y', ls.thoi_gian) = '2026'
GROUP BY nv.ma_nv;