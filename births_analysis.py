import re
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

plt.rcParams["font.family"] = "Malgun Gothic"
plt.rcParams["axes.unicode_minus"] = False

# 파일 경로
EXCEL_FILE = Path("출생아수__합계출산율__자연증가_등_20260602141745.xlsx")
SHEET_INDEX = 0

# 1) 데이터 로드
raw_df = pd.read_excel(EXCEL_FILE, sheet_name=SHEET_INDEX, engine="openpyxl")

# 2) 데이터 클렌징 및 구조 변환
first_col = raw_df.columns[0]
clean_df = raw_df.set_index(first_col).T

# 연도 인덱스를 숫자로 변환
clean_df.index = clean_df.index.astype(str).str.strip()
clean_df.index = clean_df.index.str.replace(r"^'(.*)'$", r"\1", regex=True)
clean_df.index = clean_df.index.str.replace(r"2025\s*p\)", "2025", regex=True)
clean_df.index = clean_df.index.astype(int)

# 출생아수 데이터 컬럼 선택
birth_column = clean_df.columns[0]
print(f"Using birth count column: {birth_column!r}")

births = pd.to_numeric(clean_df.iloc[:, 0], errors="coerce").rename("births")

# 3) 분석 기간 필터링
births = births.loc[1970:2025]

# 4) 누락값 처리
births = births.dropna()
if births.empty:
    raise ValueError(f"No birth count data found for 1970-2025 using column {birth_column!r}.")

# 5) 분석 결과 출력
print("=== 출생아수 데이터 분석 (1970-2025) ===")
print(f"데이터 건수: {len(births)}")
print(f"최소 출생아수: {int(births.min()):,} ({births.idxmin()})")
print(f"최대 출생아수: {int(births.max()):,} ({births.idxmax()})")
print(f"평균 출생아수: {births.mean():,.0f}")
print(f"1970-2025 기간 포함 연도: {births.index.min()} ~ {births.index.max()}")
print()
print(births.describe())

# 6) 라인 그래프 출력
plt.figure(figsize=(12, 6))
plt.plot(births.index, births.values, marker="o", linestyle="-", color="tab:blue")
plt.title("출생아수 (1970-2025)")
plt.xlabel("연도")
plt.ylabel("출생아수")
plt.grid(alpha=0.4)
plt.tight_layout()
plt.savefig("births_1970_2025.png", dpi=150)
plt.show()
