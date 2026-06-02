import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathlib import Path


DATA_FILE = Path('S&P 500 과거 데이터.csv')
OUTPUT_IMAGE = Path('sp500_close_2000_2019.png')
OUTPUT_MA_IMAGE = Path('sp500_close_2000_2019_ma.png')


def load_and_clean(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, encoding='utf-8')

    # 컬럼명 정리
    df.columns = [col.strip().replace('"', '').replace(' ', '') for col in df.columns]

    # 날짜 변환
    df['날짜'] = df['날짜'].astype(str).str.replace('"', '').str.strip()
    df['날짜'] = pd.to_datetime(df['날짜'].str.replace(' ', ''), format='%Y-%m-%d', errors='coerce')

    # 숫자형 컬럼 변환
    for col in ['종가', '시가', '고가', '저가']:
        df[col] = (
            df[col]
            .astype(str)
            .str.replace(',', '')
            .str.strip()
        )
        df[col] = pd.to_numeric(df[col], errors='coerce')

    df['변동%'] = (
        df['변동%']
        .astype(str)
        .str.replace('%', '')
        .str.replace(',', '')
        .str.strip()
    )
    df['변동%'] = pd.to_numeric(df['변동%'], errors='coerce')

    df = df.sort_values('날짜').reset_index(drop=True)
    return df


def filter_period(df: pd.DataFrame, start: str, end: str) -> pd.DataFrame:
    mask = (df['날짜'] >= start) & (df['날짜'] <= end)
    return df.loc[mask].copy()


def print_summary(df: pd.DataFrame) -> None:
    print('===== S&P 500 데이터 요약 =====')
    print(f'전체 행 수: {len(df):,}')
    print(f'기간: {df["날짜"].min().strftime("%Y-%m-%d")} ~ {df["날짜"].max().strftime("%Y-%m-%d")}')
    print(f'종가 평균: {df["종가"].mean():.2f}')
    print(f'종가 중앙값: {df["종가"].median():.2f}')
    print(f'종가 표준편차: {df["종가"].std():.2f}')
    print(f'종가 최저: {df["종가"].min():.2f}')
    print(f'종가 최고: {df["종가"].max():.2f}')
    print(f'일간 평균 변동률: {df["변동%"].mean():.4f}%')
    print(f'일간 변동률 표준편차: {df["변동%"].std():.4f}%')
    print(f'결측치(날짜): {df["날짜"].isna().sum()}')
    print(f'결측치(종가): {df["종가"].isna().sum()}')
    print()


def add_derived_metrics(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df['daily_return'] = df['종가'].pct_change()
    df['ma50'] = df['종가'].rolling(50, min_periods=1).mean()
    df['ma200'] = df['종가'].rolling(200, min_periods=1).mean()
    df['volatility_20d'] = df['daily_return'].rolling(20, min_periods=1).std() * 100
    df['cum_return'] = (1 + df['daily_return']).cumprod() - 1
    df['high_watermark'] = df['종가'].cummax()
    df['drawdown'] = df['종가'] / df['high_watermark'] - 1
    return df


def print_annual_returns(df: pd.DataFrame) -> None:
    annual = (
        df.set_index('날짜')
        .resample('YE')
        .agg({'종가': ['first', 'last'], '변동%': 'std'})
    )
    annual.columns = ['open', 'close', 'volatility_pct']
    annual['annual_return_pct'] = (annual['close'] / annual['open'] - 1) * 100
    annual = annual.round(2)

    print('===== 연간 수익률 및 변동성 =====')
    print(annual.to_string())
    print()


def print_monthly_statistics(df: pd.DataFrame) -> None:
    monthly = (
        df.set_index('날짜')['daily_return']
        .resample('ME')
        .apply(lambda x: (1 + x).prod() - 1)
    )
    month_stats = monthly.groupby(monthly.index.month).agg(['mean', 'std', 'count']).round(4)
    month_stats.index = month_stats.index.map(lambda x: f'{x:02d}')

    best_month = monthly.idxmax().strftime('%Y-%m') if not monthly.empty else 'N/A'
    worst_month = monthly.idxmin().strftime('%Y-%m') if not monthly.empty else 'N/A'

    print('===== 월별 수익률 분포 =====')
    print(month_stats.to_string())
    print(f'가장 수익률이 높은 월: {best_month}')
    print(f'가장 수익률이 낮은 월: {worst_month}')
    print()


def print_drawdown_summary(df: pd.DataFrame) -> None:
    max_dd = df['drawdown'].min()
    duration = 0
    max_duration = 0
    for drawdown in df['drawdown']:
        if drawdown < 0:
            duration += 1
        else:
            max_duration = max(max_duration, duration)
            duration = 0
    max_duration = max(max_duration, duration)

    print('===== 최대 낙폭 =====')
    print(f'최대 낙폭: {max_dd:.2%}')
    print(f'최대 낙폭 지속일수: {max_duration} 거래일')
    print(f'누적 수익률: {df["cum_return"].iloc[-1]:.2%}')
    years = (df['날짜'].iloc[-1] - df['날짜'].iloc[0]).days / 365.25
    cagr = (1 + df['cum_return'].iloc[-1]) ** (1 / years) - 1
    print(f'CAGR: {cagr:.2%}')
    print()


def plot_close_price(df: pd.DataFrame, output_path: Path) -> None:
    plt.figure(figsize=(12, 6))
    plt.plot(df['날짜'], df['종가'], color='tab:blue', linewidth=1)
    plt.title('S&P 500 Close Price (2000-01 ~ 2019-12)')
    plt.xlabel('Date')
    plt.ylabel('Close')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    print(f'그래프 파일 저장: {output_path}')


def plot_moving_averages(df: pd.DataFrame, output_path: Path) -> None:
    plt.figure(figsize=(12, 6))
    plt.plot(df['날짜'], df['종가'], color='tab:blue', label='Close', linewidth=1)
    plt.plot(df['날짜'], df['ma50'], color='tab:orange', label='MA50', linewidth=1)
    plt.plot(df['날짜'], df['ma200'], color='tab:green', label='MA200', linewidth=1)
    plt.fill_between(df['날짜'], df['종가'], df['ma50'], where=df['종가'] >= df['ma50'], facecolor='green', alpha=0.1)
    plt.fill_between(df['날짜'], df['종가'], df['ma50'], where=df['종가'] < df['ma50'], facecolor='red', alpha=0.1)
    plt.title('S&P 500 Close Price and Moving Averages (50/200)')
    plt.xlabel('Date')
    plt.ylabel('Close')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    print(f'이동평균 그래프 저장: {output_path}')


def main() -> None:
    df = load_and_clean(DATA_FILE)
    df = filter_period(df, '2000-01-01', '2019-12-31')
    df = add_derived_metrics(df)

    print_summary(df)
    print_annual_returns(df)
    print_monthly_statistics(df)
    print_drawdown_summary(df)
    plot_close_price(df, OUTPUT_IMAGE)
    plot_moving_averages(df, OUTPUT_MA_IMAGE)


if __name__ == '__main__':
    main()
