const API_URL = "";
const formatVND = (num) => new Intl.NumberFormat('vi-VN').format(num);

// Clock Timer
setInterval(() => {
    const el = document.getElementById('clock-display');
    if (el) el.innerText = new Date().toLocaleTimeString('vi-VN');
}, 1000);

// ----- Tab Navigation -----
function switchAdminTab(tabId) {
    document.querySelectorAll('.admin-tab-pane').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));

    const target = document.getElementById(`tab-${tabId}`);
    const navBtn = document.getElementById(`nav-${tabId}`);

    if (target) target.classList.add('active');
    if (navBtn) navBtn.classList.add('active');

    const titleMap = {
        'dashboard': 'Tổng quan hệ thống',
        'parking': 'Trạm kiểm soát Cổng Ra/Vào',
        'students': 'Quản lý Sinh viên & Phương tiện',
        'query': 'Tra cứu số dư & Nạp tiền tại quầy',
        'history': 'Nhật ký Lịch sử Toàn hệ thống',
        'staff-income': 'Bảng tính Thu nhập Nhân viên Bảo vệ',
        'schema': 'Bản thiết kế Schema CSDL & Thực thi SQL'
    };

    const titleEl = document.getElementById('admin-page-title');
    if (titleEl && titleMap[tabId]) titleEl.innerText = titleMap[tabId];

    if (tabId === 'dashboard') loadStats();
    if (tabId === 'students') loadStudentsList();
    if (tabId === 'history') loadAdminHistory();
    if (tabId === 'staff-income') loadStaffIncomeTable();
    if (tabId === 'parking') loadGuardSelect();
    if (tabId === 'schema') { loadSchemaInfo(); applyPresetSql(); }
}

// ----- Stats Loader -----
async function loadStats() {
    try {
        const res = await fetch(`${API_URL}/stats`);
        if (!res.ok) return;
        const data = await res.json();
        
        const elStudents = document.getElementById('stat-students');
        const elRevenue = document.getElementById('stat-revenue');
        const elCars = document.getElementById('stat-cars');
        const elTrans = document.getElementById('stat-transactions');

        if (elStudents) elStudents.innerText = data.total_students ?? 0;
        if (elRevenue) elRevenue.innerText = formatVND(data.total_revenue ?? 0) + "đ";
        if (elCars) elCars.innerText = data.cars_in_parking ?? 0;
        if (elTrans) elTrans.innerText = data.total_transactions ?? 0;

        loadDashboardRecent();
    } catch(e) {}
}

async function loadDashboardRecent() {
    try {
        const res = await fetch(`${API_URL}/history`);
        if (!res.ok) return;
        const data = await res.json();
        const tbody = document.getElementById('dashboard-recent-tbody');
        if (!tbody) return;

        if (!data || data.length === 0) {
            tbody.innerHTML = `<tr><td colspan="5" class="empty-state">Chưa có giao dịch nào được ghi nhận.</td></tr>`;
            return;
        }

        tbody.innerHTML = data.slice(0, 5).map(h => {
            let moneyText = '0đ';
            let feeStyle = 'color: #64748b;';
            if (h.so_tien > 0) {
                moneyText = `-${formatVND(h.so_tien)}đ`;
                feeStyle = 'color: #ef4444; font-weight: 600;';
            } else if (h.so_tien < 0) {
                moneyText = `+${formatVND(Math.abs(h.so_tien))}đ`;
                feeStyle = 'color: #10b981; font-weight: 600;';
            }

            return `
                <tr>
                    <td style="color: #64748b; font-size: 0.8rem;">${h.thoi_gian}</td>
                    <td><strong>${h.mssv}</strong></td>
                    <td><span class="font-mono" style="font-weight: 600;">${h.bien_so_quet || '—'}</span></td>
                    <td>${h.trang_thai}</td>
                    <td style="${feeStyle}">${moneyText}</td>
                </tr>
            `;
        }).join('');
    } catch(e) {}
}

