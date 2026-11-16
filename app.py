# -*- coding: utf-8 -*-
"""
================================================================================
ĐỒ ÁN LẬP TRÌNH PYTHON (DH23TIN07) - HỆ THỐNG GIÁM SÁT DỊCH TỄ HIV/AIDS TOÀN CẦU
================================================================================
Giao diện ứng dụng y tế chuyên nghiệp (Medical Theme):
- Phong cách: Nền trắng thanh lịch, chi tiết đỏ y tế (Medical Red / Crimson).
- Bản đồ thế giới mặc định nằm chính giữa khung nhìn (Centered World View).
- Bên trái: Bản đồ dịch tễ thế giới tương tác, tự động highlight quốc gia được chọn.
- Bên phải: Bảng thông số y tế chia thành 4 mục chuyên biệt, mỗi mục có biểu đồ riêng:
    1. Tổng quan (Hồ sơ dịch tễ & Biểu đồ tiến độ UNAIDS 95-95-95)
    2. Bảng 1: Dịch tễ (Hiện nhiễm, tử vong & Biểu đồ so sánh chuẩn WHO / Toàn cầu)
    3. Bảng 2: Điều trị ART (Tiếp cận thuốc kháng virus & Biểu đồ dải bất định Min-Max)
    4. Bảng 3: Dự báo Machine Learning (Hồi quy Ridge Task T1 & Biểu đồ đối chiếu)
================================================================================
"""

import os
import sys
import csv
import json
import math
import re
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse, unquote

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = Path(__file__).resolve().parent
DATA_RAW = BASE_DIR / "data" / "raw"
FILE_HIV = DATA_RAW / "HIV_AIDS prevalence estimates table.csv"
FILE_ART = DATA_RAW / "art_coverage_by_country_clean.csv"

# Bảng mã ISO-3
ISO3_MAP = {
    "afghanistan": "AFG", "albania": "ALB", "algeria": "DZA", "angola": "AGO",
    "argentina": "ARG", "armenia": "ARM", "australia": "AUS", "austria": "AUT",
    "azerbaijan": "AZE", "bahamas": "BHS", "bahamas, the": "BHS", "bahrain": "BHR",
    "bangladesh": "BGD", "barbados": "BRB", "belarus": "BLR", "belgium": "BEL",
    "belize": "BLZ", "benin": "BEN", "bhutan": "BTN", "bolivia": "BOL",
    "bolivia (plurinational state of)": "BOL", "bosnia and herzegovina": "BIH",
    "botswana": "BWA", "brazil": "BRA", "bulgaria": "BGR", "burkina faso": "BFA",
    "burundi": "BDI", "cambodia": "KHM", "cameroon": "CMR", "cameron": "CMR",
    "canada": "CAN", "cape verde": "CPV", "central african republic": "CAF",
    "chad": "TCD", "chile": "CHL", "china": "CHN", "colombia": "COL",
    "comoros": "COM", "congo": "COG", "congo, republic of the": "COG",
    "congo, democratic republic of": "COD", "democratic republic of the congo": "COD",
    "costa rica": "CRI", "cote d'ivoire": "CIV", "côte d'ivoire": "CIV", "ivory coast": "CIV",
    "croatia": "HRV", "cuba": "CUB", "cyprus": "CYP", "czech republic": "CZE", "czechia": "CZE",
    "denmark": "DNK", "djibouti": "DJI", "dominica": "DMA", "dominican republic": "DOM",
    "ecuador": "ECU", "egypt": "EGY", "el salvador": "SLV", "equatorial guinea": "GNQ",
    "eritrea": "ERI", "estonia": "EST", "eswatini": "SWZ", "ethiopia": "ETH",
    "fiji": "FJI", "finland": "FIN", "france": "FRA", "gabon": "GAB", "gambia": "GMB",
    "gambia, the": "GMB", "georgia": "GEO", "germany": "DEU", "ghana": "GHA",
    "greece": "GRC", "guatemala": "GTM", "guinea": "GIN", "guinea-bissau": "GNB",
    "guyana": "GUY", "haiti": "HTI", "honduras": "HND", "hungary": "HUN",
    "iceland": "ISL", "india": "IND", "indonesia": "IDN", "iran": "IRN",
    "iran (islamic republic of)": "IRN", "iraq": "IRQ", "ireland": "IRL",
    "israel": "ISR", "italy": "ITA", "jamaica": "JAM", "japan": "JPN",
    "jordan": "JOR", "kazakhstan": "KAZ", "kenya": "KEN", "kuwait": "KWT",
    "kyrgyzstan": "KGZ", "laos": "LAO", "lao people's democratic republic": "LAO",
    "latvia": "LVA", "lebanon": "LBN", "lesotho": "LSO", "liberia": "LBR",
    "libya": "LBY", "lithuania": "LTU", "luxembourg": "LUX", "madagascar": "MDG",
    "malawi": "MWI", "malaysia": "MYS", "maldives": "MDV", "mali": "MLI",
    "malta": "MLT", "mauritania": "MRT", "mauritius": "MUS", "mexico": "MEX",
    "moldova": "MDA", "republic of moldova": "MDA", "mongolia": "MNG",
    "montenegro": "MNE", "morocco": "MAR", "mozambique": "MOZ", "myanmar": "MMR", "burma": "MMR",
    "namibia": "NAM", "nepal": "NPL", "netherlands": "NLD", "new zealand": "NZL",
    "nicaragua": "NIC", "niger": "NER", "nigeria": "NGA", "north macedonia": "MKD",
    "republic of north macedonia": "MKD", "norway": "NOR", "oman": "OMN",
    "pakistan": "PAK", "panama": "PAN", "papua new guinea": "PNG", "paraguay": "PRY",
    "peru": "PER", "philippines": "PHL", "poland": "POL", "portugal": "PRT",
    "qatar": "QAT", "romania": "ROU", "russia": "RUS", "russian federation": "RUS",
    "rwanda": "RWA", "saudi arabia": "SAU", "senegal": "SEN", "serbia": "SRB",
    "sierra leone": "SLE", "singapore": "SGP", "slovakia": "SVK", "slovenia": "SVN",
    "somalia": "SOM", "south africa": "ZAF", "south sudan": "SSD", "spain": "ESP",
    "sri lanka": "LKA", "sudan": "SDN", "suriname": "SUR", "sweden": "SWE",
    "switzerland": "CHE", "syria": "SYR", "syrian arab republic": "SYR",
    "tajikistan": "TJK", "tanzania": "TZA", "united republic of tanzania": "TZA",
    "thailand": "THA", "timor-leste": "TLS", "east timor": "TLS", "togo": "TGO",
    "trinidad and tobago": "TTO", "tunisia": "TUN", "turkey": "TUR", "turkiye": "TUR",
    "turkmenistan": "TKM", "uganda": "UGA", "ukraine": "UKR",
    "united arab emirates": "ARE", "united kingdom": "GBR",
    "united kingdom of great britain and northern ireland": "GBR",
    "united states": "USA", "united states of america": "USA", "usa": "USA",
    "uruguay": "URY", "uzbekistan": "UZB", "venezuela": "VEN",
    "venezuela (bolivarian republic of)": "VEN", "vietnam": "VNM", "viet nam": "VNM",
    "yemen": "YEM", "zambia": "ZMB", "zimbabwe": "ZWE",
    "korea, south": "KOR", "south korea": "KOR", "republic of korea": "KOR",
    "korea, north": "PRK", "north korea": "PRK", "democratic people's republic of korea": "PRK"
}

# Tọa độ tâm (Lat, Lon) phục vụ hiệu ứng bay/zoom
COUNTRY_COORDS = {
    "VNM": (14.05, 108.27), "ZAF": (-30.55, 22.93), "THA": (15.87, 100.99),
    "USA": (37.09, -95.71), "FRA": (46.22, 2.21), "SWZ": (-26.52, 31.46),
    "BWA": (-22.32, 24.68), "KEN": (-0.02, 37.90), "NGA": (9.08, 8.67),
    "IND": (20.59, 78.96), "BRA": (-14.23, -51.92), "RUS": (61.52, 105.31),
    "GBR": (55.37, -3.43), "DEU": (51.16, 10.45), "ZWE": (-19.01, 29.15),
    "MOZ": (-18.66, 35.52), "UGA": (1.37, 32.29), "TZA": (-6.36, 34.88),
    "LSO": (-29.60, 28.23), "NAM": (-22.95, 18.49), "ZMB": (-13.13, 27.84),
    "MWI": (-13.25, 34.30), "RWA": (-1.94, 29.87), "CAF": (6.61, 20.93),
    "CMR": (7.36, 12.35), "COD": (-4.03, 21.75), "COG": (-0.22, 15.82),
    "AGO": (-11.20, 17.87), "GHA": (7.94, -1.02), "CIV": (7.53, -5.54),
    "SEN": (14.49, -14.45), "ETH": (9.14, 40.48), "EGY": (26.82, 30.80),
    "MAR": (31.79, -7.09), "DZA": (28.03, 1.65), "IDN": (-0.78, 113.92),
    "MYS": (4.21, 101.97), "PHL": (12.87, 121.77), "MMR": (21.91, 95.95),
    "KHM": (12.56, 104.99), "LAO": (19.85, 102.49), "JPN": (36.20, 138.25),
    "KOR": (35.90, 127.76), "CHN": (35.86, 104.19), "AUS": (-25.27, 133.77),
    "CAN": (56.13, -106.34), "MEX": (23.63, -102.55), "COL": (4.57, -74.29),
    "ARG": (-38.41, -63.61), "CHL": (-35.67, -71.54), "PER": (-9.18, -75.01),
    "ESP": (40.46, -3.74), "ITA": (41.87, 12.56), "UKR": (48.37, 31.16),
    "POL": (51.91, 19.14), "SWE": (60.12, 18.64), "TUR": (38.96, 35.24),
    "SAU": (23.88, 45.07), "IRN": (32.42, 53.68), "PAK": (30.37, 69.34)
}

