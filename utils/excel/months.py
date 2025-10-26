from typing import List

DEFAULT_ALIASES = [
    # English full
    "january","february","march","april","may","june","july","august","september","october","november","december",
    # English short
    "jan","feb","mar","apr","may","jun","jul","aug","sep","sept","oct","nov","dec",
    # Spanish full
    "enero","febrero","marzo","abril","mayo","junio","julio","agosto","septiembre","octubre","noviembre","diciembre",
    # Spanish short
    "ene","feb","mar","abr","may","jun","jul","ago","sep","set","oct","nov","dic",
]

def detect_month_columns(columns: List[str], aliases: List[str] = None) -> List[str]:
    aliases = aliases or DEFAULT_ALIASES
    found: List[str] = []
    for c in columns:
        cl = str(c).strip().lower()
        if any(
            cl == a or cl.startswith(a + " ") or cl.endswith(" " + a) or cl.startswith(a + "_") or cl.endswith("_" + a)
            for a in aliases
        ):
            found.append(c)
    return found