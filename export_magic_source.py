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

    sources = []
    for entry in area:
        if "editor_name" not in entry:
            continue

        name = entry["editor_name"][0]
        pos = entry["editor_name"][1] if len(entry["editor_name"]) > 1 else None

        if "魔力之源" != name:
            continue

        source = {
            "name": name,
            "comment1": pos,
            "comment2": None,
            "positions": list(tuple(p["position_xyz"]) for p in entry["pos"]),
        }

        sources.append(source)

    dump_data("魔力之源", sources)


if __name__ == "__main__":
    main()
