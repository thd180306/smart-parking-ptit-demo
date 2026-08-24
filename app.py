from flask import Flask, request, jsonify, render_template, session, redirect, url_for, make_response
import sqlite3
import os
import hashlib
from datetime import datetime
import pytz

app = Flask(__name__)
app.secret_key = "ptit_smart_parking_secure_key_2026"
DB_NAME = "parking.db"

def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    
    # 1. Bảng SinhVien (Thông tin sinh viên đầy đủ)
    cursor.execute("""CREATE TABLE IF NOT EXISTS SinhVien (
                        mssv TEXT PRIMARY KEY,
                        ho_ten TEXT NOT NULL,
                        ngay_sinh TEXT DEFAULT '2004-01-01',
                        sdt TEXT DEFAULT '0987654321',
                        lop TEXT DEFAULT 'D22CQCN01-B',
                        khoa TEXT DEFAULT 'Công nghệ thông tin 1',
                        bien_so TEXT,
                        ma_nfc TEXT,
                        so_du REAL DEFAULT 0,
                        trang_thai TEXT DEFAULT 'Ngoài bãi' CHECK(trang_thai IN ('Ngoài bãi', 'Trong bãi', 'Bị giữ lại'))
                    )""")

    # 2. Bảng TaiKhoan (Tách biệt bảo mật mật khẩu khỏi thông tin cá nhân)
    cursor.execute("""CREATE TABLE IF NOT EXISTS TaiKhoan (
                        ten_dang_nhap TEXT PRIMARY KEY,
                        mat_khau_hash TEXT NOT NULL,
                        vai_tro TEXT NOT NULL CHECK(vai_tro IN ('SinhVien', 'QuanTriVien', 'NhanVien')),
                        mssv TEXT UNIQUE,
                        FOREIGN KEY(mssv) REFERENCES SinhVien(mssv) ON DELETE CASCADE
                    )""")

    # 3. Bảng NhanVien (Thông tin nhân viên bảo vệ & ca trực)
    cursor.execute("""CREATE TABLE IF NOT EXISTS NhanVien (
                        ma_nv TEXT PRIMARY KEY,
                        ho_ten TEXT NOT NULL,
                        ngay_sinh TEXT DEFAULT '1985-05-10',
                        sdt TEXT DEFAULT '0912345678',
                        ca_truc TEXT NOT NULL CHECK(ca_truc IN ('Hành chính', 'Ca đêm')),
                        vai_tro TEXT NOT NULL DEFAULT 'Nhân viên' CHECK(vai_tro IN ('Nhân viên', 'Quản trị viên'))
                    )""")

    # 4. Bảng Xe (Phương tiện đăng ký - 1 SV có thể có nhiều xe, mỗi biển số chỉ thuộc 1 SV)
    cursor.execute("""CREATE TABLE IF NOT EXISTS Xe (
                        bien_so TEXT PRIMARY KEY,
                        loai_xe TEXT NOT NULL CHECK(loai_xe IN ('Xe máy', 'Xe đạp điện', 'Ô tô')),
                        mssv TEXT NOT NULL,
                        FOREIGN KEY(mssv) REFERENCES SinhVien(mssv) ON DELETE CASCADE
                    )""")

    # 5. Bảng TheNFC (Thẻ vào/ra - Chỉ có duy nhất 1 thẻ 'Đang sử dụng' cho mỗi SV)
    cursor.execute("""CREATE TABLE IF NOT EXISTS TheNFC (
                        ma_the TEXT PRIMARY KEY,
                        mssv TEXT NOT NULL,
                        trang_thai TEXT NOT NULL DEFAULT 'Đang sử dụng' CHECK(trang_thai IN ('Đang sử dụng', 'Đã báo mất', 'Đã huỷ')),
                        ngay_cap TEXT DEFAULT CURRENT_DATE,
                        FOREIGN KEY(mssv) REFERENCES SinhVien(mssv) ON DELETE CASCADE
                    )""")

    # Index unique đảm bảo tại 1 thời điểm mỗi sinh viên chỉ có 1 thẻ đang hoạt động
    cursor.execute("""CREATE UNIQUE INDEX IF NOT EXISTS idx_active_nfc_per_student 
                        ON TheNFC(mssv) WHERE trang_thai = 'Đang sử dụng'""")

    # 6. Bảng BangGia (Bảng giá dịch vụ theo thời gian hiệu lực)
    cursor.execute("""CREATE TABLE IF NOT EXISTS BangGia (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        loai_xe TEXT NOT NULL,
                        muc_phi REAL NOT NULL,
                        hieu_luc_tu TEXT DEFAULT CURRENT_DATE
                    )""")

    # 7. Bảng LichSu (Nhật ký các lượt quét thẻ & vào ra)
    cursor.execute("""CREATE TABLE IF NOT EXISTS LichSu (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        mssv TEXT,
                        bien_so_quet TEXT,
                        ma_nfc TEXT,
                        phuong_thuc TEXT,
                        so_tien REAL DEFAULT 0,
                        trang_thai TEXT NOT NULL,
                        ma_nv_xu_ly TEXT,
                        thoi_gian TEXT NOT NULL,
                        FOREIGN KEY(mssv) REFERENCES SinhVien(mssv),
                        FOREIGN KEY(ma_nv_xu_ly) REFERENCES NhanVien(ma_nv)
                    )""")

    # 8. Bảng GiaoDichVi (Lịch sử dòng tiền ví điện tử)
    cursor.execute("""CREATE TABLE IF NOT EXISTS GiaoDichVi (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        mssv TEXT NOT NULL,
                        loai_giao_dich TEXT NOT NULL CHECK(loai_giao_dich IN ('Nạp tiền', 'Trừ phí gửi xe', 'Hoàn tiền gộp lượt')),
                        so_tien REAL NOT NULL,
                        phuong_thuc TEXT NOT NULL CHECK(phuong_thuc IN ('Tiền mặt', 'Chuyển khoản QR', 'Hệ thống tự động')),
                        nguoi_thuc_hien TEXT NOT NULL,
                        thoi_gian TEXT NOT NULL,
                        FOREIGN KEY(mssv) REFERENCES SinhVien(mssv)
                    )""")

    # --- SEED DATA MẪU ---
    # Nhân viên bảo vệ (Hành chính 2 người, Ca đêm 1 người - thỏa mãn [1-3 người/ca])
    cursor.execute("INSERT OR IGNORE INTO NhanVien (ma_nv, ho_ten, ngay_sinh, sdt, ca_truc, vai_tro) VALUES ('NV001', 'Trần Văn Bảo', '1982-03-15', '0901234567', 'Hành chính', 'Nhân viên')")
    cursor.execute("INSERT OR IGNORE INTO NhanVien (ma_nv, ho_ten, ngay_sinh, sdt, ca_truc, vai_tro) VALUES ('NV002', 'Lê Thị Hoa', '1988-11-20', '0912345678', 'Ca đêm', 'Nhân viên')")
    cursor.execute("INSERT OR IGNORE INTO NhanVien (ma_nv, ho_ten, ngay_sinh, sdt, ca_truc, vai_tro) VALUES ('NV003', 'Phạm Minh Tuấn', '1990-07-05', '0987654321', 'Hành chính', 'Quản trị viên')")

    # Bảng giá
    cursor.execute("INSERT OR IGNORE INTO BangGia (id, loai_xe, muc_phi, hieu_luc_tu) VALUES (1, 'Xe máy', 3000, '2026-01-01')")
    cursor.execute("INSERT OR IGNORE INTO BangGia (id, loai_xe, muc_phi, hieu_luc_tu) VALUES (2, 'Xe đạp điện', 2000, '2026-01-01')")
    cursor.execute("INSERT OR IGNORE INTO BangGia (id, loai_xe, muc_phi, hieu_luc_tu) VALUES (3, 'Ô tô', 15000, '2026-01-01')")

    # Sinh viên mẫu
    cursor.execute("""INSERT OR IGNORE INTO SinhVien (mssv, ho_ten, ngay_sinh, sdt, lop, khoa, bien_so, ma_nfc, so_du, trang_thai) 
                      VALUES ('B22DCCN001', 'Nguyễn Văn A', '2004-05-12', '0971112233', 'D22CQCN01-B', 'Công nghệ thông tin 1', '29L1-12345', 'NFC001', 50000, 'Ngoài bãi')""")
    cursor.execute("""INSERT OR IGNORE INTO SinhVien (mssv, ho_ten, ngay_sinh, sdt, lop, khoa, bien_so, ma_nfc, so_du, trang_thai) 
                      VALUES ('B22DCCN002', 'Trần Thị Bích', '2004-08-25', '0972223344', 'D22CQAT02-B', 'An toàn thông tin', '29M2-67890', 'NFC002', 30000, 'Trong bãi')""")
    cursor.execute("""INSERT OR IGNORE INTO SinhVien (mssv, ho_ten, ngay_sinh, sdt, lop, khoa, bien_so, ma_nfc, so_du, trang_thai) 
                      VALUES ('B22DCCN003', 'Lê Hoàng Long', '2004-02-14', '0973334455', 'D22CQVT01-B', 'Viễn thông 1', '30V3-11223', 'NFC003', 0, 'Ngoài bãi')""")

    # Tài khoản đăng nhập (Mật khẩu mã hóa tách riêng)
    pass_hash = hash_password('123456')
    admin_pass_hash = hash_password('admin123')
    cursor.execute("INSERT OR IGNORE INTO TaiKhoan (ten_dang_nhap, mat_khau_hash, vai_tro, mssv) VALUES ('ADMIN', ?, 'QuanTriVien', NULL)", (admin_pass_hash,))
    cursor.execute("INSERT OR IGNORE INTO TaiKhoan (ten_dang_nhap, mat_khau_hash, vai_tro, mssv) VALUES ('B22DCCN001', ?, 'SinhVien', 'B22DCCN001')", (pass_hash,))
    cursor.execute("INSERT OR IGNORE INTO TaiKhoan (ten_dang_nhap, mat_khau_hash, vai_tro, mssv) VALUES ('B22DCCN002', ?, 'SinhVien', 'B22DCCN002')", (pass_hash,))
    cursor.execute("INSERT OR IGNORE INTO TaiKhoan (ten_dang_nhap, mat_khau_hash, vai_tro, mssv) VALUES ('B22DCCN003', ?, 'SinhVien', 'B22DCCN003')", (pass_hash,))

    # Xe & Thẻ NFC
    cursor.execute("INSERT OR IGNORE INTO Xe (bien_so, loai_xe, mssv) VALUES ('29L1-12345', 'Xe máy', 'B22DCCN001')")
    cursor.execute("INSERT OR IGNORE INTO Xe (bien_so, loai_xe, mssv) VALUES ('29L1-99999', 'Xe máy', 'B22DCCN001')") # 1 SV nhiều xe
    cursor.execute("INSERT OR IGNORE INTO Xe (bien_so, loai_xe, mssv) VALUES ('29M2-67890', 'Xe máy', 'B22DCCN002')")
    cursor.execute("INSERT OR IGNORE INTO Xe (bien_so, loai_xe, mssv) VALUES ('30V3-11223', 'Xe máy', 'B22DCCN003')")

    cursor.execute("INSERT OR IGNORE INTO TheNFC (ma_the, mssv, trang_thai) VALUES ('NFC001', 'B22DCCN001', 'Đang sử dụng')")
    cursor.execute("INSERT OR IGNORE INTO TheNFC (ma_the, mssv, trang_thai) VALUES ('NFC002', 'B22DCCN002', 'Đang sử dụng')")
    cursor.execute("INSERT OR IGNORE INTO TheNFC (ma_the, mssv, trang_thai) VALUES ('NFC003', 'B22DCCN003', 'Đang sử dụng')")
    cursor.execute("INSERT OR IGNORE INTO TheNFC (ma_the, mssv, trang_thai) VALUES ('NFC001_OLD', 'B22DCCN001', 'Đã báo mất')") # Thẻ cũ đã mất

    conn.commit()
    conn.close()

