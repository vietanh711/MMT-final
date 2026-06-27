import json
import re
import time
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import sys

API_KEY = "YOUR_API_KEY"

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-3.1-flash-lite')

DAP_AN_CHUAN = {
    1: "Application (HTTP message) → Transport (TCP segment) → Network (IP datagram) → Link (Ethernet frame). Mỗi tầng đóng gói (encapsulation) thêm header của tầng đó vào dữ liệu của tầng trên.",
    2: "4 loại trễ: trễ xử lý (processing delay), trễ hàng đợi (queuing delay), trễ truyền dẫn (transmission delay), trễ lan truyền (propagation delay). Trễ truyền dẫn (transmission delay = L/R) phụ thuộc vào kích thước gói tin (L) và băng thông (R).",
    3: "Giao thức DNS (Domain Name System). DNS thường dùng UDP vì truy vấn/đáp ứng ngắn, không cần thiết lập kết nối, ưu tiên độ trễ thấp; nếu kích thước message lớn (ví dụ DNSSEC) thì chuyển sang TCP.",
    4: "DNS-LOCAL gửi truy vấn tới Root server → Root trả về địa chỉ của TLD server (.vn) → DNS-LOCAL truy vấn TLD server → TLD trả về địa chỉ Authoritative server của abc.com.vn → DNS-LOCAL truy vấn Authoritative server → nhận được địa chỉ IP của www.abc.com.vn → trả kết quả về cho máy A.",
    5: "(1) A gửi segment SYN (SYN=1, chọn số thứ tự khởi đầu client_isn) đến WS. (2) WS trả lời bằng segment SYN-ACK (SYN=1, ACK=1, ACK number = client_isn+1, chọn server_isn). (3) A gửi segment ACK (ACK=1, ACK number = server_isn+1) xác nhận, kết nối được thiết lập (ESTABLISHED).",
    6: "TCP cung cấp dịch vụ tin cậy: có xác nhận (ACK), truyền lại (retransmission) gói mất, điều khiển luồng và điều khiển tắc nghẽn, đảm bảo dữ liệu đến đúng thứ tự, không mất. UDP không đảm bảo các điều này, gói có thể mất hoặc đến không đúng thứ tự, nhưng có overhead thấp và độ trễ thấp hơn. Với video call thời gian thực nên chọn UDP vì độ trễ thấp quan trọng hơn việc truyền lại.",
    7: "R2 duy trì bảng NAT translation table ghi lại cặp (IP private + port nguồn) ↔ (IP public của R2 + port nguồn đã được NAT đổi/ánh xạ). Khi gói trả lời về tới R2, R2 tra bảng NAT để xác định đúng máy nội bộ cần chuyển gói tới.",
    8: "Vì lượng địa chỉ IPv4 public hạn chế, không đủ để cấp cho mọi thiết bị; các thiết bị trong mạng nội bộ chỉ cần giao tiếp ra Internet thông qua router biên. Lợi ích: tiết kiệm địa chỉ IPv4 public, và tăng tính bảo mật vì các máy nội bộ không bị truy cập trực tiếp từ Internet.",
    9: "A gửi một ARP Request (broadcast tới địa chỉ MAC FF:FF:FF:FF:FF:FF) hỏi 'ai có địa chỉ IP này, cho biết MAC'. R1 trả lời bằng ARP Reply (unicast) chứa địa chỉ MAC của mình. A lưu cặp (IP, MAC) của R1 vào ARP cache.",
    10: "Cần có một thiết bị định tuyến — router hoặc switch lớp 3 — để định tuyến gói tin giữa hai VLAN khác nhau. Switch lớp 2 thông thường chỉ hoạt động ở tầng Liên kết dữ liệu, không có khả năng xử lý địa chỉ IP nên không thể tự chuyển gói."
}