DISPLAY_NAMES = {
    "viet nam": "Vietnam", "united states of america": "United States",
    "russian federation": "Russia", "united republic of tanzania": "Tanzania",
    "bolivia (plurinational state of)": "Bolivia", "venezuela (bolivarian republic of)": "Venezuela",
    "iran (islamic republic of)": "Iran", "lao people's democratic republic": "Laos",
    "syrian arab republic": "Syria", "democratic republic of the congo": "DR Congo",
    "congo, democratic republic of": "DR Congo", "congo, republic of the": "Congo",
    "republic of korea": "South Korea", "democratic people's republic of korea": "North Korea",
    "republic of moldova": "Moldova", "republic of north macedonia": "North Macedonia",
    "united kingdom of great britain and northern ireland": "United Kingdom",
    "bahamas, the": "Bahamas", "gambia, the": "Gambia"
}

def clean_num(val):
    if val is None: return None
    s = re.sub(r'\[.*?\]', '', str(val)).replace('\xa0', '').replace(' ', '').replace('%', '').replace(',', '').strip()
    if s.lower() in ['', '-', 'nodata', 'no data', 'na', 'n/a']: return None
    try:
        f = float(s)
        return int(f) if f.is_integer() else round(f, 2)
    except:
        return None

def clean_text(val):
    if val is None: return ''
    return re.sub(r'\[.*?\]', '', str(val)).replace('\xa0', ' ').strip()

def load_all_data():
    hiv_dict = {}
    if FILE_HIV.exists():
        with open(FILE_HIV, 'r', encoding='cp850', errors='replace') as f:
            for row in csv.DictReader(f):
                raw_c = clean_text(row.get('Country/Region'))
                if raw_c:
                    hiv_dict[raw_c.lower()] = {
                        'raw_country': raw_c,
                        'prevalence_raw': clean_text(row.get('Adult prevalence of HIV/AIDS')),
                        'prevalence_num': clean_num(row.get('Adult prevalence of HIV/AIDS')),
                        'plhiv_raw': clean_text(row.get('Number of people with HIV/AIDS')),
                        'plhiv_num': clean_num(row.get('Number of people with HIV/AIDS')),
                        'deaths_raw': clean_text(row.get('Annual deaths from HIV/AIDS')),
                        'deaths_num': clean_num(row.get('Annual deaths from HIV/AIDS')),
                        'year_raw': clean_text(row.get('Year of estimate'))
                    }

    art_dict = {}
    if FILE_ART.exists():
        with open(FILE_ART, 'r', encoding='utf-8', errors='replace') as f:
            for row in csv.DictReader(f):
                raw_c = clean_text(row.get('Country'))
                if raw_c:
                    art_dict[raw_c.lower()] = {
                        'raw_country': raw_c,
                        'region': clean_text(row.get('WHO Region')) or 'Không rõ',
                        'art_count_raw': clean_text(row.get('Reported number of people receiving ART')),
                        'art_count_num': clean_num(row.get('Reported number of people receiving ART')),
                        'plhiv_est_raw': clean_text(row.get('Estimated number of people living with HIV')),
                        'plhiv_median': clean_num(row.get('Estimated number of people living with HIV_median')),
                        'plhiv_min': clean_num(row.get('Estimated number of people living with HIV_min')),
                        'plhiv_max': clean_num(row.get('Estimated number of people living with HIV_max')),
                        'art_cov_raw': clean_text(row.get('Estimated ART coverage among people living with HIV (%)')),
                        'art_cov_median': clean_num(row.get('Estimated ART coverage among people living with HIV (%)_median')),
                        'art_cov_min': clean_num(row.get('Estimated ART coverage among people living with HIV (%)_min')),
                        'art_cov_max': clean_num(row.get('Estimated ART coverage among people living with HIV (%)_max'))
                    }

    def find_h(k):
        if k in hiv_dict: return hiv_dict[k]
        target_iso = ISO3_MAP.get(k)
        if target_iso:
            for alt_k, iso in ISO3_MAP.items():
                if iso == target_iso and alt_k in hiv_dict: return hiv_dict[alt_k]
        return None

    def find_a(k):
        if k in art_dict: return art_dict[k]
        target_iso = ISO3_MAP.get(k)
        if target_iso:
            for alt_k, iso in ISO3_MAP.items():
                if iso == target_iso and alt_k in art_dict: return art_dict[alt_k]
        return None

    all_keys = set(hiv_dict.keys()).union(set(art_dict.keys()))
    used_isos = {}
    country_list = []

    for k in sorted(all_keys):
        iso3 = ISO3_MAP.get(k, '')
        h = find_h(k)
        a = find_a(k)

        disp_name = DISPLAY_NAMES.get(k, k.title())
        if h: disp_name = DISPLAY_NAMES.get(k, h['raw_country'])
        elif a: disp_name = DISPLAY_NAMES.get(k, a['raw_country'])

        if iso3 and iso3 in used_isos:
            existing = used_isos[iso3]
            if not existing['table1']['has_data'] and h: existing['table1'] = make_t1(h)
            if not existing['table2']['has_data'] and a:
                existing['table2'] = make_t2(a)
                existing['region'] = a['region']
            continue

        t1 = make_t1(h)
        t2 = make_t2(a)
        kpi = make_kpi(t1, t2)
        ml = make_ml(kpi)

        coord = COUNTRY_COORDS.get(iso3, (0, 0))

        item = {
            'name': disp_name,
            'key': k,
            'iso3': iso3,
            'lat': coord[0],
            'lon': coord[1],
            'region': a['region'] if a else 'Chưa phân vùng',
            'table1': t1,
            'table2': t2,
            'kpi': kpi,
            'ml': ml
        }

        if iso3: used_isos[iso3] = item
        country_list.append(item)

    # Tính toán trung bình theo khu vực WHO
    region_stats = {}
    for c in country_list:
        r = c['region']
        if not r or r == 'Chưa phân vùng': continue
        if r not in region_stats:
            region_stats[r] = {'prev': [], 'cov': []}
        if c['kpi']['prevalence_val'] is not None:
            region_stats[r]['prev'].append(c['kpi']['prevalence_val'])
        if c['kpi']['art_cov_val'] is not None:
            region_stats[r]['cov'].append(c['kpi']['art_cov_val'])

    region_averages = {}
    for r, d in region_stats.items():
        region_averages[r] = {
            'avg_prev': round(sum(d['prev'])/len(d['prev']), 2) if d['prev'] else 1.0,
            'avg_cov': round(sum(d['cov'])/len(d['cov']), 1) if d['cov'] else 50.0
        }

    valid_plhiv = [c['kpi']['plhiv_val'] for c in country_list if c['kpi']['plhiv_val']]
    valid_deaths = [c['kpi']['deaths_val'] for c in country_list if c['kpi']['deaths_val']]
    valid_prev = [c['kpi']['prevalence_val'] for c in country_list if c['kpi']['prevalence_val'] is not None]
    valid_cov = [c['kpi']['art_cov_val'] for c in country_list if c['kpi']['art_cov_val'] is not None]

    global_stats = {
        'total_countries': len(country_list),
        'total_plhiv': f"{sum(valid_plhiv):,}" if valid_plhiv else "38,000,000+",
        'total_deaths': f"{sum(valid_deaths):,}" if valid_deaths else "630,000+",
        'avg_prev': f"{(sum(valid_prev)/len(valid_prev)):.2f}%" if valid_prev else "1.85%",
        'avg_prev_num': round(sum(valid_prev)/len(valid_prev), 2) if valid_prev else 1.85,
        'avg_art_cov': f"{(sum(valid_cov)/len(valid_cov)):.1f}%" if valid_cov else "55.6%",
        'avg_art_cov_num': round(sum(valid_cov)/len(valid_cov), 1) if valid_cov else 55.6
    }

    map_data = {
        'iso3': [],
        'name': [],
        'prevalence': [],
        'art_cov': [],
        'plhiv': [],
        'hover_text': []
    }

    for c in country_list:
        if c['iso3']:
            map_data['iso3'].append(c['iso3'])
            map_data['name'].append(c['name'])
            p_val = c['kpi']['prevalence_val']
            map_data['prevalence'].append(p_val if p_val is not None else 0)
            cov_val = c['kpi']['art_cov_val']
            map_data['art_cov'].append(cov_val if cov_val is not None else 0)
            pl_val = c['kpi']['plhiv_val']
            map_data['plhiv'].append(pl_val if pl_val is not None else 0)

            hover = (
                f"<b>{c['name']} ({c['iso3']})</b><br>"
                f"• Tỷ lệ hiện nhiễm: {c['kpi']['prevalence_display']}<br>"
                f"• Số ca sống chung (PLHIV): {c['kpi']['plhiv_display']}<br>"
                f"• Ca tử vong hàng năm: {c['kpi']['deaths_display']}<br>"
                f"• Độ bao phủ điều trị ART: {c['kpi']['art_cov_display']}<br>"
                f"<i>Nhấp chuột để xem chi tiết bên phải</i>"
            )
            map_data['hover_text'].append(hover)

    return {
        'countries': country_list,
        'global_stats': global_stats,
        'region_averages': region_averages,
        'map_data': map_data
    }

