import os
import subprocess
from random_eset import random_string
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime


osszehasonlito_path = r"C:\Users\nbozs\OneDrive\Documents\egyetem\házi\22-23_1\Szakdolgozat\mintaillesztesi_algoritmusok\c++_implementációk\k_diff_osszehasonlito.exe"
abra_path = f"C:\\Users\\nbozs\\OneDrive\\Documents\\egyetem\\házi\\22-23_1\\Szakdolgozat\\k_diff_ábrák\\{datetime.now().strftime('%m-%d_%H-%M-%S')}\\"
romeo_txt = "C:\\Users\\nbozs\\OneDrive\\Documents\\egyetem\\házi\\22-23_1\\Szakdolgozat\\romeo_and_juliet.txt"

algs = ["brute_force", "Horspool", "KMP", "Rabin-Karp", "Aho-Corasick", "Dinamikus"]
szinek = {alg: c for alg, c in zip(algs, sns.color_palette("tab10"))}


def eredmeny(output):
    sorok = [sor.rstrip().replace("\t\t", "\t").split("\t") for sor in output.rstrip().split("\n")]
    # if not all(sorok[0][1] == sor[1] for sor in sorok):
    #     print("Nem egyeznek meg az eredmények")
    #    print([sor[1] for sor in sorok])
    d = {sor[0]: float(sor[2]) for sor in sorok}
    return d


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


def teszt(szoveg, minta, k):
    # n + m < 32621
    ma = len(minta)
    a = []
    chunks, chunk_size = len(szoveg), 32000 - ma
    for i in range(ma, chunks, chunk_size):
        szelet = szoveg[i - ma : i + chunk_size]
        results = subprocess.run(
            (osszehasonlito_path, minta, szelet, str(k)), capture_output=True, text=True
        )
        a.append(eredmeny(results.stdout))
    return {k: sum(elem[k] for elem in a) for k in a[0].keys()}


def mozgo_k(n, m, sigma, k1, k2, step, proba):
    records = []
    for k in range(k1, k2 + 1, step):
        mintak = [minta for minta in random_string(m, sigma, int(proba**0.5 + 1))]
        for szoveg in random_string(n, sigma, int(proba**0.5 + 1)):
            for minta in mintak:
                row = teszt(szoveg, minta, k)
                row["Levenshtein-távolság"] = k
                records.append(row)

    return (
        pd.DataFrame.from_records(records).groupby("Levenshtein-távolság").mean(),
        f"n{n}__m{m}__Sigma{sigma}.csv",
        f"$n = {n}, m = {m}, |\\Sigma| = {sigma}$",
    )


def mozgominta(n, m1, m2, sigma, k, step, proba):
    dfs = []
    for m in range(m1, m2, step):
        records = []
        mintak = list(random_string(m, sigma, int(proba**0.5 + 1)))
        for szoveg in random_string(n, sigma, int(proba**0.5 + 1)):
            for minta in mintak:
                row = teszt(szoveg, minta, k)
                row["Mintaméret"] = m
                records.append(row)
        df = pd.DataFrame.from_records(records)
        df[["brute_force", "Dinamikus"]] = df[["brute_force", "Dinamikus"]].clip(
            df.quantile(0.1),
            df.quantile(0.9),
            axis=1,
        )
        dfs.append(df)
    miz = pd.concat(dfs)
    return (
        miz.groupby("Mintaméret").mean(),
        f"n{n}__Sigma{sigma}__k{k}.csv",
        f"$n = {n}, |\\Sigma| = {sigma}, k = {k}$",
    )


def mozgoabc(n, m, sigma1, sigma2, k, step, proba):
    dfs = []
    for sigma in range(sigma1, sigma2 + 1, step):
        records = []
        for szoveg in random_string(n, sigma, int(proba**0.5 + 1)):
            for minta in random_string(m, sigma, int(proba**0.5 + 1)):
                row = teszt(szoveg, minta, k)
                row["ábécéméret"] = sigma
                records.append(row)
        df = pd.DataFrame.from_records(records)
        df[["brute_force", "Dinamikus"]] = df[["brute_force", "Dinamikus"]].clip(
            df.quantile(0.1),
            df.quantile(0.9),
            axis=1,
        )
        dfs.append(df)
    miz = pd.concat(dfs)
    return (
        miz.groupby("ábécéméret").mean(),
        f"n{n}__m{m}__k{k}.csv",
        f"$n = {n}, m = {m}, k = {k}$",
    )


def mozgoszoveg(n1, n2, m, sigma, k, step, proba):
    dfs = []
    for n in range(n1, n2 + 1, step):
        records = []
        for szoveg in random_string(n, sigma, int(proba**0.5 + 1)):
            for minta in random_string(m, sigma, int(proba**0.5 + 1)):
                row = teszt(szoveg, minta, k)
                row["Szövegméret"] = n
                records.append(row)
            df = pd.DataFrame.from_records(records)
            df[["brute_force", "Dinamikus"]] = df[["brute_force", "Dinamikus"]].clip(
                df.quantile(0.1),
                df.quantile(0.9),
                axis=1,
            )
        dfs.append(df)
    miz = pd.concat(dfs)
    return (
        miz.groupby("Szövegméret").mean(),
        f"m{m}__Sigma{sigma}__k{k}.csv",
        f"$m = {m}, |\\Sigma| = {sigma}, k = {k}$",
    )


def shakespeare(minta, k1, k2, step, proba):
    with open(romeo_txt, "r") as f:
        szoveg = f.read()
    szoveg = "".join([c.lower() for c in szoveg if c.isalpha()])  # csak a betűk maradnak meg
    df = []
    records = []
    for k in range(k1, k2 + 1):
        row = teszt(szoveg, minta, k)
        row["Találatok száma"] = k
        records.append(row)
    df = pd.DataFrame.from_records(records)
    df[["brute_force", "Dinamikus"]] = df[["brute_force", "Dinamikus"]].clip(
        df.quantile(0.1),
        df.quantile(0.9),
        axis=1,
    )
    return (
        df.groupby("Találatok száma").mean(),
        f"n{len(szoveg)}__sigma{26}__Romeo.csv",
        f"Romeo and Juliet, $n = {len(szoveg)}, |\\Sigma| = {26}$",
    )


def myplot(df, nev, cim):
    global szinek
    fig, axis = plt.subplots(figsize=(8, 4))
    # df2 = df.apply(my_filter)
    df.plot.line(title=cim, ax=axis, ylabel="Idő (ms)", color=szinek)
    axis.set_ylim(ymin=0)
    # df2.plot.line(
    #    title=caption + " Savitzky-Golay szűrővel", ax=axis[1], ylabel="Idő (s)"
    # )
    # plt.savefig(abra_path + nev)
    df.to_csv(abra_path + nev, float_format="%.2f")
    print(f"{nev} kész")


probak = 10
if __name__ == "__main__":
    print(datetime.now())
    os.mkdir(abra_path)
    idezet = "Deny thy father and refuse thy name!\nOr, if thou wilt not, be but sworn my love,\nAnd I'll no longer be a Capulet."
    # args = shakespeare(idezet, 0, 20, 1, probak)
    # myplot(*args)
    # args = mozgo_k(30000, 50, 26, 2, 20, 2, probak)
    # myplot(*args)
    # args = mozgoabc(30000, 50, 4, 40, 3, 4, probak)
    # myplot(*args)
    args = mozgominta(30000, 40, 401, 26, 3, 40, probak)
    myplot(*args)
    # args = mozgoszoveg(10000, 100000, 100, 26, 3, 10000, probak)
    # myplot(*args)