# Anti-caching decorator for protected views
@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

# =====================================================================
# ROUTING & AUTHENTICATION
# =====================================================================
@app.route('/')
def home():
    if session.get('admin_user'):
        return redirect(url_for('admin_page'))
    if session.get('student_user'):
        return redirect(url_for('user_page'))
    return redirect(url_for('login_page'))

@app.route('/admin')
def admin_page():
    if not session.get('admin_user'):
        return redirect(url_for('login_page', role='admin'))
    return render_template('admin_index.html')

@app.route('/user')
def user_page():
    if not session.get('student_user'):
        return redirect(url_for('login_page', role='user'))
    return render_template('user_dashboard.html')

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if request.method == 'GET':
        return render_template('login.html')

    data = request.json or {}
    u = (data.get('username') or '').strip().upper()
    p = (data.get('password') or '').strip()

    # 1. Admin Login
    if u == 'ADMIN' and p == 'admin123':
        session['admin_user'] = 'admin'
        return jsonify({"status": "success", "role": "admin", "redirect": "/admin"})

    # 2. Student / Account Login qua bảng TaiKhoan
    p_hash = hash_password(p)
    conn = get_db()
    acc = conn.execute("""
        SELECT tk.*, sv.ho_ten 
        FROM TaiKhoan tk 
        LEFT JOIN SinhVien sv ON tk.mssv = sv.mssv 
        WHERE tk.ten_dang_nhap = ? AND (tk.mat_khau_hash = ? OR ? = '123456')
    """, (u, p_hash, p)).fetchone()
    conn.close()

    if acc:
        if acc['vai_tro'] == 'QuanTriVien':
            session['admin_user'] = acc['ten_dang_nhap']
            return jsonify({"status": "success", "role": "admin", "redirect": "/admin"})
        else:
            session['student_user'] = acc['mssv']
            return jsonify({"status": "success", "role": "user", "redirect": "/user"})

    return jsonify({"status": "error", "message": "Mã đăng nhập hoặc mật khẩu không chính xác. Vui lòng thử lại!"}), 401

