from __future__ import annotations

import httpx
import pandas as pd
from pathlib import Path

from app.core.config import settings

HUMAID_URLS: list[tuple[str, str]] = [
    (
        "https://raw.githubusercontent.com/rajaswa/crisis-nlp/main/data/humaid_train.csv",
        "data/raw/train.csv",
    ),
    (
        "https://raw.githubusercontent.com/rajaswa/crisis-nlp/main/data/humaid_val.csv",
        "data/raw/val.csv",
    ),
    (
        "https://raw.githubusercontent.com/rajaswa/crisis-nlp/main/data/humaid_test.csv",
        "data/raw/test.csv",
    ),
]

FALLBACK_TEMPLATES: dict[str, list[str]] = {
    "flooding": [
        "Water levels rising fast in {loc}, people trapped on rooftops need immediate rescue",
        "Flash flood warning in {loc}, roads completely submerged, residents evacuating now",
        "Flood waters entering homes in {loc}, families stranded without food or water",
        "River burst banks near {loc}, rescue boats deployed for trapped residents",
        "Severe flooding in {loc} district, hospitals and schools underwater",
        "Emergency in {loc} due to floods, hundreds of families displaced overnight",
        "Floodwaters rising in {loc}, livestock and property destroyed, help needed",
        "Rescue operations underway in {loc} as floods sweep through villages",
        "People stranded on rooftops in {loc} waiting for helicopter rescue",
        "Flood relief camp set up in {loc} for displaced families, donations needed",
        "Infrastructure damaged severely in {loc} due to unprecedented flooding",
        "Army deployed in {loc} for flood rescue and relief operations",
        "Low-lying areas of {loc} submerged, residents moved to relief camps",
        "Flooding cuts off {loc} from rest of district, supply routes blocked",
        "Dam overflow causing massive flooding in {loc}, evacuation ordered",
        "Hundreds of homes destroyed by flooding in {loc}, families homeless",
        "Flood victims in {loc} need food, clean water and medicines urgently",
        "Rivers overflowing in {loc} after heavy rainfall, situation critical",
        "Schools converted to relief shelters in {loc} as flooding worsens",
        "Death toll rising in {loc} floods as rescue teams struggle to reach victims",
    ],
    "fires": [
        "Wildfire spreading rapidly near {loc}, residents ordered to evacuate immediately",
        "Forest fire out of control in {loc}, wind pushing flames toward homes",
        "Fire department battling massive blaze in {loc} industrial zone",
        "Residential area in {loc} on fire, multiple families displaced tonight",
        "Fire breaks out in {loc} market, shops completely gutted by morning",
        "Smoke visible from miles away as fire rages through {loc}",
        "Fire crews from neighboring districts called to help control {loc} blaze",
        "Building fire in {loc} traps workers on upper floors, rescue underway",
        "Agricultural fire in {loc} threatens nearby residential areas urgently",
        "Fire destroys dozens of homes in {loc} overnight, residents homeless",
        "Gas cylinder explosion causes fire in {loc} killing several people",
        "Hospital in {loc} catches fire, patients evacuated to nearby facilities",
        "Chemical factory fire in {loc} releases toxic fumes, area evacuated",
        "Fire destroys market in {loc}, traders lose everything overnight",
        "Firefighters injured while battling blaze in {loc} residential colony",
        "Slum area in {loc} engulfed by fire, hundreds left homeless",
        "Electrical short circuit causes massive fire in {loc} apartment block",
        "Fire spreads to forest areas near {loc}, wildlife sanctuary threatened",
        "Night fire in {loc} kills family of four, children among victims",
        "Fire at fuel depot in {loc} causes massive explosion heard miles away",
    ],
    "earthquake": [
        "Strong earthquake hits {loc}, buildings collapsing, people trapped under rubble",
        "Earthquake magnitude 6.2 strikes {loc}, massive destruction reported",
        "Aftershocks continuing in {loc} after major quake, residents afraid to return",
        "Rescue teams digging through rubble in {loc} searching for survivors",
        "Hospital in {loc} damaged by earthquake, patients evacuated to tents outside",
        "Roads cracked and bridges collapsed in {loc} after devastating earthquake",
        "Hundreds missing in {loc} after earthquake destroys entire neighborhood",
        "International rescue teams arriving in {loc} after devastating earthquake",
        "Landslides triggered by earthquake blocking all roads in {loc}",
        "Earthquake leaves thousands homeless in {loc}, emergency shelters overwhelmed",
        "Historic buildings collapsed in {loc} earthquake, heritage site destroyed",
        "Earthquake strikes {loc} at dawn, most residents asleep when it hit",
        "Water and power supply cut off in {loc} after earthquake damages infrastructure",
        "Schools and colleges shut in {loc} after earthquake damages structures",
        "Rescue dogs deployed in {loc} to find survivors trapped under debris",
        "Earthquake of magnitude 5.8 felt across {loc} and surrounding districts",
        "Tremors felt in {loc} for third consecutive day, panic among residents",
        "Death toll in {loc} earthquake rises to 47 as rescue operations continue",
        "Children among survivors pulled from rubble in {loc} earthquake aftermath",
        "Earthquake damage in {loc} estimated at hundreds of crores, says official",
    ],
    "injured_or_dead_people": [
        "Multiple casualties reported in {loc} disaster, hospitals overwhelmed with injured",
        "Death toll rising in {loc} as rescue operations continue into night",
        "Injured survivors from {loc} disaster airlifted to nearest hospital",
        "Medical teams deployed to {loc} to treat disaster victims urgently",
        "Hundreds injured in {loc}, blood banks urgently requesting donations now",
        "Search and rescue teams find survivors in {loc} rubble after 48 hours",
        "Trauma centers in {loc} operating beyond capacity after disaster struck",
        "Volunteers providing first aid to injured people in {loc} relief camps",
        "Critical patients from {loc} disaster transferred to city hospitals",
        "Death toll in {loc} disaster crosses 50, rescue operations ongoing",
        "Field hospital set up in {loc} to treat mass casualties from disaster",
        "Bodies being recovered from debris in {loc} disaster zone today",
        "Disaster claims lives of entire families in {loc}, community in shock",
        "Medical emergency declared in {loc} as hospitals fill beyond capacity",
        "Children and elderly among the worst affected victims in {loc} disaster",
        "Doctors working without rest in {loc} to save disaster victims",
        "Mass casualty event in {loc} overwhelms local medical infrastructure",
        "Survivors of {loc} disaster suffering from trauma and injuries",
        "Red Cross setting up emergency medical camp in {loc} for victims",
        "Hundreds of people injured in {loc} need urgent surgical care now",
    ],
    "rescue_volunteering_or_donation_effort": [
        "Volunteers needed urgently in {loc} for disaster relief operations today",
        "Donations of food and water urgently required for {loc} disaster victims",
        "NGOs coordinating relief efforts in {loc}, more volunteers needed immediately",
        "Red Cross establishing relief center in {loc} for displaced families",
        "Community kitchen set up in {loc} feeding hundreds of disaster survivors",
        "Clothing and blankets urgently needed at {loc} relief camp tonight",
        "Volunteer doctors requested in {loc} for emergency medical relief camp",
        "Financial donations being collected for {loc} disaster victims online",
        "Rescue boats and equipment donated to {loc} relief operations today",
        "Student volunteers helping distribute relief materials across {loc}",
        "Army of volunteers mobilizing in {loc} to help disaster survivors",
        "Local temple in {loc} converted to relief center feeding thousands",
        "Corporate houses donating supplies for {loc} relief operations",
        "Crowdfunding campaign launched for {loc} disaster victims goes viral",
        "Trained rescue swimmers deployed to help flood victims in {loc}",
    ],
    "infrastructure_and_utility_damage": [
        "Power lines down across {loc}, entire district without electricity",
        "Water supply disrupted in {loc} after disaster damages main pipelines",
        "Bridge connecting {loc} to city collapsed, residents completely cut off",
        "Mobile towers destroyed in {loc}, all communication with area lost",
        "Roads in {loc} completely washed away, supply trucks cannot reach victims",
        "Railway line damaged near {loc}, all train services suspended indefinitely",
        "Sewage system collapsed in {loc}, disease outbreak feared by health officials",
        "Hospital generator failed in {loc} during extended power outage",
        "Internet and phone connectivity completely lost in {loc} disaster zone",
        "Gas pipelines ruptured in {loc}, fire risk extremely high say officials",
        "All major roads into {loc} blocked, district cut off from rest of state",
        "Airport in {loc} shut due to disaster, flights diverted to other cities",
        "Drinking water contaminated in {loc} after flooding, disease risk high",
        "Power substation damaged in {loc}, restoration may take several days",
        "Hundreds of electric poles fallen across {loc}, restoration teams working",
    ],
}

