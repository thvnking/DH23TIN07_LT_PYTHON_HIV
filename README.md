# ĐỒ ÁN LẬP TRÌNH PYTHON - PHÂN TÍCH & TRỰC QUAN HÓA DỮ LIỆU HIV/AIDS TOÀN CẦU
**Mã lớp:** DH23TIN07  
**Chủ đề:** Phân tích dữ liệu dịch tễ HIV/AIDS và ứng dụng web trực quan hóa theo quốc gia trên bản đồ thế giới.

---

## 🌟 Giới thiệu ứng dụng Web
Ứng dụng web được xây dựng hoàn toàn bằng **Python** (sử dụng thư viện chuẩn của Python, không yêu cầu cài đặt thêm các thư viện phức tạp), cho phép:
1. **Hiển thị Bản đồ thế giới tương tác (Interactive World Map)** với dữ liệu dịch tễ học của hơn 200 quốc gia và vùng lãnh thổ.
2. **Nhấp chuột vào bất kỳ quốc gia nào trên bản đồ** để xem ngay chi tiết 2 bảng số liệu:
   - **Bảng 1 (Prevalence & Mortality):** Ước tính tỷ lệ hiện nhiễm ở người lớn (%), số người sống chung với HIV/AIDS (PLHIV), số ca tử vong hàng năm và năm ước tính (từ `HIV_AIDS prevalence estimates table.csv`).
   - **Bảng 2 (ART Coverage & Treatment):** Tình hình điều trị thuốc kháng virus ART, số người đang nhận điều trị, khoảng ước tính PLHIV [Min – Max], và tỷ lệ bao phủ điều trị ART (%) [Min – Max] (từ `art_coverage_by_country_clean.csv`).
3. **Đối chiếu với mô hình hồi quy (Task T1 - Ridge Regression):** Đưa ra ước tính số ca tử vong dựa trên mô hình học máy và so sánh với số liệu thực tế.
4. **Tìm kiếm & Chọn nhanh:** Hỗ trợ thanh tìm kiếm thông minh, danh sách xổ xuống (A-Z) và các nút chọn nhanh những quốc gia tiêu biểu (Việt Nam, Nam Phi, Thái Lan, Hoa Kỳ, Pháp, v.v.).

---

## 🚀 Cách chạy ứng dụng

### Cách 1: Chạy bằng lệnh Python
Mở Terminal / PowerShell tại thư mục dự án và chạy:
```bash
python app.py
```
*(hoặc `python Python.py`)*

Server sẽ tự động khởi động tại địa chỉ: **http://127.0.0.1:8000** và tự động mở trình duyệt web.

### Cách 2: Nhấp đúp chuột (Windows)
Nhấp đúp chuột vào tệp **`run.bat`** để chạy trực tiếp.

---

## 📁 Cấu trúc thư mục dự án
```text
DH23TIN07_LT_PYTHON_HIV/
├── app.py                  # Ứng dụng Web server Python & giao diện bản đồ
├── Python.py               # Điểm khởi chạy phụ
├── run.bat                 # File chạy nhanh 1-click trên Windows
├── data/
│   └── raw/
│       ├── HIV_AIDS prevalence estimates table.csv   # Dữ liệu Bảng 1
│       └── art_coverage_by_country_clean.csv         # Dữ liệu Bảng 2
├── notebooks/
│   └── HIV_AIDS_Analysis.ipynb                       # Notebook phân tích & huấn luyện mô hình
└── README.md               # Hướng dẫn sử dụng
```
