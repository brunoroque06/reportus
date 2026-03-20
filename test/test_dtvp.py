import datetime

from src.report import dtvp
from src.time import Delta


def test_data():
    dtvp.validate()


def test_dtvp(date: tuple[datetime.date, str]):
    age = Delta(years=6, months=11)

    raw = {"eh": 108, "co": 11, "fg": 52, "vc": 10, "fc": 32}

    sub, comp, rep = dtvp.process(age, raw, date[0])

    assert [r.raw for r in sub.rows] == [108, 11, 52, 10, 32]
    assert [r.age_eq for r in sub.rows] == ["4;3", "4;8", "10;5", "5;10", "6;3"]
    assert [r.percentile for r in sub.rows] == [1, 2, 75, 25, 50]
    assert [r.scaled for r in sub.rows] == [3, 4, 12, 8, 10]
    assert [r.descriptive for r in sub.rows] == [
        "Very Poor",
        "Poor",
        "Average",
        "Average",
        "Average",
    ]

    assert [r.sum_scaled for r in comp.rows] == [7, 30, 37]
    assert [r.percentile for r in comp.rows] == [0, 50, 14]
    assert [r.descriptive for r in comp.rows] == [
        "Very Poor",
        "Average",
        "Below Average",
    ]
    assert [r.index for r in comp.rows] == [61, 100, 84]

    assert (
        rep
        == f"Developmental Test of Visual Perception (DTVP-3) - {date[1]}\n\nVisuomotorische Integration: PR <1 - Weit unter der Norm\nVisuelle Wahrnehmung mit reduzierter motorischer Reaktion: PR 50 - Norm\nGlobale visuelle Wahrnehmung: PR 14 - Unter der Norm\n\nSubtests:\nAugen-Hand-Koordination: 4;3 J (weit unterdurchschnittlich)\nAbzeichnen: 4;8 J (unterdurchschnittlich)\nFigur-Grund: 10;5 J (durchschnittlich)\nGesaltschliessen: 5;10 J (durchschnittlich)\nFormkonstanz: 6;3 J (durchschnittlich)"
    )