LOCATIONS: list[str] = [
    "Wayanad", "Thrissur", "Kochi", "Kozhikode", "Thiruvananthapuram",
    "Malappuram", "Kannur", "Kollam", "Palakkad", "Alappuzha",
    "Mumbai", "Pune", "Nagpur", "Nashik", "Aurangabad",
    "Chennai", "Coimbatore", "Madurai", "Salem", "Tiruchirappalli",
    "Bengaluru", "Mysuru", "Hubli", "Mangaluru", "Belagavi",
    "Hyderabad", "Warangal", "Nizamabad", "Karimnagar",
    "Bhopal", "Indore", "Jabalpur", "Gwalior",
    "Patna", "Gaya", "Muzaffarpur", "Bhagalpur",
    "Bhubaneswar", "Cuttack", "Rourkela", "Sambalpur",
    "Guwahati", "Jorhat", "Dibrugarh", "Silchar",
    "Dehradun", "Haridwar", "Rishikesh",
    "Shimla", "Dharamshala", "Mandi",
    "Jammu", "Srinagar", "Leh",
    "Jaipur", "Jodhpur", "Udaipur", "Ajmer",
    "Ahmedabad", "Surat", "Vadodara", "Rajkot",
    "Lucknow", "Kanpur", "Varanasi", "Prayagraj", "Agra",
    "Kolkata", "Howrah", "Siliguri", "Asansol",
    "Ranchi", "Jamshedpur", "Dhanbad",
    "Raipur", "Bilaspur",
    "Chandigarh", "Amritsar", "Ludhiana",
    "Delhi", "Noida", "Gurgaon",
]


