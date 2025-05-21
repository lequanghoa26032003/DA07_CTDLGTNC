import os
import sys
from PyQt5.QtWidgets import (
    QMainWindow, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QComboBox, QTableWidget,
    QTableWidgetItem, QHeaderView, QFileDialog, QGroupBox,
    QFormLayout, QFrame, QMessageBox, QTreeWidget, QTreeWidgetItem, QCompleter, QListWidget,
    QListWidgetItem, QProgressDialog
)
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt
from document_manager import DocumentManager
from utils import SEARCH_TIPS

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Thêm dòng này để đọc CSS từ file
        self.load_stylesheet("styles/main.css")
        
        self.setWindowIcon(QIcon("icons/library_icon.png"))
        
        # Đặt tiêu đề ứng dụng đẹp hơn
        self.setWindowTitle("Thư Viện Số Mini")
        
        # Thêm thanh trạng thái
        self.statusBar().showMessage("Sẵn sàng")
        
        self.doc_manager = DocumentManager()
        self.setWindowTitle("Quản Lý Tài Liệu Học Tập")
        self.setGeometry(100, 100, 1200, 800)
        self.init_ui()
    
    def init_ui(self):
        # Widget chính
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        
        # Các tab
        self.tabs = QTabWidget()
        self.tabs.addTab(self._create_search_tab(), "Tìm kiếm")
        self.tabs.addTab(self._create_add_tab(), "Thêm tài liệu")
        self.tabs.addTab(self._create_categories_tab(), "Danh mục")
        
        main_layout.addWidget(self.tabs)
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
        # Khởi tạo
        self.refresh_ui()
        self.setup_autocomplete()
    
    def _create_search_tab(self):
        """Tạo tab tìm kiếm"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # 1. THÊM HEADER ĐẸP
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        search_icon = QLabel()
        search_icon.setPixmap(self.get_icon("icons/search.png").scaled(32, 32, Qt.KeepAspectRatio))
        search_title = QLabel("TRA CỨU TÀI LIỆU")
        search_title.setStyleSheet("font-size: 18px; font-weight: bold;")
        header_layout.addWidget(search_icon)
        header_layout.addWidget(search_title)
        header_layout.addStretch()
        layout.addWidget(header_widget)
        
        # 2. CẢI TIẾN THANH TÌM KIẾM
        search_frame = QFrame()
        search_frame.setObjectName("search-box")  # Để CSS có thể targeting
        search_layout = QHBoxLayout(search_frame)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Nhập từ khóa tìm kiếm...")
        self.search_input.returnPressed.connect(self.search_documents)
        
        search_button = QPushButton("Tìm kiếm")
        search_button.setObjectName("search-button")
        search_button.clicked.connect(self.search_documents)
        
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(search_button)
        
        layout.addWidget(search_frame)
        
        # KHO CHỖ NÀY KHÔNG SỬA - GIỮ NGUYÊN HƯỚNG DẪN
        search_tips = QLabel(SEARCH_TIPS)
        search_tips.setWordWrap(True)
        layout.addWidget(search_tips)
        
        # Bảng kết quả
        self.results_table = QTableWidget(0, 5)
        self.results_table.setHorizontalHeaderLabels(["Tiêu đề", "Danh mục", "Ngày thêm", "Tóm tắt", "Thao tác"])
        self.results_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.results_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.results_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.results_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        
        layout.addWidget(self.results_table)
        tab.setLayout(layout)
        return tab
    
    def _create_add_tab(self):
        """Tạo tab thêm tài liệu"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # THÊM HEADER
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        add_icon = QLabel()
        add_icon.setPixmap(QPixmap("icons/add.png").scaled(32, 32, Qt.KeepAspectRatio))
        add_title = QLabel("THÊM TÀI LIỆU MỚI")
        add_title.setStyleSheet("font-size: 18px; font-weight: bold;")
        header_layout.addWidget(add_icon)
        header_layout.addWidget(add_title)
        header_layout.addStretch()
        layout.addWidget(header_widget)
        
        # NHÓM THÔNG TIN CƠ BẢN
        info_group = QGroupBox("Thông tin tài liệu")
        info_layout = QFormLayout()
        
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Nhập tiêu đề...")
        
        self.cat_input = QComboBox()
        self.cat_input.setEditable(True)
        self.cat_input.setPlaceholderText("Chọn hoặc tạo mới...")
        self.cat_input.addItems(self.doc_manager.get_all_categories())
        
        self.keywords_input = QLineEdit()
        self.keywords_input.setPlaceholderText("Nhập từ khóa cách nhau bởi dấu phẩy...")
        
        info_layout.addRow(QLabel("Tiêu đề:"), self.title_input)
        info_layout.addRow(QLabel("Danh mục:"), self.cat_input)
        info_layout.addRow(QLabel("Từ khóa:"), self.keywords_input)
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # NHÓM FILE
        file_group = QGroupBox("Tệp tài liệu")
        file_layout = QVBoxLayout()

        file_controls = QHBoxLayout()
        self.file_path_input = QLineEdit()
        self.file_path_input.setReadOnly(True)
        self.file_path_input.setPlaceholderText("Chọn tệp để tải lên...")

        self.file_browse_button = QPushButton("Duyệt...")
        self.file_browse_button.clicked.connect(self.browse_file)

        file_controls.addWidget(self.file_path_input)
        file_controls.addWidget(self.file_browse_button)

        self.files_list = QListWidget()
        self.files_list.setMaximumHeight(150)
        self.files_list.setAlternatingRowColors(True)

        file_layout.addLayout(file_controls)
        file_layout.addWidget(QLabel("Các file đã chọn:"))
        file_layout.addWidget(self.files_list)

        file_group.setLayout(file_layout)
        layout.addWidget(file_group)
        
        # NÚT THÊM TÀI LIỆU - LÀM TO VÀ NỔI BẬT 
        add_button = QPushButton("Thêm tài liệu")
        add_button.setObjectName("add-button")
        add_button.setMinimumHeight(40)
        add_button.clicked.connect(self.add_document)
        
        layout.addWidget(add_button)
        layout.addStretch(1)
        
        tab.setLayout(layout)
        return tab
    
    def _create_categories_tab(self):
        """Tạo tab danh mục"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        self.categories_tree = QTreeWidget()
        self.categories_tree.setHeaderLabels(["Danh mục"])
        self.categories_tree.itemClicked.connect(self.category_clicked)
        
        layout.addWidget(self.categories_tree)
        tab.setLayout(layout)
        return tab
    
    def refresh_ui(self):
        """Làm mới toàn bộ UI sau thay đổi"""
        self.load_categories()
        self.refresh_categories_tree()
        self.search_documents()
    
    def browse_file(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "Chọn tệp", "", "Tất cả các tệp (*)"
        )
        if files:
            self.selected_files = files
            self.file_path_input.setText(f"{len(files)} file đã được chọn")
            
            # Hiển thị trong list widget
            self.files_list.clear()
            for file_path in files:
                file_name = os.path.basename(file_path)
                item = QListWidgetItem(file_name)
                item.setToolTip(file_path)
                self.files_list.addItem(item)
    
    def add_document(self):
        # Kiểm tra nếu không có file nào được chọn
        if not hasattr(self, 'selected_files') or not self.selected_files:
            QMessageBox.warning(self, "Lỗi", "Vui lòng chọn ít nhất một tệp")
            return
        
        category = self.cat_input.currentText()
        keywords = self.keywords_input.text()
        
        if not category:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập danh mục")
            return
        
        # Xử lý từng file
        success_count = 0
        error_files = []
        
        progress = QProgressDialog("Đang thêm tài liệu...", "Hủy", 0, len(self.selected_files), self)
        progress.setWindowModality(Qt.WindowModal)
        
        for i, file_path in enumerate(self.selected_files):
            progress.setValue(i)
            if progress.wasCanceled():
                break
                
            # Ưu tiên tiêu đề thủ công, sau đó tự động trích xuất từ file
            if self.title_input.text():
                # Nếu có tiêu đề thủ công và nhiều file, thêm số thứ tự
                if len(self.selected_files) > 1:
                    title = f"{self.title_input.text()} ({i+1})"
                else:
                    title = self.title_input.text()
            else:
                # Tự động trích xuất tiêu đề từ nội dung file
                title = self.extract_title_from_file(file_path)
                
            # Tự động trích xuất từ khóa từ file nếu không nhập
            file_keywords = keywords
            if not keywords:
                try:
                    # Thử đọc từ khóa từ file (nếu có dòng "TỪ KHÓA:")
                    file_keywords = self.extract_keywords_from_file(file_path) or ""
                except:
                    file_keywords = ""
            
            success, result = self.doc_manager.add_document(file_path, title, category, file_keywords)
            
            if success:
                success_count += 1
            else:
                error_files.append(os.path.basename(file_path))
        
        progress.setValue(len(self.selected_files))
        
        # Hiển thị thông báo kết quả
        if success_count > 0:
            QMessageBox.information(
                self, 
                "Thành công", 
                f"Đã thêm {success_count}/{len(self.selected_files)} tài liệu thành công"
            )
            self.clear_add_form()
            self.refresh_ui()
        
        if error_files:
            QMessageBox.warning(
                self, 
                "Lỗi", 
                f"Không thể thêm {len(error_files)} tệp:\n{', '.join(error_files)}"
            )
    
    def clear_add_form(self):
        self.file_path_input.clear()
        self.title_input.clear()
        self.keywords_input.clear()
        self.files_list.clear()
        if hasattr(self, 'selected_files'):
            self.selected_files = []
    
    def load_categories(self):
        categories = self.doc_manager.get_all_categories()
        current_text = self.cat_input.currentText()
        
        self.cat_input.clear()
        self.cat_input.addItems(categories)
        
        if current_text:
            index = self.cat_input.findText(current_text)
            if index >= 0:
                self.cat_input.setCurrentIndex(index)
    
    def refresh_categories_tree(self):
        self.categories_tree.clear()
        
        # Thêm mục "Tất cả tài liệu"
        all_docs_item = QTreeWidgetItem(self.categories_tree, ["Tất cả tài liệu"])
        
        # Lấy danh mục và tài liệu
        categories = self.doc_manager.get_all_categories()
        for category in categories:
            category_item = QTreeWidgetItem(self.categories_tree, [category])
            docs = self.doc_manager.get_documents_by_category(category)
            for doc_id, doc_info in docs:
                doc_item = QTreeWidgetItem(category_item, [doc_info['title']])
                doc_item.setData(0, Qt.UserRole, doc_id)
        
        self.categories_tree.expandAll()
    
    def category_clicked(self, item, column):
        if item.parent() is None:
            # Lấy danh mục và hiển thị tài liệu
            category = "" if item.text(0) == "Tất cả tài liệu" else item.text(0)
            docs = self.doc_manager.get_documents_by_category(category)
            self.display_documents(docs)
            self.tabs.setCurrentIndex(0)  # Chuyển đến tab tìm kiếm
    
    def search_documents(self):
        query = self.search_input.text()
        results = self.doc_manager.search_documents(query)
        self.display_documents(results)
    
    def display_documents(self, documents):
        # Xóa tất cả dòng cũ trước khi hiển thị kết quả mới
        self.results_table.setRowCount(0)
        
        # Thêm dòng này để cập nhật trạng thái
        self.statusBar().showMessage(f"Tìm thấy {len(documents)} kết quả")
        
        # Giữ code hiện tại nhưng thêm class styling
        self.results_table.setAlternatingRowColors(True)
        self.results_table.setObjectName("results-table")
        
        for row, (doc_id, doc_info) in enumerate(documents):
            self.results_table.insertRow(row)
            
            # Tiêu đề, danh mục, ngày thêm
            title_item = QTableWidgetItem(doc_info['title'])
            title_item.setData(Qt.UserRole, doc_id)
            self.results_table.setItem(row, 0, title_item)
            self.results_table.setItem(row, 1, QTableWidgetItem(doc_info['category']))
            self.results_table.setItem(row, 2, QTableWidgetItem(doc_info['added_date']))
            
            # Tóm tắt đơn giản hóa
            self.results_table.setItem(row, 3, QTableWidgetItem(self.generate_snippet(doc_id)))
            
            # Thêm nút thao tác
            self._add_action_buttons(row, 4, doc_id)
    
    def _add_action_buttons(self, row, col, doc_id):
        """Tạo nút Mở và Xóa cho tài liệu"""
        actions_widget = QWidget()
        actions_layout = QHBoxLayout()
        actions_layout.setContentsMargins(0, 0, 0, 0)
        
        # Nút mở và xóa
        open_button = QPushButton("Mở")
        delete_button = QPushButton("Xóa")
        
        open_button.clicked.connect(lambda checked, id=doc_id: self.open_document(id))
        delete_button.clicked.connect(lambda checked, id=doc_id: self.delete_document(id))
        
        actions_layout.addWidget(open_button)
        actions_layout.addWidget(delete_button)
        actions_widget.setLayout(actions_layout)
        
        self.results_table.setCellWidget(row, col, actions_widget)
    
    def generate_snippet(self, doc_id):
        """Tạo đoạn tóm tắt đơn giản"""
        doc_info = self.doc_manager.documents[doc_id]
        try:
            with open(doc_info['path'], 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(200)  # Chỉ đọc 200 ký tự đầu
            return content + "..." if len(content) > 200 else content
        except:
            return "Không thể tạo tóm tắt"
    
    def open_document(self, doc_id):
        doc_info = self.doc_manager.documents.get(doc_id)
        if not doc_info or not os.path.exists(doc_info['path']):
            QMessageBox.warning(self, "Lỗi", "Không tìm thấy tài liệu")
            return
        
        try:
            if sys.platform == 'win32':
                os.startfile(doc_info['path'])
            elif sys.platform == 'darwin':  # macOS
                import subprocess
                subprocess.call(('open', doc_info['path']))
            else:  # Linux
                import subprocess
                subprocess.call(('xdg-open', doc_info['path']))
        except Exception as e:
            QMessageBox.warning(self, "Lỗi", f"Không thể mở tệp: {e}")
    
    def delete_document(self, doc_id):
        reply = QMessageBox.question(self, "Xác nhận", 
                                    "Bạn có chắc chắn muốn xóa tài liệu này?",
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            success, message = self.doc_manager.delete_document(doc_id)
            if success:
                QMessageBox.information(self, "Thành công", message)
                self.refresh_ui()
            else:
                QMessageBox.warning(self, "Lỗi", message)

    def setup_autocomplete(self):
        all_keywords = set()
        for doc_info in self.doc_manager.documents.values():
            if isinstance(doc_info['keywords'], list):
                all_keywords.update(doc_info['keywords'])
        
        completer = QCompleter(list(all_keywords))
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.search_input.setCompleter(completer)

    def load_stylesheet(self, stylesheet_path):
        try:
            import os
            base_dir = os.path.dirname(os.path.abspath(__file__))
            css_path = os.path.join(base_dir, stylesheet_path)
            
            with open(css_path, "r", encoding="utf-8") as f:  # Thêm encoding="utf-8"
                self.setStyleSheet(f.read())
        except Exception as e:
            print(f"Không thể tải stylesheet: {e}")
    
    def get_icon(self, icon_path):
        """Tải icon từ đường dẫn, trả về placeholder nếu không tìm thấy"""
        import os
        base_dir = os.path.dirname(os.path.abspath(__file__))
        icon_full_path = os.path.join(base_dir, icon_path)
        
        if os.path.exists(icon_full_path):
            return QPixmap(icon_full_path)
        else:
            print(f"Icon không tồn tại: {icon_path}")
            # Trả về pixmap trống thay vì null pixmap
            placeholder = QPixmap(32, 32)
            placeholder.fill(Qt.lightGray)  # Tạo màu nền để nhìn thấy
            return placeholder
    
    def extract_title_from_file(self, file_path):
        """Trích xuất tiêu đề từ nội dung file nếu có định dạng TIÊU ĐỀ:"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(2000)  # Chỉ đọc 2000 ký tự đầu tiên
                
                # Tìm kiếm cú pháp "TIÊU ĐỀ:" hoặc "TIÊU ĐỀ:"
                title_match = None
                for pattern in ["TIÊU ĐỀ:", "TIỀU ĐỀ:", "Tiêu đề:", "Title:"]:
                    if pattern in content:
                        idx = content.find(pattern) + len(pattern)
                        end_idx = content.find('\n', idx)
                        if end_idx > idx:
                            title = content[idx:end_idx].strip()
                            if title:
                                title_match = title
                                break
                
                if title_match:
                    return title_match
                
                # Nếu không tìm thấy, sử dụng tên file
                return os.path.splitext(os.path.basename(file_path))[0]
        except:
            # Nếu có lỗi, trả về tên file
            return os.path.splitext(os.path.basename(file_path))[0]
    
    def extract_keywords_from_file(self, file_path):
        """Trích xuất từ khóa từ nội dung file nếu có định dạng TỪ KHÓA:"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(2000)  # Chỉ đọc 2000 ký tự đầu tiên
                
                # Tìm kiếm cú pháp "TỪ KHÓA:" hoặc các biến thể khác
                keywords = None
                for pattern in ["TỪ KHÓA:", "Từ khóa:", "Keywords:"]:
                    if pattern in content:
                        idx = content.find(pattern) + len(pattern)
                        end_idx = content.find('\n', idx)
                        if end_idx > idx:
                            kw = content[idx:end_idx].strip()
                            if kw:
                                keywords = kw
                                break
            
            return keywords
        except:
            return None