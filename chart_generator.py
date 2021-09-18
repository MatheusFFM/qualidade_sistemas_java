import pandas as pd
import matplotlib.pyplot as plt
from enum import Enum


class XRows(Enum):
    POPULARITY = "Stars"
    SIZE = "LOC"
    ACTIVITY = "Releases"
    MATURITY = "Age"


class YRows(Enum):
    CBO = "CBO"
    DIT = "DIT"
    LCOM = "LCOM"


def generate_chart(origin, x, y, filename):
    origin.plot.scatter(x, y)
    plt.savefig(f"{filename}.png")
    plt.close()


def main():
    data = pd.read_csv("results.csv")
    for x in XRows:
        for y in YRows:
            print(f"Creating ({x.value}, {y.value}) boxplot")
            generate_chart(data, x.value, y.value, f"{x.value}-{y.value}")


if __name__ == "__main__":
    main()
