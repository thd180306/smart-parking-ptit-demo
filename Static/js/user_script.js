let studentData = null;
const formatVND = (num) => new Intl.NumberFormat('vi-VN').format(num);

// Tab switching
function switchUserTab(tabName) {
    document.querySelectorAll('.tab-pane').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('.nav-tab').forEach(el => el.classList.remove('active'));

    const targetSection = document.getElementById(`section-${tabName}`);
    const targetTabBtn = document.getElementById(`tab-btn-${tabName}`);

    if (targetSection) targetSection.classList.add('active');
    if (targetTabBtn) targetTabBtn.classList.add('active');

    if (tabName === 'parking') loadParkingHistory();
    if (tabName === 'wallet') loadWalletHistory();
}

// Fetch and load student profile
async function fetchUserProfile() {
    try {
        const res = await fetch('/user/profile');
        if (res.status === 403 || res.redirected) {
            window.location.replace('/login?role=user');
            return;
        }
        const data = await res.json();
        if (!data || !data.mssv) {
            window.location.replace('/login?role=user');
            return;
        }
        studentData = data;
        renderProfile(data);
    } catch (e) {
        console.error("Lỗi tải thông tin sinh viên:", e);
    }
}

function renderProfile(user) {
    // Header
    const nameEl = document.getElementById('top-user-name');
    const mssvEl = document.getElementById('top-user-mssv');
    const initialsEl = document.getElementById('avatar-initials');

    if (nameEl) nameEl.innerText = user.ho_ten;
    if (mssvEl) mssvEl.innerText = `MSSV: ${user.mssv}`;
    if (initialsEl) {
        const parts = user.ho_ten.split(' ');
        initialsEl.innerText = parts.length > 1 ? (parts[0][0] + parts[parts.length - 1][0]).toUpperCase() : user.mssv.slice(-2);
    }

    // Card
    const balanceText = document.getElementById('card-balance-text');
    const cardHolder = document.getElementById('card-holder-name');
    const statusPill = document.getElementById('card-parking-status');

    if (balanceText) balanceText.innerText = `${formatVND(user.so_du)} VNĐ`;
    if (cardHolder) cardHolder.innerText = user.ho_ten;

    if (statusPill) {
        statusPill.innerText = user.trang_thai;
        statusPill.className = "status-badge";
        if (user.trang_thai === 'Trong bãi') statusPill.classList.add('status-inside');
        else if (user.trang_thai === 'Bị giữ lại') statusPill.classList.add('status-held');
        else statusPill.classList.add('status-outside');
    }

    // Meta
    const metaMssv = document.getElementById('meta-mssv');
    const metaPlate = document.getElementById('meta-plate');
    const metaNfc = document.getElementById('meta-nfc');

    if (metaMssv) metaMssv.innerText = user.mssv;
    if (metaPlate) metaPlate.innerText = user.bien_so || 'Chưa đăng ký';
    if (metaNfc) metaNfc.innerText = user.ma_nfc || 'Chưa cấp thẻ';
}

// Load Parking History
async function loadParkingHistory(showToastFlag = false) {
    try {
        const res = await fetch('/user/history');
        if (!res.ok) return;
        const data = await res.json();
        
        const tbody = document.getElementById('parking-history-tbody');
        const previewList = document.getElementById('recent-preview-list');

        if (!data || data.length === 0) {
            if (tbody) tbody.innerHTML = `<tr><td colspan="5" class="empty-state">Chưa có lịch sử gửi xe nào được ghi nhận.</td></tr>`;
            if (previewList) previewList.innerHTML = `<div class="empty-state">Chưa có hoạt động gửi xe nào.</div>`;
            return;
        }

        // Table
        if (tbody) {
            tbody.innerHTML = data.map(item => {
                let feeText = '0 VNĐ';
                let feeClass = '';
                if (item.so_tien > 0) {
                    feeText = `-${formatVND(item.so_tien)} VNĐ`;
                    feeClass = 'color: #ef4444; font-weight: 600;';
                } else if (item.so_tien < 0) {
                    feeText = `+${formatVND(Math.abs(item.so_tien))} VNĐ`;
                    feeClass = 'color: #10b981; font-weight: 600;';
                }

                let badge = 'status-outside';
                if (item.trang_thai.includes('Trong bãi') || item.trang_thai.includes('Xe vào')) badge = 'status-inside';
                if (item.trang_thai.includes('Cảnh báo') || item.trang_thai.includes('giữ xe')) badge = 'status-held';

                return `
                    <tr>
                        <td style="color: #64748b; font-size: 0.85rem;">${item.thoi_gian}</td>
                        <td><span class="plate-tag font-mono">${item.bien_so_quet || '—'}</span></td>
                        <td>${item.phuong_thuc}</td>
                        <td><span class="status-badge ${badge}">${item.trang_thai}</span></td>
                        <td style="${feeClass}">${feeText}</td>
                    </tr>
                `;
            }).join('');
        }

        // Preview in Overview
        if (previewList) {
            previewList.innerHTML = data.slice(0, 4).map(item => {
                let feeColor = item.so_tien > 0 ? '#ef4444' : (item.so_tien < 0 ? '#10b981' : '#64748b');
                let sign = item.so_tien > 0 ? '-' : (item.so_tien < 0 ? '+' : '');
                let money = item.so_tien !== 0 ? `${sign}${formatVND(Math.abs(item.so_tien))} VNĐ` : 'Miễn phí';

                return `
                    <div class="recent-item">
                        <div>
                            <div style="font-weight: 600; font-size: 0.9rem; color: #0f172a;">${item.trang_thai}</div>
                            <div style="font-size: 0.78rem; color: #64748b; margin-top: 2px;">${item.thoi_gian} &bull; Biển số: ${item.bien_so_quet || '—'}</div>
                        </div>
                        <div style="font-weight: 700; font-size: 0.9rem; color: ${feeColor}; font-variant-numeric: tabular-nums;">${money}</div>
                    </div>
                `;
            }).join('');
        }

        if (showToastFlag) showToast("Đã cập nhật lịch sử gửi xe mới nhất");
    } catch (e) {
        console.error("Lỗi tải lịch sử gửi xe:", e);
    }
}