// ----- Students List -----
async function loadStudentsList() {
    try {
        const res = await fetch(`${API_URL}/students`);
        if (!res.ok) return;
        const data = await res.json();
        const tbody = document.getElementById('students-table-tbody');
        if (!tbody) return;

        if (!data || data.length === 0) {
            tbody.innerHTML = `<tr><td colspan="7" class="empty-state">Chưa có sinh viên nào trong CSDL.</td></tr>`;
            return;
        }

        tbody.innerHTML = data.map(s => {
            let badgeClass = 'bg-success';
            if (s.trang_thai === 'Trong bãi') badgeClass = 'bg-warning';
            if (s.trang_thai === 'Bị giữ lại') badgeClass = 'bg-danger';

            return `
                <tr>
                    <td><strong class="font-mono">${s.mssv}</strong></td>
                    <td>${s.ho_ten}</td>
                    <td><span class="font-mono" style="background: #f1f5f9; padding: 2px 6px; border-radius: 4px; font-weight: 600;">${s.bien_so}</span></td>
                    <td><span class="font-mono" style="color: #64748b;">${s.ma_nfc}</span></td>
                    <td style="font-weight: 700; color: #10b981;">${formatVND(s.so_du)} VNĐ</td>
                    <td><span class="badge ${badgeClass}">${s.trang_thai}</span></td>
                    <td style="text-align: right;">
                        <button type="button" class="btn-action btn-danger" style="padding: 4px 10px; font-size: 0.78rem;" onclick="deleteStudentAccount('${s.mssv}')">
                            Xóa
                        </button>
                    </td>
                </tr>
            `;
        }).join('');
    } catch(e) {}
}

// ----- Add Student Modal -----
function openAddStudentModal() {
    const modal = document.getElementById('modal-add-student');
    if (modal) modal.style.display = 'flex';
}

function closeAddStudentModal() {
    const modal = document.getElementById('modal-add-student');
    if (modal) modal.style.display = 'none';
}

async function submitAddStudent(e) {
    e.preventDefault();
    const payload = {
        mssv: document.getElementById('add-mssv').value.trim(),
        ho_ten: document.getElementById('add-name').value.trim(),
        bien_so: document.getElementById('add-plate').value.trim(),
        ma_nfc: document.getElementById('add-nfc').value.trim(),
        so_du: parseFloat(document.getElementById('add-balance').value) || 0
    };

    try {
        const res = await fetch(`${API_URL}/add_student`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (res.ok) {
            showAdminToast(data.message);
            closeAddStudentModal();
            document.getElementById('form-add-student').reset();
            loadStudentsList();
            loadStats();
        } else {
            alert(data.message || "Lỗi đăng ký sinh viên.");
        }
    } catch(err) {
        alert("Lỗi kết nối máy chủ.");
    }
}

async function deleteStudentAccount(mssv) {
    if (!confirm(`Xác nhận xóa tài khoản sinh viên ${mssv}?`)) return;
    try {
        const res = await fetch(`${API_URL}/delete_student/${mssv}`, { method: 'DELETE' });
        const data = await res.json();
        if (res.ok) {
            showAdminToast(data.message);
            loadStudentsList();
            loadStats();
        }
    } catch(e) {}
}

// ----- Parking Scanner & Barrier Control -----
function fillScanForm(plate, nfc) {
    document.getElementById('scan-plate').value = plate;
    document.getElementById('scan-nfc').value = nfc;
    document.getElementById('form-parking-scan').requestSubmit();
}

function setBarrierVisual(isOpen) {
    const rod = document.getElementById('barrier-rod');
    const led = document.getElementById('barrier-led');
    const text = document.getElementById('barrier-text-indicator');

    if (isOpen) {
        if (rod) rod.className = "barrier-rod rod-open";
        if (led) led.className = "barrier-led led-green";
        if (text) { text.innerText = "BARRIER ĐÃ MỞ (XE QUA)"; text.className = "barrier-text text-green"; }
        
        setTimeout(() => {
            if (rod) rod.className = "barrier-rod rod-closed";
            if (led) led.className = "barrier-led led-red";
            if (text) { text.innerText = "BARRIER ĐANG ĐÓNG"; text.className = "barrier-text text-red"; }
        }, 5000);
    } else {
        if (rod) rod.className = "barrier-rod rod-closed";
        if (led) led.className = "barrier-led led-red";
        if (text) { text.innerText = "BARRIER ĐANG ĐÓNG (TỪ CHỐI)"; text.className = "barrier-text text-red"; }
    }
}

let pendingDebtStudent = null;
let pendingDebtAmount = 0;
let pendingSecurityStudent = null;
let pendingSecurityPlate = null;

async function handleParkingScan(e) {
    e.preventDefault();
    const plate = document.getElementById('scan-plate').value.trim();
    const nfc = document.getElementById('scan-nfc').value.trim();

    const idleState = document.getElementById('scan-idle-state');
    const resultText = document.getElementById('scan-result-text');
    const qrFrame = document.getElementById('vietqr-frame');
    const securityFrame = document.getElementById('security-escalation-frame');

    if (idleState) idleState.style.display = 'none';
    if (resultText) resultText.style.display = 'block';
    if (qrFrame) qrFrame.style.display = 'none';
    if (securityFrame) securityFrame.style.display = 'none';

    try {
        const res = await fetch(`${API_URL}/transaction`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ bien_so: plate, nfc: nfc })
        });
        const data = await res.json();

        resultText.innerText = data.message;

        if (res.ok) {
            if (data.status === 'success') {
                resultText.style.color = '#10b981';
                showAdminToast(data.message);
                setBarrierVisual(true);
            } else if (data.status === 'warning') {
                resultText.style.color = '#ef4444';
                setBarrierVisual(false);
                if (securityFrame) securityFrame.style.display = 'block';
                pendingSecurityStudent = data.data?.mssv;
                pendingSecurityPlate = plate;
            }
        } else {
            resultText.style.color = '#ef4444';
            setBarrierVisual(false);

            if (data.code === 'INSUFFICIENT_BALANCE') {
                if (qrFrame) qrFrame.style.display = 'block';
                pendingDebtStudent = data.data.mssv;
                pendingDebtAmount = data.data.amount_due;
                const qrImg = document.getElementById('vietqr-img');
                if (qrImg) {
                    qrImg.src = `https://img.vietqr.io/image/970415-123456789-qr_only.png?amount=${pendingDebtAmount}&addInfo=PTIT%20Parking%20${pendingDebtStudent}`;
                }
            }
        }
    } catch (err) {
        console.error(err);
    }
    loadStats();
}

