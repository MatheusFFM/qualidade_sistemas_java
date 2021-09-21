import pandas as pd


def main():
    data = pd.read_csv("results.csv")
    data.drop("Name", inplace=True, axis=1)
    correlations = data.corr(method ='pearson')
    print(correlations)

main()

