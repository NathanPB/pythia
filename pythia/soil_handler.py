from typing import List
from functools import lru_cache


@lru_cache(maxsize=8)
def read_soil_profile_file_lines(soil_file: str) -> List[str]:
    """
    Reads a soil profile file and returns a list whitespace-stripped lines of the file.
    This function uses functools.lru_cache (size is hardcoded to 8) to avoid reading the file multiple times.
    :param soil_file: The path to the soil profile file.
    :return: A list of whitespace-stripped lines from the soil profile file.
    """
    with open(soil_file) as f:
        return [line.strip() for line in f]


def transpose(listOfLists):
    return list(map(list, zip(*listOfLists)))


def formatSoilData(header, current_data):
    transposed = transpose(current_data)
    return {k: v for k, v in zip(header, transposed)}


def read_soil_layers(profile: str, soil_files: List[str]):
    """
    Searches for the specified soil profile in the list of soil files and returns the soil layers of that profile.
    :param profile: The ID of the soil profile to read.
    :param soil_files: The list of all soil files to search through.
    :return: The soil layers of the specified soil profile.
    """
    profile = "*{}".format(profile)
    profilelines = []
    found = False

    for soilFile in soil_files:
        if found:
            break
        for line in read_soil_profile_file_lines(soilFile):
            line = line.strip()
            if line.startswith(profile):
                found = True
            if found and line == "":
                break
            if found:
                profilelines.append(line)

    in_data = False
    current_data = []
    header = []
    data = {}
    for line in profilelines:
        if line.startswith("@") and in_data:
            data.update(formatSoilData(header, current_data))
            header = []
            current_data = []
            in_data = False
        if line.startswith("@"):
            header = line[1:].split()
            if header[0] == "SLB":
                in_data = True
            else:
                in_data = False
        else:
            if in_data:
                current_data.append(line.split())
    data.update(formatSoilData(header, current_data))
    return data


def calculateSoilThickness(slb):
    thick = []
    for i, v in enumerate(slb):
        if i == 0:
            thick.append(v)
        else:
            thick.append(v - slb[i - 1])
    return thick


def calculateSoilMidpoint(slb):
    midpoint = []
    for i, v in enumerate(slb):
        if v < 40:
            midpoint.append(0.0)
        else:
            if i == 0:
                midpoint.append(0.0)
            elif slb[i - 1] > 100:
                midpoint.append(0.0)
            else:
                midpoint.append((min(100, v) + max(40, slb[i - 1])) / 2)
    return midpoint


def calculateTopFrac(slb, thickness):
    tf = []
    c = 0.0
    for i, v in enumerate(slb):
        if v < 40:
            c = 1.0
        else:
            c = 1 - ((v - 40) / thickness[i])
        tf.append(max(0.0, c))
    return tf


def calculateBotFrac(slb, thickness):
    bf = []
    c = 0.0
    for i, v in enumerate(slb):
        if i != 0:
            if slb[i - 1] > 100:
                c = 1.0
            else:
                c = (v - 100) / (thickness[i])
        bf.append(max(0.0, c))
    return bf


def calculateMidFrac(tf, bf):
    return [1 - bf[i] - tf[i] for i in range(len(tf))]


def calculateDepthFactor(mp, tf, mf):
    maths = [tf[i] + (mf[i] * (1 - (mp[i] - 40) / 60)) for i in range(len(mp))]
    return [max(0.05, m) for m in maths]


def calculateWeightingFactor(slbdm, thickness, df):
    return [slbdm[i] * thickness[i] * df[i] for i in range(len(slbdm))]


def calculateSoilLayerMass(slbdm, thickness):
    return sum([slbdm[i] * thickness[i] * 100000 for i in range(len(slbdm))])


def calculateNConcentration(n, mass):
    return (n / mass) * 1000000


def calculateICNTOT(wf, n, twf):
    return [f * n / twf for f in wf]


def calculateNDist(nconc, sbdm):
    return [nconc] * len(sbdm)


def calculateH2O(fractionalAW, slll, sdul):
    h2o = []
    fAW = fractionalAW / 100.0
    for i, ll in enumerate(slll):
        h2o.append((fAW * (sdul[i] - ll)) + ll)
    return h2o


def calculateICLayerData(soilData, run):
    slb = [int(v) for v in soilData["SLB"]]
    sbdm = [float(v) for v in soilData["SBDM"]]
    slll = [float(v) for v in soilData["SLLL"]]
    sdul = [float(v) for v in soilData["SDUL"]]

    thickness = calculateSoilThickness(slb)
    soil_mass = calculateSoilLayerMass(sbdm, thickness)
    nconc = calculateNConcentration(run["icin"], soil_mass)
    icndist = calculateNDist(nconc, sbdm)

    return transpose(
        [
            soilData["SLB"],
            calculateH2O(run["icsw%"], slll, sdul),
            [icnd * 0.1 for icnd in icndist],
            [icnd * 0.9 for icnd in icndist],
        ]
    )
