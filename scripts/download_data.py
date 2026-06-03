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
        "Flash flood warning in {loc}, roads completely submerged, residents evacuating",
        "Flood waters entering homes in {loc}, families stranded without food or water",
        "River burst banks near {loc}, rescue boats deployed for trapped residents",
        "Severe flooding in {loc} district, hospitals and schools underwater",
        "Emergency in {loc} due to floods, hundreds of families displaced overnight",
        "Floodwaters rising in {loc}, livestock and property destroyed",
        "Rescue operations underway in {loc} as floods sweep through villages",
        "People stranded on rooftops in {loc} waiting for helicopter rescue",
        "Flood relief camp set up in {loc} for displaced families",
        "Infrastructure damaged severely in {loc} due to unprecedented flooding",
        "Army deployed in {loc} for flood rescue and relief operations",
    ],
    "fires": [
        "Wildfire spreading rapidly near {loc}, residents ordered to evacuate immediately",
        "Forest fire out of control in {loc}, wind pushing flames toward homes",
        "Fire department battling massive blaze in {loc} industrial zone",
        "Residential area in {loc} on fire, multiple families displaced",
        "Fire breaks out in {loc} market, shops completely gutted",
        "Smoke visible from miles away as fire rages in {loc}",
        "Fire crews from neighboring districts called to help control {loc} blaze",
        "Building fire in {loc} traps workers on upper floors",
        "Agricultural fire in {loc} threatens nearby residential areas",
        "Fire destroys dozens of homes in {loc} overnight",
    ],
    "earthquake": [
        "Strong earthquake hits {loc}, buildings collapsing, people trapped under rubble",
        "Earthquake magnitude 6.2 strikes {loc}, massive destruction reported",
        "Aftershocks continuing in {loc} after major quake, residents afraid to return home",
        "Rescue teams digging through rubble in {loc} searching for survivors",
        "Hospital in {loc} damaged by earthquake, patients evacuated to tents",
        "Roads cracked and bridges collapsed in {loc} after earthquake",
        "Hundreds missing in {loc} after earthquake destroys entire neighborhood",
        "International rescue teams arriving in {loc} after devastating earthquake",
        "Landslides triggered by earthquake block roads in {loc}",
        "Earthquake leaves thousands homeless in {loc}, emergency shelters overwhelmed",
    ],
    "injured_or_dead_people": [
        "Multiple casualties reported in {loc} disaster, hospitals overwhelmed with injured",
        "Death toll rising in {loc} as rescue operations continue into night",
        "Injured survivors from {loc} disaster airlifted to nearest hospital",
        "Medical teams deployed to {loc} to treat disaster victims",
        "Hundreds injured in {loc}, blood banks urgently need donations",
        "Search and rescue teams find survivors in {loc} rubble after 48 hours",
        "Trauma centers in {loc} operating beyond capacity after disaster",
        "Volunteers providing first aid to injured in {loc} relief camps",
        "Critical patients from {loc} disaster transferred to city hospitals",
        "Death toll in {loc} disaster crosses 50, rescue operations ongoing",
        "Field hospital set up in {loc} to treat mass casualties",
        "Bodies being recovered from debris in {loc} disaster zone",
        "Disaster claims lives of entire families in {loc}",
        "Medical emergency declared in {loc} as hospitals fill up",
    ],
    "rescue_volunteering_or_donation_effort": [
        "Volunteers needed urgently in {loc} for disaster relief operations",
        "Donations of food and water urgently required for {loc} disaster victims",
        "NGOs coordinating relief efforts in {loc}, need more volunteers",
        "Red Cross establishing relief center in {loc} for displaced families",
        "Community kitchen set up in {loc} feeding hundreds of disaster survivors",
        "Clothing and blankets needed urgently at {loc} relief camp",
        "Volunteer doctors requested in {loc} for medical relief camp",
        "Financial donations being collected for {loc} disaster victims",
        "Rescue boats and equipment donated to {loc} relief operations",
        "Student volunteers helping distribute relief materials in {loc}",
    ],
    "infrastructure_and_utility_damage": [
        "Power lines down across {loc}, entire district without electricity for 3 days",
        "Water supply disrupted in {loc} after disaster damages main pipelines",
        "Bridge connecting {loc} to city collapsed, residents completely cut off",
        "Mobile towers destroyed in {loc}, communication with affected areas lost",
        "Roads in {loc} completely washed away, supply trucks cannot reach victims",
        "Railway line damaged in {loc}, train services suspended indefinitely",
        "Sewage system collapsed in {loc}, disease outbreak feared",
        "Hospital generator failed in {loc} during power outage",
        "Internet and phone connectivity lost in {loc} disaster zone",
        "Gas pipelines ruptured in {loc}, fire risk extremely high",
    ],
}

LOCATIONS: list[str] = [
    "Wayanad",
    "Kerala",
    "Chennai",
    "Mumbai",
    "Odisha",
    "Assam",
    "Bihar",
    "Uttarakhand",
    "Himachal Pradesh",
    "Gujarat",
    "Rajasthan",
    "Karnataka",
    "Tamil Nadu",
    "Andhra Pradesh",
    "Telangana",
    "West Bengal",
    "Manipur",
    "Nagaland",
    "Tripura",
    "Sikkim",
    "Arunachal Pradesh",
    "Meghalaya",
    "Mizoram",
    "Jammu",
    "Ladakh",
    "Punjab",
    "Haryana",
    "Madhya Pradesh",
    "Chhattisgarh",
    "Jharkhand",
    "Vidarbha",
    "Konkan",
    "Brahmaputra valley",
    "Sundarbans",
    "Leh",
    "Coorg",
    "Nilgiris",
    "Cauvery delta",
    "Godavari basin",
]


def _generate_fallback(n_per_class: int = 300) -> pd.DataFrame:
    import random

    random.seed(42)
    rows: list[dict[str, str]] = []
    for label, templates in FALLBACK_TEMPLATES.items():
        for _ in range(n_per_class):
            template = random.choice(templates)
            loc = random.choice(LOCATIONS)
            text = template.format(loc=loc)
            rows.append({"tweet_text": text, "class_label": label})
    df = pd.DataFrame(rows)
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    return df


def main() -> None:
    out_dir = Path("data/raw")
    out_dir.mkdir(parents=True, exist_ok=True)
    downloaded = False
    with httpx.Client(follow_redirects=True, timeout=60) as client:
        frames: list[pd.DataFrame] = []
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
        df = _generate_fallback(n_per_class=300)
        save_path = out_dir / "train.csv"
        df.to_csv(save_path, index=False)
        print(f"Saved {len(df)} rows to {save_path}")


if __name__ == "__main__":
    main()