async function confirmCashPayment() {
    if (!pendingDebtStudent || pendingDebtAmount <= 0) return;
    try {
        const res = await fetch(`${API_URL}/deposit`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ mssv: pendingDebtStudent, amount: pendingDebtAmount })
        });
        if (res.ok) {
            showAdminToast("Đã thu tiền mặt tại quầy thành công!");
            document.getElementById('vietqr-frame').style.display = 'none';
            document.getElementById('scan-result-text').innerText = "Đã thu tiền mặt thành công. Vui lòng quét lại thẻ để xe ra bãi.";
            document.getElementById('scan-result-text').style.color = '#10b981';
            loadStats();
        }
    } catch(e) {}
}

async function resolveSecurityAlert(action) {
    const maNv = document.getElementById('select-guard')?.value || 'NV001';
    try {
        const res = await fetch(`${API_URL}/force_action`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ action, mssv: pendingSecurityStudent, bien_so: pendingSecurityPlate, ma_nv: maNv })
        });
        const data = await res.json();
        if (res.ok) {
            showAdminToast(data.message);
            document.getElementById('security-escalation-frame').style.display = 'none';
            document.getElementById('scan-result-text').innerText = data.message;
            if (action === 'release') setBarrierVisual(true);
            loadStats();
        }
    } catch(e) {}
}

// ----- Query & Deposit -----
async function queryStudentBalance() {
    const mssv = document.getElementById('query-input-mssv').value.trim();
    if (!mssv) return alert("Vui lòng nhập MSSV!");

    try {
        const res = await fetch(`${API_URL}/query_balance/${mssv}`);
        const data = await res.json();
        const box = document.getElementById('query-result-box');

        if (res.ok && data.status === 'success') {
            box.style.display = 'block';
            document.getElementById('q-name').innerText = data.data.ho_ten;
            document.getElementById('q-mssv').innerText = `MSSV: ${data.data.mssv}`;
            document.getElementById('q-balance').innerText = `${formatVND(data.data.so_du)} VNĐ`;
            
            const pill = document.getElementById('q-status-pill');
            pill.innerText = data.data.trang_thai;
            pill.className = "badge";
            if (data.data.trang_thai === 'Trong bãi') pill.classList.add('bg-warning');
            else if (data.data.trang_thai === 'Bị giữ lại') pill.classList.add('bg-danger');
            else pill.classList.add('bg-success');
        } else {
            alert(data.message || "Không tìm thấy thông tin sinh viên.");
            box.style.display = 'none';
        }
    } catch(e) {}
}

async function submitAdminDeposit() {
    const mssv = document.getElementById('query-input-mssv').value.trim();
    const amount = parseFloat(document.getElementById('inp-admin-deposit').value);
    if (!amount || amount <= 0) return alert("Vui lòng nhập số tiền hợp lệ!");

    try {
        const res = await fetch(`${API_URL}/deposit`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ mssv, amount })
        });
        const data = await res.json();
        if (res.ok) {
            showAdminToast(data.message);
            document.getElementById('inp-admin-deposit').value = '';
            queryStudentBalance();
            loadStats();
        } else {
            alert(data.message || "Giao dịch thất bại.");
        }
    } catch(e) {}
}