def make_t1(h):
    if not h:
        return {
            'has_data': False,
            'country_raw': 'Không có bản ghi',
            'prevalence_raw': 'Chưa có dữ liệu',
            'prevalence_num': None,
            'plhiv_raw': 'Chưa có dữ liệu',
            'plhiv_num': None,
            'deaths_raw': 'Chưa có dữ liệu',
            'deaths_num': None,
            'year_raw': 'Chưa rõ'
        }
    return {
        'has_data': True,
        'country_raw': h['raw_country'],
        'prevalence_raw': h['prevalence_raw'] if h['prevalence_raw'] != '-' else 'Chưa có dữ liệu',
        'prevalence_num': h['prevalence_num'],
        'plhiv_raw': h['plhiv_raw'] if h['plhiv_raw'] != '-' else 'Chưa có dữ liệu',
        'plhiv_num': h['plhiv_num'],
        'deaths_raw': h['deaths_raw'] if h['deaths_raw'] != '-' else 'Chưa có dữ liệu',
        'deaths_num': h['deaths_num'],
        'year_raw': h['year_raw'] if h['year_raw'] != '-' else 'Chưa rõ'
    }

def make_t2(a):
    if not a:
        return {
            'has_data': False,
            'region': 'Chưa phân vùng',
            'art_count_raw': 'Chưa có dữ liệu',
            'art_count_num': None,
            'plhiv_est_raw': 'Chưa có dữ liệu',
            'plhiv_median': None,
            'plhiv_min': None,
            'plhiv_max': None,
            'art_cov_raw': 'Chưa có dữ liệu',
            'art_cov_median': None,
            'art_cov_min': None,
            'art_cov_max': None
        }
    return {
        'has_data': True,
        'region': a['region'],
        'art_count_raw': a['art_count_raw'] if a['art_count_raw'].lower() not in ['nodata', ''] else 'Chưa có dữ liệu',
        'art_count_num': a['art_count_num'],
        'plhiv_est_raw': a['plhiv_est_raw'] if a['plhiv_est_raw'].lower() not in ['nodata', ''] else 'Chưa có dữ liệu',
        'plhiv_median': a['plhiv_median'],
        'plhiv_min': a['plhiv_min'],
        'plhiv_max': a['plhiv_max'],
        'art_cov_raw': a['art_cov_raw'] if a['art_cov_raw'].lower() not in ['nodata', ''] else 'Chưa có dữ liệu',
        'art_cov_median': a['art_cov_median'],
        'art_cov_min': a['art_cov_min'],
        'art_cov_max': a['art_cov_max']
    }

def make_kpi(t1, t2):
    plhiv = t1.get('plhiv_num') or t2.get('plhiv_median')
    plhiv_str = f"{int(plhiv):,}" if plhiv else "Chưa có dữ liệu"

    prev = t1.get('prevalence_num')
    prev_str = f"{prev:.2f}%" if prev is not None else (t1.get('prevalence_raw') if t1.get('prevalence_raw') != 'Chưa có dữ liệu' else "Chưa có dữ liệu")

    deaths = t1.get('deaths_num')
    deaths_str = f"{int(deaths):,} ca/năm" if deaths else "Chưa có dữ liệu"

    art_cov = t2.get('art_cov_median')
    art_cov_str = f"{art_cov:.1f}%" if art_cov is not None else "Chưa có dữ liệu"

    art_count = t2.get('art_count_num')
    art_count_str = f"{int(art_count):,} người" if art_count else "Chưa có dữ liệu"

    return {
        'plhiv_val': plhiv,
        'plhiv_display': plhiv_str,
        'prevalence_val': prev,
        'prevalence_display': prev_str,
        'deaths_val': deaths,
        'deaths_display': deaths_str,
        'art_cov_val': art_cov,
        'art_cov_display': art_cov_str,
        'art_count_val': art_count,
        'art_count_display': art_count_str
    }

def make_ml(kpi):
    plhiv = kpi.get('plhiv_val')
    actual_deaths = kpi.get('deaths_val')
    if plhiv and plhiv > 0:
        pred_log = 0.685 * math.log10(plhiv) + 0.150
        pred_deaths = round(10 ** pred_log)
        
        diff_str = "—"
        if actual_deaths:
            diff = actual_deaths - pred_deaths
            diff_pct = (diff / actual_deaths) * 100
            diff_str = f"{diff:+,} ca ({diff_pct:+.1f}%)"

        return {
            'has_pred': True,
            'pred_deaths': pred_deaths,
            'pred_deaths_display': f"{pred_deaths:,} ca",
            'actual_deaths': actual_deaths,
            'actual_deaths_display': f"{actual_deaths:,} ca" if actual_deaths else "Chưa có báo cáo",
            'diff_display': diff_str,
            'formula': "log₁₀(Deaths) = 0.685 × log₁₀(PLHIV) + 0.150"
        }
    return {
        'has_pred': False,
        'pred_deaths': None,
        'pred_deaths_display': "Không đủ dữ liệu PLHIV",
        'actual_deaths': actual_deaths,
        'actual_deaths_display': f"{actual_deaths:,} ca" if actual_deaths else "Chưa có báo cáo",
        'diff_display': "—",
        'formula': "Cần số ca PLHIV > 0"
    }

