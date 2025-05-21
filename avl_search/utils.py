import unicodedata

import os

def load_vietnamese_stopwords(file_path=None):
    """
    Đọc danh sách stop words từ file text
    Tương đương với chức năng của file index.js trong repository
    """
    if file_path is None:
        # Tự động tìm file trong thư mục dự án
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        potential_paths = [
            os.path.join(base_dir, "data", "vietnamese-stopwords.txt"),
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "vietnamese-stopwords", "vietnamese-stopwords.txt")
        ]
        
        for path in potential_paths:
            if os.path.exists(path):
                file_path = path
                break
    
    if not file_path or not os.path.exists(file_path):
        print("Không tìm thấy file vietnamese-stopwords.txt")
        return set()
        
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            # Đọc từng dòng, loại bỏ khoảng trắng và lọc dòng rỗng
            stopwords = [word.strip() for word in f.readlines()]
            stopwords = [word for word in stopwords if word and len(word) > 0]
            return set(stopwords)  # Chuyển thành set để tìm kiếm hiệu quả hơn
    except Exception as e:
        print(f"Lỗi khi đọc file stop words: {e}")
        return set()

# Biến toàn cục để lưu danh sách stop words
VIETNAMESE_STOPWORDS = load_vietnamese_stopwords()

def is_stopword(word):
    """Kiểm tra xem từ có phải là stop word không"""
    return word.lower() in VIETNAMESE_STOPWORDS

def remove_stopwords(text_list):
    return [word for word in text_list if not is_stopword(word)]
def remove_accents(input_str):
    if not input_str:
        return ""
    s = input_str
    s = unicodedata.normalize('NFD', s)
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    return s
SEARCH_TIPS = """
"""

# Các hàm/biến này được sử dụng ở:
# - document_manager.py: remove_accents, VIETNAMESE_STOPWORDS, remove_stopwords (trích xuất và xử lý từ khóa)
# - ui.py: SEARCH_TIPS (hiển thị hướng dẫn tìm kiếm)