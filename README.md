# ITS Group 9: Nhận diện phương tiện ưu tiên

Dự án demo cho tiểu luận môn Hệ thống Giao thông Thông minh (ITS).
Đề tài: nhận diện phương tiện ưu tiên trong giao thông (xe cứu thương, xe cứu hỏa, xe công an).

- Nhóm: 9
- Giảng viên hướng dẫn: Vũ Đình Long
- Thành viên: Trịnh Tuấn Văn, Nguyễn Thanh Toàn, Trần Thị Đài Trang, Nguyễn Trí Quý

## Trạng thái

Dự án đang trong giai đoạn khởi tạo. Cấu trúc thư mục đã có, mã nguồn đang được viết.

## Chức năng dự kiến

- Người dùng chọn loại xe từ danh sách, hệ thống cho biết đó có phải phương tiện ưu tiên không.
- Người dùng tải ảnh xe lên, hệ thống nhận diện ảnh và cho biết đó có phải phương tiện ưu tiên không.
- Hệ thống không lưu lịch sử nhận diện.

## Công nghệ dự kiến

| Phần | Công nghệ |
| --- | --- |
| Giao diện (frontend) | HTML, CSS, JavaScript |
| Máy chủ (backend) | Python, FastAPI |
| Nhận diện ảnh | Sẽ chốt sau (mô hình nhận diện theo mô tả hoặc tự huấn luyện) |

## Cấu trúc thư mục

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

## Cách chạy

Sẽ cập nhật khi có mã nguồn.

## Lưu ý

Đây là sản phẩm demo phục vụ học tập. Kết quả nhận diện chỉ mang tính minh họa.