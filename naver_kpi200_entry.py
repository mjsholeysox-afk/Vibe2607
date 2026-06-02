import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from openpyxl import Workbook
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QMessageBox, QLabel, QLineEdit

BASE_URL = 'https://finance.naver.com'
ENTRY_URL = 'https://finance.naver.com/sise/entryJongmok.naver?type=KPI200'


def fetch_kpi200_entry_top(limit=None):
    """KPI200 편입종목상위 정보를 크롤링합니다.

    전체 페이지를 순회하면서 모든 편입종목상위 데이터를 수집합니다.
    limit가 지정된 경우 최대 limit개까지만 가져옵니다.
    HTML 구조:
    <div class="box_type_m">...
      <table class="type_1">...
        <tr>종목별 / 현재가 / 전일비 / 등락률 / 거래량 / 거래대금(백만) / 시가총액(억)</tr>
        <tr>...종목 데이터...</tr>
    """
    headers = {'User-Agent': 'Mozilla/5.0'}
    items = []
    page = 1

    while True:
        url = f'{ENTRY_URL}&page={page}'
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        rows = soup.select('table.type_1 tr')

        page_items = []
        for row in rows:
            cells = row.find_all('td')
            if len(cells) != 7:
                continue

            link = cells[0].find('a')
            stock_code = None
            stock_url = None
            if link and link.get('href'):
                stock_url = urljoin(BASE_URL, link['href'])
                if 'code=' in link['href']:
                    stock_code = link['href'].split('code=')[-1]

            item = {
                'name': cells[0].get_text(strip=True),
                'code': stock_code,
                'url': stock_url,
                'current_price': cells[1].get_text(strip=True),
                'change_amount': cells[2].get_text(strip=True),
                'change_rate': cells[3].get_text(strip=True),
                'volume': cells[4].get_text(strip=True),
                'trading_value': cells[5].get_text(strip=True),
                'market_sum': cells[6].get_text(strip=True),
            }
            page_items.append(item)
            if limit is not None and len(page_items) >= limit - len(items):
                break

        if not page_items:
            break

        items.extend(page_items)
        if limit is not None and len(items) >= limit:
            break

        page += 1

    return items


def save_items_to_excel(items, filename='kpi200_entry_top.xlsx'):
    wb = Workbook()
    ws = wb.active
    ws.title = 'KPI200 편입종목상위'

    headers = ['순번', '종목명', '종목코드', '현재가', '전일비', '등락률', '거래량', '거래대금(백만)', '시가총액(억)']
    ws.append(headers)

    for row, item in enumerate(items, start=1):
        ws.append([
            row,
            item.get('name', ''),
            item.get('code', ''),
            item.get('current_price', ''),
            item.get('change_amount', ''),
            item.get('change_rate', ''),
            item.get('volume', ''),
            item.get('trading_value', ''),
            item.get('market_sum', ''),
        ])

    wb.save(filename)
    return filename


def save_kpi200_entry_top_to_excel(limit=None, filename='kpi200_entry_top.xlsx'):
    items = fetch_kpi200_entry_top(limit=limit)
    return save_items_to_excel(items, filename=filename)


def parse_change_rate(value):
    try:
        return float(value.replace('%', '').replace('+', '').replace('−', '-').strip())
    except Exception:
        return 0.0


def parse_int(value):
    try:
        return int(value.replace(',', '').replace('—', '0').strip())
    except Exception:
        return 0


def summarize_change(items):
    if not items:
        return '등락률 최고/최저 종목 정보 없음', ''

    highest = max(items, key=lambda x: parse_change_rate(x.get('change_rate', '0%')))
    lowest = min(items, key=lambda x: parse_change_rate(x.get('change_rate', '0%')))

    summary = (
        f"최고 등락률: {highest.get('name', '')}({highest.get('code', '')}) {highest.get('change_rate', '')} | "
        f"최저 등락률: {lowest.get('name', '')}({lowest.get('code', '')}) {lowest.get('change_rate', '')}"
    )

    hi_vol = parse_int(highest.get('volume', '0'))
    lo_vol = parse_int(lowest.get('volume', '0'))

    analysis_lines = [
        f"상승률 최고 종목은 {highest.get('name', '')}으로 {highest.get('change_rate', '')} 상승했습니다.",
    ]
    if hi_vol > 500_000:
        analysis_lines.append('거래량이 높아 수급 집중이나 호재성 뉴스가 있었을 가능성이 큽니다.')
    else:
        analysis_lines.append('거래량이 낮으면 개별 이슈 중심의 급등일 수 있습니다.')

    analysis_lines.append(
        f"하락률 최저 종목은 {lowest.get('name', '')}으로 {lowest.get('change_rate', '')} 하락했습니다."
    )
    if lo_vol > 500_000:
        analysis_lines.append('큰 거래량을 동반한 하락은 차익 매도나 매도 압력이 강했을 수 있습니다.')
    else:
        analysis_lines.append('거래량이 적으면 종목별 악재나 업종 약세 영향일 수 있습니다.')

    return summary, ' '.join(analysis_lines)


