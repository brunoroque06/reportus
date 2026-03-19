import pytest

from src.report import mabc
from src.time import Delta


def test_data():
    mabc.validate()


@pytest.mark.parametrize(
    ("age", "raw", "comp_res", "agg_res", "exp_rep"),
    [
        (
            Delta(years=6),
            {
                "hg11": 17,
                "hg12": 29,
                "hg2": None,
                "hg3": 0,
                "bf1": 4,
                "bf2": 0,
                "bl11": 9,
                "bl12": 7,
                "bl2": 20,
                "bl3": 1,
            },
            {
                "bf1": 5,
                "bf2": 1,
                "bl1": 7,
                "bl11": 6,
                "bl12": 8,
                "bl2": 11,
                "bl3": 1,
                "hg1": 6,
                "hg11": 11,
                "hg12": 1,
                "hg2": 1,
                "hg3": 11,
            },
            {
                "bf": 1,
                "bl": 6,
                "hg": 5,
                "total": 3,
            },
            "Movement Assessment Battery for Children 2nd Edition (M-ABC 2) - 19.03.2026\nProtokollbogen Altersgruppe: 3-6 Jahre\n\nHandgeschicklichkeit: PR 5.0 - therapiebedürftig\nHändigkeit: Rechts\nBallfertigkeit: PR 0.1 - therapiebedürftig\nBalance: PR 9.0 - kritisch\n\nGesamttestwert: PR 1.0 - therapiebedürftig",
        ),
        (
            Delta(years=9),
            {
                "hg11": 28,
                "hg12": 25,
                "hg2": 25,
                "hg3": 1,
                "bf1": 9,
                "bf2": 7,
                "bl11": 30,
                "bl12": 9,
                "bl2": 7,
                "bl31": 5,
                "bl32": 4,
            },
            {
                "bf1": 12,
                "bf2": 11,
                "bl1": 12,
                "bl11": 13,
                "bl12": 10,
                "bl2": 1,
                "bl3": 8,
                "bl31": 11,
                "bl32": 6,
                "hg1": 11,
                "hg11": 8,
                "hg12": 14,
                "hg2": 9,
                "hg3": 6,
            },
            {
                "bf": 12,
                "bl": 6,
                "hg": 9,
                "total": 8,
            },
            "Movement Assessment Battery for Children 2nd Edition (M-ABC 2) - 19.03.2026\nProtokollbogen Altersgruppe: 7-10 Jahre\n\nHandgeschicklichkeit: PR 37.0 - unauffällig\nHändigkeit: Rechts\nBallfertigkeit: PR 75.0 - unauffällig\nBalance: PR 9.0 - kritisch\n\nGesamttestwert: PR 25.0 - unauffällig",
        ),
        (
            Delta(years=12),
            {
                "hg11": 17,
                "hg12": 23,
                "hg2": 36,
                "hg3": 4,
                "bf11": 6,
                "bf12": 5,
                "bf2": 9,
                "bl1": 18,
                "bl2": 13,
                "bl31": 4,
                "bl32": 3,
            },
            {
                "bf1": 8,
                "bf11": 7,
                "bf12": 9,
                "bf2": 16,
                "bl1": 9,
                "bl2": 11,
                "bl3": 2,
                "bl31": 1,
                "bl32": 3,
                "hg1": 9,
                "hg11": 11,
                "hg12": 8,
                "hg2": 10,
                "hg3": 6,
            },
            {
                "bf": 13,
                "bl": 6,
                "hg": 8,
                "total": 8,
            },
            "Movement Assessment Battery for Children 2nd Edition (M-ABC 2) - 19.03.2026\nProtokollbogen Altersgruppe: 11-16 Jahre\n\nHandgeschicklichkeit: PR 25.0 - unauffällig\nHändigkeit: Rechts\nBallfertigkeit: PR 84.0 - unauffällig\nBalance: PR 9.0 - kritisch\n\nGesamttestwert: PR 25.0 - unauffällig",
        ),
    ],
)
def test_mabc(
    age: Delta,
    raw: dict[str, int | None],
    comp_res: dict[str, int],
    agg_res: dict[str, int],
    exp_rep: str,
):
    comp, agg, rep = mabc.process(age, raw)

    for k, v in comp_res.items():
        assert comp.filter(id=k).item().standard == v

    for k, v in agg_res.items():
        assert agg.filter(id=k).item().standard == v

    assert rep == exp_rep
