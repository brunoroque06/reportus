import datetime

from src.report import dtvpa
from src.time import Delta


def test_data():
    dtvpa.validate()


def test_dtvpa(date: tuple[datetime.date, str]):
    sub, comp, rep = dtvpa.process(
        Delta(years=12),
        {"co": 13, "fg": 4, "vse": 60, "vc": 12, "vsp": 29, "fc": 6},
        date[0],
    )

    assert [r.raw for r in sub.rows] == [13, 4, 60, 12, 29, 6]
    assert [r.percentile for r in sub.rows] == [25, 9, 9, 25, 9, 16]
    assert [r.standard for r in sub.rows] == [8, 6, 6, 8, 6, 7]

    assert [r.sum_standard for r in comp.rows] == [41, 21, 20]
    assert [r.index for r in comp.rows] == [78, 81, 79]
    assert [r.percentile for r in comp.rows] == [7, 10, 8]

    assert (
        rep
        == f"Developmental Test of Visual Perception - Adolescent and Adult (DTVP-A) - ({date[1]})\n\nVisuomotorische Integration: PR 8 - Weit unter der Norm\nMotorik-Reduzierte Wahrnehmung: PR 10 - Unter der Norm\nGlobale Visuelle Wahrnehmung: PR 7 - Weit unter der Norm\n\nSubtests:\nAbzeichnen: PR 25 - durchschnittlich\nFigur-Grund: PR 9 - unterdurchschnittlich\nVisuomotorisches Suchen: PR 9 - unterdurchschnittlich\nGesaltschliessen: PR 25 - durchschnittlich\nVisuomotorische Geschwindigkeit: PR 9 - unterdurchschnittlich\nFormkonstanz: PR 16 - unterdurchschnittlich"
    )