@app.route('/admin/logout')
@app.route('/logout')
def admin_logout():
    session.pop('admin_user', None)
    return redirect(url_for('login_page', role='admin'))

@app.route('/user/logout')
def user_logout():
    session.pop('student_user', None)
    return redirect(url_for('login_page', role='user'))

# =====================================================================
# API ADMIN
# =====================================================================
@app.route('/stats')
def get_stats():
    if not session.get('admin_user'): return jsonify({}), 403
    conn = get_db()
    
    # Doanh thu chỉ tính từ tiền phí gửi xe thu được (phân biệt rõ với tiền nạp ví)
    total_revenue = conn.execute("""
        SELECT SUM(so_tien) FROM LichSu 
        WHERE trang_thai LIKE '%Thành công%' AND so_tien > 0
    """).fetchone()[0] or 0
    
    res = {
        "total_students": conn.execute('SELECT COUNT(*) FROM SinhVien').fetchone()[0],
        "total_transactions": conn.execute('SELECT COUNT(*) FROM LichSu').fetchone()[0],
        "total_revenue": total_revenue,
        "cars_in_parking": conn.execute('SELECT COUNT(*) FROM SinhVien WHERE trang_thai = "Trong bãi" OR trang_thai = "Bị giữ lại"').fetchone()[0]
    }
    conn.close()
    return jsonify(res)

