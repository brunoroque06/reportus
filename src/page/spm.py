from collections.abc import Callable
from typing import Literal

from src import ui
from src.report import spm
from src.report.spm import Filer
from src.time import today


def page():
    hori, vert = ui.structure("SPM")

    with hori():
        with vert():
            date = today()

            def ver1():
                return ver == 1

            with hori():
                ver: Literal[1, 2] = ui.selectbox("Version", (1, 2))
                asmt = ui.date_input("Assessment", date, key="spm", max_value=date)
            with hori():
                form = ui.selectbox("Form", spm.forms(ver))
                filer_fmt: Callable[[Filer], str] = lambda f: f.name
                filer = ui.selectbox(
                    "Filled by",
                    spm.filers(form),
                    format_func=filer_fmt,
                )

            scores = spm.get_scores()

            left_forms = (
                ["soc", "vis", "hea"]
                if ver1()
                else ["vis", "hea", "tou", "t&s", "bod", "bal"]
            )
            right_forms = (
                ["tou", "t&s", "bod", "bal", "pln"] if ver1() else ["pln", "soc"]
            )

            raw: dict[str, int] = {}

            with hori():
                with vert():
                    for s in left_forms:
                        raw[s] = ui.number_input(scores[s], step=1)

                with vert():
                    for s in right_forms:
                        raw[s] = ui.number_input(scores[s], step=1)

            name = None
            if not ver1():
                name = ui.text_input("Name")

        with vert():
            res, rep = spm.process(asmt, form, ver, filer, name, raw)
            ui.text(rep)
            ui.table(res)
