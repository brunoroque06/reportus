from collections.abc import Callable

from src import ui
from src.report import mabc
from src.time import Delta


def display_age(a: Delta) -> ui.Color:
    if a.years < 7:
        return "red"
    if a.years < 11:
        return "green"
    return "blue"


def page():
    hori, vert = ui.structure("MABC")

    with hori():
        with vert():
            asmt_date, _, age = ui.dates(5, 16, disp=display_age, key="mabc")

            comps = mabc.get_comps(age)
            comp_ids = list(comps.keys())

            with hori():
                hand = ui.selectbox("Preferred Hand", ("Right", "Left"))
                failed = ui.multiselect(
                    "Failed", mabc.get_failed(), format_func=str.upper
                )

            raw: dict[str, int | None] = {}

            with hori():
                for comp_id in comp_ids:
                    with vert():
                        ui.markdown(f"**{comp_id}**")
                        for exe in comps[comp_id]:
                            raw[exe] = ui.number_input(
                                label=exe.upper(),
                                min_value=0,
                                max_value=150,
                                step=1,
                                disabled=(exe in failed),
                            )

            for f in failed:
                raw[f] = None

        with vert():
            comp, agg, rep = mabc.process(age, raw, asmt=asmt_date, hand=hand)
            ui.text(rep)

            with hori():
                for c in ["hg", "bf", "bl"]:
                    same_cat: Callable[[str], bool] = lambda i, pre=c: i.startswith(pre)
                    t = comp.filter(id=same_cat)
                    t = t.sort(key=lambda r: r.id if len(r.id) == 4 else r.id + "z")
                    ui.table(t)

            ui.table(agg)
