import pandas as pd
from pyfpgrowth import find_frequent_patterns, generate_association_rules


def find_rules(data, support_threshold, confidence_threshold):
    patterns = find_frequent_patterns(
        transactions=data,
        support_threshold=support_threshold
    )
    rules = generate_association_rules(
        patterns=patterns,
        confidence_threshold=confidence_threshold
    )

    return rules


def extract_results(rules):
    results = []
    for k, v in rules.items():
        temp = []
        temp.append(k)
        temp.append(v[0][0])
        temp.append(v[1])
        results.append(temp)

    return results


def calculate_champions_frequency(df, champions):
    total = len(df)
    champions_count = len(df.loc[
        (df["top"] == champions)
        | (df["jungle"] == champions)
        | (df["mid"] == champions)
        | (df["bottom"] == champions)
        | (df["support"] == champions),
        :
    ])
    return champions_count / total


def generate_pick_rules():
    df = pd.read_csv("match_picks.csv")
    data = df.loc[:, "top": "support"].values
    rules = find_rules(data, 2, 0.2)

    results = extract_results(rules)
    for rule in results:
        lift = rule[2] / calculate_champions_frequency(df, rule[1])
        rule.append(lift)

    return pd.DataFrame(
        results,
        columns=["picked", "recommend", "confidence", "lift"]
    )