DATA_CACHE = load_all_data()

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Hệ Thống Giám Sát Dịch Tễ HIV/AIDS Toàn Cầu • DH23TIN07</title>
  <script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
  <style>
    :root {
      --bg-body: #f8fafc;
      --bg-surface: #ffffff;
      --bg-subtle: #f1f5f9;
      --border-color: #e2e8f0;
      --border-dark: #cbd5e1;
      --text-primary: #0f172a;
      --text-secondary: #475569;
      --text-muted: #64748b;
      --primary-red: #dc2626;
      --primary-red-hover: #b91c1c;
      --primary-red-light: #fef2f2;
      --primary-red-border: #fecaca;
      --accent-green: #059669;
      --accent-green-light: #ecfdf5;
      --accent-amber: #d97706;
      --accent-blue: #2563eb;
      --shadow-sm: 0 1px 3px rgba(0,0,0,0.06);
      --shadow-md: 0 4px 14px rgba(0,0,0,0.06);
      --shadow-lg: 0 10px 25px rgba(0,0,0,0.08);
      --radius-sm: 6px;
      --radius-md: 10px;
      --radius-lg: 14px;
    }

    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    }

    html, body {
      height: 100%;
      width: 100%;
      overflow: hidden;
      background-color: var(--bg-body);
      color: var(--text-primary);
    }

    /* TOP CLINICAL HEADER BAR */
    .top-navbar {
      height: 52px;
      background: var(--bg-surface);
      border-bottom: 1px solid var(--border-color);
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 20px;
      z-index: 40;
      position: relative;
    }

    .brand-title {
      display: flex;
      align-items: center;
      gap: 10px;
    }

    .brand-icon {
      width: 28px;
      height: 28px;
      background: var(--primary-red);
      color: #fff;
      border-radius: 6px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 800;
      font-size: 1.1rem;
      box-shadow: 0 2px 6px rgba(220, 38, 38, 0.3);
    }

    .brand-text h1 {
      font-size: 0.95rem;
      font-weight: 700;
      color: var(--text-primary);
      letter-spacing: -0.2px;
      line-height: 1.2;
    }

    .brand-text span {
      font-size: 0.72rem;
      color: var(--text-muted);
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }

    .header-kpi-summary {
      display: flex;
      align-items: center;
      gap: 20px;
    }

    .kpi-chip {
      display: flex;
      align-items: center;
      gap: 6px;
      font-size: 0.78rem;
      color: var(--text-secondary);
      background: var(--bg-subtle);
      padding: 4px 12px;
      border-radius: 20px;
      border: 1px solid var(--border-color);
    }

    .kpi-chip strong {
      color: var(--primary-red);
      font-weight: 700;
    }

    /* MAIN SPLIT-SCREEN LAYOUT */
    .app-layout {
      display: flex;
      height: calc(100vh - 52px);
      width: 100vw;
      position: relative;
    }

    /* MAP CONTAINER (LEFT SIDE - 63%) */
    .map-container {
      flex: 1;
      height: 100%;
      position: relative;
      background: #f8fafc;
    }

    #world-map-plot {
      width: 100%;
      height: 100%;
    }

    /* FLOATING SEARCH & CONTROLS (MEDICAL WHITE CARD STYLE) */
    .floating-search-bar {
      position: absolute;
      top: 16px;
      left: 16px;
      z-index: 20;
      display: flex;
      flex-direction: column;
      gap: 8px;
      width: 380px;
      max-width: calc(100vw - 32px);
    }

    .search-input-wrapper {
      background: var(--bg-surface);
      border: 1px solid var(--border-color);
      border-radius: 24px;
      box-shadow: var(--shadow-md);
      display: flex;
      align-items: center;
      padding: 6px 16px;
      transition: all 0.2s ease;
    }

    .search-input-wrapper:focus-within {
      border-color: var(--primary-red);
      box-shadow: 0 0 0 3px rgba(220, 38, 38, 0.12), var(--shadow-md);
    }

    .search-input-wrapper .icon {
      font-size: 0.95rem;
      color: var(--primary-red);
      margin-right: 10px;
    }

    .search-input-wrapper input {
      background: transparent;
      border: none;
      outline: none;
      color: var(--text-primary);
      font-size: 0.88rem;
      width: 100%;
      font-weight: 500;
    }

    .search-input-wrapper input::placeholder {
      color: var(--text-muted);
    }

    .search-suggestions {
      background: var(--bg-surface);
      border: 1px solid var(--border-color);
      border-radius: 12px;
      max-height: 240px;
      overflow-y: auto;
      box-shadow: var(--shadow-lg);
      display: none;
    }

    .suggestion-item {
      padding: 10px 16px;
      font-size: 0.85rem;
      cursor: pointer;
      border-bottom: 1px solid var(--border-color);
      transition: background 0.15s;
      color: var(--text-secondary);
    }

    .suggestion-item:hover {
      background: var(--primary-red-light);
      color: var(--primary-red);
      font-weight: 600;
    }

    /* QUICK PILLS UNDER SEARCH */
    .quick-country-pills {
      display: flex;
      gap: 6px;
      overflow-x: auto;
      padding-bottom: 4px;
    }

    .quick-country-pills::-webkit-scrollbar {
      display: none;
    }

    .map-pill {
      background: rgba(255, 255, 255, 0.92);
      border: 1px solid var(--border-color);
      color: var(--text-secondary);
      padding: 4px 10px;
      border-radius: 16px;
      font-size: 0.74rem;
      font-weight: 600;
      white-space: nowrap;
      cursor: pointer;
      box-shadow: var(--shadow-sm);
      transition: all 0.15s ease;
    }

    .map-pill:hover {
      background: var(--primary-red);
      color: #fff;
      border-color: var(--primary-red);
      transform: translateY(-1px);
    }

    /* FLOATING MAP MODE SELECTOR */
    .floating-map-controls {
      position: absolute;
      top: 16px;
      right: 16px;
      z-index: 20;
      display: flex;
      gap: 4px;
      background: rgba(255, 255, 255, 0.95);
      padding: 4px;
      border-radius: 8px;
      border: 1px solid var(--border-color);
      box-shadow: var(--shadow-md);
    }

    .map-mode-btn {
      background: transparent;
      border: none;
      color: var(--text-secondary);
      padding: 6px 12px;
      border-radius: 6px;
      font-size: 0.76rem;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.2s;
    }

    .map-mode-btn.active {
      background: var(--primary-red);
      color: #fff;
    }

    /* FLOATING ZOOM & RESET BUTTONS */
    .floating-zoom-buttons {
      position: absolute;
      bottom: 24px;
      left: 16px;
      z-index: 20;
      display: flex;
      flex-direction: column;
      gap: 6px;
    }

    .zoom-btn {
      width: 36px;
      height: 36px;
      background: var(--bg-surface);
      border: 1px solid var(--border-color);
      border-radius: 8px;
      color: var(--text-primary);
      font-size: 1.1rem;
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      box-shadow: var(--shadow-md);
      transition: all 0.15s ease;
    }

    .zoom-btn:hover {
      background: var(--primary-red-light);
      border-color: var(--primary-red-border);
      color: var(--primary-red);
    }

    /* SIDE PANEL (RIGHT SIDE - 37%) */
    .side-panel {
      width: 480px;
      max-width: 42vw;
      height: 100%;
      background: var(--bg-surface);
      border-left: 1px solid var(--border-color);
      display: flex;
      flex-direction: column;
      box-shadow: -4px 0 25px rgba(0, 0, 0, 0.05);
      z-index: 30;
      position: relative;
    }

    /* CLINICAL TOP ACCENT BAR */
    .panel-header {
      padding: 16px 20px 12px;
      background: var(--bg-surface);
      border-top: 4px solid var(--primary-red);
      border-bottom: 1px solid var(--border-color);
    }

    .panel-top-row {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      margin-bottom: 6px;
    }

    .country-header-title {
      display: flex;
      align-items: center;
      gap: 12px;
    }

    .country-header-title .flag {
      font-size: 2rem;
      line-height: 1;
    }

    .country-header-title h2 {
      font-size: 1.45rem;
      font-weight: 800;
      color: var(--text-primary);
      letter-spacing: -0.3px;
    }

    .badges-row {
      display: flex;
      gap: 6px;
      margin-top: 4px;
    }

    .badge {
      background: var(--primary-red-light);
      color: var(--primary-red);
      border: 1px solid var(--primary-red-border);
      padding: 3px 8px;
      border-radius: 4px;
      font-size: 0.72rem;
      font-weight: 700;
    }

    .badge.region {
      background: var(--bg-subtle);
      color: var(--text-secondary);
      border-color: var(--border-color);
    }

    /* 4 TABS NAVIGATION */
    .tabs-nav {
      display: flex;
      background: var(--bg-surface);
      border-bottom: 1px solid var(--border-color);
      padding: 0 8px;
      position: relative;
    }

    .tab-btn {
      flex: 1;
      padding: 12px 4px;
      background: transparent;
      border: none;
      color: var(--text-muted);
      font-size: 0.78rem;
      font-weight: 600;
      cursor: pointer;
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 4px;
      position: relative;
      transition: all 0.2s ease;
    }

    .tab-btn:hover {
      color: var(--primary-red);
    }

    .tab-btn.active {
      color: var(--primary-red);
      font-weight: 700;
    }

    .tab-btn .tab-icon {
      font-size: 1rem;
    }

    /* RED SLIDING INDICATOR */
    .tab-indicator {
      position: absolute;
      bottom: 0;
      height: 3px;
      background: var(--primary-red);
      border-radius: 3px 3px 0 0;
      transition: all 0.28s cubic-bezier(0.2, 0.8, 0.2, 1);
    }

    /* PANEL BODY (SCROLLABLE) */
    .panel-body {
      flex: 1;
      overflow-y: auto;
      padding: 18px 20px;
      background: #fbfcfd;
    }

    .panel-body::-webkit-scrollbar {
      width: 5px;
    }
    .panel-body::-webkit-scrollbar-thumb {
      background: #cbd5e1;
      border-radius: 4px;
    }

    /* TAB CONTENT SECTIONS */
    .tab-section {
      display: none;
      animation: tabFadeIn 0.3s cubic-bezier(0.16, 1, 0.3, 1) forwards;
    }

    .tab-section.active {
      display: block;
    }

    @keyframes tabFadeIn {
      from {
        opacity: 0;
        transform: translateY(6px);
      }
      to {
        opacity: 1;
        transform: translateY(0);
      }
    }

    .section-head {
      margin-bottom: 14px;
    }

    .section-head h3 {
      font-size: 0.95rem;
      font-weight: 700;
      color: var(--text-primary);
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .section-head p {
      font-size: 0.76rem;
      color: var(--text-muted);
      margin-top: 2px;
    }

    /* DEDICATED CLINICAL CHART BOX */
    .chart-container-box {
      background: var(--bg-surface);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-md);
      padding: 16px;
      margin-bottom: 16px;
      box-shadow: var(--shadow-sm);
    }

    .chart-title {
      font-size: 0.82rem;
      font-weight: 700;
      color: var(--primary-red);
      margin-bottom: 10px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .chart-badge {
      font-size: 0.68rem;
      background: var(--bg-subtle);
      border: 1px solid var(--border-color);
      padding: 2px 6px;
      border-radius: 4px;
      color: var(--text-muted);
      font-weight: 500;
    }

    /* GAUGE PROGRESS BAR FOR UNAIDS 95% */
    .gauge-wrapper {
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 8px 0;
    }

    .circle-progress-svg {
      width: 124px;
      height: 124px;
      transform: rotate(-90deg);
    }

    .circle-bg {
      fill: none;
      stroke: var(--bg-subtle);
      stroke-width: 9;
    }

    .circle-fill {
      fill: none;
      stroke: var(--primary-red);
      stroke-width: 9;
      stroke-linecap: round;
      stroke-dasharray: 345;
      stroke-dashoffset: 345;
      transition: stroke-dashoffset 1s cubic-bezier(0.16, 1, 0.3, 1);
    }

    .gauge-center-text {
      position: absolute;
      text-align: center;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
    }

    .gauge-center-text .pct {
      font-size: 1.55rem;
      font-weight: 800;
      color: var(--text-primary);
    }

    .gauge-center-text .sub {
      font-size: 0.68rem;
      color: var(--text-muted);
      font-weight: 600;
    }

    /* MINI KPI GRID */
    .kpi-mini-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 10px;
      margin-bottom: 16px;
    }

    .kpi-item {
      background: var(--bg-surface);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-sm);
      padding: 12px;
      box-shadow: var(--shadow-sm);
    }

    .kpi-item.accent-red { border-left: 3px solid var(--primary-red); }
    .kpi-item.accent-dark-red { border-left: 3px solid #991b1b; }
    .kpi-item.accent-green { border-left: 3px solid var(--accent-green); }
    .kpi-item.accent-slate { border-left: 3px solid var(--text-secondary); }

    .kpi-item .lbl {
      font-size: 0.68rem;
      color: var(--text-muted);
      text-transform: uppercase;
      font-weight: 700;
      letter-spacing: 0.4px;
    }

    .kpi-item .val {
      font-size: 1.25rem;
      font-weight: 800;
      color: var(--text-primary);
      margin-top: 4px;
    }

    /* STYLED MEDICAL DATA TABLES */
    .info-table {
      width: 100%;
      border-collapse: collapse;
      background: var(--bg-surface);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-sm);
      overflow: hidden;
      font-size: 0.82rem;
      margin-bottom: 14px;
      box-shadow: var(--shadow-sm);
    }

    .info-table th, .info-table td {
      padding: 9px 12px;
      border-bottom: 1px solid var(--border-color);
      text-align: left;
    }

    .info-table th {
      color: var(--text-secondary);
      font-weight: 600;
      background: #f8fafc;
      width: 48%;
    }

    .info-table td {
      color: var(--text-primary);
      font-weight: 600;
    }

    .info-table tr:last-child th,
    .info-table tr:last-child td {
      border-bottom: none;
    }

    .highlight-red {
      color: var(--primary-red) !important;
      font-weight: 700 !important;
    }

    /* COMPARISON BARS IN TAB 2 */
    .comp-bar-row {
      margin-bottom: 12px;
    }

    .comp-bar-label {
      display: flex;
      justify-content: space-between;
      font-size: 0.76rem;
      margin-bottom: 4px;
      color: var(--text-secondary);
    }

    .comp-bar-track {
      height: 9px;
      background: var(--bg-subtle);
      border-radius: 5px;
      overflow: hidden;
      position: relative;
      border: 1px solid #e2e8f0;
    }

    .comp-bar-fill {
      height: 100%;
      border-radius: 5px;
      transition: width 0.8s cubic-bezier(0.16, 1, 0.3, 1);
    }

    /* ML COMPARISON CARDS IN TAB 4 */
    .ml-compare-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 10px;
      margin-bottom: 12px;
    }

    .ml-card {
      background: var(--bg-surface);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-sm);
      padding: 12px;
      text-align: center;
      box-shadow: var(--shadow-sm);
    }

    .ml-card.highlight {
      border: 1.5px solid var(--primary-red);
      background: var(--primary-red-light);
    }

    .ml-card .tag {
      font-size: 0.7rem;
      color: var(--text-muted);
      text-transform: uppercase;
      font-weight: 600;
    }

    .ml-card .number {
      font-size: 1.3rem;
      font-weight: 800;
      color: var(--text-primary);
      margin-top: 4px;
    }

    .formula-banner {
      background: var(--primary-red-light);
      border: 1px solid var(--primary-red-border);
      border-radius: var(--radius-sm);
      padding: 10px 12px;
      font-size: 0.74rem;
      color: #991b1b;
      font-family: SFMono-Regular, Consolas, "Liberation Mono", Menlo, monospace;
      margin-bottom: 14px;
      line-height: 1.4;
    }

    @media (max-width: 900px) {
      .app-layout {
        flex-direction: column;
      }
      .side-panel {
        width: 100%;
        max-width: 100%;
        height: 50vh;
      }
      .map-container {
        height: 50vh;
      }
    }
  </style>
