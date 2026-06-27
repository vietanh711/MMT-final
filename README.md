# I. Hướng dẫn sử dụng Tool chấm tự luận cuối kì Mạng máy tính sử dụng Gemini API



## 1. Chuẩn bị



Cài đặt Python và các thư viện cần thiết:



```bash

pip install selenium google-generativeai google-api-core

```



Truy cập: https://aistudio.google.com/apps để tạo **Gemini API Key**.



Mở file `mmt.py` và thay API Key:



```python

API_KEY = "YOUR_API_KEY"

```



Mặc định chương trình sử dụng model `gemini-3.1-flash-lite`, phù hợp cho việc chấm bài với tốc độ cao và quota lớn.



## 2. Mở hệ thống chấm thi



Khởi động Google Chrome ở chế độ Debug (đối với Windows):



```bash

"C:\Users\Admin\AppData\Local\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\chrome-temp"

```



Đối với macOS, thực hiện tương tự bằng cách mở Chrome với cổng `9222`.



Sau khi cửa sổ Chrome mới xuất hiện, đăng nhập vào hệ thống chấm thi và mở danh sách các bài cần chấm.



## 3. Chạy chương trình



Thực hiện lệnh:



```bash

python mmt.py

```



Chương trình sẽ hiển thị tổng số phách cần chấm.



* Nhấn **Enter** để chấm từ bài đầu tiên.

* Hoặc nhập **số phách** để tiếp tục chấm từ bài mong muốn.



## 4. Quá trình chấm



Sau khi chạy, chương trình sẽ tự động:



* Mở từng bài thi.

* Đọc câu hỏi và câu trả lời của sinh viên.

* Gửi nội dung đến Gemini để chấm điểm.

* Nhập điểm và nhận xét vào hệ thống.

* Nhấn **Ghi nhận** và chuyển sang bài tiếp theo.



## 5. Thay đổi đáp án



Để sử dụng cho học phần khác, chỉ cần cập nhật biến `DAP_AN_CHUAN` trong file `mmt.py`. Các phần còn lại của chương trình không cần chỉnh sửa.

# II. Quy trình phát triển Tool

## 1. Khảo sát hệ thống chấm thi

Trước khi phát triển chương trình, cần khảo sát cấu trúc của hệ thống chấm thi nhằm xác định các thành phần mà chương trình sẽ tự động thao tác.

Các thành phần cần xác định bao gồm:

- Danh sách số phách của các bài thi.
- Khu vực chứa từng bài làm.
- Cấu trúc hiển thị câu hỏi.
- Khu vực chứa câu trả lời của sinh viên.
- Ô nhập điểm.
- Ô nhập nhận xét.
- Nút "Ghi nhận".

Trong chương trình, Selenium sử dụng các XPath, ID và ClassName để truy cập các thành phần này. Do đó, nếu giao diện hệ thống thay đổi thì chỉ cần cập nhật lại các Selector tương ứng mà không cần sửa đổi thuật toán xử lý.

---

## 2. Xây dựng đáp án chuẩn

Sau khi khảo sát đề thi, xây dựng đáp án chuẩn cho từng câu hỏi.

Đáp án được lưu trong Dictionary `DAP_AN_CHUAN`, trong đó:

- Key là số thứ tự câu hỏi.
- Value là đáp án chuẩn tương ứng.

Ví dụ:

```python
DAP_AN_CHUAN = {
    1: "...",
    2: "...",
    ...
}
```

Việc tách đáp án ra khỏi chương trình giúp:

- Dễ cập nhật khi đề thi thay đổi.
- Có thể sử dụng lại thuật toán cho nhiều học phần khác nhau.
- Không cần chỉnh sửa phần xử lý của chương trình.

---

## 3. Thiết kế Prompt chấm điểm

Prompt là thành phần quan trọng nhất của hệ thống.

Chương trình không gửi trực tiếp bài làm của sinh viên tới Gemini mà xây dựng một Prompt hoàn chỉnh gồm nhiều thành phần.

### 3.1. Bối cảnh hệ thống

Prompt đầu tiên mô tả toàn bộ bối cảnh mạng của đề thi.

Ví dụ:

- Cấu trúc mạng.
- Vai trò của các máy.
- Router.
- DNS.
- NAT.
- Trạng thái ban đầu.

Việc cung cấp bối cảnh giúp Gemini hiểu ngữ cảnh của câu hỏi mà không cần suy diễn.

### 3.2. Nội dung câu hỏi

Chương trình đọc trực tiếp câu hỏi từ hệ thống chấm thi.

Điều này giúp Prompt luôn khớp với đề thi thực tế.

### 3.3. Đáp án chuẩn

Đáp án chuẩn của câu hỏi tương ứng được lấy từ biến `DAP_AN_CHUAN`.

Gemini sử dụng đáp án này làm mốc để đánh giá.

### 3.4. Bài làm của sinh viên

Chương trình đọc toàn bộ câu trả lời của sinh viên từ hệ thống.

Không thực hiện bất kỳ bước tiền xử lý nào nhằm đảm bảo AI đánh giá đúng nội dung gốc.

