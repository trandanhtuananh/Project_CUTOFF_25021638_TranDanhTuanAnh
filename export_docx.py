import os
import csv
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def create_report_docx():
    csv_file = 'experiment_results.csv'
    if not os.path.exists(csv_file):
        print("CSV file does not exist.")
        return

    # Read data using standard csv module
    data_by_n = {}
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for r in reader:
            N = int(r['N'])
            if N not in data_by_n:
                data_by_n[N] = []
            data_by_n[N].append({
                'cutoff': int(r['Cutoff']),
                'mean': float(r['Mean_Time_ms']),
                'std': float(r['StdDev_ms']),
                'min': float(r['Min_Time_ms']),
                'max': float(r['Max_Time_ms']),
                'speedup': float(r['Speedup_Percent'])
            })

    doc = Document()

    # Margin settings
    for section in doc.sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)

    # Styles
    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Times New Roman'
    normal_style.font.size = Pt(11.5)
    normal_style.font.color.rgb = RGBColor(0x22, 0x22, 0x22)

    # Title
    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_title = title.add_run("BÁO CÁO THỰC NGHIỆM KHOA HỌC\nXÁC ĐỊNH NGƯỠNG CUTOFF TỐI ƯU CHO THUẬT TOÁN MERGESORT")
    run_title.font.name = 'Times New Roman'
    run_title.font.size = Pt(18)
    run_title.bold = True
    run_title.font.color.rgb = RGBColor(0x1a, 0x36, 0x5d)

    subtitle = doc.add_paragraph()
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_sub = subtitle.add_run("Học phần: Cấu trúc Dữ liệu & Giải thuật | Phân tích Hiệu năng Thuật toán Thực nghiệm")
    run_sub.font.size = Pt(12)
    run_sub.italic = True
    run_sub.font.color.rgb = RGBColor(0x4a, 0x55, 0x68)

    doc.add_paragraph()

    # 1. Mục tiêu & Cơ sở lý thuyết
    doc.add_heading("1. Mục tiêu bài toán và Cơ sở lý thuyết", level=1)
    
    p1 = doc.add_paragraph()
    p1.add_run("1.1. Mục tiêu nghiên cứu:\n").bold = True
    p1.add_run(
        "Thuật toán Mergesort (sắp xếp trộn) là thuật toán sắp xếp dựa trên mô hình chia để trị (Divide and Conquer) "
        "đạt độ phức tạp tiệm cận tối ưu O(N log N) trong mọi trường hợp. Tuy nhiên, trong môi trường phần cứng máy tính hiện đại, "
        "chi phí đệ quy ở các tầng lá (khi mảng con có kích thước nhỏ k ≤ 15) thường mang lại overhead rất lớn do việc tạo/hủy stack frame "
        "và chi phí sao chép mảng phụ (auxiliary array). Mục tiêu của đề tài là khảo sát thực nghiệm để tìm ra giá trị ngưỡng chuyển đổi CUTOFF "
        "từ Mergesort sang Insertion Sort tối ưu nhất trên kiến trúc máy tính thực tế."
    )

    p2 = doc.add_paragraph()
    p2.add_run("1.2. Phân tích chi phí bộ nhớ đệm và vi kiến trúc CPU:\n").bold = True
    p2.add_run(
        "• Mergesort chuẩn và chi phí truy cập mảng: Theo lý thuyết của Sedgewick, Mergesort cần trung bình ~6N lg N lần truy cập mảng. "
        "Khi kích thước mảng con xuống mức rất nhỏ (k = 2, 3, 4), Mergesort vẫn phải cấp phát các lời gọi đệ quy, tính mid, chia đôi và gọi hàm merge(). "
        "Trong hàm merge(), việc lặp sao chép sang mảng phụ aux[] rồi đọc ngược lại a[] làm tăng đáng kể lưu lượng băng thông bộ nhớ.\n"
        "• Insertion Sort và tính địa phương bộ nhớ đệm (Cache Locality): Dù Insertion Sort có độ phức tạp thời gian O(N²), "
        "nhưng đối với mảng con kích thước nhỏ (k < 15), số phép toán so sánh và hoán vị trung bình chỉ xấp xỉ k(k-1)/4 (ví dụ với k=8 chỉ mất ~14 phép tính). "
        "Đặc biệt, Insertion Sort sắp xếp tại chỗ (in-place), toàn bộ dữ liệu nằm trọn vẹn trong L1 Data Cache (32KB-48KB của CPU), "
        "tỷ lệ Cache Hit đạt gần 100%, không phát sinh chi phí stack frame, và mã máy được thực thi tuần tự trong bộ xử lý pipeline mà không bị branch misprediction.\n"
        "• Lịch sử giá trị CUTOFF: Giáo sư Robert Sedgewick từng đề xuất ngưỡng CUTOFF = 7 trong các ấn bản kinh điển. Trong các giáo trình hiện đại, "
        "ngưỡng khuyến nghị thường được nâng lên mức 10 do kích thước bộ nhớ đệm L1/L2 của các CPU hiện nay đã lớn hơn trước rất nhiều."
    )

    # 2. Cấu hình & Thiết kế thí nghiệm
    doc.add_heading("2. Cấu hình hệ thống và Phương pháp thiết kế thí nghiệm", level=1)

    p3 = doc.add_paragraph()
    p3.add_run("2.1. Cấu hình phần cứng và môi trường thực thi:\n").bold = True
    p3.add_run(
        "• Hệ điều hành (OS): Microsoft Windows 11 Home 64-bit (Build 10.0.26200)\n"
        "• Bộ vi xử lý (CPU): 12th Gen Intel(R) Core(TM) i7-1255U (10 nhân: 2 P-Cores xung nhịp lên đến 4.70 GHz, 8 E-Cores; 12 luồng xử lý)\n"
        "• Bộ nhớ RAM: 16.0 GB DDR4/DDR5\n"
        "• Môi trường Java: Java SE Runtime Environment (build 25.0.2+10-LTS-69), Java HotSpot(TM) 64-Bit Server VM\n"
        "• Tham số JVM Heap: -Xms4g -Xmx4g (cố định kích thước heap 4GB để triệt tiêu chi phí cấp phát mở rộng heap)"
    )

    p4 = doc.add_paragraph()
    p4.add_run("2.2. Phương pháp thiết kế thí nghiệm và kiểm soát sai số (Statistical Methodology):\n").bold = True
    p4.add_run(
        "Theo đúng chuẩn phân tích thực nghiệm trong giáo trình Cấu trúc dữ liệu & Giải thuật (Mục 1.3 Algorithm Analysis):\n"
        "1. Khử nhiễu JIT Compiler (JVM Warm-up): Máy ảo HotSpot có cơ chế biên dịch động JIT C1/C2 (Tiered Compilation). "
        "Trước khi đo, chương trình thực hiện warm-up 5 lần chạy trên mảng 200,000 phần tử với các mức cutoff khác nhau để đảm bảo toàn bộ mã bytecode "
        "của các phương thức merge, sort, insertionSort, less, exch đều đã được biên dịch thành mã máy tối ưu.\n"
        "2. Đảm bảo tính tái lập (Deterministic Benchmark): Sử dụng cố định hạt giống new Random(42) để sinh mảng dữ liệu gốc Integer[]. "
        "Mỗi lượt thử nghiệm đều clone độc lập từ mảng gốc này.\n"
        "3. Số lần lặp T = 20 trials và đo chính xác: Tại mỗi giá trị CUTOFF từ 1 đến 32, thực hiện 20 lần lặp độc lập. "
        "Chỉ đo đúng thời gian thực thi của Merge.sort bằng System.nanoTime(). Sau đó tính toán:\n"
        "   - Giá trị trung bình mẫu (Sample Mean):  x̄ = (1 / T) * Σ xᵢ\n"
        "   - Độ lệch chuẩn mẫu (Sample StdDev):  s = sqrt( (1 / (T - 1)) * Σ (xᵢ - x̄)² )\n"
        "   - % Cải thiện tốc độ so với Cutoff = 1:  Speedup = ((x̄_c1 - x̄_c) / x̄_c1) * 100%"
    )

    # 3. Kết quả thực nghiệm
    doc.add_heading("3. Bảng số liệu thống kê kết quả thực nghiệm", level=1)

    for N in sorted(data_by_n.keys()):
        p_data = data_by_n[N]
        doc.add_paragraph().add_run(f"Bảng dữ liệu thực nghiệm với kích thước mảng N = {N:,} phần tử (T = 20 trials):").bold = True

        table = doc.add_table(rows=1, cols=6)
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        headers = ["Cutoff", "Mean (ms)", "StdDev (ms)", "Min (ms)", "Max (ms)", "Speedup (%)"]
        hdr_cells = table.rows[0].cells
        for i, h in enumerate(headers):
            hdr_cells[i].text = h
            hdr_cells[i].paragraphs[0].runs[0].font.bold = True
            hdr_cells[i].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
            set_cell_background(hdr_cells[i], "1a365d")
            hdr_cells[i].paragraphs[0].runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

        opt_d = min(p_data, key=lambda d: d['mean'])

        for d in p_data:
            row_cells = table.add_row().cells
            row_cells[0].text = str(d['cutoff'])
            row_cells[1].text = f"{d['mean']:.3f}"
            row_cells[2].text = f"{d['std']:.3f}"
            row_cells[3].text = f"{d['min']:.3f}"
            row_cells[4].text = f"{d['max']:.3f}"
            row_cells[5].text = f"{d['speedup']:+.2f}%"

            for i in range(6):
                row_cells[i].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT if i > 0 else WD_ALIGN_PARAGRAPH.CENTER

            # Highlight Cutoff 7, 10
            if d['cutoff'] in [7, 10]:
                for i in range(6):
                    set_cell_background(row_cells[i], "EBF8FF")
            # Highlight Optimal
            if d['cutoff'] == opt_d['cutoff']:
                for i in range(6):
                    set_cell_background(row_cells[i], "FEFCBF")
                    row_cells[i].paragraphs[0].runs[0].font.bold = True

        doc.add_paragraph()

    # 4. Biểu đồ trực quan
    doc.add_heading("4. Biểu đồ trực quan hóa dữ liệu thực nghiệm", level=1)

    if os.path.exists("cutoff_vs_time.png"):
        doc.add_paragraph().add_run("Hình 1: Đồ thị thời gian thực thi trung bình theo giá trị CUTOFF (N = 500,000 và N = 1,000,000):").bold = True
        doc.add_picture("cutoff_vs_time.png", width=Inches(6.5))

    if os.path.exists("cutoff_with_errorbar.png"):
        doc.add_paragraph().add_run("Hình 2: Đồ thị thời gian kèm thanh sai số độ lệch chuẩn mẫu (Error Bars ±1 StdDev):").bold = True
        doc.add_picture("cutoff_with_errorbar.png", width=Inches(6.5))

    if os.path.exists("speedup_comparison.png"):
        doc.add_paragraph().add_run("Hình 3: Tỷ lệ phần trăm cải thiện tốc độ so với Mergesort thuần túy (CUTOFF = 1):").bold = True
        doc.add_picture("speedup_comparison.png", width=Inches(6.0))

    # 5. Phân tích & Kết luận
    doc.add_heading("5. Phân tích kết quả và Kết luận học thuật", level=1)

    d500 = data_by_n[500000]
    opt_500 = min(d500, key=lambda d: d['mean'])
    c7_500 = next(d for d in d500 if d['cutoff'] == 7)
    c10_500 = next(d for d in d500 if d['cutoff'] == 10)

    p_disc = doc.add_paragraph()
    p_disc.add_run("5.1. Phân tích hình thái đường cong (Đặc tính hình chữ U có đáy thoải - Flat U-curve):\n").bold = True
    p_disc.add_run(
        "Kết quả thực nghiệm trên máy tính thể hiện rõ nét hình thái chữ U có vùng đáy rất thoải:\n"
        "1. Giai đoạn tăng tốc mạnh (CUTOFF từ 1 đến 6): Ở CUTOFF = 1 (Mergesort thuần túy không dùng Insertion Sort), "
        "chi phí cuộc gọi đệ quy phân mảnh tới tận từng phần tử đơn lẻ làm tiêu hao nhiều chu kỳ CPU nhất (458.50 ms ở N=500k và 1099.51 ms ở N=1M). "
        "Chỉ cần chuyển đổi ở ngưỡng CUTOFF nhỏ (CUTOFF = 5-6), thời gian chạy lập tức giảm rõ rệt.\n"
        f"2. Vùng đáy tối ưu thoải (Flat Optimal Basin, CUTOFF ∈ [6..16]): Đây là vùng ngọt (sweet spot) của thuật toán. "
        f"Tại N = 500,000, điểm tối ưu ghi nhận tại CUTOFF = {opt_500['cutoff']} với thời gian trung bình đạt {opt_500['mean']:.3f} ms (cải thiện {opt_500['speedup']:+.2f}%). "
        f"Các mốc CUTOFF = 7 ({c7_500['mean']:.3f} ms, +{c7_500['speedup']:.2f}%) và CUTOFF = 10 ({c10_500['mean']:.3f} ms, +{c10_500['speedup']:.2f}%) "
        "đều nằm trọn trong vùng đáy tối ưu này với độ chênh lệch hiệu năng rất nhỏ (dưới 1-2%, nằm gọn trong khoảng sai số độ lệch chuẩn mẫu).\n"
        "3. Giai đoạn suy giảm hiệu năng (CUTOFF > 20): Khi CUTOFF tăng vượt quá 20 và tiến tới 32, độ phức tạp O(k²) của Insertion Sort "
        "bắt đầu bộc lộ nhược điểm, số phép toán so sánh và hoán vị tăng nhanh theo hàm bậc hai, lấn át hoàn toàn lợi ích của bộ nhớ đệm CPU, "
        "khiến thời gian thực thi tăng vọt (ở CUTOFF = 32, thời gian chậm hơn tới -15.24% ở N=500k và -12.75% ở N=1M so với CUTOFF=1)."
    )

    p_conc = doc.add_paragraph()
    p_conc.add_run("5.2. So sánh với giáo trình và Khuyến nghị kỹ thuật:\n").bold = True
    p_conc.add_run(
        "• Khẳng định tính đúng đắn của mốc CUTOFF = 7 (Sedgewick classic) và CUTOFF = 10 (Modern): "
        "Cả hai ngưỡng khuyến nghị trong giáo trình đều là những lựa chọn vô cùng an toàn và hiệu quả, mang lại mức cải thiện hiệu năng thực tế từ 4% đến 6% "
        "mà không bao giờ bị rơi vào vùng suy giảm hiệu năng do kích thước Insertion Sort quá lớn.\n"
        "• Khuyến nghị áp dụng thực tế: Trên các bộ xử lý x86-64 hiện đại thế hệ 12 trở lên với dung lượng L1 Data Cache lớn (48 KB), "
        "ngưỡng CUTOFF có thể chọn linh hoạt trong dải từ 8 đến 14 để đạt được hiệu năng tối đa."
    )

    # 6. Danh mục tệp bàn giao
    doc.add_heading("6. Danh mục tệp bàn giao của Project", level=1)
    p_deliv = doc.add_paragraph()
    p_deliv.add_run("Toàn bộ mã nguồn, dữ liệu thực nghiệm và tài liệu báo cáo được lưu trữ đồng bộ trong thư mục project:\n")
    deliverables = [
        "1. Merge.java: Mã nguồn thuật toán chuẩn nguyên bản 100%.",
        "2. DatasetGenerator.java: Chương trình sinh các tập dữ liệu mẫu.",
        "3. CutoffExperiment.java: Chương trình đo lường thực nghiệm khoa học tự động.",
        "4. plot_charts.py: Script tạo 3 đồ thị trực quan độ phân giải cao.",
        "5. export_docx.py: Script xuất báo cáo học thuật định dạng Microsoft Word.",
        "6. experiment_results.csv: File dữ liệu thô toàn bộ kết quả đo lường thực tế.",
        "7. cutoff_vs_time.png, cutoff_with_errorbar.png, speedup_comparison.png: Các hình ảnh biểu đồ học thuật.",
        "8. Bao_Cao_Thi_Nghiem.md: Báo cáo khoa học định dạng Markdown chuẩn.",
        "9. Bao_Cao_Thi_Nghiem_CUTOFF_Mergesort.docx: Báo cáo khoa học định dạng Microsoft Word hoàn chỉnh.",
        "10. Log_chat_AI.pdf: Bản ghi log thảo luận và thiết kế thực nghiệm cùng AI.",
        "11. Thư mục datasets/: Chứa các tệp dữ liệu mẫu random_10k.txt, partially_sorted_10k.txt, reverse_10k.txt."
    ]
    for item in deliverables:
        p_item = doc.add_paragraph()
        p_item.paragraph_format.left_indent = Inches(0.25)
        p_item.add_run(item)

    out_file = "Bao_Cao_Thi_Nghiem_CUTOFF_Mergesort.docx"
    doc.save(out_file)
    print(f"Report exported to {out_file} successfully.")

if __name__ == '__main__':
    create_report_docx()
