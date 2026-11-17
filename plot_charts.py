import csv
import math
from PIL import Image, ImageDraw, ImageFont

def load_data(filename):
    data = {}
    with open(filename, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            N = int(row['N'])
            if N not in data:
                data[N] = []
            data[N].append({
                'cutoff': int(row['Cutoff']),
                'mean': float(row['Mean_Time_ms']),
                'std': float(row['StdDev_ms']),
                'min': float(row['Min_Time_ms']),
                'max': float(row['Max_Time_ms']),
                'speedup': float(row['Speedup_Percent'])
            })
    for N in data:
        data[N].sort(key=lambda x: x['cutoff'])
    return data

def get_font(size, bold=False):
    font_paths = [
        "C:/Windows/Fonts/segoeui.ttf" if not bold else "C:/Windows/Fonts/segoeuib.ttf",
        "C:/Windows/Fonts/arial.ttf" if not bold else "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/calibri.ttf" if not bold else "C:/Windows/Fonts/calibrib.ttf"
    ]
    for path in font_paths:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            pass
    return ImageFont.load_default()

def draw_rotated_text(img, text, font, fill, center_x, center_y, angle=90):
    bbox = font.getbbox(text)
    w = bbox[2] - bbox[0] + 16
    h = bbox[3] - bbox[1] + 16
    txt_img = Image.new('RGBA', (w, h), (255, 255, 255, 0))
    d = ImageDraw.Draw(txt_img)
    d.text((-bbox[0] + 8, -bbox[1] + 8), text, fill=fill, font=font)
    rotated = txt_img.rotate(angle, expand=True, resample=Image.BICUBIC)
    rx = int(center_x - rotated.width / 2)
    ry = int(center_y - rotated.height / 2)
    img.paste(rotated, (rx, ry), rotated)

def draw_arrow(draw, x1, y1, x2, y2, color, width=2, arrow_len=14, arrow_angle=25):
    # Draw shaft
    draw.line([(x1, y1), (x2, y2)], fill=color, width=width)
    # Draw arrowhead pointing towards (x2, y2)
    angle = math.atan2(y2 - y1, x2 - x1)
    angle_rad = math.radians(arrow_angle)
    ax1 = x2 - arrow_len * math.cos(angle - angle_rad)
    ay1 = y2 - arrow_len * math.sin(angle - angle_rad)
    ax2 = x2 - arrow_len * math.cos(angle + angle_rad)
    ay2 = y2 - arrow_len * math.sin(angle + angle_rad)
    draw.polygon([(x2, y2), (ax1, ay1), (ax2, ay2)], fill=color)

def draw_chart(data, include_errorbars=False, output_filename='chart.png'):
    width = 2200
    height = 1100
    img = Image.new('RGB', (width, height), '#fcfdfd')
    draw = ImageDraw.Draw(img)

    f_title = get_font(38, bold=True)
    f_sub = get_font(24)
    f_axis = get_font(24, bold=True)
    f_tick = get_font(18)
    f_callout = get_font(18, bold=True)
    f_legend = get_font(20)

    # Title & Subtitle
    title_text = "Mergesort Execution Time vs. CUTOFF Threshold" if not include_errorbars else "Mergesort CUTOFF Analysis with Error Bars (Sample StdDev)"
    draw.text((width // 2, 45), title_text, fill='#1a202c', font=f_title, anchor='mm')
    sub_text = "Comprehensive Empirical Benchmark on Intel Core i7-1255U | JDK 25 HotSpot 64-Bit"
    draw.text((width // 2, 90), sub_text, fill='#4a5568', font=f_sub, anchor='mm')

    panels = [
        {'N': 500000, 'rect': (170, 160, 1110, 960), 'color': '#1f77b4', 'target_callout_y': 525.0},
        {'N': 1000000, 'rect': (1280, 160, 2120, 960), 'color': '#d62728', 'target_callout_y': 1400.0}
    ]

    for panel in panels:
        N = panel['N']
        if N not in data:
            continue
        p_data = data[N]
        x1, y1, x2, y2 = panel['rect']

        means = [d['mean'] for d in p_data]
        if include_errorbars:
            min_val = min(d['mean'] - d['std'] for d in p_data)
            max_val = max(d['mean'] + d['std'] for d in p_data)
        else:
            min_val = min(means)
            max_val = max(means)

        y_min = math.floor(min_val / 50.0) * 50.0 - 20
        y_max = math.ceil(max_val / 50.0) * 50.0 + 30
        if y_min < 0: y_min = 0

        # Adjust y_max if needed to fit callout
        if panel['target_callout_y'] + 50 > y_max:
            y_max = panel['target_callout_y'] + 60

        draw.rectangle([x1, y1, x2, y2], fill='#ffffff', outline='#cbd5e1', width=2)

        # Panel header
        p_title = f"Dataset: N = {N:,} Elements (T = 20 Trials)"
        draw.text((x1 + (x2 - x1) // 2, y1 - 30), p_title, fill='#2d3748', font=f_axis, anchor='mm')

        # Grid lines and Y ticks
        num_y_ticks = 6
        step_y = (y_max - y_min) / num_y_ticks
        for i in range(num_y_ticks + 1):
            y_val = y_min + i * step_y
            py = y2 - (y_val - y_min) / (y_max - y_min) * (y2 - y1)
            draw.line([(x1, py), (x2, py)], fill='#f1f5f9', width=1)
            draw.text((x1 - 15, py), f"{y_val:.0f}", fill='#64748b', font=f_tick, anchor='rm')

        def to_px(cutoff):
            return x1 + (cutoff - 1) / (32 - 1) * (x2 - x1)

        def to_py(val):
            return y2 - (val - y_min) / (y_max - y_min) * (y2 - y1)

        # X ticks
        for c in range(1, 33):
            px = to_px(c)
            if c % 2 == 1 or c == 32:
                draw.line([(px, y2), (px, y2 + 6)], fill='#64748b', width=1)
                draw.text((px, y2 + 20), str(c), fill='#64748b', font=f_tick, anchor='mm')
            draw.line([(px, y1), (px, y2)], fill='#f8fafc', width=1)

        opt_item = min(p_data, key=lambda d: d['mean'])
        opt_cutoff = opt_item['cutoff']
        opt_mean = opt_item['mean']

        def draw_dashed_vline(cx, color, width_px=2):
            dash_len = 8
            y_curr = y1
            while y_curr < y2:
                draw.line([(cx, y_curr), (cx, min(y_curr + dash_len, y2))], fill=color, width=width_px)
                y_curr += dash_len * 2

        draw_dashed_vline(to_px(7), '#16a34a', 2)
        draw_dashed_vline(to_px(10), '#ea580c', 2)
        draw_dashed_vline(to_px(opt_cutoff), '#7c3aed', 3)

        # Shaded band for error bars
        if include_errorbars:
            band_pts_top = []
            band_pts_bot = []
            for d in p_data:
                c = d['cutoff']
                px = to_px(c)
                py_top = to_py(d['mean'] + d['std'])
                py_bot = to_py(d['mean'] - d['std'])
                band_pts_top.append((px, py_top))
                band_pts_bot.append((px, py_bot))
            poly_pts = band_pts_top + list(reversed(band_pts_bot))
            band_overlay = Image.new('RGBA', (width, height), (255, 255, 255, 0))
            band_draw = ImageDraw.Draw(band_overlay)
            rgba_fill = (31, 119, 180, 45) if N == 500000 else (214, 39, 40, 45)
            band_draw.polygon(poly_pts, fill=rgba_fill)
            img.paste(Image.alpha_composite(img.convert('RGBA'), band_overlay).convert('RGB'))
            draw = ImageDraw.Draw(img)

            # Error bars
            for d in p_data:
                px = to_px(d['cutoff'])
                py_top = to_py(d['mean'] + d['std'])
                py_bot = to_py(d['mean'] - d['std'])
                draw.line([(px, py_top), (px, py_bot)], fill='#94a3b8', width=2)
                draw.line([(px - 4, py_top), (px + 4, py_top)], fill='#94a3b8', width=2)
                draw.line([(px - 4, py_bot), (px + 4, py_bot)], fill='#94a3b8', width=2)

        # Main curve
        line_pts = [(to_px(d['cutoff']), to_py(d['mean'])) for d in p_data]
        draw.line(line_pts, fill=panel['color'], width=4)

        for d in p_data:
            px = to_px(d['cutoff'])
            py = to_py(d['mean'])
            r = 5
            draw.ellipse([px - r, py - r, px + r, py + r], fill='#ffffff', outline=panel['color'], width=3)

        c7_item = next(d for d in p_data if d['cutoff'] == 7)
        c10_item = next(d for d in p_data if d['cutoff'] == 10)

        draw.ellipse([to_px(7)-7, to_py(c7_item['mean'])-7, to_px(7)+7, to_py(c7_item['mean'])+7],
                     fill='#16a34a', outline='#ffffff', width=2)
        draw.ellipse([to_px(10)-7, to_py(c10_item['mean'])-7, to_px(10)+7, to_py(c10_item['mean'])+7],
                     fill='#ea580c', outline='#ffffff', width=2)
        draw.ellipse([to_px(opt_cutoff)-9, to_py(opt_mean)-9, to_px(opt_cutoff)+9, to_py(opt_mean)+9],
                     fill='#7c3aed', outline='#ffffff', width=3)

        # -------------------------------------------------------------
        # Re-positioned Callout Box at upper clear region with Arrow
        # -------------------------------------------------------------
        box_w, box_h = 240, 92
        # Position box above in the upper area (e.g. Y = target_callout_y)
        call_center_y = to_py(panel['target_callout_y'])
        call_y = int(call_center_y - box_h / 2)
        call_x = int(to_px(opt_cutoff) - box_w / 2)

        # Ensure call_x is inside panel
        if call_x < x1 + 20: call_x = x1 + 20
        if call_x + box_w > x2 - 20: call_x = x2 - box_w - 20

        # Draw callout box
        draw.rectangle([call_x, call_y, call_x + box_w, call_y + box_h], fill='#fef9c3', outline='#eab308', width=2)

        # Draw arrow from bottom of callout box pointing down to optimal point
        arrow_start_x = int(to_px(opt_cutoff))
        arrow_start_y = call_y + box_h
        arrow_end_x = int(to_px(opt_cutoff))
        arrow_end_y = int(to_py(opt_mean) - 12) # slight gap above point
        draw_arrow(draw, arrow_start_x, arrow_start_y, arrow_end_x, arrow_end_y, color='#ca8a04', width=3, arrow_len=14)

        # Text inside callout box (NO unicode star, plain text)
        draw.text((call_x + 14, call_y + 10), f"Optimal CUTOFF = {opt_cutoff}", fill='#854d0e', font=f_callout)
        draw.text((call_x + 14, call_y + 36), f"Mean Time: {opt_mean:.2f} ms", fill='#1e293b', font=f_tick)
        draw.text((call_x + 14, call_y + 62), f"Speedup: {opt_item['speedup']:+.2f}% vs C=1", fill='#15803d', font=f_callout)

        # Panel X Axis Label
        draw.text((x1 + (x2 - x1) // 2, y2 + 55), "CUTOFF Threshold (Threshold to Insertion Sort)", fill='#334155', font=f_axis, anchor='mm')

        # -------------------------------------------------------------
        # Rotated Y-Axis Label (90 degrees, vertical)
        # -------------------------------------------------------------
        draw_rotated_text(img, "Execution Time (ms)", f_axis, fill='#334155',
                          center_x=x1 - 95, center_y=y1 + (y2 - y1) // 2, angle=90)

        # Legend at top-right of panel
        leg_x = x2 - 290
        leg_y = y1 + 18
        draw.rectangle([leg_x, leg_y, leg_x + 275, leg_y + 115], fill='#f8fafc', outline='#e2e8f0', width=1)
        draw.line([(leg_x + 12, leg_y + 20), (leg_x + 35, leg_y + 20)], fill='#16a34a', width=2)
        draw.text((leg_x + 45, leg_y + 12), f"Cutoff = 7 ({c7_item['mean']:.1f}ms)", fill='#16a34a', font=f_tick)

        draw.line([(leg_x + 12, leg_y + 50), (leg_x + 35, leg_y + 50)], fill='#ea580c', width=2)
        draw.text((leg_x + 45, leg_y + 42), f"Cutoff = 10 ({c10_item['mean']:.1f}ms)", fill='#ea580c', font=f_tick)

        draw.line([(leg_x + 12, leg_y + 80), (leg_x + 35, leg_y + 80)], fill='#7c3aed', width=3)
        draw.text((leg_x + 45, leg_y + 72), f"Optimal = {opt_cutoff} ({opt_mean:.1f}ms)", fill='#7c3aed', font=f_tick)

    img.save(output_filename, dpi=(300, 300))
    print(f"Exported chart successfully to: {output_filename}")

def draw_speedup_chart(data, output_filename='speedup_comparison.png'):
    width = 1800
    height = 950
    img = Image.new('RGB', (width, height), '#fcfdfd')
    draw = ImageDraw.Draw(img)

    f_title = get_font(36, bold=True)
    f_sub = get_font(22)
    f_axis = get_font(22, bold=True)
    f_tick = get_font(17)
    f_legend = get_font(19, bold=True)

    draw.text((width // 2, 45), "Speedup Comparison Relative to Pure Mergesort (CUTOFF = 1)", fill='#1a202c', font=f_title, anchor='mm')
    draw.text((width // 2, 85), "% Performance Improvement across Cutoff Range [1..32]", fill='#4a5568', font=f_sub, anchor='mm')

    x1, y1, x2, y2 = 170, 150, 1660, 830
    draw.rectangle([x1, y1, x2, y2], fill='#ffffff', outline='#cbd5e1', width=2)

    all_speedups = [d['speedup'] for N in data for d in data[N]]
    min_sp = min(all_speedups)
    max_sp = max(all_speedups)
    y_min = math.floor(min_sp / 5.0) * 5.0 - 5.0
    y_max = math.ceil(max_sp / 5.0) * 5.0 + 5.0

    def to_px(cutoff):
        return x1 + (cutoff - 1) / (32 - 1) * (x2 - x1)

    def to_py(val):
        return y2 - (val - y_min) / (y_max - y_min) * (y2 - y1)

    num_y_ticks = 8
    step_y = (y_max - y_min) / num_y_ticks
    for i in range(num_y_ticks + 1):
        y_val = y_min + i * step_y
        py = to_py(y_val)
        draw.line([(x1, py), (x2, py)], fill='#f1f5f9', width=1)
        draw.text((x1 - 15, py), f"{y_val:+.1f}%", fill='#64748b', font=f_tick, anchor='rm')

    # Baseline 0% line
    py_zero = to_py(0.0)
    draw.line([(x1, py_zero), (x2, py_zero)], fill='#94a3b8', width=2)

    for c in range(1, 33):
        px = to_px(c)
        if c % 2 == 1 or c == 32:
            draw.line([(px, y2), (px, y2 + 6)], fill='#64748b', width=1)
            draw.text((px, y2 + 20), str(c), fill='#64748b', font=f_tick, anchor='mm')
        draw.line([(px, y1), (px, y2)], fill='#f8fafc', width=1)

    colors = {500000: '#1f77b4', 1000000: '#d62728'}
    for N in data:
        p_data = data[N]
        pts = [(to_px(d['cutoff']), to_py(d['speedup'])) for d in p_data]
        c = colors.get(N, '#333333')
        draw.line(pts, fill=c, width=3)
        for d in p_data:
            px = to_px(d['cutoff'])
            py = to_py(d['speedup'])
            draw.ellipse([px-4, py-4, px+4, py+4], fill='#ffffff', outline=c, width=2)

    def draw_dashed_vline(cx, color):
        y_curr = y1
        while y_curr < y2:
            draw.line([(cx, y_curr), (cx, min(y_curr + 6, y2))], fill=color, width=2)
            y_curr += 12

    draw_dashed_vline(to_px(7), '#16a34a')
    draw_dashed_vline(to_px(10), '#ea580c')

    # Labels
    draw.text((x1 + (x2 - x1) // 2, y2 + 55), "CUTOFF Threshold", fill='#334155', font=f_axis, anchor='mm')
    
    # Rotated Y-Axis Label
    draw_rotated_text(img, "Speedup (%) vs Pure Mergesort", f_axis, fill='#334155',
                      center_x=x1 - 95, center_y=y1 + (y2 - y1) // 2, angle=90)

    # Legend
    leg_x = x2 - 340
    leg_y = y1 + 20
    draw.rectangle([leg_x, leg_y, leg_x + 320, leg_y + 140], fill='#f8fafc', outline='#e2e8f0', width=1)
    draw.line([(leg_x + 15, leg_y + 25), (leg_x + 45, leg_y + 25)], fill='#1f77b4', width=3)
    draw.text((leg_x + 55, leg_y + 15), "N = 500,000 Elements", fill='#1f77b4', font=f_legend)

    draw.line([(leg_x + 15, leg_y + 60), (leg_x + 45, leg_y + 60)], fill='#d62728', width=3)
    draw.text((leg_x + 55, leg_y + 50), "N = 1,000,000 Elements", fill='#d62728', font=f_legend)

    draw.line([(leg_x + 15, leg_y + 95), (leg_x + 45, leg_y + 95)], fill='#16a34a', width=2)
    draw.text((leg_x + 55, leg_y + 85), "Sedgewick Cutoff = 7", fill='#16a34a', font=f_tick)

    draw.line([(leg_x + 15, leg_y + 125), (leg_x + 45, leg_y + 125)], fill='#ea580c', width=2)
    draw.text((leg_x + 55, leg_y + 115), "Modern Cutoff = 10", fill='#ea580c', font=f_tick)

    img.save(output_filename, dpi=(300, 300))
    print(f"Exported chart successfully to: {output_filename}")

if __name__ == '__main__':
    data = load_data('experiment_results.csv')
    draw_chart(data, include_errorbars=False, output_filename='cutoff_vs_time.png')
    draw_chart(data, include_errorbars=True, output_filename='cutoff_with_errorbar.png')
    draw_speedup_chart(data, output_filename='speedup_comparison.png')