def cham_diem_bang_ai(cau_hoi, cau_tra_loi, dap_an_chuan):
    ngu_canh_he_thong = """Bối cảnh mạng của Công ty ABC:
    1. Hạ tầng VP Hà Nội: Máy tính A, B, C, Web Server WS và DNS-LOCAL cắm vào Switch L2 (SW1). SW1 nối tới Router R1 (thực hiện NAT, ra Internet).
    2. Hạ tầng VP Đà Nẵng: Máy tính M, N kết nối Wi-Fi vào AP1. AP1 nối vào SW2, SW2 nối tới Router R2 (thực hiện NAT, ra Internet).
    3. Định danh: Hoa (A), Nam (B), An (WS), Linh (M).
    4. Kỹ thuật: Mạng nội bộ dùng IP Private. R1, R2 mỗi router có 1 IP public.
    5. Trạng thái: Các bảng cache (ARP, DNS, MAC) đều trống trước khi bắt đầu câu hỏi."""

    prompt = f"""
    Bạn là một giảng viên môn Mạng máy tính. Hãy chấm bài thi với tiêu chí CÔNG TÂM, KHÁCH QUAN, đánh giá đúng năng lực hiểu bài của sinh viên.

    [Ngữ cảnh hệ thống]:
    {ngu_canh_he_thong}

    [Câu hỏi]:
    {cau_hoi}

    [Barem Đáp Án Chuẩn (Mốc 5.0 điểm)]:
    {dap_an_chuan}

    [Câu trả lời của sinh viên]:
    {cau_tra_loi}

    ---
    [Hướng dẫn chấm điểm - CÔNG TÂM VÀ CÂN BẰNG]:
    1. ƯU TIÊN BẢN CHẤT, KHÔNG BẮT BẺ TỪ KHÓA: Sinh viên có thể diễn đạt bằng ngôn từ riêng. Nếu logic mạng và bản chất kỹ thuật đúng, hãy tính điểm phần đó.
    2. CHẤM ĐIỂM THEO TỶ LỆ CHÍNH XÁC: Phân bổ 5.0 điểm đều cho các ý trong Barem.
    3. XỬ LÝ LỖI SAI: 
       - Trừ điểm nặng (1.0 - 2.0 điểm) nếu sai lệch hoàn toàn về mặt bản chất ở một ý nào đó.
       - Trừ điểm nhẹ (0.5 điểm) nếu thiếu một chi tiết phụ nhỏ nhưng không làm hỏng logic toàn cục.
    4. KHI NÀO CHO 0 ĐIỂM: Câu trả lời hoàn toàn trống, chứa ký tự rác, trả lời lạc đề 100%, hoặc sai hoàn toàn kiến thức cốt lõi.
    5. Thang điểm từ 0.0 đến 5.0 (CHỈ ĐƯỢC 1 CHỮ SỐ SAU DẤU PHẢY).
    6. CHUẨN MỰC NGÔN TỪ: TUYỆT ĐỐI THỐNG NHẤT dùng đại từ "sinh viên" hoặc "bài làm" để nhận xét. KHÔNG ĐƯỢC dùng từ "học sinh" hay "họ".

    ---
    [Yêu cầu định dạng đầu ra]:
    ĐẦU RA CUỐI CÙNG trả về chỉ được chứa DUY NHẤT một chuỗi JSON. Không thêm bất kỳ văn bản nào khác.

    {{
        "reasoning": "Giải thích ngắn gọn lý do trừ điểm hoặc cho điểm tối đa",
        "score": <số_điểm_dạng_float>
    }}
    """
    
    response = model.generate_content(prompt, generation_config={"temperature": 0.1}) 
    text_out = response.text.strip()
    
    try:
        clean_json = re.sub(r'```json|```', '', text_out).strip()
        data = json.loads(clean_json)
        return float(data.get("score", 0.0)), data.get("reasoning", "")
    except Exception:
        try:
            match_fallback = re.search(r'([0-5]\.\d+|[0-5])', text_out)
            score = float(match_fallback.group(1)) if match_fallback else 0.0
            return score, ""
        except Exception:
            return 0.0, ""

chrome_options = Options()
chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
driver = webdriver.Chrome(options=chrome_options)

