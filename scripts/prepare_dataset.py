import json
import sys
from pathlib import Path

import pandas as pd

from app.core.config import settings

LABEL_MAP: dict[str, str | None] = {
    "flooding": "flood",
    "infrastructure_and_utility_damage": "flood",
    "infrastructure_and_utilities": "flood",
    "fires": "fire",
    "earthquake": "earthquake",
    "injured_or_dead_people": "medical",
    "rescue_volunteering_or_donation_effort": "medical",
    "caution_and_advice": None,
    "not_humanitarian": None,
    "other_relevant_information": None,
    "sympathy_and_support": None,
    "affected_individuals": "medical",
    "displaced_people_and_evacuations": "flood",
    "donation_needs": None,
    "requests_or_urgent_needs": "medical",
    "response_efforts": None,
}


def _gather_raw_files() -> list[Path]:
    raw_dir = Path("data/raw")
    csv_files = sorted(raw_dir.glob("*.csv"))
    tsv_files = sorted(raw_dir.glob("*.tsv"))

    if csv_files:
        return csv_files
    return tsv_files


def main() -> None:
    dfs = []
    raw_files = _gather_raw_files()
    if not raw_files:
        raise FileNotFoundError("No raw dataset files found in data/raw")

    for data_file in raw_files:
        kwargs = {"sep": "\t"} if data_file.suffix == ".tsv" else {}
        df = pd.read_csv(data_file, **kwargs)
        dfs.append(df)

    df = pd.concat(dfs, ignore_index=True)

    df["label"] = df["class_label"].map(LABEL_MAP)
    df = df.dropna(subset=["label"])

    df = df.rename(columns={"tweet_text": "text"})

    df = df[["text", "label"]]

    df = df[df["text"].str.strip().astype(bool)]

    df = df.drop_duplicates(subset=["text"], keep="first")

    output_dir = Path("data/processed")
    output_dir.mkdir(parents=True, exist_ok=True)

    df.to_csv("data/processed/crisis_dataset.csv", index=False)

    print(df["label"].value_counts().to_string())
    print(f"Total: {len(df)} samples")


if __name__ == "__main__":
    main()