// Load Wallet Transactions
async function loadWalletHistory() {
    try {
        const res = await fetch('/user/history');
        if (!res.ok) return;
        const data = await res.json();
        
        const tbody = document.getElementById('wallet-history-tbody');
        if (!tbody) return;

        if (!data || data.length === 0) {
            tbody.innerHTML = `<tr><td colspan="4" class="empty-state">Chưa có giao dịch tài chính nào.</td></tr>`;
            return;
        }

        tbody.innerHTML = data.map(item => {
            let moneyText = '0 VNĐ';
            let feeClass = 'color: #64748b;';
            if (item.so_tien > 0) {
                moneyText = `-${formatVND(item.so_tien)} VNĐ`;
                feeClass = 'color: #ef4444; font-weight: 700;';
            } else if (item.so_tien < 0) {
                moneyText = `+${formatVND(Math.abs(item.so_tien))} VNĐ`;
                feeClass = 'color: #10b981; font-weight: 700;';
            }

            return `
                <tr>
                    <td style="color: #64748b; font-size: 0.85rem;">${item.thoi_gian}</td>
                    <td style="font-weight: 600;">${item.trang_thai}</td>
                    <td>${item.phuong_thuc}</td>
                    <td style="${feeClass} font-variant-numeric: tabular-nums;">${moneyText}</td>
                </tr>
            `;
        }).join('');
    } catch(e) {}
}

// Modal Controls
function openDepositModal() {
    const modal = document.getElementById('modal-deposit');
    if (modal) {
        modal.style.display = 'flex';
        updateDepositQr();
    }
}

function closeDepositModal() {
    const modal = document.getElementById('modal-deposit');
    if (modal) modal.style.display = 'none';
}

function handleModalBackdropClick(e) {
    if (e.target.id === 'modal-deposit') {
        closeDepositModal();
    }
}

function selectDepositAmount(amount) {
    const inp = document.getElementById('inp-deposit-amount');
    if (inp) {
        inp.value = amount;
        updateDepositQr();
    }
    document.querySelectorAll('.amount-chip').forEach(btn => {
        btn.classList.toggle('active', btn.innerText.includes(formatVND(amount)));
    });
}

function updateDepositQr() {
    const inp = document.getElementById('inp-deposit-amount');
    const qrImg = document.getElementById('deposit-qr-img');
    const amount = inp ? (parseFloat(inp.value) || 50000) : 50000;
    const mssv = studentData ? studentData.mssv : 'B22DCCN001';
    if (qrImg) {
        qrImg.src = `https://img.vietqr.io/image/970415-123456789-qr_only.png?amount=${amount}&addInfo=PTIT%20Parking%20${mssv}`;
    }
}

document.getElementById('inp-deposit-amount')?.addEventListener('input', updateDepositQr);

async function submitDeposit() {
    const inp = document.getElementById('inp-deposit-amount');
    const amount = parseFloat(inp.value);
    if (!amount || amount <= 0) {
        alert("Vui lòng nhập số tiền nạp hợp lệ (tối thiểu 1.000 VNĐ)!");
        return;
    }

    const btn = document.getElementById('btn-confirm-deposit');
    const btnText = document.getElementById('btn-confirm-deposit-text');
    btn.disabled = true;
    btnText.innerText = "Đang xử lý nạp tiền...";

    try {
        const res = await fetch('/api/user/deposit', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ amount })
        });
        const data = await res.json();
        
        if (res.ok) {
            closeDepositModal();
            showToast(`Nạp thành công ${formatVND(amount)} VNĐ vào ví!`);
            fetchUserProfile();
            loadParkingHistory();
            loadWalletHistory();
        } else {
            alert(data.message || "Giao dịch không thành công.");
        }
    } catch (err) {
        alert("Lỗi kết nối máy chủ khi nạp tiền.");
    } finally {
        btn.disabled = false;
        btnText.innerText = "Xác nhận Nạp tiền";
    }
}

// Toast
function showToast(msg) {
    const toast = document.getElementById('toast-message');
    if (!toast) return;
    toast.innerText = msg;
    toast.classList.add('show');
    setTimeout(() => { toast.classList.remove('show'); }, 3500);
}

// Logout
function handleLogout() {
    if (confirm("Bạn có chắc chắn muốn đăng xuất khỏi cổng sinh viên?")) {
        window.location.replace('/user/logout');
    }
}

// Init
window.addEventListener('DOMContentLoaded', () => {
    fetchUserProfile();
    loadParkingHistory();
});
