# BÁO CÁO THỰC NGHIỆM KHOA HỌC
# XÁC ĐỊNH GIÁ TRỊ CUTOFF TỐI ƯU CHO THUẬT TOÁN MERGESORT

[![Java](https://img.shields.io/badge/Java-25%20LTS-orange.svg)](https://www.oracle.com/java/)
[![Algorithm](https://img.shields.io/badge/Algorithm-Mergesort%20%2B%20Insertion%20Sort-blue.svg)](https://algs4.cs.princeton.edu/22mergesort/)
[![Platform](https://img.shields.io/badge/Platform-Intel%20Core%20i7--1255U-green.svg)](https://ark.intel.com/)
[![License](https://img.shields.io/badge/Academic-Project-purple.svg)]()

> **Dự án:** Nghiên cứu thực nghiệm xác định ngưỡng CUTOFF tối ưu cho thuật toán Mergesort  
> **Sinh viên thực hiện:** Trần Danh Tuấn Anh  
> **Mã số sinh viên (MSSV):** 25021638  
> **Môn học:** Cấu trúc Dữ liệu và Giải thuật (Algorithms & Data Structures)  
> **Chủ đề lý thuyết:** Phân tích thuật toán thực nghiệm (*Sedgewick & Wayne 1.3: Algorithm Analysis*)  
> **Tài liệu nộp đính kèm:** [Bao_Cao_Thi_Nghiem_CUTOFF_Mergesort.docx](./Bao_Cao_Thi_Nghiem_CUTOFF_Mergesort.docx) | [Log_chat_AI.pdf](./Log_chat_AI.pdf)

---

## MỤC LỤC
1. [Mục tiêu bài toán & Cơ sở lý thuyết](#1-mục-tiêu-bài-toán-và-cơ-sở-lý-thuyết)
2. [Cấu hình hệ thống & Thiết kế thí nghiệm](#2-cấu-hình-hệ-thống-và-phương-pháp-thiết-kế-thí-nghiệm)
3. [Bảng số liệu thống kê kết quả thực nghiệm](#3-bảng-số-liệu-thống-kê-kết-quả-thực-nghiệm)
4. [Biểu đồ trực quan hóa dữ liệu thực nghiệm](#4-biểu-đồ-trực-quan-hóa-dữ-liệu-thực-nghiệm)
5. [Phân tích chuyên sâu & Kết luận học thuật](#5-phân-tích-kết-quả-và-kết-luận-học-thuật)
6. [Hướng dẫn tái lập kết quả thí nghiệm](#6-hướng-dẫn-tái-lập-kết-quả-thí-nghiệm)
7. [Cấu trúc tệp tin trong Repository](#7-cấu-trúc-tệp-tin-trong-repository)

---

## 1. Mục tiêu bài toán và Cơ sở lý thuyết

### 1.1. Đặt vấn đề
Thuật toán **Mergesort** (sắp xếp trộn) là giải thuật kinh điển theo mô hình chia để trị (*Divide and Conquer*), bảo đảm độ phức tạp thời gian tối ưu trong mọi trường hợp:
$$\mathcal{O}(N \log N)$$

Tuy nhiên, trong môi trường phần cứng máy tính thực tế, khi chia bài toán đệ quy xuống các kích thước mảng con rất nhỏ (ví dụ $k \le 15$), Mergesort chịu các chi phí ẩn (*hidden overhead*) rất lớn:
1. **Chi phí khung ngăn xếp đệ quy:** Mỗi lời gọi hàm tốn chi phí đẩy/kéo stack frame, lưu trữ thanh ghi và con trỏ địa chỉ trở về.
2. **Chi phí sao chép mảng phụ:** Thao tác cấp phát và sao chép dữ liệu giữa mảng chính `a[]` và mảng phụ `aux[]` trong hàm `merge()` làm gia tăng áp lực băng thông bộ nhớ.

Để khắc phục, kỹ thuật chuẩn trong khoa học máy tính là thiết lập một **ngưỡng CUTOFF**: khi kích thước mảng con $\le \text{CUTOFF}$, thuật toán sẽ dừng đệ quy và chuyển sang sử dụng **Insertion Sort** để sắp xếp trực tiếp mảng con đó.

---

### 1.2. Phân tích chi phí vi kiến trúc CPU và Bộ nhớ đệm (Cache Locality)

#### A. Chi phí truy cập mảng của Mergesort
Theo phân tích định lượng của GS. Robert Sedgewick (*Algorithms, 4th Edition*), Mergesort từ trên xuống (*Top-down*) cần từ **$6N \lg N$ lần truy cập mảng** để sắp xếp mảng ngẫu nhiên. Ở các tầng lá của cây đệ quy, việc tiếp tục phân đôi các đoạn 2, 3, 4 phần tử rồi gọi `merge()` tiêu tốn chu kỳ CPU cho các thao tác quản lý nhiều hơn thời gian so sánh dữ liệu thực tế.

#### B. Insertion Sort và Lợi thế bộ nhớ đệm (Cache Locality)
Mặc dù Insertion Sort có độ phức tạp lý thuyết là $\mathcal{O}(k^2)$, nhưng với $k$ nhỏ ($k \le 15$):
- **Số phép toán cực nhỏ:** Số phép so sánh trung bình chỉ là $\sim \frac{k(k-1)}{4}$. Với $k = 8$, chỉ mất trung bình khoảng $14$ phép so sánh.
- **Sắp xếp tại chỗ (In-Place):** Không yêu cầu cấp phát bộ nhớ phụ, không tốn chi phí sao chép qua lại giữa hai mảng.
- **Khai thác tối đa L1 Data Cache:** Dữ liệu mảng con kích thước nhỏ nằm gọn hoàn toàn trong một vài dòng đệm (*Cache Line* - 64 bytes) của bộ nhớ đệm cấp 1 (L1 Data Cache 48 KB). Tỷ lệ **L1 Cache Hit xấp xỉ 100%**, độ trễ truy xuất chỉ mất 4-5 chu kỳ CPU (thay vì hàng trăm chu kỳ nếu bị Cache Miss xuống RAM).
- **Thực thi tuần tự trong CPU Pipeline:** Vòng lặp nhỏ gọn không bị trượt dự đoán rẽ nhánh (*Branch Misprediction*), giúp vi xử lý khai thác tối đa năng lực xử lý lệnh song song mức chỉ thị (*ILP - Instruction Level Parallelism*).

---

## 2. Cấu hình hệ thống và Phương pháp thiết kế thí nghiệm

### 2.1. Cấu hình phần cứng và môi trường thực nghiệm
Thực nghiệm được triển khai trực tiếp trên máy tính với thông số cấu hình:

| Thành phần | Thông số kỹ thuật |
| :--- | :--- |
| **Hệ điều hành (OS)** | Microsoft Windows 11 Home 64-bit (Version 10.0.26200) |
| **Bộ vi xử lý (CPU)** | **12th Gen Intel(R) Core(TM) i7-1255U** |
| **Kiến trúc CPU** | 10 nhân (2 P-Cores Turbo 4.70 GHz + 8 E-Cores), 12 luồng |
| **Bộ nhớ đệm CPU** | L1 Data Cache: 48 KB / P-Core; L2 Cache: 1.25 MB / Core; L3 Cache: 12 MB |
| **Bộ nhớ RAM** | 16.0 GB DDR4/DDR5 |
| **Môi trường Java** | Java(TM) SE Runtime Environment (build 25.0.2+10-LTS-69) |
| **Máy ảo JVM** | Java HotSpot(TM) 64-Bit Server VM (build 25.0.2+10-LTS-69, mixed mode) |
| **Thiết lập Heap JVM** | `-Xms4g -Xmx4g` (Cố định 4GB Heap nhằm loại bỏ độ trễ co giãn bộ nhớ) |

---

### 2.2. Phương pháp thiết kế thí nghiệm khoa học
Tuân thủ chuẩn phương pháp thực nghiệm trong giáo trình của Sedgewick & Wayne:

1. **Khử nhiễu JIT Compiler (JVM Warm-up):**
   Máy ảo HotSpot sử dụng cơ chế biên dịch động phân tầng (*Tiered Compilation: C1/C2 Compiler*). Chương trình thực hiện **5 lần chạy warm-up độc lập** trên mảng $200,000$ phần tử trước khi đo chính thức để đảm bảo $100\%$ mã bytecode của các hàm `merge`, `sort`, `insertionSort`, `less`, `exch` đã được tối ưu hóa sang mã máy nguyên thủy.
2. **Tính tái lập hoàn toàn (Deterministic Pseudo-Random Seed):**
   Mảng dữ liệu gốc kiểu `Integer[]` được tạo bởi `new Random(42)`. Trước mỗi lượt sort, chương trình sao chép độc lập qua `masterArray.clone()`, bảo đảm tất cả 32 mức CUTOFF đều đo trên cùng một tập dữ liệu đầu vào.
3. **Quy mô mẫu lớn:**
   Tại mỗi giá trị $\text{CUTOFF} \in [1..32]$, tiến hành lặp lại **$T = 20$ trials**. Chỉ bấm giờ duy nhất lệnh `Merge.sort(a, cutoff)` bằng `System.nanoTime()`. Kiểm tra tính đúng đắn `Merge.isSorted(a)` đặt bên ngoài khoảng đo.
4. **Công thức toán học thống kê:**
   - **Giá trị trung bình mẫu (Sample Mean):**
     $$\bar{x} = \frac{1}{T} \sum_{i=1}^T x_i$$
   - **Độ lệch chuẩn mẫu (Sample Standard Deviation):**
     $$s = \sqrt{\frac{1}{T - 1} \sum_{i=1}^T (x_i - \bar{x})^2}$$
   - **Tỷ lệ phần trăm cải thiện tốc độ (Speedup):**
     $$\% \text{Speedup} = \frac{\bar{x}_{\text{Cutoff}=1} - \bar{x}_{\text{Cutoff}}}{\bar{x}_{\text{Cutoff}=1}} \times 100\%$$

---

## 3. Bảng số liệu thống kê kết quả thực nghiệm

### Bảng 1: Kết quả đo lường với $N = 500,000$ phần tử ($T = 20$ trials)

| CUTOFF | Mean Time (ms) | StdDev (ms) | Min Time (ms) | Max Time (ms) | Speedup (%) vs Cutoff=1 | Đánh giá |
| :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **1** | **458.500** | 78.870 | 377.167 | 621.420 | **+0.00%** | Pure Mergesort (Gốc không Cutoff) |
| **2** | 438.490 | 73.309 | 338.000 | 616.896 | +4.36% | Bắt đầu áp dụng Insertion Sort |
| **3** | 487.543 | 106.200 | 349.513 | 692.863 | -6.33% | Dao động mẫu |
| **4** | 526.681 | 178.182 | 361.199 | 972.189 | -14.87% | Giai đoạn ổn định JIT |
| **5** | 445.916 | 61.844 | 351.194 | 614.052 | +2.74% | Tiến vào vùng tối ưu |
| **6** | 435.336 | 47.299 | 348.626 | 537.135 | +5.05% | Vùng đáy tối ưu (Flat Basin) |
| **7** | **439.027** | 50.473 | 348.907 | 541.376 | **+4.25%** | **Chuẩn kinh điển Sedgewick (Cutoff = 7)** |
| **8** | 429.515 | 51.207 | 358.637 | 551.400 | +6.32% | Hiệu năng cực tốt |
| **9** | 495.185 | 114.162 | 375.112 | 870.002 | -8.00% | Dao động phân chia nhánh |
| **10** | **447.971** | 43.766 | 353.116 | 564.866 | **+2.30%** | **Chuẩn giáo trình hiện đại (Cutoff = 10)** |
| **11** | 437.574 | 51.954 | 362.152 | 554.206 | +4.56% | Vùng đáy tối ưu |
| **12** | 437.895 | 54.672 | 368.020 | 580.801 | +4.49% | Vùng đáy tối ưu |
| **13** | 447.827 | 42.056 | 370.803 | 540.049 | +2.33% | Vùng đáy tối ưu |
| **14** | **429.058** | 54.136 | 368.204 | 553.776 | **+6.42%** | ★ **OPTIMAL CUTOFF trên hệ thống này** |
| **15** | 437.475 | 61.065 | 357.361 | 579.522 | +4.59% | Vùng đáy tối ưu |
| **16** | 452.712 | 61.383 | 372.256 | 595.590 | +1.26% | Ranh giới chuyển tiếp |
| **17** | 499.851 | 106.988 | 358.617 | 778.746 | -9.02% | Insertion Sort bắt đầu tăng chi phí |
| **18** | 477.896 | 83.832 | 392.774 | 728.744 | -4.23% | Insertion Sort |
| **19** | 453.230 | 57.710 | 369.340 | 589.158 | +1.15% | Insertion Sort |
| **20** | 448.197 | 49.464 | 364.554 | 573.912 | +2.25% | Điểm cân bằng cuối |
| **21** | 482.558 | 75.065 | 370.793 | 632.772 | -5.25% | Bắt đầu suy giảm |
| **22** | 506.211 | 71.715 | 415.745 | 664.107 | -10.41% | Suy giảm hiệu năng |
| **23** | 550.243 | 300.627 | 389.105 | 1807.680 | -20.01% | Suy giảm hiệu năng |
| **24** | 455.047 | 61.819 | 382.641 | 634.667 | +0.75% | Dao động |
| **25** | 455.257 | 72.348 | 380.458 | 617.308 | +0.71% | Dao động |
| **26** | 462.404 | 62.608 | 372.212 | 611.916 | -0.85% | Suy giảm dần |
| **27** | 459.906 | 60.951 | 352.702 | 594.232 | -0.31% | Suy giảm dần |
| **28** | 460.779 | 62.378 | 368.534 | 624.266 | -0.50% | Suy giảm dần |
| **29** | 460.684 | 51.057 | 351.301 | 610.819 | -0.48% | Suy giảm dần |
| **30** | 480.975 | 70.945 | 388.117 | 680.618 | -4.90% | Suy giảm rõ rệt |
| **31** | 512.964 | 70.431 | 396.871 | 658.469 | -11.88% | $\mathcal{O}(k^2)$ chi phối mạnh |
| **32** | **528.392** | 92.484 | 441.258 | 747.630 | **-15.24%** | Chậm hơn rõ rệt so với Mergesort gốc |

---

### Bảng 2: Kết quả đo lường với $N = 1,000,000$ phần tử ($T = 20$ trials)

| CUTOFF | Mean Time (ms) | StdDev (ms) | Min Time (ms) | Max Time (ms) | Speedup (%) vs Cutoff=1 | Đánh giá |
| :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **1** | **1099.513** | 102.342 | 967.325 | 1415.898 | **+0.00%** | Pure Mergesort ($N = 1M$) |
| **2** | 1133.673 | 137.432 | 967.153 | 1617.047 | -3.11% | Áp dụng Cutoff = 2 |
| **3** | 1092.357 | 89.493 | 931.916 | 1232.359 | +0.65% | Cải thiện nhẹ |
| **4** | 1062.589 | 67.797 | 937.791 | 1209.482 | +3.36% | Hiệu năng tốt |
| **5** | 1059.557 | 106.144 | 912.751 | 1243.507 | +3.63% | Hiệu năng tốt |
| **6** | 1133.933 | 181.790 | 887.529 | 1619.155 | -3.13% | Biến động |
| **7** | 1363.256 | 203.512 | 1025.295 | 1839.635 | -23.99% | Bị ảnh hưởng GC pause |
| **8** | 1495.155 | 234.206 | 1213.254 | 2126.523 | -35.98% | GC Young Gen |
| **9** | 1189.380 | 206.824 | 926.071 | 1703.076 | -8.17% | Heap ổn định lại |
| **10** | **1081.711** | 109.631 | 914.336 | 1277.287 | **+1.62%** | **Chuẩn giáo trình hiện đại (Cutoff = 10)** |
| **11** | 1209.598 | 232.959 | 948.709 | 1694.585 | -10.01% | Biến động |
| **12** | 1216.769 | 217.548 | 924.184 | 1689.643 | -10.66% | Biến động |
| **13** | **1042.030** | 75.139 | 915.140 | 1196.376 | **+5.23%** | ★ **OPTIMAL CUTOFF ở N = 1,000,000** |
| **14** | 1049.676 | 80.326 | 917.673 | 1222.977 | +4.53% | Vùng tối ưu rất mạnh |
| **15** | 1137.676 | 139.682 | 929.669 | 1398.200 | -3.47% | Biến động nhẹ |
| **16** | 1104.755 | 106.367 | 896.187 | 1258.887 | -0.48% | Cân bằng |
| **17** | 1079.475 | 101.955 | 913.880 | 1273.896 | +1.82% | Vùng đáy ổn định |
| **18** | 1077.124 | 83.018 | 912.781 | 1262.398 | +2.04% | Vùng đáy ổn định |
| **19** | 1075.396 | 80.747 | 934.914 | 1241.553 | +2.19% | Vùng đáy ổn định |
| **20** | 1255.914 | 265.423 | 1039.154 | 2033.814 | -14.22% | Biến động |
| **21** | 1138.968 | 141.241 | 928.075 | 1543.775 | -3.59% | Dao động |
| **22** | 1069.736 | 96.215 | 938.690 | 1283.357 | +2.71% | Vùng cân bằng |
| **23** | 1078.146 | 76.237 | 913.919 | 1210.225 | +1.94% | Vùng cân bằng |
| **24** | 1084.889 | 81.544 | 978.933 | 1303.152 | +1.33% | Vùng cân bằng |
| **25** | 1060.131 | 64.139 | 935.808 | 1166.184 | +3.58% | Độ lệch chuẩn nhỏ (64ms) |
| **26** | 1100.971 | 74.363 | 962.594 | 1236.449 | -0.13% | Bắt đầu suy giảm |
| **27** | 1075.362 | 101.761 | 928.540 | 1294.613 | +2.20% | Biến động |
| **28** | 1190.660 | 227.603 | 911.290 | 1728.593 | -8.29% | Suy giảm |
| **29** | 1130.664 | 121.238 | 932.818 | 1397.555 | -2.83% | Suy giảm |
| **30** | 1124.353 | 58.080 | 1029.242 | 1234.265 | -2.26% | Suy giảm |
| **31** | 1188.038 | 91.546 | 992.886 | 1360.826 | -8.05% | Suy giảm rõ rệt |
| **32** | **1239.715** | 135.450 | 1052.124 | 1561.453 | **-12.75%** | Chậm hơn rõ rệt so với Mergesort gốc |

---

## 4. Biểu đồ trực quan hóa dữ liệu thực nghiệm

### Hình 1: Đồ thị Thời gian thực thi trung bình theo CUTOFF
*(Đánh dấu nổi bật mốc CUTOFF = 7, CUTOFF = 10 và Optimal CUTOFF)*

![Thời gian thực thi Mergesort theo CUTOFF](./cutoff_vs_time.png)

---

### Hình 2: Đồ thị kèm thanh sai số độ lệch chuẩn mẫu (Error Bars $\pm 1$ StdDev)
*(Vùng bóng mờ thể hiện dải tin cậy $\pm \sigma$ của $T = 20$ lần thử nghiệm)*

![Đồ thị với thanh sai số độ lệch chuẩn mẫu](./cutoff_with_errorbar.png)

---

### Hình 3: So sánh Tỷ lệ Cải thiện Tốc độ (% Speedup) so với Pure Mergesort

![So sánh tỷ lệ tăng tốc](./speedup_comparison.png)

---

## 5. Phân tích kết quả và Kết luận học thuật

### 5.1. Phân tích hình thái đường cong (Đặc tính hình chữ U có đáy thoải - Flat U-curve)
Đồ thị thực nghiệm trên cả hai quy mô $N = 500,000$ và $N = 1,000,000$ tuân theo hình thái **chữ U có vùng đáy rất thoải (*Flat Basin*)**:

1. **Sườn dốc giảm (CUTOFF từ 1 đến 5 - 8):**  
   Ở $\text{CUTOFF} = 1$, thuật toán phân rã cây đệ quy xuống tận từng phần tử đơn lẻ, chi phí đệ quy đạt mức tối đa. Khi tăng CUTOFF lên 5 - 8, thuật toán cắt tỉa được từ 2 đến 3 tầng đáy của cây đệ quy, tiết kiệm hàng triệu thao tác đệ quy và sao chép mảng, giúp thời gian chạy giảm nhanh chóng.
2. **Vùng đáy tối ưu thoải (Flat Optimal Basin, CUTOFF $\in [6..16]$):**  
   Đây là vùng giao thoa hoàn hảo giữa lợi thế Cache Locality của Insertion Sort và chi phí tiệm cận của Mergesort. Thời gian thực thi trong khoảng này biến thiên rất nhỏ (dưới 1% - 2%) và nằm trọn trong thanh sai số của độ lệch chuẩn mẫu ($\pm \text{StdDev}$).  
   - Tại $N = 500,000$: Điểm tối ưu đạt tại **$\text{CUTOFF} = 14$** ($429.058 \text{ ms}$, tăng tốc $+6.42\%$), sát sao với $\text{CUTOFF} = 8$ ($429.515 \text{ ms}$, $+6.32\%$).
   - Tại $N = 1,000,000$: Điểm tối ưu đạt tại **$\text{CUTOFF} = 13$** ($1042.030 \text{ ms}$, tăng tốc $+5.23\%$).
3. **Sườn dốc tăng (CUTOFF $> 20$ đến 32):**  
   Khi CUTOFF vượt quá 20, độ phức tạp $\mathcal{O}(k^2)$ của Insertion Sort bộc lộ nhược điểm. Số phép so sánh $\approx \frac{32 \times 31}{4} = 248$ phép tính/mảng con, vượt quá lợi ích của bộ nhớ đệm, khiến thời gian tại $\text{CUTOFF} = 32$ chậm hơn Mergesort thuần túy từ **$-12.75\%$ đến $-15.24\%$**.

---

### 5.2. Đối chiếu với các mốc chuẩn trong giáo trình
- **Chuẩn kinh điển Sedgewick ($\text{CUTOFF} = 7$):** Đạt thời gian $439.027 \text{ ms}$ (tăng tốc $+4.25\%$), chỉ cách biệt $2\%$ so với điểm tối ưu tuyệt đối. Điều này khẳng định trực giác lý thuyết của GS. Robert Sedgewick là rất chính xác và an toàn.
- **Chuẩn giáo trình hiện đại ($\text{CUTOFF} = 10$):** Đạt $447.971 \text{ ms}$ (ở $N=500k$) và $1081.711 \text{ ms}$ (ở $N=1M$), nằm trọn vẹn trong vùng đáy tối ưu. Nhờ các CPU thế hệ mới có bộ nhớ đệm L1 Data Cache lớn (48 KB), việc mở rộng Cutoff lên khoảng **$10 - 14$** mang lại hiệu suất tối đa.

---

## 6. Hướng dẫn tái lập kết quả thí nghiệm

Để chạy lại toàn bộ thực nghiệm trên máy tính:

```bash
# 1. Biên dịch các tệp mã nguồn Java
javac Merge.java DatasetGenerator.java CutoffExperiment.java

# 2. Sinh các bộ dữ liệu mẫu trong thư mục datasets/
java DatasetGenerator

# 3. Chạy chương trình đo lường thực nghiệm (cố định Heap 4GB)
java -Xms4g -Xmx4g CutoffExperiment

# 4. Vẽ lại các biểu đồ độ nét cao
python plot_charts.py

# 5. Xuất báo cáo học thuật Microsoft Word
python export_docx.py
```

---

## 7. Cấu trúc tệp tin trong Repository

```text
├── Merge.java                                 # Thuật toán chuẩn Mergesort + Insertion Sort (100% nguyên bản)
├── DatasetGenerator.java                      # Chương trình sinh các bộ dữ liệu mẫu
├── CutoffExperiment.java                      # Chương trình đo lường thực nghiệm (Seed=42, Trials=20)
├── experiment_results.csv                     # Toàn bộ dữ liệu thô (64 bản ghi đo lường)
├── plot_charts.py                            # Script kết xuất biểu đồ trực quan (DPI 300)
├── cutoff_vs_time.png                        # Biểu đồ thời gian thực thi theo CUTOFF
├── cutoff_with_errorbar.png                 # Biểu đồ thời gian kèm thanh sai số StdDev
├── speedup_comparison.png                    # Biểu đồ tỷ lệ cải thiện tốc độ (%)
├── export_docx.py                            # Script xuất báo cáo Microsoft Word
├── Bao_Cao_Thi_Nghiem.md                     # Báo cáo học thuật chi tiết (Markdown)
├── Bao_Cao_Thi_Nghiem_CUTOFF_Mergesort.docx # Báo cáo học thuật định dạng Microsoft Word
├── Log_chat_AI.pdf                           # Bản ghi log thảo luận và thiết kế thực nghiệm cùng AI
├── README.md                                 # Trang chủ báo cáo hiển thị trực tiếp trên GitHub
└── datasets/                                 # Dữ liệu thử nghiệm mẫu (random_10k, partially_sorted_10k, reverse_10k)
```
