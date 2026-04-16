import datetime

import orjson
import polars as pl

DATA_DIR = "rocom.aoe.top/public/data/BinData"


def load_data(name: str) -> dict:
    with open(f"{DATA_DIR}/{name}.json", "rb") as f:
        return orjson.loads(f.read())


def clean(data: list):
    df = pl.DataFrame(data)
    df = df.select(
        col
        for col in df.columns
        if col == "is_rare" or df[col].filter(df[col].is_not_null()).n_unique() > 1
    )
    return df


def main():
    # accu_pool = load_data("BONUS_EVENT_ACCU_POOL_CONF")
    nightmare_map = load_data("NPC_REFRESH_CONTENT_CONF")["RocoDataRows"]
    unit_type_map = load_data("TYPE_DICTIONARY")["RocoDataRows"]
    event_pool = load_data("BONUS_EVENT_POOL_CONF")
    petbase = load_data("PETBASE_CONF")

    pets: list[dict] = list(petbase["RocoDataRows"].values())
    bonus_events = list(event_pool["RocoDataRows"].values())

    # Filter out events known to be expired
    bonus_events = [
        bonus_event
        for bonus_event in bonus_events
        if "disabletime" not in bonus_event
        or datetime.datetime.fromisoformat(bonus_event["disabletime"]).year == 2026
    ]

    evo_map: dict[tuple[int, ...], str] = {}
    for pet in pets:
        if "pet_evolution_id" not in pet:
            continue
        key = tuple(pet["pet_evolution_id"])
        if key not in evo_map:
            evo_map[key] = pet["name"]

    bonus_event: dict
    for bonus_event in bonus_events:
        bonus_param = bonus_event["bonus_param"][0]
        nightmare_pet = nightmare_map[str(bonus_param)]

        bonus_event["nightmare"] = nightmare_pet["editor_name"][0]

        if "petbase_field_param" in bonus_event:
            field_param = bonus_event["petbase_field_param"]
            match bonus_event["petbase_field"]:
                case "unit_type":
                    condition = f"{unit_type_map[field_param[0]]['type_name']}混抓"
                case "pet_evolution_id":
                    evo_key = tuple(map(int, field_param))
                    condition = f"进化链-{evo_map.get(evo_key, '未知')}"
            bonus_event["condition"] = condition
        else:
            bonus_event["condition"] = "随意捕获"

        for field in ["bonus_param", "petbase_field", "petbase_field_param"]:
            bonus_event.pop(field, None)

    clean(bonus_events).with_columns(
        pl.col("is_rare").fill_null(False),
    ).sort(
        [
            pl.col("condition"),
            pl.col("weight").mul(-1),
            pl.col("accumulate_type"),
        ]
    ).write_excel(
        "bonus_events.xlsx",
    )
    clean(pets).write_excel("petbase.xlsx")


if __name__ == "__main__":
    main()
