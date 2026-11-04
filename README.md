# ITS Group 9: Nhận diện phương tiện ưu tiên

Dự án demo cho tiểu luận kết thúc học phần môn **Hệ thống Giao thông Thông minh (ITS)**.
Đề tài: nhận diện phương tiện ưu tiên trong giao thông (xe cứu thương, xe cứu hỏa, xe công an).

| | |
| --- | --- |
| Nhóm | 9 |
| Giảng viên hướng dẫn | Vũ Đình Long |
| Thành viên | Trịnh Tuấn Văn, Nguyễn Thanh Toàn, Trần Thị Đài Trang, Nguyễn Trí Quý |

## Trạng thái

Dự án đang trong giai đoạn khởi tạo: cấu trúc thư mục đã có, mã nguồn đang được viết.
Các mục ghi "dự kiến" dưới đây có thể thay đổi trong quá trình làm.

## 1. Giới thiệu

Trong giao thông đô thị, phương tiện ưu tiên như xe cứu thương, xe cứu hỏa, xe công an
cần di chuyển nhanh và an toàn, nhưng thường bị chậm do ùn tắc. Muốn hỗ trợ các xe này
(ví dụ ưu tiên tín hiệu đèn, cảnh báo cho các xe xung quanh) thì trước hết hệ thống phải
**nhận ra** xe nào là xe ưu tiên.

Dự án này xây dựng một website demo đơn giản cho bước nhận diện đó, để minh họa
nội dung tiểu luận.

## 2. Mục tiêu và phạm vi

Mục tiêu:
- Minh họa chức năng nhận diện phương tiện ưu tiên bằng một website đơn giản.
- Hỗ trợ trình bày tiểu luận trước giảng viên.

Phạm vi:
- Chỉ làm chức năng **nhận diện**, không điều khiển đèn tín hiệu.
- Không có đăng nhập, không có trang quản trị.
- Không lưu lịch sử nhận diện.

## 3. Chức năng dự kiến

1. **Nhận diện theo danh sách:** người dùng chọn loại xe (cứu thương, cứu hỏa, công an,
   xe con, xe tải...), hệ thống cho biết đó có phải phương tiện ưu tiên không.
2. **Nhận diện theo ảnh:** người dùng tải ảnh xe lên, hệ thống nhận diện ảnh và cho biết
   đó có phải phương tiện ưu tiên không, kèm độ tin cậy.

## 4. Công nghệ dự kiến

| Phần | Công nghệ |
| --- | --- |
| Giao diện (frontend) | HTML, CSS, JavaScript |
| Máy chủ (backend) | Python, FastAPI |
| Nhận diện ảnh | Sẽ chốt sau: mô hình nhận diện theo mô tả hoặc tự huấn luyện |

## 5. Luồng hoạt động

```
Người dùng  ->  Giao diện web  ->  API (FastAPI)  ->  Dịch vụ nhận diện  ->  Kết quả
 (chọn loại xe                    (kiểm tra dữ liệu)    (theo danh sách          (xe ưu tiên
  hoặc tải ảnh)                                           hoặc theo ảnh)           hay không)
```

## 6. Thiết kế API dự kiến

| Method | Đường dẫn | Mô tả |
| --- | --- | --- |
| GET | `/api/health` | Kiểm tra máy chủ đang chạy |
| POST | `/api/detect/type` | Nhận loại xe được chọn, trả về kết quả nhận diện |
| POST | `/api/detect/image` | Nhận ảnh tải lên, trả về kết quả nhận diện |

Ví dụ kết quả trả về:
```json
{
  "is_priority": true,
  "vehicle_type": "ambulance",
  "confidence": 0.93
}
```
Tài liệu API tự sinh sẽ có tại `/docs` khi chạy máy chủ.

## 7. Cấu trúc thư mục

```
.github/workflows/      Cấu hình tự động kiểm tra (nếu dùng)
backend/app/
  routers/detection/    API nhận diện
  services/             Logic nhận diện
  schemas/              Kiểm tra dữ liệu vào, ra
  core/                 Cấu hình
  ml/                   Mô hình nhận diện ảnh
frontend/
  css/                  Giao diện
  js/                   Mã JavaScript
  assets/               Ảnh, biểu tượng
storage/uploads/        Ảnh người dùng tải lên (không đưa lên GitHub)
tests/                  Kiểm thử (feature, unit)
docs/                   Tài liệu, dàn ý tiểu luận, sơ đồ
```

## 8. Yêu cầu hệ thống

- Windows 10 trở lên
- Python 3.14 (hoặc 3.11 trở lên)
- Git
- Trình duyệt hiện đại (Chrome, Edge, Brave...)

## 9. Cài đặt và chạy

Phần này sẽ hoàn thiện khi có mã nguồn. Các bước dự kiến:

1. Tải mã nguồn:
   ```
   git clone https://github.com/ttv14dev/ITS-Group-9.git
   cd ITS-Group-9
   ```
2. Tạo môi trường ảo và cài thư viện:
   ```
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   pip install -r backend\requirements.txt
   ```
3. Chạy máy chủ (từ thư mục gốc của dự án):
   ```
   uvicorn backend.main:app --reload
   ```
4. Mở trình duyệt vào `http://127.0.0.1:8000`.

## 10. Làm việc nhóm

- Mỗi thành viên làm trên một branch riêng, đặt tên theo tên mình, ví dụ `feature/ten-ban`.
- Không đẩy trực tiếp lên `main`; tạo Pull Request để cả nhóm xem trước khi gộp.
- Viết nội dung commit rõ ràng, ví dụ "Thêm API nhận diện theo ảnh".
- Không đưa lên GitHub: thư mục `.venv`, file `.env`, ảnh trong `storage/uploads`.

## 11. Hướng phát triển

- Thay phần nhận diện mô phỏng bằng mô hình nhận diện ảnh thật.
- Thêm nhận diện bằng âm thanh (tiếng còi hú).
- Kết hợp với điều khiển tín hiệu đèn để ưu tiên xe cứu thương, xe cứu hỏa.
