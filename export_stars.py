import orjson

DATA_DIR = "rocom.aoe.top/public/data/BinData"


def load_data(name: str) -> dict:
    with open(f"{DATA_DIR}/{name}.json", "rb") as f:
        return orjson.loads(f.read())


def dump_data(name: str, obj):
    with open(f"{name}.json", "wb") as f:
        f.write(orjson.dumps(obj, option=orjson.OPT_INDENT_2))


def main():
    area = load_data("AREA_CONF")["RocoDataRows"].values()

    stars = []
    for entry in area:
        if "editor_name" not in entry:
            continue

        name = entry["editor_name"][0]
        comment1 = entry["editor_name"][1] if len(entry["editor_name"]) > 1 else None
        comment2 = entry["editor_name"][2] if len(entry["editor_name"]) > 2 else None

        if comment1 is not None and "光点" in comment1:
            name, comment1 = comment1, name

        if any(
            kw in name
            for kw in [
                "-眠枭-",
                "-小眠枭-",
                "-海边小眠枭-",
                "眠枭庇护所区域",
                "眠枭石像测试数据",
            ]
        ):
            continue
        if "眠枭" not in name:
            continue

        star = {
            "name": name,
            "comment1": comment1 if comment1 else comment2,
            "comment2": comment2 if comment1 else None,
            "positions": list(tuple(p["position_xyz"]) for p in entry["pos"]),
        }

        stars.append(star)

    dump_data("眠枭之星", stars)


if __name__ == "__main__":
    main()
