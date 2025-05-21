# Hướng dẫn cài đặt

## Yêu cầu hệ thống

- Python 3.7 hoặc cao hơn
- Đủ quyền cài đặt packages trên hệ thống

## Thư viện bắt buộc

- **PyQt5**: Thư viện giao diện đồ họa

## Thư viện tùy chọn

- **python-docx**: Thư viện đọc file .docx (Word)
- **PyPDF2**: Thư viện đọc file PDF

## Cách cài đặt

### Cách 1: Cài đặt bằng requirements.txt

```bash
pip install -r requirements.txt
```

### Cách 2: Cài đặt từng thư viện

Cài đặt thư viện bắt buộc:

```bash
pip install PyQt5==5.15.4
```

Cài đặt các thư viện tùy chọn (để hỗ trợ đọc file docx và pdf):

```bash
pip install python-docx==0.8.11
pip install PyPDF2==2.11.1
```

## Chạy chương trình

Sau khi cài đặt xong, bạn có thể chạy chương trình bằng lệnh:

```bash
python avl_search/main.py
```

## Lưu ý

- Nếu không cài đặt các thư viện tùy chọn, chương trình vẫn hoạt động nhưng sẽ không đọc được các file docx và pdf.
- Đôi khi có thể cần sử dụng `pip3` thay vì `pip` tùy thuộc vào cách Python được cài đặt trên hệ thống của bạn.
