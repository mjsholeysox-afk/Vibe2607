import os
import pandas as pd
import matplotlib.pyplot as plt

# 웹 상의 타이타닉 데이터셋 URL
DATA_URL = "https://raw.githubusercontent.com/datasciencedojo/datasets/master/titanic.csv"


def load_titanic_data(url: str) -> pd.DataFrame:
    """웹에서 타이타닉 데이터를 로드합니다."""
    return pd.read_csv(url)


def analyze_survival_by_gender(df: pd.DataFrame) -> pd.DataFrame:
    """성별 생존 비율을 계산합니다."""
    grouped = df.groupby("Sex")["Survived"]
    survival_rate = grouped.mean() * 100
    count = grouped.count()
    result = pd.DataFrame({
        "survival_rate": survival_rate,
        "count": count,
    })
    return result


def plot_survival_by_gender(stats: pd.DataFrame, output_path: str) -> None:
    """성별 생존 비율을 바 차트로 저장합니다."""
    plt.figure(figsize=(8, 5))
    bars = plt.bar(stats.index, stats["survival_rate"], color=["#1f77b4", "#ff7f0e"])
    plt.title("Titanic Survival Rate by Gender")
    plt.xlabel("Gender")
    plt.ylabel("Survival Rate (%)")
    plt.ylim(0, 100)
    plt.grid(axis="y", linestyle="--", alpha=0.4)

    for bar in bars:
        height = bar.get_height()
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            height + 1,
            f"{height:.1f}%",
            ha="center",
            va="bottom",
            fontsize=11,
        )

    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()


if __name__ == "__main__":
    print("Loading Titanic dataset from web...")
    df = load_titanic_data(DATA_URL)
    print(f"Loaded {len(df)} rows")

    stats = analyze_survival_by_gender(df)
    print("Survival rates by gender:")
    print(stats)

    output_image = os.path.join(os.path.dirname(__file__), "titanic_survival_by_gender.png")
    plot_survival_by_gender(stats, output_image)
    print(f"Bar chart saved to: {output_image}")