### 3.5. Quy tắc chấm điểm

Prompt quy định rõ:

- Ưu tiên bản chất kiến thức.
- Không bắt lỗi diễn đạt.
- Chấm theo tỷ lệ đúng.
- Quy định mức trừ điểm.
- Khi nào cho 0 điểm.
- Thang điểm 0–5.

Nhờ vậy, Gemini luôn chấm theo cùng một tiêu chí.

### 3.6. Chuẩn hóa nhận xét

Prompt yêu cầu:

- Chỉ sử dụng từ "sinh viên".
- Không sử dụng từ "học sinh".
- Không sử dụng đại từ "họ".

Điều này giúp toàn bộ nhận xét thống nhất. Đặc điểm của các LLM thấp là hay dùng từ ngoài phạm vi như "họ" nên cần chỉnh lại.

### 3.7. Định dạng đầu ra

Prompt yêu cầu Gemini chỉ trả về JSON.

Ví dụ:

```json
{
    "reasoning":"...",
    "score":4.5
}
```

Định dạng này giúp chương trình có thể tự động phân tích kết quả.

---

## 4. Tích hợp Gemini API

Sau khi Prompt hoàn thiện, chương trình tích hợp Gemini API.

Các bước thực hiện:

- Khai báo API Key.
- Khởi tạo GenerativeModel.
- Thiết lập model mặc định.

Model sử dụng:

```
gemini-3.1-flash-lite
```

Model này được lựa chọn vì:

- tốc độ phản hồi nhanh;
- quota lớn;
- chi phí thấp;
- chất lượng đủ tốt cho bài toán chấm tự luận.

---

## 5. Thiết kế cơ chế xử lý kết quả AI

Sau khi Gemini trả lời, chương trình thực hiện nhiều bước kiểm tra.

### Bước 1

Đọc chuỗi JSON.

Nếu thành công sẽ lấy:

- score
- reasoning

### Bước 2

Nếu Gemini trả về Markdown hoặc thêm ký tự ngoài JSON, chương trình tự loại bỏ.

### Bước 3

Nếu JSON lỗi, chương trình sử dụng Regular Expression để tìm điểm số trong văn bản.

### Bước 4

Nếu vẫn thất bại, chương trình trả về:

- điểm = 0
- nhận xét rỗng

Nhờ vậy chương trình không bị dừng giữa quá trình chấm.

---

## 6. Thiết kế cơ chế chống giới hạn API

Trong quá trình chấm hàng trăm bài thi, Gemini có thể trả về lỗi giới hạn số lượt gọi.

Chương trình xử lý bằng cách:

- phát hiện ngoại lệ `ResourceExhausted`;
- chờ 30 giây;
- gửi lại yêu cầu;
- thử tối đa 3 lần.

Nhờ đó có thể chấm số lượng lớn bài thi mà không cần thao tác thủ công.

---

## 7. Tự động hóa trình duyệt

Chương trình sử dụng Selenium WebDriver kết hợp Chrome Remote Debugging.

Thay vì đăng nhập tự động, chương trình kết nối vào phiên Chrome đã đăng nhập sẵn.

Ưu điểm:

- Không phải xử lý CAPTCHA.
- Không lưu mật khẩu.
- Không bị hết phiên đăng nhập giữa quá trình chấm.

---

## 8. Thuật toán xử lý bài thi

Sau khi kết nối thành công, chương trình thực hiện:

1. Đọc toàn bộ danh sách số phách.
2. Cho phép nhập số phách bắt đầu.
3. Mở từng bài thi.
4. Truy cập từng iframe.
5. Đọc câu hỏi.
6. Đọc câu trả lời.
7. Ghép Prompt.
8. Gửi Gemini.
9. Nhận điểm.
10. Nhập điểm.
11. Nhập nhận xét.
12. Chuyển sang câu tiếp theo.
13. Sau khi hoàn thành bài thi, nhấn nút **Ghi nhận**.
14. Tiếp tục sang số phách tiếp theo.

Quá trình trên lặp lại cho đến khi hoàn thành toàn bộ danh sách bài thi.

---

## 9. Chuẩn hóa nhận xét

Sau khi AI trả về kết quả, chương trình tiếp tục xử lý nhận xét bằng Regular Expression.

Các từ như:

- học sinh
- Học sinh
- họ
- Họ

được thay thế thành:

- sinh viên
- Sinh viên

Điều này đảm bảo nhận xét thống nhất với quy định của học phần.

---

## 10. Khả năng mở rộng

Kiến trúc chương trình được chia thành ba phần độc lập:

- Dữ liệu (Đáp án chuẩn).
- AI (Prompt và Gemini).
- Selenium (Tự động thao tác trên hệ thống).

Nhờ kiến trúc này, khi triển khai cho học phần khác chỉ cần:

- cập nhật đáp án chuẩn;
- điều chỉnh Prompt;
- cập nhật XPath nếu giao diện thay đổi.

Toàn bộ thuật toán xử lý chính có thể giữ nguyên.