def process_and_grade(driver):
    phach_labels = driver.find_elements(By.XPATH, "//table[@id='tbleas']//label[contains(@class, 'ta-primary')]")
    total_phach = len(phach_labels)
    
    if total_phach == 0:
        print("Không tìm thấy phách nào! Hãy kiểm tra lại trang web.")
        return
        
    print(f"Tìm thấy tổng cộng {total_phach} phách bài làm cần chấm.")

    user_input = input("Nhập số phách muốn bắt đầu (VD: 1160, 1207...) [Ấn Enter để chạy từ đầu]: ").strip()
    
    start_idx = 0
    if user_input:
        found = False
        for idx in range(total_phach):
            if phach_labels[idx].text.strip() == user_input:
                start_idx = idx
                found = True
                break
        
        if not found:
            print(f"\nLỖI: KHÔNG TÌM THẤY phách '{user_input}' trên trang này. Vui lòng kiểm tra lại!")
            sys.exit()
        
        print(f"\n=> Tìm thấy phách {user_input} ở vị trí thứ {start_idx + 1}/{total_phach}. Bắt đầu chạy từ đây.\n")
    else:
        print("\n=> Sẽ chạy từ phách đầu tiên đến hết.\n")

    for idx in range(start_idx, total_phach):
        try:
            phach_labels = driver.find_elements(By.XPATH, "//table[@id='tbleas']//label[contains(@class, 'ta-primary')]")
            current_label = phach_labels[idx]
            phach_text = current_label.text.strip()
            
            print(f"\nĐANG CHẤM PHÁCH {idx + 1}/{total_phach} (Số phách: {phach_text})")
            
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", current_label)
            time.sleep(0.5)
            current_label.click()
            time.sleep(3) 

            iframes = driver.find_elements(By.CLASS_NAME, "tae-internal")
            total_cau_hoi = len(iframes)
            print(f"Phách này có {total_cau_hoi} câu hỏi cần chấm.")
            
            for i in range(total_cau_hoi):
                time.sleep(3) 
                id_cau_hoi = i + 1
                dap_an_tham_khao = DAP_AN_CHUAN.get(id_cau_hoi, "Không có đáp án chuẩn.")
                
                try:
                    current_iframes = driver.find_elements(By.CLASS_NAME, "tae-internal")
                    driver.switch_to.frame(current_iframes[i])
                    
                    questions = driver.find_elements(By.CSS_SELECTOR, "div.q-problem p")
                    cau_hoi = questions[-1].text.strip() if questions else ""
                    
                    answer_div = driver.find_element(By.CLASS_NAME, "ta-text-answer-0")
                    cau_tra_loi = answer_div.text.strip()
                    
                    diem = 0.0
                    ly_do = ""
                    for retry in range(3): 
                        try:
                            diem, ly_do = cham_diem_bang_ai(cau_hoi, cau_tra_loi, dap_an_tham_khao)
                            break 
                        except ResourceExhausted:
                            print(f"Câu {id_cau_hoi} dính lỗi hạn mức API. Đang đợi 30 giây...")
                            time.sleep(30)
                        except Exception as e:
                            print(f"Lỗi API: {e}")
                            break

                    print(f"Câu {id_cau_hoi} | Điểm AI: {diem} | Lý do: {ly_do if ly_do else 'BỎ QUA DO LỖI JSON'}")
                    
                    mark_input = driver.find_element(By.ID, "tamark")
                    mark_input.clear()
                    mark_input.send_keys(str(diem))
                    
                    comment_input = driver.find_element(By.ID, "tacomment")
                    comment_input.clear()
                    
                    if ly_do:
                        ly_do_sach = re.sub(r'\b[Hh]ọc\s+sinh\b', lambda m: 'Sinh viên' if m.group(0)[0].isupper() else 'sinh viên', ly_do)
                        ly_do_sach = re.sub(r'\b[Hh]ọ\b', lambda m: 'Sinh viên' if m.group(0)[0].isupper() else 'sinh viên', ly_do_sach)
                        comment_input.send_keys(str(ly_do_sach))
                    
                    driver.switch_to.default_content()
                    
                except Exception as e:
                    print(f"Lỗi ở iframe {i} của phách {idx + 1}: {e}")
                    driver.switch_to.default_content()
                    
            save_button = driver.find_element(By.XPATH, "//input[@class='btn btn-info' and @value='Ghi nhận']")
            save_button.click()
            print(f"Đã hoàn thành và bấm Ghi nhận cho phách {idx + 1}.")
            time.sleep(2)
            
        except Exception as e:
            print(f"Lỗi hệ thống khi xử lý tại phách thứ {idx + 1}: {e}")
            driver.switch_to.default_content()

    print("\n[Hoàn tất chấm điểm tất cả các phách!]")

process_and_grade(driver)