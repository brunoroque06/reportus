from reportus import dtvpa
from reportus.time import Delta


def test_data():
    dtvpa.validate()


def test_dtvpa():
    sub, comp, rep = dtvpa.process(
        Delta(years=12),
        {"co": 13, "fg": 4, "vse": 60, "vc": 12, "vsp": 29, "fc": 6},
    )

    assert sub["raw"].eq([13, 4, 60, 12, 29, 6]).all()  # type: ignore
    assert sub["%ile"].eq(["25", "9", "9", "25", "9", "16"]).all()  # type: ignore
    assert sub["standard"].eq([8, 6, 6, 8, 6, 7]).all()  # type: ignore

    assert comp["sum_standard"].eq([41, 21, 20]).all()  # type: ignore
    assert comp["index"].eq([78, 81, 79]).all()  # type: ignore
    assert comp["%ile"].eq(["7", "10", "8"]).all()  # type: ignore

    assert len(rep) > 0