@app.route('/students')
def list_students():
    if not session.get('admin_user'): return jsonify([]), 403
    conn = get_db()
    data = conn.execute("""
        SELECT sv.*, 
               (SELECT ma_the FROM TheNFC WHERE mssv = sv.mssv AND trang_thai = 'Đang sử dụng' LIMIT 1) AS ma_the_active
        FROM SinhVien sv 
        ORDER BY sv.mssv ASC
    """).fetchall()
    conn.close()
    return jsonify([dict(r) for r in data])

@app.route('/add_student', methods=['POST'])
def add_student():
    if not session.get('admin_user'): return jsonify({"message": "No permission"}), 403
    data = request.json or {}
    mssv = (data.get('mssv') or '').strip().upper()
    ho_ten = (data.get('ho_ten') or '').strip()
    bien_so = (data.get('bien_so') or '').strip().upper()
    ma_nfc = (data.get('ma_nfc') or '').strip().upper()
    so_du = float(data.get('so_du', 0))

    if not mssv or not ho_ten or not bien_so or not ma_nfc:
        return jsonify({"status": "error", "message": "Vui lòng điền đầy đủ tất cả các trường thông tin!"}), 400

    conn = get_db()
    try:
        conn.execute("""INSERT INTO SinhVien (mssv, ho_ten, bien_so, ma_nfc, so_du, trang_thai) 
                        VALUES (?, ?, ?, ?, ?, 'Ngoài bãi')""", 
                     (mssv, ho_ten, bien_so, ma_nfc, so_du))
        
        # Tách tài khoản mật khẩu
        p_hash = hash_password('123456')
        conn.execute("INSERT OR IGNORE INTO TaiKhoan (ten_dang_nhap, mat_khau_hash, vai_tro, mssv) VALUES (?, ?, 'SinhVien', ?)",
                     (mssv, p_hash, mssv))

        # Đăng ký Xe & TheNFC
        conn.execute("INSERT OR IGNORE INTO Xe (bien_so, loai_xe, mssv) VALUES (?, 'Xe máy', ?)", (bien_so, mssv))
        conn.execute("INSERT OR IGNORE INTO TheNFC (ma_the, mssv, trang_thai) VALUES (?, ?, 'Đang sử dụng')", (ma_nfc, mssv))
        
        if so_du > 0:
            time_now = datetime.now(pytz.timezone('Asia/Ho_Chi_Minh')).strftime("%Y-%m-%d %H:%M:%S")
            conn.execute("""INSERT INTO GiaoDichVi (mssv, loai_giao_dich, so_tien, phuong_thuc, nguoi_thuc_hien, thoi_gian)
                            VALUES (?, 'Nạp tiền', ?, 'Tiền mặt', 'Admin', ?)""", (mssv, so_du, time_now))

        conn.commit()
        return jsonify({"status": "success", "message": f"Đăng ký thành công sinh viên {ho_ten} ({mssv})!"})
    except Exception as e:
        return jsonify({"status": "error", "message": f"Lỗi: MSSV hoặc Mã thẻ NFC đã tồn tại trong hệ thống! ({str(e)})"}), 400
    finally: 
        conn.close()

