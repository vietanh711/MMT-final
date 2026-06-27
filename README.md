# Hướng dẫn sử dụng Tool chấm tự luận cuối kì Mạng máy tính sử dụng Gemini API



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