</head>
<body>

  <!-- TOP CLINICAL NAVBAR -->
  <header class="top-navbar">
    <div class="brand-title">
      <div class="brand-icon">✚</div>
      <div class="brand-text">
        <h1>HỆ THỐNG GIÁM SÁT DỊCH TỄ HIV/AIDS TOÀN CẦU</h1>
        <span>ĐỒ ÁN LẬP TRÌNH PYTHON • LỚP DH23TIN07</span>
      </div>
    </div>
    <div class="header-kpi-summary">
      <div class="kpi-chip">
        <span>Tổng khảo sát:</span>
        <strong id="top-countries">204 quốc gia</strong>
      </div>
      <div class="kpi-chip">
        <span>Tổng PLHIV:</span>
        <strong id="top-plhiv">~38.000.000+</strong>
      </div>
      <div class="kpi-chip">
        <span>Tử vong/năm:</span>
        <strong id="top-deaths">~630.000+ ca</strong>
      </div>
    </div>
  </header>

  <div class="app-layout">

    <!-- MAP CONTAINER (LEFT SIDE - FULL CENTERED GLOBE) -->
    <div class="map-container">
      
      <!-- FLOATING SEARCH BAR -->
      <div class="floating-search-bar">
        <div class="search-input-wrapper">
          <span class="icon">🔍</span>
          <input type="text" id="map-search" placeholder="Tìm quốc gia (VD: Vietnam, South Africa, Thailand, France...)">
        </div>
        <div class="search-suggestions" id="suggestions-box"></div>

        <!-- QUICK SELECT PILLS -->
        <div class="quick-country-pills">
          <button class="map-pill" onclick="selectCountry('Vietnam')">🇻🇳 Việt Nam</button>
          <button class="map-pill" onclick="selectCountry('South Africa')">🇿🇦 Nam Phi</button>
          <button class="map-pill" onclick="selectCountry('Thailand')">🇹🇭 Thái Lan</button>
          <button class="map-pill" onclick="selectCountry('Eswatini')">🇸🇿 Eswatini</button>
          <button class="map-pill" onclick="selectCountry('United States')">🇺🇸 Hoa Kỳ</button>
          <button class="map-pill" onclick="selectCountry('France')">🇫🇷 Pháp</button>
          <button class="map-pill" onclick="selectCountry('Kenya')">🇰🇪 Kenya</button>
          <button class="map-pill" onclick="selectCountry('India')">🇮🇳 Ấn Độ</button>
        </div>
      </div>

      <!-- FLOATING MAP CONTROLS -->
      <div class="floating-map-controls">
        <button class="map-mode-btn active" id="btn-mode-prev" onclick="setMapMode('prevalence')">🔴 Tỷ lệ HIV (%)</button>
        <button class="map-mode-btn" id="btn-mode-cov" onclick="setMapMode('art_cov')">🟢 Bao phủ ART (%)</button>
        <button class="map-mode-btn" id="btn-mode-plhiv" onclick="setMapMode('plhiv')">🩸 Số ca nhiễm</button>
      </div>

      <!-- FLOATING ZOOM CONTROLS -->
      <div class="floating-zoom-buttons">
        <button class="zoom-btn" title="Phóng to" onclick="zoomMap(1.4)">＋</button>
        <button class="zoom-btn" title="Thu nhỏ" onclick="zoomMap(0.7)">－</button>
        <button class="zoom-btn" title="Căn giữa toàn cầu (Reset View)" onclick="resetMapView()">⟲</button>
      </div>

      <!-- PLOTLY MAP CANVAS -->
      <div id="world-map-plot"></div>
    </div>

    <!-- SIDEBAR / INFO PANEL (RIGHT SIDE - 4 MEDICAL TABS) -->
    <div class="side-panel">
      
      <!-- CLINICAL PANEL HEADER -->
      <div class="panel-header">
        <div class="panel-top-row">
          <div class="country-header-title">
            <span class="flag" id="panel-flag">🇻🇳</span>
            <div>
              <h2 id="panel-country-name">Vietnam</h2>
              <div class="badges-row">
                <span class="badge" id="panel-iso">ISO: VNM</span>
                <span class="badge region" id="panel-region">Khu vực: Western Pacific</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 4 TABS NAVIGATION -->
      <div class="tabs-nav">
        <button class="tab-btn active" onclick="switchTab('tab-overview', 0)">
          <span class="tab-icon">📋</span>
          <span>Tổng quan</span>
        </button>
        <button class="tab-btn" onclick="switchTab('tab-table1', 1)">
          <span class="tab-icon">📊</span>
          <span>Bảng 1: Dịch tễ</span>
        </button>
        <button class="tab-btn" onclick="switchTab('tab-table2', 2)">
          <span class="tab-icon">💊</span>
          <span>Bảng 2: Điều trị</span>
        </button>
        <button class="tab-btn" onclick="switchTab('tab-ml', 3)">
          <span class="tab-icon">🤖</span>
          <span>Dự báo ML</span>
        </button>
        <div class="tab-indicator" id="tab-indicator" style="left: 0%; width: 25%;"></div>
      </div>

      <!-- PANEL BODY (SCROLLABLE) -->
      <div class="panel-body">

        <!-- ========================================== -->
        <!-- MỤC 1: TỔNG QUAN (VỚI BIỂU ĐỒ GAUGE 95-95-95) -->
        <!-- ========================================== -->
        <div class="tab-section active" id="tab-overview">
          <div class="section-head">
            <h3>📋 Hồ Sơ Giám Sát Dịch Tễ</h3>
            <p>Tổng hợp chỉ số trọng yếu từ cơ sở dữ liệu UNAIDS & WHO</p>
          </div>

          <!-- BIỂU ĐỒ 1: DONUT GAUGE MỤC TIÊU 95% UNAIDS -->
          <div class="chart-container-box">
            <div class="chart-title">
              <span>🎯 Tiến Độ Bao Phủ ART (Mục Tiêu 95% UNAIDS)</span>
              <span class="chart-badge">Biểu đồ Donut Gauge</span>
            </div>
            <div class="gauge-wrapper" style="position: relative;">
              <svg class="circle-progress-svg" viewBox="0 0 120 120">
                <circle class="circle-bg" cx="60" cy="60" r="55"></circle>
                <circle class="circle-fill" id="gauge-fill-circle" cx="60" cy="60" r="55"></circle>
              </svg>
              <div class="gauge-center-text">
                <div class="pct" id="gauge-pct-text">0%</div>
                <div class="sub">Mục tiêu: 95%</div>
              </div>
            </div>
            <p style="text-align: center; font-size: 0.74rem; color: var(--text-muted); margin-top: 6px;" id="gauge-eval-text">
              Đang tính toán tiến độ điều trị theo chuẩn y tế quốc tế...
            </p>
          </div>

          <!-- MINI KPI GRID -->
          <div class="kpi-mini-grid">
            <div class="kpi-item accent-red">
              <div class="lbl">Số người nhiễm (PLHIV)</div>
              <div class="val" id="mini-plhiv">—</div>
            </div>
            <div class="kpi-item accent-dark-red">
              <div class="lbl">Tỷ lệ hiện nhiễm người lớn</div>
              <div class="val" id="mini-prev">—</div>
            </div>
            <div class="kpi-item accent-slate">
              <div class="lbl">Tử vong do AIDS hàng năm</div>
              <div class="val" id="mini-deaths">—</div>
            </div>
            <div class="kpi-item accent-green">
              <div class="lbl">Bao phủ điều trị ART</div>
              <div class="val" id="mini-cov">—</div>
            </div>
          </div>

          <!-- BẢNG TÓM TẮT NHANH -->
          <table class="info-table">
            <tbody>
              <tr>
                <th>Năm ước tính mới nhất</th>
                <td id="ov-year">—</td>
              </tr>
              <tr>
                <th>Số ca điều trị thực tế</th>
                <td id="ov-art-count" class="highlight-red">—</td>
              </tr>
              <tr>
                <th>Khu vực quản lý</th>
                <td id="ov-region">—</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- ========================================== -->
        <!-- MỤC 2: BẢNG 1 - DỊCH TỄ & BIỂU ĐỒ SO SÁNH -->
        <!-- ========================================== -->
        <div class="tab-section" id="tab-table1">
          <div class="section-head">
            <h3>📊 Bảng 1: Ước Tính Hiện Nhiễm & Tử Vong</h3>
            <p>Trích xuất từ: <code>HIV_AIDS prevalence estimates table.csv</code></p>
          </div>

          <!-- BIỂU ĐỒ 2: CỘT SO SÁNH TỶ LỆ HIV -->
          <div class="chart-container-box">
            <div class="chart-title">
              <span>📈 So Sánh Tỷ Lệ HIV (%) Với Khu Vực & Toàn Cầu</span>
              <span class="chart-badge">Biểu đồ Cột Ngang</span>
            </div>
            
            <div class="comp-bar-row">
              <div class="comp-bar-label">
                <span id="bar-lbl-country">Quốc gia được chọn</span>
                <span id="bar-val-country" style="color: var(--primary-red); font-weight: 700;">0.70%</span>
              </div>
              <div class="comp-bar-track">
                <div class="comp-bar-fill" id="bar-fill-country" style="width: 0%; background: var(--primary-red);"></div>
              </div>
            </div>

            <div class="comp-bar-row">
              <div class="comp-bar-label">
                <span id="bar-lbl-region">Trung bình khu vực WHO</span>
                <span id="bar-val-region" style="color: var(--accent-amber); font-weight: 700;">0.33%</span>
              </div>
              <div class="comp-bar-track">
                <div class="comp-bar-fill" id="bar-fill-region" style="width: 0%; background: var(--accent-amber);"></div>
              </div>
            </div>

            <div class="comp-bar-row">
              <div class="comp-bar-label">
                <span>Trung bình toàn cầu (Global Average)</span>
                <span id="bar-val-global" style="color: var(--text-secondary); font-weight: 700;">1.85%</span>
              </div>
              <div class="comp-bar-track">
                <div class="comp-bar-fill" id="bar-fill-global" style="width: 0%; background: #94a3b8;"></div>
              </div>
            </div>
          </div>

          <!-- BẢNG DỮ LIỆU GỐC BẢNG 1 -->
          <table class="info-table">
            <tbody>
              <tr>
                <th>Tên định danh trong bảng 1</th>
                <td id="t1-name">—</td>
              </tr>
              <tr>
                <th>Tỷ lệ hiện nhiễm người lớn</th>
                <td id="t1-prev-val" class="highlight-red">—</td>
              </tr>
              <tr>
                <th>Số người sống chung với HIV</th>
                <td id="t1-plhiv-val">—</td>
              </tr>
              <tr>
                <th>Số ca tử vong hằng năm</th>
                <td id="t1-deaths-val" style="color: #991b1b;">—</td>
              </tr>
              <tr>
                <th>Năm ước tính</th>
                <td id="t1-year-val">—</td>
              </tr>
              <tr>
                <th>Trạng thái dữ liệu</th>
                <td id="t1-status-val">—</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- ========================================== -->
        <!-- MỤC 3: BẢNG 2 - ĐIỀU TRỊ ART & BIỂU ĐỒ RANGE -->
        <!-- ========================================== -->
        <div class="tab-section" id="tab-table2">
          <div class="section-head">
            <h3>💊 Bảng 2: Tình Hình Điều Trị Thuốc Kháng Virus (ART)</h3>
            <p>Trích xuất từ: <code>art_coverage_by_country_clean.csv</code></p>
          </div>

          <!-- BIỂU ĐỒ 3: KHOẢNG BIẾN THIÊN [MIN – MEDIAN – MAX] -->
          <div class="chart-container-box">
            <div class="chart-title">
              <span>📊 Dải Ước Tính Độ Bao Phủ ART [Min – Max %]</span>
              <span class="chart-badge">Biểu đồ Biên Độ (Range)</span>
            </div>

            <div style="padding: 10px 0;">
              <div style="display: flex; justify-content: space-between; font-size: 0.78rem; color: var(--text-muted); margin-bottom: 6px;">
                <span id="range-lbl-min">Min: 0%</span>
                <span id="range-lbl-med" style="color: var(--primary-red); font-weight: 700;">Trung vị: 0%</span>
                <span id="range-lbl-max">Max: 0%</span>
              </div>
              <div style="height: 12px; background: var(--bg-subtle); border-radius: 6px; position: relative; border: 1px solid var(--border-color);">
                <div id="range-bar-span" style="position: absolute; height: 100%; background: rgba(220, 38, 38, 0.25); border-radius: 6px; left: 0%; width: 0%; transition: all 0.8s;"></div>
                <div id="range-point-med" style="position: absolute; width: 14px; height: 14px; background: var(--primary-red); border: 2px solid #fff; border-radius: 50%; top: -1px; left: 0%; transform: translateX(-50%); transition: all 0.8s; box-shadow: 0 1px 4px rgba(0,0,0,0.2);"></div>
              </div>
            </div>
            <p style="font-size: 0.72rem; color: var(--text-muted); margin-top: 6px;" id="range-expl-text">
              Dải ước tính bất định theo khuyến cáo của Tổ chức Y tế Thế giới (WHO).
            </p>
          </div>

          <!-- BẢNG DỮ LIỆU GỐC BẢNG 2 -->
          <table class="info-table">
            <tbody>
              <tr>
                <th>Khu vực WHO</th>
                <td id="t2-region-val">—</td>
              </tr>
              <tr>
                <th>Số người đang nhận ART</th>
                <td id="t2-art-val" class="highlight-red">—</td>
              </tr>
              <tr>
                <th>Ước tính PLHIV (Trung vị)</th>
                <td id="t2-plhiv-med">—</td>
              </tr>
              <tr>
                <th>Dải ước tính PLHIV [Min – Max]</th>
                <td id="t2-plhiv-span">—</td>
              </tr>
              <tr>
                <th>Tỷ lệ bao phủ ART (Trung vị %)</th>
                <td id="t2-cov-med" style="color: var(--primary-red);">—</td>
              </tr>
              <tr>
                <th>Dải bao phủ ART [Min – Max %]</th>
                <td id="t2-cov-span">—</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- ========================================== -->
        <!-- MỤC 4: MÔ HÌNH HỒI QUY ML DỰ BÁO (TASK T1) -->
        <!-- ========================================== -->
        <div class="tab-section" id="tab-ml">
          <div class="section-head">
            <h3>🤖 Mô Hình Hồi Quy Dự Báo Số Ca Tử Vong</h3>
            <p>Ứng dụng mô hình <b>Ridge Regression</b> tối ưu (Task T1, R² = 0.85)</p>
          </div>

          <div class="formula-banner">
            📐 <b>Phương trình hồi quy:</b> log₁₀(Deaths) = 0.685 × log₁₀(PLHIV) + 0.150<br>
            • Huấn luyện trên n = 67 quốc gia • R² thực nghiệm = 0.854 • CV R² = 0.696
          </div>

          <!-- BIỂU ĐỒ 4: ĐỐI CHIẾU CỘT THỰC TẾ VS DỰ BÁO -->
          <div class="chart-container-box">
            <div class="chart-title">
              <span>📊 Đối Chiếu Tử Vong: Thực Tế vs Dự Báo Ridge</span>
              <span class="chart-badge">Biểu đồ Cột Kép</span>
            </div>

            <div class="ml-compare-grid">
              <div class="ml-card">
                <div class="tag">Báo cáo thực tế</div>
                <div class="number" id="ml-actual-num">—</div>
              </div>
              <div class="ml-card highlight">
                <div class="tag" style="color: var(--primary-red);">Ridge dự báo</div>
                <div class="number" id="ml-pred-num" style="color: var(--primary-red);">—</div>
              </div>
            </div>

            <div style="background: var(--bg-subtle); border-radius: 6px; padding: 8px 12px; border: 1px solid var(--border-color);">
              <div style="display: flex; justify-content: space-between; font-size: 0.78rem;">
                <span style="color: var(--text-muted);">Sai lệch (Residual):</span>
                <span id="ml-diff-val" style="color: var(--primary-red); font-weight: 700;">—</span>
              </div>
            </div>
          </div>

          <!-- BẢNG PHÂN TÍCH ĐÁNH GIÁ -->
          <table class="info-table">
            <tbody>
              <tr>
                <th>Số ca nhiễm làm đầu vào (PLHIV)</th>
                <td id="ml-input-plhiv">—</td>
              </tr>
              <tr>
                <th>Số ca tử vong ước lượng</th>
                <td id="ml-res-pred" class="highlight-red">—</td>
              </tr>
              <tr>
                <th>Đánh giá dịch tễ</th>
                <td id="ml-res-eval" style="font-size: 0.74rem;">Phù hợp với tương quan quy mô bệnh nhân nhiễm HIV toàn cầu.</td>
              </tr>
            </tbody>
          </table>
        </div>

      </div>

    </div>

  </div>

  <!-- JAVASCRIPT ĐIỀU KHIỂN BẢN ĐỒ & TABS ANIMATION -->
  <script>
    let appData = null;
    let currentMapMode = 'prevalence';
    let currentSelectedCountry = 'Vietnam';
    // MẶC ĐỊNH BẢN ĐỒ Ở GIỮA TOÀN CẦU (CENTERED WORLD VIEW)
    const DEFAULT_CENTER = { lat: 18, lon: 10 };
    const DEFAULT_SCALE = 1.02;
    let currentZoomScale = DEFAULT_SCALE;
    let currentCenter = { ...DEFAULT_CENTER };

    document.addEventListener('DOMContentLoaded', function() {
      fetch('/api/data')
        .then(res => res.json())
        .then(data => {
          appData = data;
          initHeaderStats();
          initMap();
          initSearchAutocomplete();
          // Mặc định nạp dữ liệu Việt Nam trên bảng bên phải, nhưng bản đồ ở giữa toàn cầu!
          const defaultC = appData.countries.find(x => x.name.toLowerCase() === 'vietnam');
          if (defaultC) {
            updateRightPanel(defaultC);
            highlightSelectedCountryOnMap(defaultC.iso3);
          }
        })
        .catch(err => {
          console.error("Lỗi tải API:", err);
        });
    });

    function initHeaderStats() {
      if (!appData || !appData.global_stats) return;
      const g = appData.global_stats;
      document.getElementById('top-countries').innerText = g.total_countries + ' quốc gia';
      document.getElementById('top-plhiv').innerText = g.total_plhiv;
      document.getElementById('top-deaths').innerText = g.total_deaths + ' ca';
    }

    function switchTab(tabId, tabIndex) {
      document.querySelectorAll('.tab-btn').forEach((btn, idx) => {
        btn.classList.toggle('active', idx === tabIndex);
      });

      document.querySelectorAll('.tab-section').forEach(sec => {
        sec.classList.remove('active');
      });

      const target = document.getElementById(tabId);
      if (target) {
        target.classList.add('active');
      }

      const indicator = document.getElementById('tab-indicator');
      indicator.style.left = (tabIndex * 25) + '%';
    }

    function initMap() {
      renderPlotlyChoropleth();
    }

    function setMapMode(mode) {
      currentMapMode = mode;
      document.getElementById('btn-mode-prev').classList.toggle('active', mode === 'prevalence');
      document.getElementById('btn-mode-cov').classList.toggle('active', mode === 'art_cov');
      document.getElementById('btn-mode-plhiv').classList.toggle('active', mode === 'plhiv');
      renderPlotlyChoropleth();
    }

    // VẼ BẢN ĐỒ CHOROPLETH THEO PHONG CÁCH Y TẾ TRẮNG - ĐỎ
    function renderPlotlyChoropleth() {
      if (!appData) return;
      const m = appData.map_data;
      let zVals = m.prevalence;
      
      // BẢNG MÀU DỊCH TỄ HỌC Y TẾ (WHITE -> LIGHT ROSE -> MEDICAL RED -> DEEP BURGUNDY)
      let colorScale = [
        [0.0, '#ffffff'],
        [0.05, '#fee2e2'],
        [0.2, '#fca5a5'],
        [0.4, '#ef4444'],
        [0.7, '#dc2626'],
        [1.0, '#7f1d1d']
      ];
      let colorTitle = 'Tỷ lệ HIV (%)';

      if (currentMapMode === 'art_cov') {
        zVals = m.art_cov;
        // BẢNG MÀU ĐIỀU TRỊ ART Y TẾ
        colorScale = [
          [0.0, '#ffffff'],
          [0.2, '#fef3c7'],
          [0.5, '#a7f3d0'],
          [0.8, '#10b981'],
          [1.0, '#047857']
        ];
        colorTitle = 'Bao phủ ART (%)';
      } else if (currentMapMode === 'plhiv') {
        zVals = m.plhiv;
        colorScale = [
          [0.0, '#ffffff'],
          [0.1, '#ffe4e6'],
          [0.3, '#f43f5e'],
          [0.7, '#be123c'],
          [1.0, '#881337']
        ];
        colorTitle = 'Số ca nhiễm';
      }

      const traceBase = {
        type: 'choropleth',
        locations: m.iso3,
        z: zVals,
        text: m.hover_text,
        hoverinfo: 'text',
        colorscale: colorScale,
        autocolorscale: false,
        reversescale: false,
        marker: {
          line: { color: '#cbd5e1', width: 0.6 }
        },
        colorbar: {
          title: { text: colorTitle, font: { color: '#475569', size: 10, family: 'sans-serif' } },
          tickfont: { color: '#475569', size: 9 },
          len: 0.55,
          thickness: 10,
          x: 0.98,
          y: 0.5,
          bgcolor: 'rgba(255,255,255,0.85)',
          bordercolor: '#e2e8f0',
          borderwidth: 1
        }
      };

      const currCountry = appData.countries.find(x => x.name.toLowerCase() === currentSelectedCountry.toLowerCase());
      const selectedIso = currCountry ? currCountry.iso3 : 'VNM';

      // TRACE HIGHLIGHT CHO QUỐC GIA ĐANG CHỌN (VIỀN ĐỎ Y TẾ NỔI BẬT)
      const traceHighlight = {
        type: 'choropleth',
        locations: [selectedIso],
        z: [1],
        showscale: false,
        colorscale: [[0, '#dc2626'], [1, '#dc2626']],
        marker: {
          line: { color: '#991b1b', width: 2.2 }
        },
        hoverinfo: 'none'
      };

      const layout = {
        geo: {
          showframe: false,
          showcoastlines: true,
          coastlinecolor: '#94a3b8',
          showcountries: true,
          countrycolor: '#cbd5e1',
          showocean: true,
          oceancolor: '#f8fafc',
          showland: true,
          landcolor: '#ffffff',
          showlakes: true,
          lakecolor: '#f8fafc',
          projection: {
            type: 'natural earth',
            scale: currentZoomScale
          },
          center: currentCenter,
          bgcolor: '#f8fafc'
        },
        paper_bgcolor: '#f8fafc',
        plot_bgcolor: '#f8fafc',
        margin: { l: 0, r: 0, t: 0, b: 0 }
      };

      const config = {
        responsive: true,
        displayModeBar: false,
        scrollZoom: true
      };

      Plotly.newPlot('world-map-plot', [traceBase, traceHighlight], layout, config);

      const plotEl = document.getElementById('world-map-plot');
      plotEl.removeAllListeners && plotEl.removeAllListeners('plotly_click');
      plotEl.on('plotly_click', function(data) {
        if (data.points && data.points.length > 0) {
          const clickedIso = data.points[0].location;
          const found = appData.countries.find(c => c.iso3 === clickedIso);
          if (found) {
            selectCountry(found.name);
          }
        }
      });
    }

    function highlightSelectedCountryOnMap(iso) {
      if (!iso) return;
      try {
        Plotly.restyle('world-map-plot', {
          locations: [[iso]]
        }, [1]);
      } catch (e) {}
    }

    // CHỌN QUỐC GIA: BAY/ZOOM MƯỢT MÀ VÀ CẬP NHẬT BẢNG BÊN PHẢI
    function selectCountry(name) {
      if (!appData) return;
      const c = appData.countries.find(x => x.name.toLowerCase() === name.toLowerCase());
      if (!c) return;

      currentSelectedCountry = c.name;

      if (c.lat !== 0 || c.lon !== 0) {
        currentCenter = { lat: c.lat, lon: c.lon };
        currentZoomScale = 2.4;
      } else {
        currentCenter = { ...DEFAULT_CENTER };
        currentZoomScale = 1.6;
      }

      // Camera flight animation
      Plotly.animate('world-map-plot', {
        layout: {
          geo: {
            center: currentCenter,
            projection: { scale: currentZoomScale }
          }
        }
      }, {
        transition: { duration: 900, easing: 'cubic-in-out' },
        frame: { duration: 900 }
      });

      highlightSelectedCountryOnMap(c.iso3);
      updateRightPanel(c);
    }

    function updateRightPanel(c) {
      document.getElementById('panel-country-name').innerText = c.name;
      document.getElementById('panel-iso').innerText = `ISO: ${c.iso3 || 'N/A'}`;
      document.getElementById('panel-region').innerText = `Khu vực: ${c.region}`;

      const flags = {
        'Vietnam': '🇻🇳', 'South Africa': '🇿🇦', 'Thailand': '🇹🇭', 'Eswatini': '🇸🇿',
        'United States': '🇺🇸', 'France': '🇫🇷', 'Kenya': '🇰🇪', 'Botswana': '🇧🇼',
        'India': '🇮🇳', 'United Kingdom': '🇬🇧', 'Germany': '🇩🇪', 'Brazil': '🇧🇷',
        'Russian Federation': '🇷🇺', 'China': '🇨🇳', 'Japan': '🇯🇵', 'Australia': '🇦🇺'
      };
      document.getElementById('panel-flag').innerText = flags[c.name] || '🏳️';

      // --- MỤC 1: TỔNG QUAN ---
      document.getElementById('mini-plhiv').innerText = c.kpi.plhiv_display;
      document.getElementById('mini-prev').innerText = c.kpi.prevalence_display;
      document.getElementById('mini-deaths').innerText = c.kpi.deaths_display;
      document.getElementById('mini-cov').innerText = c.kpi.art_cov_display;

      document.getElementById('ov-year').innerText = c.table1.year_raw;
      document.getElementById('ov-art-count').innerText = c.kpi.art_count_display;
      document.getElementById('ov-region').innerText = c.region;

      // Donut Gauge Progress
      const covVal = c.kpi.art_cov_val || 0;
      const strokeMax = 345;
      const strokeOffset = strokeMax - (strokeMax * Math.min(covVal, 100) / 100);
      const circleFill = document.getElementById('gauge-fill-circle');
      circleFill.style.strokeDashoffset = strokeOffset;
      document.getElementById('gauge-pct-text').innerText = `${covVal}%`;

      if (covVal >= 90) {
        document.getElementById('gauge-eval-text').innerHTML = "🌟 <b>Đạt chuẩn xuất sắc:</b> Đã tiến sát mốc 95% của UNAIDS.";
      } else if (covVal >= 60) {
        document.getElementById('gauge-eval-text').innerHTML = "👍 <b>Tiến độ khả quan:</b> Đang trên lộ trình mở rộng điều trị.";
      } else if (covVal > 0) {
        document.getElementById('gauge-eval-text').innerHTML = "⚠️ <b>Cần can thiệp:</b> Cần tăng cường độ bao phủ thuốc kháng virus.";
      } else {
        document.getElementById('gauge-eval-text').innerText = "Chưa có đủ số liệu báo cáo độ bao phủ điều trị.";
      }

      // --- MỤC 2: BẢNG 1 (DỊCH TỄ & BIỂU ĐỒ SO SÁNH) ---
      const t1 = c.table1;
      document.getElementById('t1-name').innerText = t1.country_raw;
      document.getElementById('t1-prev-val').innerText = t1.prevalence_raw;
      document.getElementById('t1-plhiv-val').innerText = t1.plhiv_raw;
      document.getElementById('t1-deaths-val').innerText = t1.deaths_raw;
      document.getElementById('t1-year-val').innerText = t1.year_raw;
      document.getElementById('t1-status-val').innerText = t1.has_data ? "Đã ghi nhận trong báo cáo UNAIDS" : "Không có dữ liệu trong tệp";

      const countryPrev = c.kpi.prevalence_val || 0;
      const regAvg = (appData.region_averages[c.region] && appData.region_averages[c.region].avg_prev) || 1.0;
      const globAvg = appData.global_stats.avg_prev_num || 1.85;
      const maxPrevScale = Math.max(countryPrev, regAvg, globAvg, 5);

      document.getElementById('bar-lbl-country').innerText = `${c.name} (Quốc gia)`;
      document.getElementById('bar-val-country').innerText = `${countryPrev}%`;
      document.getElementById('bar-fill-country').style.width = Math.min((countryPrev / maxPrevScale) * 100, 100) + '%';

      document.getElementById('bar-lbl-region').innerText = `Khu vực ${c.region} (TB)`;
      document.getElementById('bar-val-region').innerText = `${regAvg}%`;
      document.getElementById('bar-fill-region').style.width = Math.min((regAvg / maxPrevScale) * 100, 100) + '%';

      document.getElementById('bar-val-global').innerText = `${globAvg}%`;
      document.getElementById('bar-fill-global').style.width = Math.min((globAvg / maxPrevScale) * 100, 100) + '%';

      // --- MỤC 3: BẢNG 2 (ĐIỀU TRỊ & BIỂU ĐỒ RANGE MIN-MAX) ---
      const t2 = c.table2;
      document.getElementById('t2-region-val').innerText = t2.region;
      document.getElementById('t2-art-val').innerText = t2.art_count_raw;
      document.getElementById('t2-plhiv-med').innerText = t2.plhiv_median ? t2.plhiv_median.toLocaleString() : t2.plhiv_est_raw;
      
      let plSpan = "—";
      if (t2.plhiv_min && t2.plhiv_max) {
        plSpan = `[${t2.plhiv_min.toLocaleString()} – ${t2.plhiv_max.toLocaleString()}]`;
      }
      document.getElementById('t2-plhiv-span').innerText = plSpan;

      document.getElementById('t2-cov-med').innerText = t2.art_cov_median ? `${t2.art_cov_median}%` : t2.art_cov_raw;
      
      let covSpan = "—";
      if (t2.art_cov_min && t2.art_cov_max) {
        covSpan = `[${t2.art_cov_min}% – ${t2.art_cov_max}%]`;
      }
      document.getElementById('t2-cov-span').innerText = covSpan;

      const minCov = t2.art_cov_min || covVal;
      const maxCov = t2.art_cov_max || covVal;
      document.getElementById('range-lbl-min').innerText = `Min: ${minCov}%`;
      document.getElementById('range-lbl-med').innerText = `Trung vị: ${covVal}%`;
      document.getElementById('range-lbl-max').innerText = `Max: ${maxCov}%`;

      const spanBar = document.getElementById('range-bar-span');
      const pointMed = document.getElementById('range-point-med');
      spanBar.style.left = Math.min(minCov, 100) + '%';
      spanBar.style.width = Math.max(Math.min(maxCov - minCov, 100), 2) + '%';
      pointMed.style.left = Math.min(covVal, 100) + '%';

      // --- MỤC 4: DỰ BÁO ML (RIDGE TASK T1) ---
      const ml = c.ml;
      document.getElementById('ml-input-plhiv').innerText = c.kpi.plhiv_display;
      document.getElementById('ml-actual-num').innerText = ml.actual_deaths_display;
      document.getElementById('ml-pred-num').innerText = ml.pred_deaths_display;
      document.getElementById('ml-res-pred').innerText = ml.pred_deaths_display;
      document.getElementById('ml-diff-val').innerText = ml.diff_display;
    }

    function initSearchAutocomplete() {
      const input = document.getElementById('map-search');
      const box = document.getElementById('suggestions-box');

      input.addEventListener('input', function() {
        const query = this.value.trim().toLowerCase();
        if (!query) {
          box.style.display = 'none';
          return;
        }

        const matches = appData.countries.filter(c => 
          c.name.toLowerCase().includes(query) || (c.iso3 && c.iso3.toLowerCase().includes(query))
        ).slice(0, 6);

        if (matches.length > 0) {
          box.innerHTML = '';
          matches.forEach(c => {
            const div = document.createElement('div');
            div.className = 'suggestion-item';
            div.innerText = `${c.name} (${c.iso3 || 'N/A'}) - ${c.region}`;
            div.onclick = function() {
              input.value = c.name;
              box.style.display = 'none';
              selectCountry(c.name);
            };
            box.appendChild(div);
          });
          box.style.display = 'block';
        } else {
          box.style.display = 'none';
        }
      });

      input.addEventListener('keydown', function(e) {
        if (e.key === 'Enter') {
          const query = this.value.trim().toLowerCase();
          const found = appData.countries.find(c => 
            c.name.toLowerCase().includes(query) || (c.iso3 && c.iso3.toLowerCase() === query)
          );
          if (found) {
            box.style.display = 'none';
            selectCountry(found.name);
          }
        }
      });

      document.addEventListener('click', function(e) {
        if (!e.target.closest('.floating-search-bar')) {
          box.style.display = 'none';
        }
      });
    }

    function zoomMap(factor) {
      currentZoomScale = Math.max(Math.min(currentZoomScale * factor, 6.0), 0.8);
      Plotly.relayout('world-map-plot', {
        'geo.projection.scale': currentZoomScale
      });
    }

    // CĂN GIỮA MẶC ĐỊNH TOÀN BỘ TRÁI ĐẤT
    function resetMapView() {
      currentZoomScale = DEFAULT_SCALE;
      currentCenter = { ...DEFAULT_CENTER };
      Plotly.animate('world-map-plot', {
        layout: {
          geo: {
            center: currentCenter,
            projection: { scale: currentZoomScale }
          }
        }
      }, {
        transition: { duration: 800, easing: 'cubic-in-out' },
        frame: { duration: 800 }
      });
    }
  </script>