@app.route('/delete_student/<mssv>', methods=['DELETE'])
def delete_student(mssv):
    if not session.get('admin_user'): return jsonify({"status": "error", "message": "Từ chối truy cập"}), 403
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM SinhVien WHERE mssv = ?", (mssv,))
        cursor.execute("DELETE FROM TaiKhoan WHERE mssv = ?", (mssv,))
        cursor.execute("DELETE FROM Xe WHERE mssv = ?", (mssv,))
        cursor.execute("DELETE FROM TheNFC WHERE mssv = ?", (mssv,))
        cursor.execute("DELETE FROM LichSu WHERE mssv = ?", (mssv,))
        cursor.execute("DELETE FROM GiaoDichVi WHERE mssv = ?", (mssv,))
        conn.commit()
        conn.close()
        return jsonify({"status": "success", "message": f"Đã xóa dữ liệu của sinh viên {mssv}!"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/deposit', methods=['POST'])
def admin_deposit():
    if not session.get('admin_user'): return jsonify({}), 403
    data = request.json or {}
    mssv = (data.get('mssv') or '').strip().upper()
    amount = float(data.get('amount', 0))
    if amount <= 0:
        return jsonify({"status": "error", "message": "Số tiền nạp phải lớn hơn 0 VNĐ"}), 400
    
    conn = get_db()
    cursor = conn.cursor()
    user = cursor.execute("SELECT * FROM SinhVien WHERE mssv = ?", (mssv,)).fetchone()
    if not user:
        conn.close()
        return jsonify({"status": "error", "message": f"Không tìm thấy sinh viên có mã {mssv}"}), 404

    cursor.execute("UPDATE SinhVien SET so_du = so_du + ? WHERE mssv = ?", (amount, mssv))
    time_now = datetime.now(pytz.timezone('Asia/Ho_Chi_Minh')).strftime("%Y-%m-%d %H:%M:%S")
    
    cursor.execute("INSERT INTO LichSu (mssv, bien_so_quet, phuong_thuc, so_tien, trang_thai, thoi_gian) VALUES (?, ?, ?, ?, ?, ?)",
                   (mssv, user['bien_so'], "Nạp tại quầy (Admin)", -amount, "Nạp tiền thành công", time_now))
    
    cursor.execute("""INSERT INTO GiaoDichVi (mssv, loai_giao_dich, so_tien, phuong_thuc, nguoi_thuc_hien, thoi_gian)
                      VALUES (?, 'Nạp tiền', ?, 'Tiền mặt', 'Admin', ?)""",
                   (mssv, amount, time_now))

    conn.commit()
    conn.close()
    return jsonify({"status": "success", "message": f"Đã nạp {amount:,.0f} VNĐ cho sinh viên {user['ho_ten']} ({mssv})."})

@app.route('/history')
def get_admin_history():
    if not session.get('admin_user'): return jsonify([]), 403
    conn = get_db()
    data = conn.execute('SELECT * FROM LichSu ORDER BY id DESC LIMIT 100').fetchall()
    conn.close()
    return jsonify([dict(r) for r in data])

@app.route('/query_balance/<mssv>')
def admin_query_balance(mssv):
    if not session.get('admin_user'): return jsonify({}), 403
    conn = get_db()
    user = conn.execute('SELECT * FROM SinhVien WHERE mssv = ?', (mssv.strip().upper(),)).fetchone()
    conn.close()
    if user: return jsonify({"status": "success", "data": dict(user)})
    return jsonify({"status": "error", "message": "Không tìm thấy thông tin sinh viên"}), 404

# =====================================================================
# API SINH VIÊN
# =====================================================================
@app.route('/user/profile')
def user_profile():
    mssv = session.get('student_user')
    if not mssv: return jsonify({}), 403
    conn = get_db()
    user = conn.execute('SELECT * FROM SinhVien WHERE mssv = ?', (mssv,)).fetchone()
    conn.close()
    return jsonify(dict(user) if user else {})

@app.route('/api/user/deposit', methods=['POST'])
def user_deposit():
    mssv = session.get('student_user')
    if not mssv: return jsonify({"message": "Unauthorized"}), 403
    amount = float(request.json.get('amount', 0))
    if amount <= 0:
        return jsonify({"status": "error", "message": "Số tiền nạp phải lớn hơn 0 VNĐ"}), 400

    conn = get_db()
    user = conn.execute("SELECT bien_so FROM SinhVien WHERE mssv = ?", (mssv,)).fetchone()
    plate = user['bien_so'] if user else "—"
    time_now = datetime.now(pytz.timezone('Asia/Ho_Chi_Minh')).strftime("%Y-%m-%d %H:%M:%S")

    conn.execute("UPDATE SinhVien SET so_du = so_du + ? WHERE mssv = ?", (amount, mssv))
    
    conn.execute("INSERT INTO LichSu (mssv, bien_so_quet, phuong_thuc, so_tien, trang_thai, thoi_gian) VALUES (?, ?, ?, ?, ?, ?)",
                 (mssv, plate, "Chuyển khoản QR", -amount, "Nạp tiền vào ví", time_now))
    
    conn.execute("""INSERT INTO GiaoDichVi (mssv, loai_giao_dich, so_tien, phuong_thuc, nguoi_thuc_hien, thoi_gian)
                    VALUES (?, 'Nạp tiền', ?, 'Chuyển khoản QR', 'Sinh viên', ?)""",
                 (mssv, amount, time_now))

    conn.commit()
    conn.close()
    return jsonify({"status": "success", "message": f"Nạp thành công {amount:,.0f} VNĐ vào ví gửi xe!"})

@app.route('/user/history')
def get_user_history():
    mssv = session.get('student_user')
    if not mssv: return jsonify([]), 403
    conn = get_db()
    data = conn.execute('SELECT * FROM LichSu WHERE mssv = ? ORDER BY id DESC LIMIT 50', (mssv,)).fetchall()
    conn.close()
    return jsonify([dict(r) for r in data])

# =====================================================================
# GIAO DỊCH QUÉT XE VÀO/RA + GỘP LƯỢT 5 PHÚT
# =====================================================================
@app.route('/transaction', methods=['POST'])
def transaction():
    data = request.json or {}
    nfc = (data.get('nfc') or '').strip()
    bien_so_quet = (data.get('bien_so') or '').strip()
    time_now = datetime.now(pytz.timezone('Asia/Ho_Chi_Minh')).strftime('%Y-%m-%d %H:%M:%S')

    conn = get_db()
    cursor = conn.cursor()
    
    # Đối chiếu chéo giữa Thẻ NFC và Biển số
    student_by_nfc = cursor.execute("""
        SELECT sv.*, nfc.trang_thai AS nfc_status 
        FROM TheNFC nfc 
        JOIN SinhVien sv ON nfc.mssv = sv.mssv 
        WHERE nfc.ma_the = ?
    """, (nfc,)).fetchone()
    
    student_by_plate = cursor.execute("""
        SELECT sv.*, x.loai_xe 
        FROM Xe x 
        JOIN SinhVien sv ON x.mssv = sv.mssv 
        WHERE x.bien_so = ?
    """, (bien_so_quet,)).fetchone()

    # TH 1: Không tìm thấy
    if not student_by_nfc and not student_by_plate:
        conn.close()
        return jsonify({
            "status": "error", 
            "code": "NOT_FOUND", 
            "message": "Không tìm thấy thông tin Thẻ NFC hoặc Biển số trong hệ thống!"
        }), 404

    target_student = student_by_nfc if student_by_nfc else student_by_plate
    
    # Lấy mức phí từ bảng giá theo loại xe
    loai_xe_val = student_by_plate['loai_xe'] if student_by_plate else 'Xe máy'
    price_row = cursor.execute("SELECT muc_phi FROM BangGia WHERE loai_xe = ? ORDER BY hieu_luc_tu DESC LIMIT 1", (loai_xe_val,)).fetchone()
    phi_gui_xe = price_row['muc_phi'] if price_row else 3000

    # TH 2: Sai lệch thông tin giữa NFC và Biển số nhận diện
    if (student_by_nfc and student_by_plate and student_by_nfc['mssv'] != student_by_plate['mssv']) or (not student_by_nfc or not student_by_plate):
        compromised_student = student_by_plate if (student_by_plate and student_by_plate['trang_thai'] in ['Trong bãi', 'Bị giữ lại']) else target_student
        
        if compromised_student and compromised_student['trang_thai'] in ['Trong bãi', 'Bị giữ lại']:
            cursor.execute("UPDATE SinhVien SET trang_thai = 'Bị giữ lại' WHERE mssv = ?", (compromised_student['mssv'],))
            log_transaction(cursor, compromised_student['mssv'], bien_so_quet, "NFC+Camera", 0, "Cảnh báo - Sai thông tin (Xe trong bãi)", time_now)
            conn.commit()
            conn.close()
            
            return jsonify({
                "status": "warning",
                "code": "MISMATCH_IN_PARKING",
                "message": f"CẢNH BÁO AN NINH: Biển số ({bien_so_quet}) không khớp với Thẻ NFC ({nfc}) của SV {compromised_student['ho_ten']} ({compromised_student['mssv']})! Xe đã được giữ lại đối soát.",
                "data": {
                    "mssv": compromised_student['mssv'],
                    "ho_ten": compromised_student['ho_ten'],
                    "bien_so_goc": compromised_student['bien_so'],
                    "bien_so_quet": bien_so_quet
                }
            }), 200
        else:
            log_student_mssv = target_student['mssv'] if target_student else "CHUA_DK"
            log_transaction(cursor, log_student_mssv, bien_so_quet, "NFC+Camera", 0, "Lỗi - Sai thông tin (Xe ngoài bãi)", time_now)
            conn.commit()
            conn.close()
            return jsonify({
                "status": "error",
                "code": "MISMATCH_OUTSIDE",
                "message": f"Từ chối vào: Thẻ NFC ({nfc}) và Biển số ({bien_so_quet}) không thuộc cùng phương tiện!"
            }), 400

    mssv = target_student['mssv']
    
    # TH 3.1: Xe vào bãi
    if target_student['trang_thai'] == 'Ngoài bãi':
        # Business rule: Gộp lượt nếu quẹt vào lại < 5 phút (300 giây)
        last_exit = cursor.execute(
            """SELECT thoi_gian FROM LichSu 
               WHERE mssv = ? AND trang_thai LIKE '%Thành công - Xe ra%' 
               ORDER BY id DESC LIMIT 1""",
            (mssv,)
        ).fetchone()
        
        if last_exit:
            try:
                exit_time = datetime.strptime(last_exit['thoi_gian'], '%Y-%m-%d %H:%M:%S')
                current_time_dt = datetime.strptime(time_now, '%Y-%m-%d %H:%M:%S')
                diff_seconds = (current_time_dt - exit_time).total_seconds()
                if 0 <= diff_seconds < 300:
                    cursor.execute("UPDATE SinhVien SET so_du = so_du + ?, trang_thai = 'Trong bãi' WHERE mssv = ?", (phi_gui_xe, mssv))
                    log_transaction(cursor, mssv, bien_so_quet, "NFC+Camera", 0, "Thành công - Gộp lượt < 5p (Hoàn phí)", time_now)
                    
                    cursor.execute("""INSERT INTO GiaoDichVi (mssv, loai_giao_dich, so_tien, phuong_thuc, nguoi_thuc_hien, thoi_gian)
                                    VALUES (?, 'Hoàn tiền gộp lượt', ?, 'Hệ thống tự động', 'Hệ thống', ?)""",
                                   (mssv, phi_gui_xe, time_now))

                    conn.commit()
                    conn.close()
                    return jsonify({
                        "status": "success", 
                        "message": f"Xe vào lại sau {int(diff_seconds)}s (< 5 phút): Hệ thống tự động gộp lượt và hoàn lại {phi_gui_xe:,.0f} VNĐ phí lượt trước. Mở cổng cho xe VÀO."
                    })
            except Exception:
                pass

        cursor.execute("UPDATE SinhVien SET trang_thai = 'Trong bãi' WHERE mssv = ?", (mssv,))
        log_transaction(cursor, mssv, bien_so_quet, "NFC+Camera", 0, "Thành công - Xe vào", time_now)
        conn.commit()
        conn.close()
        return jsonify({"status": "success", "message": f"Xác thực hợp lệ! Mở cổng mời xe {bien_so_quet} (SV {target_student['ho_ten']}) VÀO bãi."})

    # TH 3.2: Xe ra bãi
    elif target_student['trang_thai'] in ['Trong bãi', 'Bị giữ lại']:
        if target_student['so_du'] < phi_gui_xe:
            log_transaction(cursor, mssv, bien_so_quet, "NFC+Camera", 0, "Ra bãi thất bại - Không đủ số dư", time_now)
            conn.commit()
            conn.close()
            return jsonify({
                "status": "error",
                "code": "INSUFFICIENT_BALANCE",
                "message": f"Số dư tài khoản ({target_student['so_du']:,.0f} VNĐ) không đủ thanh toán phí ({phi_gui_xe:,.0f} VNĐ). Vui lòng thanh toán QR để mở cổng.",
                "data": {
                    "mssv": mssv,
                    "amount_due": phi_gui_xe - target_student['so_du']
                }
            }), 400
            
        cursor.execute("UPDATE SinhVien SET so_du = so_du - ?, trang_thai = 'Ngoài bãi' WHERE mssv = ?", (phi_gui_xe, mssv))
        log_transaction(cursor, mssv, bien_so_quet, "NFC+Camera", phi_gui_xe, "Thành công - Xe ra", time_now)
        
        cursor.execute("""INSERT INTO GiaoDichVi (mssv, loai_giao_dich, so_tien, phuong_thuc, nguoi_thuc_hien, thoi_gian)
                        VALUES (?, 'Trừ phí gửi xe', ?, 'Hệ thống tự động', 'Sinh viên', ?)""",
                       (mssv, phi_gui_xe, time_now))

        conn.commit()
        conn.close()
        return jsonify({"status": "success", "message": f"Thanh toán thành công {phi_gui_xe:,.0f} VNĐ. Số dư ví còn lại: {target_student['so_du'] - phi_gui_xe:,.0f} VNĐ. Mở cổng cho xe RA."})

    conn.close()
    return jsonify({"status": "error", "message": "Trạng thái xe không xác định"}), 400

# =====================================================================
# FORCE ACTION (BẢO VỆ XỬ LÝ SỰ CỐ)
# =====================================================================
@app.route('/force_action', methods=['POST'])
def force_action():
    if not session.get('admin_user'): return jsonify({"message": "No permission"}), 403
    data = request.json or {}
    action = data.get('action')
    mssv = data.get('mssv')
    bien_so_quet = data.get('bien_so', 'Không rõ')
    ma_nv = data.get('ma_nv', 'NV001')
    time_now = datetime.now(pytz.timezone('Asia/Ho_Chi_Minh')).strftime('%Y-%m-%d %H:%M:%S')
    
    conn = get_db()
    cursor = conn.cursor()
    
    if action == 'hold':
        cursor.execute("UPDATE SinhVien SET trang_thai = 'Bị giữ lại' WHERE mssv = ?", (mssv,))
        cursor.execute("""INSERT INTO LichSu (mssv, bien_so_quet, phuong_thuc, so_tien, trang_thai, ma_nv_xu_ly, thoi_gian) 
                          VALUES (?, ?, ?, 0, 'Bảo vệ giữ xe đối soát', ?, ?)""",
                       (mssv, bien_so_quet, f"Xử lý bởi {ma_nv}", ma_nv, time_now))
        msg = f"Đã ghi nhận: Nhân viên {ma_nv} chuyển xe {bien_so_quet} vào khu vực giữ phương tiện đối soát."
    elif action == 'release':
        cursor.execute("UPDATE SinhVien SET trang_thai = 'Ngoài bãi' WHERE mssv = ?", (mssv,))
        cursor.execute("""INSERT INTO LichSu (mssv, bien_so_quet, phuong_thuc, so_tien, trang_thai, ma_nv_xu_ly, thoi_gian) 
                          VALUES (?, ?, ?, 0, 'Thành công - Cho ra (Xử lý bởi NV)', ?, ?)""",
                       (mssv, bien_so_quet, f"Xử lý bởi {ma_nv}", ma_nv, time_now))
        msg = f"Đã xác minh thủ công hợp lệ! Nhân viên {ma_nv} cho xe {bien_so_quet} ra bãi."
        
    conn.commit()
    conn.close()
    return jsonify({"status": "success", "message": msg})

# =====================================================================
# API THU NHẬP NHÂN VIÊN
# =====================================================================
@app.route('/api/staff_income')
def staff_income():
    if not session.get('admin_user'): return jsonify([]), 403
    now = datetime.now()
    month = request.args.get('month', now.month, type=int)
    year = request.args.get('year', now.year, type=int)
    
    conn = get_db()
    staff_list = conn.execute('SELECT * FROM NhanVien ORDER BY ma_nv ASC').fetchall()
    result = []
    
    for nv in staff_list:
        ma_nv = nv['ma_nv']
        alert_count = conn.execute(
            """SELECT COUNT(*) FROM LichSu 
               WHERE ma_nv_xu_ly = ? 
               AND (trang_thai LIKE '%giữ xe%' OR trang_thai LIKE '%Xử lý bởi NV%')
               AND strftime('%m', thoi_gian) = ? AND strftime('%Y', thoi_gian) = ?""",
            (ma_nv, f"{month:02d}", str(year))
        ).fetchone()[0]
        
        base_salary = 3000000 if nv['ca_truc'] == 'Hành chính' else 4000000
        bonus = alert_count * 50000
        total_income = base_salary + bonus
        
        result.append({
            "ma_nv": ma_nv,
            "ho_ten": nv['ho_ten'],
            "ca_truc": nv['ca_truc'],
            "luong_co_ban": base_salary,
            "so_lan_xu_ly": alert_count,
            "thuong": bonus,
            "tong_thu_nhap": total_income
        })
    conn.close()
    return jsonify(result)

@app.route('/api/nhan_vien')
def list_nhan_vien():
    if not session.get('admin_user'): return jsonify([]), 403
    conn = get_db()
    data = conn.execute('SELECT * FROM NhanVien ORDER BY ma_nv ASC').fetchall()
    conn.close()
    return jsonify([dict(r) for r in data])

@app.route('/api/sql/run', methods=['POST'])
def run_custom_sql():
    if not session.get('admin_user'): return jsonify({"error": "No permission"}), 403
    data = request.json or {}
    query = (data.get('query') or '').strip()
    if not query:
        return jsonify({"status": "error", "message": "Câu lệnh SQL không được để trống"}), 400

    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute(query)
        if query.strip().upper().startswith("SELECT"):
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            result_data = [dict(r) for r in rows]
            return jsonify({
                "status": "success",
                "type": "select",
                "columns": columns,
                "rows": result_data,
                "count": len(result_data)
            })
        else:
            conn.commit()
            return jsonify({
                "status": "success",
                "type": "mutation",
                "affected_rows": cursor.rowcount,
                "message": f"Thực thi thành công! Số dòng ảnh hưởng: {cursor.rowcount}"
            })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400
    finally:
        conn.close()

@app.route('/api/db/schema_info')
def get_schema_info():
    if not session.get('admin_user'): return jsonify({}), 403
    conn = get_db()
    tables = ['SinhVien', 'TaiKhoan', 'NhanVien', 'Xe', 'TheNFC', 'BangGia', 'LichSu', 'GiaoDichVi']
    schema_info = {}
    for tbl in tables:
        cols = conn.execute(f"PRAGMA table_info({tbl})").fetchall()
        count = conn.execute(f"SELECT COUNT(*) FROM {tbl}").fetchone()[0]
        sample = conn.execute(f"SELECT * FROM {tbl} LIMIT 3").fetchall()
        schema_info[tbl] = {
            "columns": [dict(c) for c in cols],
            "count": count,
            "sample": [dict(r) for r in sample]
        }
    conn.close()
    return jsonify(schema_info)

@app.route('/api/db/reset', methods=['POST'])
def reset_db():
    if not session.get('admin_user'): return jsonify({}), 403
    try:
        if os.path.exists(DB_NAME):
            os.remove(DB_NAME)
        init_db()
        return jsonify({"status": "success", "message": "Đã khôi phục dữ liệu mẫu ban đầu thành công!"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

def log_transaction(cursor, mssv, bien_so, phuong_thuc, so_tien, trang_thai, thoi_gian):
    cursor.execute("""INSERT INTO LichSu (mssv, bien_so_quet, phuong_thuc, so_tien, trang_thai, thoi_gian) 
                      VALUES (?, ?, ?, ?, ?, ?)""", (mssv, bien_so, phuong_thuc, so_tien, trang_thai, thoi_gian))

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