// ----- History -----
async function loadAdminHistory(showToastFlag = false) {
    try {
        const res = await fetch(`${API_URL}/history`);
        if (!res.ok) return;
        const data = await res.json();
        const tbody = document.getElementById('admin-history-tbody');
        if (!tbody) return;

        if (!data || data.length === 0) {
            tbody.innerHTML = `<tr><td colspan="6" class="empty-state">Chưa có bản ghi lịch sử nào.</td></tr>`;
            return;
        }

        tbody.innerHTML = data.map(h => {
            let feeText = '0 VNĐ';
            let feeStyle = 'color: #64748b;';
            if (h.so_tien > 0) {
                feeText = `-${formatVND(h.so_tien)} VNĐ`;
                feeStyle = 'color: #ef4444; font-weight: 600;';
            } else if (h.so_tien < 0) {
                feeText = `+${formatVND(Math.abs(h.so_tien))} VNĐ`;
                feeStyle = 'color: #10b981; font-weight: 600;';
            }

            let badgeClass = 'bg-success';
            if (h.trang_thai.includes('Cảnh báo') || h.trang_thai.includes('giữ xe')) badgeClass = 'bg-danger';
            if (h.trang_thai.includes('Gộp lượt') || h.trang_thai.includes('Trong bãi')) badgeClass = 'bg-warning';

            return `
                <tr>
                    <td style="color: #64748b; font-size: 0.8rem;">${h.thoi_gian}</td>
                    <td><strong class="font-mono">${h.mssv}</strong></td>
                    <td><span class="font-mono">${h.bien_so_quet || '—'}</span></td>
                    <td>${h.phuong_thuc}</td>
                    <td style="${feeStyle}">${feeText}</td>
                    <td><span class="badge ${badgeClass}">${h.trang_thai}</span></td>
                </tr>
            `;
        }).join('');

        if (showToastFlag) showAdminToast("Đã cập nhật nhật ký lịch sử mới nhất");
    } catch(e) {}
}

// ----- Staff Income -----
async function loadStaffIncomeTable() {
    const month = document.getElementById('sel-income-month')?.value || (new Date().getMonth() + 1);
    const year = document.getElementById('inp-income-year')?.value || 2026;

    try {
        const res = await fetch(`${API_URL}/api/staff_income?month=${month}&year=${year}`);
        if (!res.ok) return;
        const data = await res.json();
        const tbody = document.getElementById('staff-income-tbody');
        if (!tbody) return;

        tbody.innerHTML = data.map(nv => `
            <tr>
                <td><strong class="font-mono">${nv.ma_nv}</strong></td>
                <td><strong>${nv.ho_ten}</strong></td>
                <td><span class="badge ${nv.ca_truc === 'Hành chính' ? 'bg-success' : 'bg-warning'}">${nv.ca_truc}</span></td>
                <td>${formatVND(nv.luong_co_ban)} VNĐ</td>
                <td style="text-align: center; font-weight: 700; color: #2563eb;">${nv.so_lan_xu_ly} lần</td>
                <td style="color: #10b981; font-weight: 700;">+${formatVND(nv.thuong)} VNĐ</td>
                <td style="font-weight: 700; font-size: 1rem; color: #0f172a;">${formatVND(nv.tong_thu_nhap)} VNĐ</td>
            </tr>
        `).join('');
    } catch(e) {}
}

async function loadGuardSelect() {
    try {
        const res = await fetch(`${API_URL}/api/nhan_vien`);
        const data = await res.json();
        const sel = document.getElementById('select-guard');
        if (sel) {
            sel.innerHTML = data.map(nv => `<option value="${nv.ma_nv}">${nv.ma_nv} — ${nv.ho_ten} (${nv.ca_truc})</option>`).join('');
        }
    } catch(e) {}
}

// ----- Schema & Live SQL Console -----
async function loadSchemaInfo() {
    try {
        const res = await fetch(`${API_URL}/api/db/schema_info`);
        const data = await res.json();
        const list = document.getElementById('schema-table-list');
        if (!list) return;

        let html = '';
        for (const [tbl, info] of Object.entries(data)) {
            const cols = info.columns.map(c => `<code>${c.name}</code> (${c.type})`).join(', ');
            html += `
                <div class="schema-item">
                    <div class="schema-item-top">
                        <span class="schema-table-title">${tbl}</span>
                        <span class="badge bg-success">${info.count} bản ghi</span>
                    </div>
                    <div class="schema-cols">${cols}</div>
                </div>
            `;
        }
        list.innerHTML = html;
    } catch(e) {}
}

