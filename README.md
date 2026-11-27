# ITS Group 9: Nhận diện phương tiện ưu tiên

Dự án demo cho tiểu luận kết thúc học phần môn **Hệ thống Giao thông Thông minh (ITS)**.
Đề tài: nhận diện phương tiện ưu tiên trong giao thông (xe cứu thương, xe cứu hỏa, xe công an).

| | |
| --- | --- |
| Nhóm | 9 |
| Giảng viên hướng dẫn | Vũ Đình Long |
| Thành viên | Trịnh Tuấn Văn, Nguyễn Thanh Toàn, Trần Thị Đài Trang, Nguyễn Trí Quý |

## Trạng thái

Website demo đã chạy được: nhận diện theo ảnh và theo video.
Phần nhận diện xe ưu tiên dùng **mô hình YOLOv8n do nhóm tự huấn luyện** (3 lớp: xe cứu thương,
xe cứu hỏa, xe công an), xuất sang ONNX và chạy bằng OpenCV (xem mục 4 và mục 11).

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

## 3. Chức năng

1. **Nhận diện theo ảnh:** người dùng tải ảnh lên (JPG, PNG, WEBP), mô hình tìm các xe ưu tiên trong
   ảnh, cho biết loại xe, độ tin cậy và vẽ khung quanh từng xe.
2. **Nhận diện theo video:** người dùng tải video lên (MP4, AVI, MOV, MKV, WEBM). Hệ thống lấy
   khoảng 2 khung hình mỗi giây, nhận diện từng khung rồi tổng hợp: video có xe ưu tiên hay
   không, xuất hiện ở những giây nào (dòng thời gian). Cần thấy xe ưu tiên ở ít nhất 2 khung
   hình để tránh nhận nhầm một lần.

## 4. Công nghệ

| Phần | Công nghệ |
| --- | --- |
| Giao diện (frontend) | HTML, CSS, JavaScript |
| Máy chủ (backend) | Python, FastAPI |
| Nhận diện xe ưu tiên | YOLOv8n tự huấn luyện, xuất sang ONNX (`backend/app/ml/models/priority_yolov8n.onnx`), chạy bằng OpenCV, không cần PyTorch |
| Đọc video | OpenCV |

Cách nhận diện, theo thứ tự:
1. Ảnh được đưa về 640x640 (giữ tỉ lệ, chèn viền xám).
2. Mô hình YOLOv8n cho ra khung, loại xe (Ambulance / Fire truck / Police car) và độ tin cậy.
3. Giữ các khung có độ tin cậy từ 0,50 trở lên (đổi bằng biến môi trường `DETECT_CONF`), loại khung trùng bằng NMS.

