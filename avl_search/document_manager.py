import os
import json
from datetime import datetime
from avl_tree import AVLTree
from utils import remove_accents
from utils import VIETNAMESE_STOPWORDS, remove_stopwords

# Thêm các import cho đọc pdf, docx
try:
    import docx
except ImportError:
    docx = None
try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

class DocumentManager:
    def __init__(self, data_dir=DATA_DIR):
        self.data_dir = data_dir
        self.docs_dir = os.path.join(self.data_dir, "documents")
        self.index_file = os.path.join(self.data_dir, "index.json")
        self.documents = {}
        self.search_index = AVLTree()
        os.makedirs(self.docs_dir, exist_ok=True)
        self.load_index()
    
    def load_index(self):
        if os.path.exists(self.index_file):
            try:
                with open(self.index_file, 'r', encoding='utf-8') as f:
                    self.documents = json.load(f)
                
                # Xây dựng lại chỉ mục tìm kiếm
                for doc_id, doc_info in self.documents.items():
                    keywords = set()
                    keywords.update(self._extract_keywords(doc_info['title']))
                    if isinstance(doc_info['keywords'], list):
                        keywords.update(doc_info['keywords'])
                    self.search_index.add_document(keywords, doc_id)
            except Exception as e:
                print(f"Lỗi khi tải chỉ mục: {e}")
                self.documents = {}
    
    def save_index(self):
        try:
            with open(self.index_file, 'w', encoding='utf-8') as f:
                json.dump(self.documents, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Lỗi khi lưu chỉ mục: {e}")
    
    def _extract_keywords(self, text):
        if not text:
            return set()
        
        text = ''.join(c if c.isalnum() or c.isspace() else ' ' for c in text.lower())
        text = remove_accents(text)
        
        words = text.split()
        
        words = [word for word in words if len(word) > 1 and word not in VIETNAMESE_STOPWORDS]
        
        return set(words)
    
    def _generate_doc_id(self, file_path):
        file_name = os.path.basename(file_path)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"{timestamp}_{file_name}"
    
    def add_document(self, file_path, title, category, keywords):
        if not os.path.exists(file_path):
            return False, "Tệp không tồn tại"

        doc_id = self._generate_doc_id(file_path)
        category_dir = os.path.join(self.docs_dir, category)
        os.makedirs(category_dir, exist_ok=True)
        dest_path = os.path.join(category_dir, os.path.basename(file_path))

        try:
            content_words = set()
            ext = os.path.splitext(file_path)[1].lower()
            try:
                if ext == ".txt":
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content_words = self._extract_keywords(f.read())
                elif ext == ".pdf" and PyPDF2:
                    with open(file_path, 'rb') as f:
                        reader = PyPDF2.PdfReader(f)
                        text = ""
                        for page in reader.pages:
                            text += page.extract_text() or ""
                        content_words = self._extract_keywords(text)
                elif ext == ".docx" and docx:
                    doc = docx.Document(file_path)
                    text = "\n".join([para.text for para in doc.paragraphs])
                    content_words = self._extract_keywords(text)
            except Exception as e:
                pass

            # Copy file vào thư mục đích
            with open(file_path, 'rb') as src, open(dest_path, 'wb') as dst:
                dst.write(src.read())

            # Tạo từ khóa từ tiêu đề, danh mục và nội dung
            all_keywords = set(keywords.lower().split(',')) if keywords else set()
            all_keywords.update(self._extract_keywords(title))
            all_keywords.add(category.lower())
            all_keywords.update(content_words)

            doc_info = {
                'title': title,
                'category': category,
                'keywords': list(all_keywords),
                'path': dest_path,
                'added_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

            self.documents[doc_id] = doc_info
            self.search_index.add_document(all_keywords, doc_id)
            self.save_index()
            return True, doc_id

        except Exception as e:
            return False, f"Lỗi khi thêm tài liệu: {e}"
    
    def search_documents(self, query):
        """
        Tìm kiếm tài liệu theo logic AND (tất cả từ khóa phải xuất hiện) và xếp hạng kết quả:
        +10 điểm cho mỗi từ khóa xuất hiện trong tiêu đề
        +5 điểm cho mỗi từ khóa xuất hiện trong danh mục
        +1 điểm cho mỗi từ khóa khớp chính xác trong nội dung
        +0.5 điểm cho mỗi từ khóa là tiền tố của từ trong nội dung
        """
        keywords = self._extract_keywords(query)
        if not keywords:
            return list(self.documents.items())
        doc_ids = self.search_index.search(list(keywords))
        ranked_docs = []
        for doc_id in doc_ids:
            doc_info = self.documents[doc_id]
            score = 0
            title = doc_info['title'].lower()
            category = doc_info['category'].lower()
            # Đọc nội dung file (nếu có thể)
            content = ""
            try:
                with open(doc_info['path'], 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
            except:
                pass
            content_words = set(content.lower().split())
            for kw in keywords:
                # Tiêu đề
                if kw in title:
                    score += 10
                # Danh mục
                if kw in category:
                    score += 5
                # Nội dung: khớp chính xác
                if kw in content_words:
                    score += 1
                # Nội dung: tiền tố
                if any(word.startswith(kw) and word != kw for word in content_words):
                    score += 0.5
            ranked_docs.append((doc_id, doc_info, score))
        # Sắp xếp giảm dần theo điểm
        ranked_docs.sort(key=lambda x: x[2], reverse=True)
        # Trả về [(doc_id, doc_info)]
        return [(doc_id, doc_info) for doc_id, doc_info, _ in ranked_docs]

    def search_documents_ranked(self, query):
        """Trả về các tài liệu liên quan, xếp hạng theo số lượng từ khóa khớp (logic OR, không ảnh hưởng hàm cũ)"""
        keywords = self._extract_keywords(query)
        if not keywords:
            return []
        doc_match_count = {}
        for keyword in keywords:
            docs = self.search_index._search_partial(keyword)
            for doc_id in docs:
                doc_match_count[doc_id] = doc_match_count.get(doc_id, 0) + 1
        ranked = sorted(doc_match_count.items(), key=lambda x: x[1], reverse=True)
        return [(doc_id, self.documents[doc_id]) for doc_id, _ in ranked if doc_id in self.documents]

    def get_all_categories(self):
        categories = set()
        for doc_info in self.documents.values():
            categories.add(doc_info['category'])
        return sorted(list(categories))
    
    def get_documents_by_category(self, category):
        if not category:
            return list(self.documents.items())
        
        return [(doc_id, doc_info) for doc_id, doc_info in self.documents.items() 
                if doc_info['category'] == category]
    
    def delete_document(self, doc_id):
        if doc_id not in self.documents:
            return False, "Không tìm thấy tài liệu"
        
        try:
            # Xóa tệp và cập nhật chỉ mục
            file_path = self.documents[doc_id]['path']
            if os.path.exists(file_path):
                os.remove(file_path)
            
            self.search_index.delete_document(doc_id)
            del self.documents[doc_id]
            self.save_index()
            
            return True, "Xóa tài liệu thành công"
        except Exception as e:
            return False, f"Lỗi khi xóa tài liệu: {e}"