class KPI200EntryTable(QMainWindow):
    def __init__(self, items):
        super().__init__()
        self.setWindowTitle('KPI200 편입종목상위')
        self.resize(1000, 600)

        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            '순번', '종목명', '종목코드', '현재가', '전일비', '등락률', '거래량', '거래대금(백만)', '시가총액(억)'
        ])

        self.last_updated_label = QLabel('업데이트: 아직 없음')
        self.last_updated_label.setStyleSheet('font-weight: bold;')

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText('종목명 또는 코드로 검색')
        self.search_input.setMaximumWidth(250)
        self.search_input.textChanged.connect(self.on_search_text_changed)

        self.summary_label = QLabel('등락률 최고/최저 종목 정보')
        self.summary_label.setWordWrap(True)
        self.summary_label.setStyleSheet('font-weight: bold; margin-top: 8px;')

        self.analysis_label = QLabel('분석 정보가 여기에 표시됩니다.')
        self.analysis_label.setWordWrap(True)
        self.analysis_label.setStyleSheet('margin-bottom: 8px;')

        save_button = QPushButton('엑셀 저장')
        save_button.clicked.connect(self.on_save_button_clicked)

        refresh_button = QPushButton('새로고침')
        refresh_button.clicked.connect(self.on_refresh_button_clicked)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.last_updated_label)
        button_layout.addWidget(self.search_input)
        button_layout.addStretch()
        button_layout.addWidget(refresh_button)
        button_layout.addWidget(save_button)

        container = QWidget()
        layout = QVBoxLayout()
        layout.addLayout(button_layout)
        layout.addWidget(self.summary_label)
        layout.addWidget(self.analysis_label)
        layout.addWidget(self.table)
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.all_items = items
        self.items = []
        self.load_items(items)

    def filter_items(self, query):
        query = query.strip().lower()
        if not query:
            return self.all_items

        filtered = []
        for item in self.all_items:
            name = item.get('name', '').lower()
            code = (item.get('code') or '').lower()
            if query in name or query in code:
                filtered.append(item)
        return filtered

    def on_search_text_changed(self, text):
        filtered_items = self.filter_items(text)
        self.load_items(filtered_items)

    def load_items(self, items):
        self.items = items
        self.table.setRowCount(len(items))
        for row, item in enumerate(items):
            self.table.setItem(row, 0, QTableWidgetItem(str(row + 1)))
            self.table.setItem(row, 1, QTableWidgetItem(item.get('name', '')))
            self.table.setItem(row, 2, QTableWidgetItem(item.get('code', '')))
            self.table.setItem(row, 3, QTableWidgetItem(item.get('current_price', '')))
            self.table.setItem(row, 4, QTableWidgetItem(item.get('change_amount', '')))
            self.table.setItem(row, 5, QTableWidgetItem(item.get('change_rate', '')))
            self.table.setItem(row, 6, QTableWidgetItem(item.get('volume', '')))
            self.table.setItem(row, 7, QTableWidgetItem(item.get('trading_value', '')))
            self.table.setItem(row, 8, QTableWidgetItem(item.get('market_sum', '')))

        self.table.resizeColumnsToContents()
        self.update_timestamp()
        self.update_summary()

    def update_timestamp(self):
        from datetime import datetime
        self.last_updated_label.setText('업데이트: ' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

    def update_summary(self):
        summary_text, analysis_text = summarize_change(self.items)
        self.summary_label.setText(summary_text)
        self.analysis_label.setText(analysis_text)

    def on_save_button_clicked(self):
        try:
            filename = save_items_to_excel(self.items)
            QMessageBox.information(self, '저장 완료', f'엑셀 파일로 저장되었습니다:\n{filename}')
        except Exception as e:
            QMessageBox.critical(self, '저장 실패', str(e))

    def on_refresh_button_clicked(self):
        try:
            refreshed_items = fetch_kpi200_entry_top(limit=None)
            self.all_items = refreshed_items
            self.load_items(refreshed_items)
            QMessageBox.information(self, '새로고침 완료', '데이터가 갱신되었습니다.')
        except Exception as e:
            QMessageBox.critical(self, '새로고침 실패', str(e))


if __name__ == '__main__':
    items = fetch_kpi200_entry_top(limit=None)
    app = QApplication([])
    window = KPI200EntryTable(items)
    window.show()
    app.exec_()