Dữ liệu huấn luyện: bộ "Ambulance-Fire-Police Computer Vision Dataset" của tác giả jaa trên Roboflow
Universe, phiên bản 5, giấy phép CC BY 4.0
(https://universe.roboflow.com/jaa-ifc6q/ambulance-fire-police/dataset/5). Nhóm chia lại theo ảnh gốc
thành train 8352 / valid 1027 / test 1028 ảnh, huấn luyện 30 epoch từ `yolov8n.pt` trên Google Colab (GPU T4).
Notebook, đồ thị huấn luyện và ma trận nhầm lẫn nằm trong `docs/training/`.
(Lưu ý: bản notebook sắp xếp tên file trước khi chia để lần chạy lại ra kết quả cố định, nên tập test khi chạy lại
sẽ lệch vài ảnh so với lần nhóm đã chạy để lấy số liệu ở trên.)

Kết quả trên tập test (cùng nguồn dữ liệu với tập train, nên dễ hơn ảnh ngoài thực tế):

| Lớp | Precision | Recall | mAP@0.5 |
| --- | --- | --- | --- |
| Tất cả | 0,929 | 0,891 | 0,943 |
| Ambulance | 0,911 | 0,853 | 0,923 |
| Fire truck | 0,954 | 0,943 | 0,966 |
| Police car | 0,923 | 0,878 | 0,940 |

Hạn chế cần nêu trong báo cáo:
- Mô hình chỉ biết 3 lớp xe ưu tiên, không có lớp "xe thường". Log huấn luyện ghi `0 backgrounds`, nghĩa là
  không có ảnh nào không chứa xe ưu tiên, nên mô hình chưa học cách nói "đây không phải xe ưu tiên".
- Vì vậy xe thường có hình dáng, màu sắc giống xe ưu tiên có thể bị nhận nhầm. Các ví dụ đã gặp:
  xe buýt màu xanh trên đường phố Việt Nam bị báo là xe cứu hỏa (độ tin cậy khoảng 0,76);
  xe máy điện màu đỏ bị báo là xe cứu hỏa (khoảng 0,58).
- Các ảnh mẫu của bộ dữ liệu mà nhóm xem qua phần lớn là xe nước ngoài, nên xe ưu tiên tại Việt Nam có thể nhận diện kém hơn.

Cách giảm nhận nhầm:
- Cách nhanh (chỉ che được một phần): nâng ngưỡng tin cậy. Trên PowerShell:
  ```
  $env:DETECT_CONF="0.8"
  uvicorn backend.main:app --reload
  ```
  Với ngưỡng 0,8, hai ví dụ nhận nhầm ở trên không còn bị báo, nhưng xe ưu tiên thật mà mô hình chỉ tin 50-80% sẽ bị bỏ sót.
  Nhóm mới thử trên rất ít ảnh nên chưa biết ngưỡng nào tốt nhất.
- Cách sửa thật: thêm ảnh xe thường (xe máy, ô tô, xe buýt, xe tải, tốt nhất là đường phố Việt Nam) làm mẫu âm
  (ảnh có nhãn rỗng), huấn luyện lại rồi đo lại trên tập test.

## 5. Luồng hoạt động

```
Người dùng  ->  Giao diện web  ->  API (FastAPI)  ->  Dịch vụ nhận diện  ->  Kết quả
  (tải ảnh/video)                  (kiểm tra file)      YOLOv8 tìm xe          (xe ưu tiên hay
                                                       ưu tiên                  không, ảnh có khung)
```

## 6. API

| Method | Đường dẫn | Mô tả |
| --- | --- | --- |
| GET | `/api/health` | Kiểm tra máy chủ đang chạy |
| POST | `/api/detect/image` | Nhận ảnh tải lên, trả về kết quả nhận diện |
| POST | `/api/detect/video` | Nhận video tải lên, trả về kết quả tổng hợp và dòng thời gian |

Ví dụ kết quả trả về:
```json
{
  "is_priority": true,
  "vehicle_type": "ambulance",
  "label_vi": "Xe cứu thương",
  "confidence": 0.93,
  "mode": "phan_tich_anh",
  "message": "Phát hiện 1 xe ưu tiên: Xe cứu thương (số 1, 93%).",
  "detections": [ { "index": 1, "box": [0, 51, 754, 387], "...": "..." } ],
  "annotated_image": "data:image/jpeg;base64,..."
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
  ml/                   YOLOv8 ONNX (yolo_detector.py), file mô hình (models/)
frontend/
  css/                  Giao diện
  js/app.js             Mã JavaScript (chọn file, gọi API, hiển thị kết quả)
  assets/               Ảnh, biểu tượng
storage/uploads/        Chỗ lưu tạm file đang xử lý, xong là xóa (không đưa lên GitHub)
tests/                  Kiểm thử (feature, unit)
docs/                   Tài liệu, dàn ý tiểu luận, sơ đồ
docs/training/          Notebook huấn luyện, kết quả huấn luyện, trọng số best.pt
```

## 8. Yêu cầu hệ thống

- Windows 10 trở lên
- Python 3.14 (hoặc 3.11 trở lên)
- Git
- Trình duyệt hiện đại (Chrome, Edge, Brave...)

## 9. Cài đặt và chạy

Các bước:

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
5. Chạy kiểm thử: `python -m pytest`

Lưu ý:
- File mô hình (khoảng 13 MB) nằm sẵn trong `backend/app/ml/models/priority_yolov8n.onnx`, không cần tải thêm.
  Nếu thiếu file này, máy chủ báo lỗi 503.
- Nên dùng OpenCV 4.8 trở lên (đã ghi trong `requirements.txt`) để đọc được file ONNX của YOLOv8.
- Đổi ngưỡng tin cậy: đặt biến môi trường `DETECT_CONF` (mặc định 0.50).
- Ảnh tối đa 10 MB, video tối đa 50 MB và chỉ phân tích tối đa 60 giây đầu. Có thể đổi bằng biến môi trường
  `MAX_UPLOAD_MB`, `MAX_VIDEO_MB`, `MAX_VIDEO_SECONDS`, `MAX_VIDEO_FRAMES`.

## 10. Làm việc nhóm

- Mỗi thành viên làm trên một branch riêng, đặt tên theo tên mình, ví dụ `feature/ten-ban`.
- Không đẩy trực tiếp lên `main`; tạo Pull Request để cả nhóm xem trước khi gộp.
- Viết nội dung commit rõ ràng, ví dụ "Thêm API nhận diện theo ảnh".
- Không đưa lên GitHub: thư mục `.venv`, file `.env`, ảnh trong `storage/uploads`.

## 11. Hướng phát triển

- Bổ sung ảnh xe cứu thương, cứu hỏa, công an của Việt Nam và ảnh xe thường (xe máy, ô tô, xe buýt, xe tải) làm mẫu âm, huấn luyện lại để giảm nhận nhầm.
- Thêm nhận diện bằng âm thanh (tiếng còi hú).
- Nhận diện video theo thời gian thực từ camera (hiện chỉ xử lý file video tải lên).
- Kết hợp với điều khiển tín hiệu đèn để ưu tiên xe cứu thương, xe cứu hỏa.
