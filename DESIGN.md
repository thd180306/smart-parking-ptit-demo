# Design System

<!-- impeccable:design-schema 1 -->
/* Hallmark · macrostructure: Workbench · theme: Cobalt Steel · pre-emit critique: P5 H5 E5 S5 R5 V5 */

## Visual Authority & Theme Direction

- **Theme:** Cobalt Steel (Kỷ nguyên kỹ thuật & Công nghệ Học viện)
- **Primary Tone:** Deep Technical Navy (`#0f172a`, `#1e293b`), Crisp Steel Borders (`#e2e8f0`, `#cbd5e1`), Precise Electric Indigo Accent (`#2563eb`, `#1d4ed8`), Monospace Technical Figures.
- **Avoidances (Anti-AI Slop):** 
  - KHÔNG dùng gradient màu tím-hồng trên tiêu đề hoặc nền.
  - KHÔNG lồng card trong card vô nghĩa (Card-in-card tell).
  - KHÔNG dùng 3 cột icon giống hệt nhau.
  - KHÔNG dùng font icon bên ngoài dễ bị vỡ `▯`. Sử dụng hệ thống Vector SVG chuẩn.
  - KHÔNG bo góc quá đà (border-radius giới hạn 6px - 10px cho component, 12px cho modal).

## Typography

- **Display & Headings:** `Plus Jakarta Sans`, `-apple-system`, `BlinkMacSystemFont`, `sans-serif` (Roman only, font-weight 700, letter-spacing -0.02em).
- **Body:** `Inter`, `-apple-system`, `BlinkMacSystemFont`, `Segoe UI`, `sans-serif` (line-height 1.5, font-weight 400 & 500).
- **Data & Codes:** `JetBrains Mono`, `ui-monospace`, `SFMono-Regular`, `Menlo`, `Monaco`, `monospace` (font-variant-numeric: tabular-nums).

## Color Tokens (CSS Variables)

```css
:root {
    --bg-base: #f8fafc;
    --surface-card: #ffffff;
    --surface-inset: #f1f5f9;
    --border-subtle: #e2e8f0;
    --border-strong: #cbd5e1;
    --text-primary: #0f172a;
    --text-secondary: #475569;
    --text-tertiary: #94a3b8;
    --accent: #2563eb;
    --accent-hover: #1d4ed8;
    --accent-subtle: #eff6ff;
    --status-success: #059669;
    --status-success-bg: #ecfdf5;
    --status-danger: #dc2626;
    --status-danger-bg: #fef2f2;
    --status-warning: #d97706;
    --status-warning-bg: #fffbeb;
}
```

## Component Architecture

1. **Admin Workbench Navigation (N3 Side-rail):** Thanh điều hướng sẫm màu gọn gàng, định vị rõ phân hệ đang làm việc.
2. **Gate Control Simulator:** Tích hợp màn hình Camera AI OCR có đường quét laser chuyển động thực tế + Mô hình cần gạt Barrier cơ học chuyển động xoay góc thực nghiệm.
3. **Student Pass Digital Wallet:** Thiết kế thẻ vật lý kỹ thuật số có vi mạch bảo mật, số dư định dạng số liệu kế toán rõ ràng, tích hợp mã QR thanh toán động.
4. **Interactive SQL Console:** Khung soạn thảo lệnh SQL tối màu cho kỹ sư với bảng hiển thị dữ liệu lưới tiêu chuẩn CSDL.
