I. CÁCH SỬ DỤNG TOOL CHẤM TỰ LUẬN CUỐI KÌ MMT SỬ DỤNG GEMINI API
1. Chuẩn bị
Cài đặt Python và các thư viện cần thiết:

pip install selenium 
google-generativeai 
google-api-core

Truy cập vào: https://aistudio.google.com/apps để tạo GEMINI API KEY
Mở file mmt.py và thay API Key:
API_KEY = "YOUR_API_KEY"
Mặc định sử dụng model Gemini-3.1-flash-lite (có nhiều Quota, mạnh mẽ)

2. Mở hệ thống chấm thi

Khởi động Google Chrome ở chế độ Debug(Áp dụng cho máy Windows, máy Mac làm tương tự):

"C:\Users\Admin\AppData\Local\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\chrome-temp"

Một cửa sô chrome mới hiện ra. Đăng nhập vào hệ thống chấm thi và mở danh sách các bài cần chấm.

3. Chạy chương trình

Thực hiện lệnh:

python mmt.py

Chương trình sẽ hiển thị tổng số phách cần chấm.

Nhấn Enter để chấm từ đầu.
Hoặc nhập số phách để tiếp tục chấm từ bài mong muốn.

4. Quá trình chấm
Sau khi chạy, chương trình sẽ tự động:
Mở từng bài thi.
Đọc câu hỏi và câu trả lời của sinh viên.
Gửi nội dung đến AI để chấm điểm.
Nhập điểm và nhận xét vào hệ thống.
Nhấn nút Ghi nhận và chuyển sang bài tiếp theo.

5. Thay đổi đáp án
Để sử dụng cho môn học khác, chỉ cần cập nhật đáp án trong biến DAP_AN_CHUAN của file mmt.py. Các phần còn lại của chương trình không cần chỉnh sửa.