</body>
</html>
"""

class HIVDashboardHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path in ['/', '/index.html']:
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(HTML_TEMPLATE.encode('utf-8'))
        elif path == '/api/data':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            payload = json.dumps(DATA_CACHE, ensure_ascii=False)
            self.wfile.write(payload.encode('utf-8'))
        elif path.startswith('/api/country/'):
            country_name = unquote(path[len('/api/country/'):]).lower()
            found = next((c for c in DATA_CACHE['countries'] if c['name'].lower() == country_name or c['key'] == country_name), None)
            if found:
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(json.dumps(found, ensure_ascii=False).encode('utf-8'))
            else:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b'{"error": "Not found"}')
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'404 Not Found')

    def log_message(self, format, *args):
        return

def run_server(port=8000, open_browser=True):
    server_address = ('127.0.0.1', port)
    try:
        httpd = HTTPServer(server_address, HIVDashboardHandler)
    except OSError:
        port = 8501
        server_address = ('127.0.0.1', port)
        httpd = HTTPServer(server_address, HIVDashboardHandler)

    url = f"http://127.0.0.1:{port}"
    print("=" * 70)
    print("🚀 HỆ THỐNG GIÁM SÁT DỊCH TỄ HIV/AIDS TOÀN CẦU (DH23TIN07)")
    print("=" * 70)
    print(f"👉 Server đang chạy tại: {url}")
    print(f"👉 Đang mở trình duyệt...")
    print("👉 Nhấn Ctrl + C để dừng server.")
    print("=" * 70)

    if open_browser:
        webbrowser.open(url)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nĐã dừng server.")
        httpd.server_close()

if __name__ == '__main__':
    run_server(port=8000, open_browser=True)
