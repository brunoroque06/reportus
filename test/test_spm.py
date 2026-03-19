import datetime

import pytest

from src.report import spm


@pytest.mark.parametrize(("ver"), [1, 2])
def test_data(ver: spm.Version):
    spm.validate(ver)


@pytest.mark.parametrize(
    ("form", "ver", "raw", "ts", "exp_rep"),
    [
        (
            "Classroom",
            1,
            {
                "soc": 27,
                "vis": 4,
                "hea": 15,
                "tou": 12,
                "t&s": 4,
                "bod": 10,
                "bal": 24,
                "pln": 28,
            },
            {
                "soc": 64,
                "vis": 40,
                "hea": 69,
                "tou": 63,
                "bod": 57,
                "bal": 72,
                "pln": 70,
                "st": 63,
            },
            'Sensory Processing Measure (SPM 1): Classroom Form\nFragebogen zur sensorischen Verarbeitung ausgefüllt von ignore des Kindes (03.2026)\n\nVision: PR 16 - "Typical"\nHearing: PR 97 - "Some Problems"\nTouch: PR 90 - "Some Problems"\nBody Awareness: PR 76 - "Typical"\nBalance and Motion: PR 98 - "Definite Dysfunction"\n\nGesamttestwert: PR 90 - "Some Problems"\n\nPlanning and Ideas: PR 97 - "Definite Dysfunction"\nSocial: PR 92 - "Some Problems"',
        ),
        (
            "Home",
            1,
            {
                "soc": 26,
                "vis": 14,
                "hea": 11,
                "tou": 18,
                "t&s": 8,
                "bod": 22,
                "bal": 18,
                "pln": 26,
            },
            {
                "soc": 66,
                "vis": 57,
                "hea": 59,
                "tou": 63,
                "bod": 67,
                "bal": 63,
                "pln": 72,
                "st": 63,
            },
            'Sensory Processing Measure (SPM 1): Home Form\nElternfragebogen zur sensorischen Verarbeitung ausgefüllt von ignore des Kindes (03.2026)\nDie Fähigkeit, sensorische Reize zu verarbeiten, beeinflusst die motorischen und selbstregulativen Fähigkeiten eines Kindes sowie sein soziales Verhalten.\n\nVision: PR 76 - "Typical"\nHearing: PR 82 - "Typical"\nTouch: PR 90 - "Some Problems"\nBody Awareness: PR 95 - "Some Problems"\nBalance and Motion: PR 90 - "Some Problems"\n\nGesamttestwert: PR 90 - "Some Problems"\n\nPlanning and Ideas: PR 98 - "Definite Dysfunction"\nSocial: PR 95 - "Some Problems"',
        ),
        (
            "Home",
            2,
            {
                "soc": 26,
                "vis": 14,
                "hea": 11,
                "tou": 18,
                "t&s": 8,
                "bod": 22,
                "bal": 18,
                "pln": 26,
            },
            {
                "soc": 65,
                "vis": 55,
                "hea": 47,
                "tou": 63,
                "bod": 68,
                "bal": 66,
                "pln": 71,
                "st": 59,
            },
            'Sensory Processing Measure (SPM 2): Home Form\nElternfragebogen zur sensorischen Verarbeitung ausgefüllt von ignore des Kindes (03.2026)\nDie Fähigkeit, sensorische Reize zu verarbeiten, beeinflusst die motorischen und selbstregulativen Fähigkeiten eines Kindes sowie sein soziales Verhalten.\n\nVision: PR 69 - "Typical"\nHearing: PR 38 - "Typical"\nTouch: PR 90 - "Moderate Difficulties"\nTaste and Smell: PR 16 - "Typical"\nBody Awareness: PR 96 - "Moderate Difficulties"\nBalance and Motion: PR 95 - "Moderate Difficulties"\n\nGesamttestwert: PR 82 - "Typical"\n\nPlanning and Ideas: PR 98 - "Severe Difficulties"\nSocial: PR 93 - "Moderate Difficulties"\n\n sensorisches Profil liegt im Bereich "Typical" und ist somit unauffällig.',
        ),
    ],
)
def test_spm(
    form: spm.Form,
    ver: spm.Version,
    raw: dict[str, int],
    ts: dict[str, int],
    exp_rep: str,
):
    today = datetime.date.today()

    res, rep = spm.process(today, form, ver, spm.Filer(None, "ignore"), "", raw)

    for i, t in ts.items():
        assert res.filter(id=i).item().t == t

    assert rep == exp_rep