def _generate_fallback(n_per_class: int = 500) -> pd.DataFrame:
    import random
    from collections import defaultdict

    random.seed(42)
    rows: list[dict[str, str]] = []
    for label, templates in FALLBACK_TEMPLATES.items():
        for _ in range(n_per_class):
            template = random.choice(templates)
            loc = random.choice(LOCATIONS)
            text = template.format(loc=loc)
            rows.append({"tweet_text": text, "class_label": label})

    balanced_rows: list[dict[str, str]] = []
    by_label: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        by_label[row["class_label"]].append(row)

    random.seed(99)
    for label, label_rows in by_label.items():
        if len(label_rows) > 500:
            label_rows = random.sample(label_rows, 500)
        while len(label_rows) < 500:
            label_rows.append(random.choice(label_rows))
        balanced_rows.extend(label_rows)

    random.shuffle(balanced_rows)
    df = pd.DataFrame(balanced_rows)
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    return df


def _save_fallback_splits(df: pd.DataFrame) -> None:
    out_dir = Path("data/raw")
    out_dir.mkdir(parents=True, exist_ok=True)

    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    n = len(df)
    train_end = int(n * 0.70)
    val_end = train_end + int(n * 0.15)

    splits = {
        "train": df.iloc[:train_end],
        "val": df.iloc[train_end:val_end],
        "test": df.iloc[val_end:],
    }

    for split_name, split_df in splits.items():
        csv_path = out_dir / f"{split_name}.csv"
        tsv_path = out_dir / f"{split_name}.tsv"
        split_df.to_csv(csv_path, index=False)
        split_df.to_csv(tsv_path, sep="\t", index=False)
        print(f"Saved {len(split_df)} rows to {csv_path}")
        print(f"Saved {len(split_df)} rows to {tsv_path}")


def main() -> None:
    out_dir = Path("data/raw")
    out_dir.mkdir(parents=True, exist_ok=True)
    downloaded = False
    with httpx.Client(follow_redirects=True, timeout=60) as client:
        for url, save_path in HUMAID_URLS:
            try:
                resp = client.get(url)
                if resp.status_code == 200 and len(resp.content) > 1000:
                    Path(save_path).parent.mkdir(parents=True, exist_ok=True)
                    Path(save_path).write_text(resp.text, encoding="utf-8")
                    print(f"Saved {save_path}")
                    downloaded = True
            except Exception:
                pass
    if not downloaded:
        print("Remote download failed. Generating high-quality synthetic dataset.")
        df = _generate_fallback(n_per_class=500)
        _save_fallback_splits(df)


if __name__ == "__main__":
    main()

