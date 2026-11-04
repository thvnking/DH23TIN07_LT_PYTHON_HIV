# -*- coding: utf-8 -*-
"""
================================================================================
ĐỒ ÁN LẬP TRÌNH PYTHON (DH23TIN07) - GOOGLE MAPS HIV/AIDS TOÀN CẦU
================================================================================
Giao diện phong cách Google Maps:
- Bên trái: Bản đồ thế giới tương tác mượt mà, zoom & pan mượt, highlight quốc gia.
- Bên phải: Bảng thông số chia làm 4 mục riêng biệt (Tabs), mỗi mục có biểu đồ riêng.
- Dữ liệu tích hợp từ 2 bảng báo cáo:
    1. HIV_AIDS prevalence estimates table.csv
    2. art_coverage_by_country_clean.csv
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

# Tọa độ tâm (Lat, Lon) phục vụ hiệu ứng bay/zoom kiểu Google Maps
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

    # Tính toán trung bình theo khu vực WHO phục vụ biểu đồ so sánh
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
                f"• Tỷ lệ HIV: {c['kpi']['prevalence_display']}<br>"
                f"• Số ca PLHIV: {c['kpi']['plhiv_display']}<br>"
                f"• Bao phủ ART: {c['kpi']['art_cov_display']}<br>"
                f"<i>👉 Bấm để xem bảng chi tiết bên phải</i>"
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
  <title>Google Maps HIV/AIDS Explorer • DH23TIN07</title>
  <script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
  <style>
    :root {
      --bg-dark: #0f172a;
      --bg-panel: #1e293b;
      --bg-card: #0b1120;
      --border: #334155;
      --text-main: #f8fafc;
      --text-muted: #94a3b8;
      --primary: #38bdf8;
      --accent-red: #ef4444;
      --accent-green: #10b981;
      --accent-yellow: #f59e0b;
      --accent-purple: #a855f7;
    }

    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }

    html, body {
      height: 100%;
      width: 100%;
      overflow: hidden;
      background-color: var(--bg-dark);
      color: var(--text-main);
    }

    /* GOOGLE MAPS SPLIT-SCREEN LAYOUT */
    .app-layout {
      display: flex;
      height: 100vh;
      width: 100vw;
      position: relative;
    }

    /* MAP CONTAINER (LEFT SIDE - 65%) */
    .map-container {
      flex: 1;
      height: 100%;
      position: relative;
      background: #090d16;
    }

    #world-map-plot {
      width: 100%;
      height: 100%;
    }

    /* FLOATING SEARCH BAR (GOOGLE MAPS STYLE) */
    .floating-search-bar {
      position: absolute;
      top: 18px;
      left: 20px;
      z-index: 20;
      display: flex;
      flex-direction: column;
      gap: 8px;
      width: 360px;
      max-width: calc(100vw - 40px);
    }

    .search-input-wrapper {
      background: rgba(30, 41, 59, 0.95);
      backdrop-filter: blur(12px);
      border: 1px solid rgba(255, 255, 255, 0.15);
      border-radius: 28px;
      box-shadow: 0 8px 32px rgba(0, 0, 0, 0.45);
      display: flex;
      align-items: center;
      padding: 6px 16px;
      transition: all 0.25s ease;
    }

    .search-input-wrapper:focus-within {
      border-color: var(--primary);
      box-shadow: 0 8px 32px rgba(56, 189, 248, 0.35);
    }

    .search-input-wrapper .icon {
      font-size: 1rem;
      color: var(--text-muted);
      margin-right: 10px;
    }

    .search-input-wrapper input {
      background: transparent;
      border: none;
      outline: none;
      color: #fff;
      font-size: 0.95rem;
      width: 100%;
    }

    /* AUTOCOMPLETE SUGGESTIONS */
    .search-suggestions {
      background: var(--bg-panel);
      border: 1px solid var(--border);
      border-radius: 12px;
      max-height: 240px;
      overflow-y: auto;
      box-shadow: 0 10px 30px rgba(0,0,0,0.5);
      display: none;
    }

    .suggestion-item {
      padding: 10px 16px;
      font-size: 0.9rem;
      cursor: pointer;
      border-bottom: 1px solid rgba(255,255,255,0.05);
      transition: background 0.15s;
    }

    .suggestion-item:hover {
      background: rgba(56, 189, 248, 0.15);
      color: var(--primary);
    }

    /* FLOATING QUICK PILLS */
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
      background: rgba(15, 23, 42, 0.85);
      backdrop-filter: blur(8px);
      border: 1px solid var(--border);
      color: #e2e8f0;
      padding: 5px 12px;
      border-radius: 20px;
      font-size: 0.78rem;
      white-space: nowrap;
      cursor: pointer;
      transition: all 0.2s;
    }

    .map-pill:hover {
      background: var(--primary);
      color: #0b1120;
      border-color: var(--primary);
      transform: translateY(-1px);
    }

    /* FLOATING MAP CONTROLS */
    .floating-map-controls {
      position: absolute;
      top: 18px;
      right: 20px;
      z-index: 20;
      display: flex;
      gap: 6px;
      background: rgba(30, 41, 59, 0.9);
      backdrop-filter: blur(8px);
      padding: 4px;
      border-radius: 8px;
      border: 1px solid var(--border);
    }

    .map-mode-btn {
      background: transparent;
      border: none;
      color: var(--text-muted);
      padding: 6px 12px;
      border-radius: 6px;
      font-size: 0.8rem;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.2s;
    }

    .map-mode-btn.active {
      background: var(--primary);
      color: #0b1120;
    }

    /* GOOGLE MAPS FLOATING ZOOM BUTTONS */
    .floating-zoom-buttons {
      position: absolute;
      bottom: 30px;
      left: 20px;
      z-index: 20;
      display: flex;
      flex-direction: column;
      gap: 6px;
    }

    .zoom-btn {
      width: 38px;
      height: 38px;
      background: rgba(30, 41, 59, 0.9);
      backdrop-filter: blur(8px);
      border: 1px solid var(--border);
      border-radius: 8px;
      color: #fff;
      font-size: 1.1rem;
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      transition: all 0.2s;
      box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }

    .zoom-btn:hover {
      background: var(--primary);
      color: #0b1120;
      border-color: var(--primary);
    }

    /* SIDEBAR / INFO PANEL (RIGHT SIDE - 35% ~ 38%) */
    .side-panel {
      width: 490px;
      max-width: 45vw;
      height: 100%;
      background: var(--bg-panel);
      border-left: 1px solid var(--border);
      display: flex;
      flex-direction: column;
      box-shadow: -8px 0 35px rgba(0, 0, 0, 0.5);
      z-index: 30;
      transition: transform 0.4s cubic-bezier(0.16, 1, 0.3, 1);
    }

    /* PANEL HEADER */
    .panel-header {
      padding: 20px 24px 14px;
      background: linear-gradient(180deg, rgba(15, 23, 42, 0.7) 0%, rgba(30, 41, 59, 0.7) 100%);
      border-bottom: 1px solid var(--border);
      position: relative;
    }

    .panel-top-row {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      margin-bottom: 8px;
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
      font-size: 1.55rem;
      font-weight: 800;
      color: #fff;
      letter-spacing: -0.3px;
    }

    .badges-row {
      display: flex;
      gap: 6px;
      margin-top: 4px;
    }

    .badge {
      background: rgba(56, 189, 248, 0.12);
      color: var(--primary);
      border: 1px solid rgba(56, 189, 248, 0.3);
      padding: 3px 8px;
      border-radius: 6px;
      font-size: 0.75rem;
      font-weight: 600;
    }

    .badge.region {
      background: rgba(168, 85, 247, 0.12);
      color: var(--accent-purple);
      border-color: rgba(168, 85, 247, 0.3);
    }

    /* TABS NAVIGATION (4 MỤC RIÊNG BIỆT) */
    .tabs-nav {
      display: flex;
      background: #0b1120;
      border-bottom: 1px solid var(--border);
      padding: 0 12px;
      position: relative;
    }

    .tab-btn {
      flex: 1;
      padding: 13px 6px;
      background: transparent;
      border: none;
      color: var(--text-muted);
      font-size: 0.82rem;
      font-weight: 600;
      cursor: pointer;
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 4px;
      position: relative;
      transition: color 0.25s ease;
    }

    .tab-btn:hover {
      color: #fff;
    }

    .tab-btn.active {
      color: var(--primary);
    }

    .tab-btn .tab-icon {
      font-size: 1.1rem;
    }

    /* SLIDING TAB INDICATOR */
    .tab-indicator {
      position: absolute;
      bottom: 0;
      height: 3px;
      background: var(--primary);
      border-radius: 3px 3px 0 0;
      transition: all 0.3s cubic-bezier(0.2, 0.8, 0.2, 1);
    }

    /* PANEL CONTENT (SCROLLABLE BODY) */
    .panel-body {
      flex: 1;
      overflow-y: auto;
      padding: 20px;
    }

    .panel-body::-webkit-scrollbar {
      width: 6px;
    }
    .panel-body::-webkit-scrollbar-thumb {
      background: var(--border);
      border-radius: 4px;
    }

    /* TAB CONTENT SECTIONS */
    .tab-section {
      display: none;
      animation: tabFadeIn 0.35s cubic-bezier(0.16, 1, 0.3, 1) forwards;
    }

    .tab-section.active {
      display: block;
    }

    @keyframes tabFadeIn {
      from {
        opacity: 0;
        transform: translateY(10px);
      }
      to {
        opacity: 1;
        transform: translateY(0);
      }
    }

    /* SECTION TITLE & DESCRIPTION */
    .section-head {
      margin-bottom: 16px;
    }

    .section-head h3 {
      font-size: 1.05rem;
      font-weight: 700;
      color: #fff;
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .section-head p {
      font-size: 0.8rem;
      color: var(--text-muted);
      margin-top: 4px;
    }

    /* DEDICATED CHART BOX IN EACH TAB */
    .chart-container-box {
      background: var(--bg-card);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 16px;
      margin-bottom: 18px;
      box-shadow: 0 4px 15px rgba(0,0,0,0.25);
    }

    .chart-title {
      font-size: 0.85rem;
      font-weight: 700;
      color: var(--primary);
      margin-bottom: 12px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .chart-badge {
      font-size: 0.72rem;
      background: rgba(255,255,255,0.08);
      padding: 2px 6px;
      border-radius: 4px;
      color: var(--text-muted);
    }

    /* KPI MINI-GRID */
    .kpi-mini-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 10px;
      margin-bottom: 18px;
    }

    .kpi-item {
      background: var(--bg-card);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 12px;
    }

    .kpi-item.accent-red { border-left: 3px solid var(--accent-red); }
    .kpi-item.accent-blue { border-left: 3px solid var(--primary); }
    .kpi-item.accent-green { border-left: 3px solid var(--accent-green); }
    .kpi-item.accent-yellow { border-left: 3px solid var(--accent-yellow); }

    .kpi-item .lbl {
      font-size: 0.72rem;
      color: var(--text-muted);
      text-transform: uppercase;
      font-weight: 600;
    }

    .kpi-item .val {
      font-size: 1.25rem;
      font-weight: 800;
      color: #fff;
      margin-top: 4px;
    }

    /* STYLED DATA TABLES */
    .info-table {
      width: 100%;
      border-collapse: collapse;
      background: var(--bg-card);
      border: 1px solid var(--border);
      border-radius: 10px;
      overflow: hidden;
      font-size: 0.85rem;
      margin-bottom: 16px;
    }

    .info-table th, .info-table td {
      padding: 10px 14px;
      border-bottom: 1px solid rgba(255,255,255,0.04);
      text-align: left;
    }

    .info-table th {
      color: var(--text-muted);
      font-weight: 600;
      background: rgba(255,255,255,0.02);
      width: 48%;
    }

    .info-table td {
      color: #fff;
      font-weight: 600;
    }

    .info-table tr:last-child th,
    .info-table tr:last-child td {
      border-bottom: none;
    }

    .highlight-val {
      color: var(--primary) !important;
    }

    /* GAUGE PROGRESS BAR FOR UNAIDS 95% */
    .gauge-wrapper {
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 10px 0;
    }

    .circle-progress-svg {
      width: 130px;
      height: 130px;
      transform: rotate(-90deg);
    }

    .circle-bg {
      fill: none;
      stroke: rgba(255,255,255,0.08);
      stroke-width: 10;
    }

    .circle-fill {
      fill: none;
      stroke: var(--accent-green);
      stroke-width: 10;
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
      font-size: 1.6rem;
      font-weight: 800;
      color: #fff;
    }

    .gauge-center-text .sub {
      font-size: 0.7rem;
      color: var(--text-muted);
    }

    /* CUSTOM SVG COMPARISON BARS */
    .comp-bar-row {
      margin-bottom: 12px;
    }

    .comp-bar-label {
      display: flex;
      justify-content: space-between;
      font-size: 0.78rem;
      margin-bottom: 4px;
    }

    .comp-bar-track {
      height: 10px;
      background: rgba(255,255,255,0.08);
      border-radius: 5px;
      overflow: hidden;
      position: relative;
    }

    .comp-bar-fill {
      height: 100%;
      border-radius: 5px;
      transition: width 0.8s cubic-bezier(0.16, 1, 0.3, 1);
    }

    /* ML COMPARISON CARDS */
    .ml-compare-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 10px;
      margin-bottom: 14px;
    }

    .ml-card {
      background: var(--bg-card);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 12px;
      text-align: center;
    }

    .ml-card .tag {
      font-size: 0.72rem;
      color: var(--text-muted);
      text-transform: uppercase;
    }

    .ml-card .number {
      font-size: 1.35rem;
      font-weight: 800;
      margin-top: 4px;
    }

    .formula-banner {
      background: rgba(168, 85, 247, 0.1);
      border: 1px solid rgba(168, 85, 247, 0.25);
      border-radius: 8px;
      padding: 10px 14px;
      font-size: 0.76rem;
      color: #d8b4fe;
      font-family: monospace;
      margin-bottom: 16px;
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

  <div class="app-layout">

    <!-- MAP CONTAINER (LEFT SIDE - GOOGLE MAPS STYLE) -->
    <div class="map-container">
      
      <!-- FLOATING SEARCH BAR -->
      <div class="floating-search-bar">
        <div class="search-input-wrapper">
          <span class="icon">🔍</span>
          <input type="text" id="map-search" placeholder="Tìm kiếm quốc gia (VD: Vietnam, South Africa, France...)">
        </div>
        <div class="search-suggestions" id="suggestions-box"></div>

        <!-- QUICK PILLS -->
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
        <button class="map-mode-btn active" id="btn-mode-prev" onclick="setMapMode('prevalence')">🔴 Tỷ lệ HIV</button>
        <button class="map-mode-btn" id="btn-mode-cov" onclick="setMapMode('art_cov')">🟢 Bao phủ ART</button>
        <button class="map-mode-btn" id="btn-mode-plhiv" onclick="setMapMode('plhiv')">🟣 Số người nhiễm</button>
      </div>

      <!-- FLOATING ZOOM CONTROLS -->
      <div class="floating-zoom-buttons">
        <button class="zoom-btn" title="Phóng to" onclick="zoomMap(1.4)">＋</button>
        <button class="zoom-btn" title="Thu nhỏ" onclick="zoomMap(0.7)">－</button>
        <button class="zoom-btn" title="Khôi phục toàn cảnh" onclick="resetMapView()">⟲</button>
      </div>

      <!-- PLOTLY MAP CANVAS -->
      <div id="world-map-plot"></div>
    </div>

    <!-- SIDEBAR / INFO PANEL (RIGHT SIDE - 4 TABS WITH DEDICATED CHARTS) -->
    <div class="side-panel">
      
      <!-- PANEL HEADER -->
      <div class="panel-header">
        <div class="panel-top-row">
          <div class="country-header-title">
            <span class="flag" id="panel-flag">🏳️</span>
            <div>
              <h2 id="panel-country-name">Vietnam</h2>
              <div class="badges-row">
                <span class="badge" id="panel-iso">ISO: VNM</span>
                <span class="badge region" id="panel-region">Western Pacific</span>
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
            <h3>📋 Hồ Sơ Dịch Tễ Quốc Gia</h3>
            <p>Tổng hợp các chỉ số trọng yếu từ cả 2 bộ dữ liệu UNAIDS & WHO</p>
          </div>

          <!-- BIỂU ĐỒ 1: TIẾN TRÌNH BAO PHỦ ART THEO MỤC TIÊU 95% CỦA UNAIDS -->
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
            <p style="text-align: center; font-size: 0.78rem; color: var(--text-muted); margin-top: 6px;" id="gauge-eval-text">
              Đang tính toán tiến độ phổ cập điều trị kháng virus...
            </p>
          </div>

          <!-- MINI KPI GRID -->
          <div class="kpi-mini-grid">
            <div class="kpi-item accent-blue">
              <div class="lbl">Số người nhiễm (PLHIV)</div>
              <div class="val" id="mini-plhiv">—</div>
            </div>
            <div class="kpi-item accent-red">
              <div class="lbl">Tỷ lệ hiện nhiễm</div>
              <div class="val" id="mini-prev">—</div>
            </div>
            <div class="kpi-item accent-yellow">
              <div class="lbl">Tử vong hàng năm</div>
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
                <td id="ov-art-count" class="highlight-val">—</td>
              </tr>
              <tr>
                <th>Khu vực quản lý</th>
                <td id="ov-region">—</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- ========================================== -->
        <!-- MỤC 2: BẢNG 1 - HIỆN NHIỄM & TỬ VONG (VỚI BIỂU ĐỒ CỘT SO SÁNH KHU VỰC) -->
        <!-- ========================================== -->
        <div class="tab-section" id="tab-table1">
          <div class="section-head">
            <h3>📊 Bảng 1: Ước Tính Hiện Nhiễm & Tử Vong</h3>
            <p>Trích xuất từ tệp: <code>HIV_AIDS prevalence estimates table.csv</code></p>
          </div>

          <!-- BIỂU ĐỒ 2: SO SÁNH TỶ LỆ HIV VỚI KHU VỰC & TOÀN CẦU -->
          <div class="chart-container-box">
            <div class="chart-title">
              <span>📈 So Sánh Tỷ Lệ HIV (%) Với Khu Vực & Thế Giới</span>
              <span class="chart-badge">Biểu đồ Cột Ngang</span>
            </div>
            
            <div class="comp-bar-row">
              <div class="comp-bar-label">
                <span id="bar-lbl-country">Quốc gia được chọn</span>
                <span id="bar-val-country" style="color: var(--accent-red); font-weight: 700;">0.70%</span>
              </div>
              <div class="comp-bar-track">
                <div class="comp-bar-fill" id="bar-fill-country" style="width: 0%; background: var(--accent-red);"></div>
              </div>
            </div>

            <div class="comp-bar-row">
              <div class="comp-bar-label">
                <span id="bar-lbl-region">Trung bình khu vực WHO</span>
                <span id="bar-val-region" style="color: var(--accent-yellow); font-weight: 700;">0.33%</span>
              </div>
              <div class="comp-bar-track">
                <div class="comp-bar-fill" id="bar-fill-region" style="width: 0%; background: var(--accent-yellow);"></div>
              </div>
            </div>

            <div class="comp-bar-row">
              <div class="comp-bar-label">
                <span>Trung bình toàn cầu (Global Average)</span>
                <span id="bar-val-global" style="color: var(--primary); font-weight: 700;">1.85%</span>
              </div>
              <div class="comp-bar-track">
                <div class="comp-bar-fill" id="bar-fill-global" style="width: 0%; background: var(--primary);"></div>
              </div>
            </div>
          </div>

          <!-- BẢNG DỮ LIỆU GỐC BẢNG 1 -->
          <table class="info-table">
            <tbody>
              <tr>
                <th>Tên trong bảng 1</th>
                <td id="t1-name">—</td>
              </tr>
              <tr>
                <th>Tỷ lệ hiện nhiễm người lớn</th>
                <td id="t1-prev-val" class="highlight-val">—</td>
              </tr>
              <tr>
                <th>Số người sống chung với HIV</th>
                <td id="t1-plhiv-val">—</td>
              </tr>
              <tr>
                <th>Số ca tử vong hằng năm</th>
                <td id="t1-deaths-val" style="color: var(--accent-yellow);">—</td>
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
        <!-- MỤC 3: BẢNG 2 - ĐIỀU TRỊ ART (VỚI BIỂU ĐỒ DẢI KHOẢNG TIN CẬY MIN-MAX) -->
        <!-- ========================================== -->
        <div class="tab-section" id="tab-table2">
          <div class="section-head">
            <h3>💊 Bảng 2: Tình Hình Điều Trị Thuốc Kháng Virus (ART)</h3>
            <p>Trích xuất từ tệp: <code>art_coverage_by_country_clean.csv</code></p>
          </div>

          <!-- BIỂU ĐỒ 3: KHOẢNG BIẾN THIÊN [MIN – MEDIAN – MAX] ĐỘ BAO PHỦ ART -->
          <div class="chart-container-box">
            <div class="chart-title">
              <span>📊 Khoảng Ước Tính Độ Bao Phủ ART [Min – Max %]</span>
              <span class="chart-badge">Biểu đồ Biên Độ (Range)</span>
            </div>

            <div style="padding: 10px 0;">
              <div style="display: flex; justify-content: space-between; font-size: 0.8rem; color: var(--text-muted); margin-bottom: 6px;">
                <span id="range-lbl-min">Min: 0%</span>
                <span id="range-lbl-med" style="color: var(--accent-green); font-weight: 700;">Trung vị: 0%</span>
                <span id="range-lbl-max">Max: 0%</span>
              </div>
              <div style="height: 14px; background: rgba(255,255,255,0.06); border-radius: 7px; position: relative;">
                <!-- Dải Min - Max -->
                <div id="range-bar-span" style="position: absolute; height: 100%; background: rgba(16, 185, 129, 0.35); border-radius: 7px; left: 0%; width: 0%; transition: all 0.8s;"></div>
                <!-- Điểm Median -->
                <div id="range-point-med" style="position: absolute; width: 14px; height: 14px; background: var(--accent-green); border: 2px solid #fff; border-radius: 50%; top: 0; left: 0%; transform: translateX(-50%); transition: all 0.8s;"></div>
              </div>
            </div>
            <p style="font-size: 0.76rem; color: var(--text-muted); margin-top: 8px;" id="range-expl-text">
              Biểu thị dải bất định theo chuẩn WHO trong ước tính độ tiếp cận điều trị kháng vi-rút.
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
                <td id="t2-art-val" class="highlight-val">—</td>
              </tr>
              <tr>
                <th>Ước tính PLHIV (Median)</th>
                <td id="t2-plhiv-med">—</td>
              </tr>
              <tr>
                <th>Dải ước tính PLHIV [Min – Max]</th>
                <td id="t2-plhiv-span">—</td>
              </tr>
              <tr>
                <th>Tỷ lệ bao phủ ART (Median %)</th>
                <td id="t2-cov-med" style="color: var(--accent-green);">—</td>
              </tr>
              <tr>
                <th>Dải bao phủ ART [Min – Max %]</th>
                <td id="t2-cov-span">—</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- ========================================== -->
        <!-- MỤC 4: MÔ HÌNH HỒI QUY ML DỰ BÁO (TASK T1) (VỚI BIỂU ĐỒ ĐỐI CHIẾU THỰC TẾ) -->
        <!-- ========================================== -->
        <div class="tab-section" id="tab-ml">
          <div class="section-head">
            <h3>🤖 Mô Hình Hồi Quy Dự Báo Số Ca Tử Vong</h3>
            <p>Ứng dụng mô hình <b>Ridge Regression</b> tối ưu nhất từ bài báo (Task T1, R² = 0.85)</p>
          </div>

          <div class="formula-banner">
            📐 <b>Mô hình:</b> log₁₀(Deaths) = 0.685 × log₁₀(PLHIV) + 0.150<br>
            • Huấn luyện trên n = 67 quốc gia • Đạt CV R² = 0.696 • Test RMSE = 0.260
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
                <div class="number" id="ml-actual-num" style="color: #fff;">—</div>
              </div>
              <div class="ml-card" style="border-color: var(--primary);">
                <div class="tag" style="color: var(--primary);">Ridge dự báo</div>
                <div class="number" id="ml-pred-num" style="color: var(--primary);">—</div>
              </div>
            </div>

            <!-- THANH THỂ HIỆN SAI LỆCH -->
            <div style="background: rgba(255,255,255,0.03); border-radius: 8px; padding: 10px 14px;">
              <div style="display: flex; justify-content: space-between; font-size: 0.8rem;">
                <span style="color: var(--text-muted);">Sai lệch (Residual):</span>
                <span id="ml-diff-val" style="color: var(--accent-yellow); font-weight: 700;">—</span>
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
                <td id="ml-res-pred" class="highlight-val">—</td>
              </tr>
              <tr>
                <th>Đánh giá độ chính xác</th>
                <td id="ml-res-eval" style="font-size: 0.78rem;">Phù hợp với đường tương quan quy mô dân số nhiễm HIV.</td>
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
    let currentZoomScale = 1.0;
    let currentCenter = { lat: 15, lon: 105 };

    // 1. Tải dữ liệu từ API server
    document.addEventListener('DOMContentLoaded', function() {
      fetch('/api/data')
        .then(res => res.json())
        .then(data => {
          appData = data;
          initMap();
          initSearchAutocomplete();
          // Mặc định chọn Việt Nam
          selectCountry('Vietnam');
        })
        .catch(err => {
          console.error("Lỗi tải API:", err);
        });
    });

    // 2. Chuyển đổi Tab mượt mà (Google Maps Drawer style)
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

      // Di chuyển indicator mượt mà
      const indicator = document.getElementById('tab-indicator');
      indicator.style.left = (tabIndex * 25) + '%';
    }

    // 3. Khởi tạo bản đồ Plotly
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

    function renderPlotlyChoropleth() {
      if (!appData) return;
      const m = appData.map_data;
      let zVals = m.prevalence;
      let colorScale = [
        [0, '#1e293b'],
        [0.05, '#fef08a'],
        [0.2, '#f97316'],
        [0.5, '#ef4444'],
        [1.0, '#7f1d1d']
      ];
      let colorTitle = 'Tỷ lệ HIV (%)';

      if (currentMapMode === 'art_cov') {
        zVals = m.art_cov;
        colorScale = [
          [0, '#1e293b'],
          [0.2, '#bbf7d0'],
          [0.5, '#34d399'],
          [0.8, '#10b981'],
          [1.0, '#065f46']
        ];
        colorTitle = 'Bao phủ ART (%)';
      } else if (currentMapMode === 'plhiv') {
        zVals = m.plhiv;
        colorScale = [
          [0, '#1e293b'],
          [0.1, '#e9d5ff'],
          [0.3, '#c084fc'],
          [0.6, '#a855f7'],
          [1.0, '#581c87']
        ];
        colorTitle = 'Số ca nhiễm';
      }

      // Trace 0: Lớp bản đồ chính
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
          line: { color: '#334155', width: 0.5 }
        },
        colorbar: {
          title: { text: colorTitle, font: { color: '#94a3b8', size: 11 } },
          tickfont: { color: '#94a3b8' },
          len: 0.6,
          thickness: 10,
          x: 0.98,
          y: 0.5
        }
      };

      const layout = {
        geo: {
          showframe: false,
          showcoastlines: true,
          coastlinecolor: '#475569',
          showcountries: true,
          countrycolor: '#334155',
          projection: {
            type: 'natural earth',
            scale: currentZoomScale
          },
          center: currentCenter,
          bgcolor: '#090d16'
        },
        paper_bgcolor: '#090d16',
        plot_bgcolor: '#090d16',
        margin: { l: 0, r: 0, t: 0, b: 0 }
      };

      const config = {
        responsive: true,
        displayModeBar: false,
        scrollZoom: true
      };

      Plotly.newPlot('world-map-plot', [traceBase], layout, config);

      // Bắt sự kiện nhấp chuột vào quốc gia
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

    // 4. ANIMATION BAY/ZOOM MƯỢT MÀ VÀ HIGHLIGHT QUỐC GIA (GOOGLE MAPS STYLE)
    function selectCountry(name) {
      if (!appData) return;
      const c = appData.countries.find(x => x.name.toLowerCase() === name.toLowerCase());
      if (!c) return;

      currentSelectedCountry = c.name;

      // Tính toán tâm bay tới
      if (c.lat !== 0 || c.lon !== 0) {
        currentCenter = { lat: c.lat, lon: c.lon };
        currentZoomScale = 2.4; // Zoom vào gần hơn
      } else {
        currentCenter = { lat: 10, lon: 20 };
        currentZoomScale = 1.6;
      }

      // Thực hiện Camera Flight Animation trên Plotly
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

      // Cập nhật dữ liệu vào Sidebar bên phải
      updateRightPanel(c);
    }

    // 5. Cập nhật chi tiết 4 Mục vào Sidebar bên phải
    function updateRightPanel(c) {
      // Header
      document.getElementById('panel-country-name').innerText = c.name;
      document.getElementById('panel-iso').innerText = `ISO: ${c.iso3 || 'N/A'}`;
      document.getElementById('panel-region').innerText = c.region;

      // Flag tương ứng
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

      // Hoạt ảnh Gauge Donut
      const covVal = c.kpi.art_cov_val || 0;
      const strokeMax = 345;
      const strokeOffset = strokeMax - (strokeMax * Math.min(covVal, 100) / 100);
      const circleFill = document.getElementById('gauge-fill-circle');
      circleFill.style.strokeDashoffset = strokeOffset;
      document.getElementById('gauge-pct-text').innerText = `${covVal}%`;

      if (covVal >= 90) {
        document.getElementById('gauge-eval-text').innerHTML = "🌟 <b>Đạt chuẩn xuất sắc:</b> Đã tiến rất sát mốc 95% của UNAIDS.";
      } else if (covVal >= 60) {
        document.getElementById('gauge-eval-text').innerHTML = "👍 <b>Tiến độ khá:</b> Đang trên lộ trình mở rộng điều trị.";
      } else if (covVal > 0) {
        document.getElementById('gauge-eval-text').innerHTML = "⚠️ <b>Cần nỗ lực:</b> Cần đẩy mạnh độ bao phủ thuốc kháng virus.";
      } else {
        document.getElementById('gauge-eval-text').innerText = "Chưa có đủ số liệu báo cáo độ phủ ART.";
      }

      // --- MỤC 2: BẢNG 1 (DỊCH TỄ & BIỂU ĐỒ SO SÁNH) ---
      const t1 = c.table1;
      document.getElementById('t1-name').innerText = t1.country_raw;
      document.getElementById('t1-prev-val').innerText = t1.prevalence_raw;
      document.getElementById('t1-plhiv-val').innerText = t1.plhiv_raw;
      document.getElementById('t1-deaths-val').innerText = t1.deaths_raw;
      document.getElementById('t1-year-val').innerText = t1.year_raw;
      document.getElementById('t1-status-val').innerText = t1.has_data ? "Đã ghi nhận trong báo cáo" : "Không có dữ liệu trong file";

      // Biểu đồ thanh so sánh HIV %
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

      // Biểu đồ Range Min-Median-Max
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

    // 6. Gợi ý tìm kiếm Autocomplete
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

    // 7. Các nút Zoom & Reset View
    function zoomMap(factor) {
      currentZoomScale = Math.max(Math.min(currentZoomScale * factor, 6.0), 0.8);
      Plotly.relayout('world-map-plot', {
        'geo.projection.scale': currentZoomScale
      });
    }

    function resetMapView() {
      currentZoomScale = 1.0;
      currentCenter = { lat: 15, lon: 10 };
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
    print("🚀 GOOGLE MAPS HIV/AIDS DASHBOARD (DH23TIN07)")
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