function applyPresetSql() {
    const sel = document.getElementById('sel-preset-sql');
    const input = document.getElementById('sql-console-input');
    if (sel && input) input.value = sel.value;
}

async function runSqlConsole() {
    const query = document.getElementById('sql-console-input')?.value.trim();
    if (!query) return alert("Vui lòng nhập câu lệnh SQL!");

    const display = document.getElementById('sql-result-display');
    display.innerHTML = `<p style="color: #2563eb;">Đang thực thi truy vấn...</p>`;

    try {
        const res = await fetch(`${API_URL}/api/sql/run`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query })
        });
        const data = await res.json();

        if (res.ok && data.status === 'success') {
            if (data.type === 'select') {
                if (data.rows.length === 0) {
                    display.innerHTML = `<p class="text-muted">Truy vấn thành công! (0 rows trả về).</p>`;
                    return;
                }
                let tableHtml = `<table class="table" style="margin:0;"><thead><tr>`;
                data.columns.forEach(c => tableHtml += `<th>${c}</th>`);
                tableHtml += `</tr></thead><tbody>`;
                data.rows.forEach(r => {
                    tableHtml += `<tr>`;
                    data.columns.forEach(c => {
                        let val = r[c] !== null ? r[c] : '<span style="color:gray;">NULL</span>';
                        tableHtml += `<td>${val}</td>`;
                    });
                    tableHtml += `</tr>`;
                });
                tableHtml += `</tbody></table>`;
                display.innerHTML = tableHtml;
                showAdminToast(`Truy vấn SELECT hoàn tất (${data.count} dòng)`);
            } else {
                display.innerHTML = `<p style="color: #10b981; font-weight: bold;">${data.message}</p>`;
                showAdminToast(data.message);
                loadStats();
                loadSchemaInfo();
            }
        } else {
            display.innerHTML = `<p style="color: #ef4444; font-weight: bold;">Lỗi SQL: ${data.message}</p>`;
        }
    } catch(err) {
        display.innerHTML = `<p style="color: #ef4444;">Lỗi kết nối máy chủ.</p>`;
    }
}

// Cars in Parking Modal
async function openCarsInParkingModal() {
    const modal = document.getElementById('modal-cars-parking');
    const tbody = document.getElementById('cars-in-parking-tbody');
    if (!modal || !tbody) return;

    try {
        const res = await fetch(`${API_URL}/students`);
        const data = await res.json();
        const carsIn = data.filter(s => s.trang_thai === 'Trong bãi' || s.trang_thai === 'Bị giữ lại');

        if (carsIn.length === 0) {
            tbody.innerHTML = `<tr><td colspan="3" class="empty-state">Hiện không có phương tiện nào trong bãi.</td></tr>`;
        } else {
            tbody.innerHTML = carsIn.map(s => {
                const badgeClass = s.trang_thai === 'Trong bãi' ? 'bg-warning' : 'bg-danger';
                return `
                    <tr>
                        <td><strong class="font-mono">${s.mssv}</strong></td>
                        <td>${s.ho_ten}</td>
                        <td><span class="badge ${badgeClass}">${s.bien_so} (${s.trang_thai})</span></td>
                    </tr>
                `;
            }).join('');
        }
        modal.style.display = 'flex';
    } catch(e) {}
}

function closeCarsInParkingModal() {
    const modal = document.getElementById('modal-cars-parking');
    if (modal) modal.style.display = 'none';
}

function handleModalOverlayClick(e, modalId) {
    if (e.target.id === modalId) {
        document.getElementById(modalId).style.display = 'none';
    }
}

// Toast
function showAdminToast(msg) {
    const toast = document.getElementById('admin-toast');
    if (!toast) return;
    toast.innerText = msg;
    toast.classList.add('show');
    setTimeout(() => { toast.classList.remove('show'); }, 3500);
}

// Logout
function handleAdminLogout() {
    if (confirm("Bạn có chắc chắn muốn đăng xuất khỏi trang Quản trị?")) {
        window.location.replace('/admin/logout');
    }
}

// Init
window.addEventListener('DOMContentLoaded', () => {
    loadStats();
    loadGuardSelect();
    const selMonth = document.getElementById('sel-income-month');
    if (selMonth) selMonth.value = new Date().getMonth() + 1;
});
