import os
import subprocess
from random_eset import random_string
import pandas as pd
from itertools import count
from datetime import datetime
import matplotlib.pyplot as plt
from binascii import 


tobb_minta_path = r"C:\Users\nbozs\OneDrive\Documents\egyetem\házi\22-23_1\Szakdolgozat\mintaillesztesi_algoritmusok\c++_implementációk\tobb_minta.exe"
abra_path = f"C:\\Users\\nbozs\\OneDrive\\Documents\\egyetem\\házi\\22-23_1\\Szakdolgozat\\több_mintás_ábrák\\{datetime.now().strftime('%m-%d_%H-%M-%S')}\\"
eredmeny_path = abra_path + "\\eredmenyek\\"


def eredmeny(output):
    sorok = [sor.rstrip().replace("\t\t", "\t").split("\t") for sor in output.rstrip().split("\n")]
    # if not all(sorok[0][1] == sor[1] for sor in sorok):
    #     print("Nem egyeznek meg az eredmények")
    #    print([sor[1] for sor in sorok])
    d = {sor[0]: float(sor[2]) for sor in sorok}
    return d


def teszt(szoveg, mintak):
    ma = max(len(minta) + 1 for minta in mintak)
    l = len(mintak) * (ma)
    a = []
    for i in range(0, len(szoveg), 32000 - l):
        szelet = szoveg[i : min(i + 32000 - l, len(szoveg))]
        results = subprocess.run((tobb_minta_path, *mintak, szelet), capture_output=True, text=True)
        a.append(eredmeny(results.stdout))
    return {k: sum(elem[k] for elem in a) for k in a[0].keys()}


def mozgo_minta_szam(n, m, sigma, db1, db2, step, proba):
    dfs = []
    for db in range(db1, db2 + 1, step):
        records = []
        for szoveg in random_string(n, sigma, int(proba**0.5 + 1)):
            for i in range(int(proba**0.5 + 1)):
                mintak = list(random_string(m, sigma, db))
                row = teszt(szoveg, mintak)
                row["Minták száma"] = db
                records.append(row)
        df = pd.DataFrame.from_records(records)
        df[["brute_force", "Horspool", "KMP", "Karp-Rabin", "Aho-Corasick"]] = df[
            ["brute_force", "Horspool", "KMP", "Karp-Rabin", "Aho-Corasick"]
        ].clip(
            df.quantile(0.1),
            df.quantile(0.9),
            axis=1,
        )
        dfs.append(df)
    miz = pd.concat(dfs)
    return (
        miz.groupby("Minták száma").mean(),
        {"n = ": n, "|\\Sigma| = ": sigma, "m = ": f"{m}"},
    )


def mozgo_minta_meret(n, m1, m2, sigma, db, step, proba):
    dfs = []
    for m in range(m1, m2 + 1, step):
        records = []
        for szoveg in random_string(n, sigma, proba):
            mintak = list(random_string(m, sigma, db))
            row = teszt(szoveg, mintak)
            row["Minták mérete"] = m
            records.append(row)
        df = pd.DataFrame.from_records(records)
        df[["brute_force", "Horspool", "KMP", "Karp-Rabin", "Aho-Corasick"]] = df[
            ["brute_force", "Horspool", "KMP", "Karp-Rabin", "Aho-Corasick"]
        ].clip(
            df.quantile(0.1),
            df.quantile(0.9),
            axis=1,
        )
        dfs.append(df)
    miz = pd.concat(dfs)
    return (
        miz.groupby("Minták mérete").mean(),
        {"n = ": n, "|\\Sigma| = ": sigma, "k = ": f"{db}"},
    )


def mozgo_szoveg_meret(n1, n2, m, sigma, db, step, proba):
    dfs = []
    for n in range(n1, n2 + 1, step):
        records = []
        mintak = list(random_string(m, sigma, db))
        for szoveg in random_string(n, sigma, proba):
            row = teszt(szoveg, mintak)
            row["Szöveg mérete"] = n
            records.append(row)
        df = pd.DataFrame.from_records(records)
        df[["brute_force", "Horspool", "KMP", "Karp-Rabin", "Aho-Corasick"]] = df[
            ["brute_force", "Horspool", "KMP", "Karp-Rabin", "Aho-Corasick"]
        ].clip(
            df.quantile(0.1),
            df.quantile(0.9),
            axis=1,
        )
        dfs.append(df)
    miz = pd.concat(dfs)
    return (
        miz.groupby("Szöveg mérete").mean(),
        {"m = ": m, "|\\Sigma| = ": sigma, "k = ": f"{db}"},
    )


def cim(k):
    return ", ".join(f"${key}{value}$" for key, value in k.items())


def fajl(folder, k, tipus):
    alpha = lambda x: "".join(filter(str.isalpha, x))
    return (
        folder
        + "__".join(f"{alpha(key)}_{value}" for key, value in k.items())
        .replace("\\", "")
        .replace("$", "")
        .replace("[", "")
        .replace("]", "")
        + f".{tipus}"
    )


def myplot(df, miz):
    def my_filter(window, order):
        return lambda x: savgol_filter(x, window, order)

    caption = cim(miz)
    fig, axis = plt.subplots(figsize=(8, 4))
    # df2 = df.apply(my_filter(3, 1))
    print(df)
    df.plot.line(title=caption, ax=axis, ylabel="Idő (ms)")
    axis.set_ylim(ymin=0)
    plt.savefig(fajl(abra_path, miz, "svg"))
    print(f"{fajl(abra_path, miz, 'svg')} kész")
    df.to_csv(fajl(eredmeny_path, miz, "csv"))
    # fig, axes = plt.subplots(nrows=5, sharex=True, figsize=(8, 6))
    # fig.suptitle(caption)
    # for i, col in enumerate(df.columns):
    #    df.plot.line(y=col, ax=axes[i], color=szinek[col])
    #    axes[i].set_ylim(ymin=0)
    # plt.savefig(fajl(miz, "s"))


probak = 10
if __name__ == "__main__":
    print(datetime.now())
    os.mkdir(abra_path)
    os.mkdir(eredmeny_path)

    args = mozgo_minta_szam(20000, 100, 2, 4, 204, 20, probak)  # 2 elemű abc rövid minták
    myplot(*args)
    args = mozgo_minta_szam(20000, 100, 4, 4, 204, 20, probak)  # 2 elemű abc rövid minták
    myplot(*args)
    args = mozgo_minta_szam(20000, 100, 26, 4, 204, 20, probak)  # 2 elemű abc rövid minták
    myplot(*args)

    args = mozgo_minta_meret(20000, 4, 404, 2, 70, 40, probak)  # 2 elemű abc rövid minták
    myplot(*args)
    args = mozgo_minta_meret(20000, 4, 404, 4, 70, 40, probak)  # 4 elemű abc rövid minták
    myplot(*args)
    args = mozgo_minta_meret(20000, 4, 404, 26, 70, 40, probak)  # 26 elemű abc rövid minták
    myplot(*args)

    args = mozgo_szoveg_meret(10000, 200000, 100, 2, 70, 10000, probak)
    myplot(*args)
    args = mozgo_szoveg_meret(10000, 200000, 100, 4, 70, 10000, probak)
    myplot(*args)
    args = mozgo_szoveg_meret(10000, 200000, 100, 26, 70, 10000, probak)
    myplot(*args)
    print(datetime.now())
