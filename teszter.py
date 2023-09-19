import os
import subprocess
from random_eset import random_string
from random import randint
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime


algs = ["brute_force", "Horspool", "KMP", "Karp-Rabin", "Aho-Corasick"]
szinek = {alg: c for alg, c in zip(algs, sns.color_palette("tab10"))}

osszehasonlito_path = r"C:\Users\nbozs\OneDrive\Documents\egyetem\házi\22-23_1\Szakdolgozat\mintaillesztesi_algoritmusok\c++_implementációk\osszehasonlito.exe"
abra_path = f"C:\\Users\\nbozs\\OneDrive\\Documents\\egyetem\\házi\\22-23_1\\Szakdolgozat\\ábrák\\{datetime.now().strftime('%m-%d_%H-%M-%S')}\\"
eredmeny_path = abra_path + "eredmenyek\\"
romeo_txt = "C:\\Users\\nbozs\\OneDrive\\Documents\\egyetem\\házi\\22-23_1\\Szakdolgozat\\romeo_and_juliet.txt"
dna_path = r"C:\Users\nbozs\OneDrive\Documents\egyetem\házi\22-23_1\Szakdolgozat\dna"


def eredmeny(output):
    sorok = [sor.rstrip().replace("\t\t", "\t").split("\t") for sor in output.rstrip().split("\n")]
    # if not all(sorok[0][1] == sor[1] for sor in sorok):
    #     print("Nem egyeznek meg az eredmények")
    #    print([sor[1] for sor in sorok])
    d = {sor[0]: float(sor[2]) for sor in sorok}
    return d


def ascii_to_binary(minta):
    return "".join(["{0:08b}".format(ord(c)) for c in minta])


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


def teszt(szoveg, minta):
    # n + m < 32621
    ma = len(minta)
    a = []
    chunks, chunk_size = len(szoveg), 32000 - ma
    for i in range(ma, chunks, chunk_size):
        szelet = szoveg[i - ma : i + chunk_size]
        results = subprocess.run(
            (osszehasonlito_path, minta, szelet), capture_output=True, text=True
        )
        a.append(eredmeny(results.stdout))
    return {k: sum(elem[k] for elem in a) for k in a[0].keys()}


def mozgominta(n, m1, m2, sigma, step, proba):
    dfs = []
    for m in range(m1, m2, step):
        records = []
        mintak = list(random_string(m, sigma, int(proba**0.5 + 1)))
        for szoveg in random_string(n, sigma, int(proba**0.5 + 1)):
            for minta in mintak:
                row = teszt(szoveg, minta)
                row["Mintaméret"] = m
                records.append(row)
        df = pd.DataFrame.from_records(records)
        df[["brute_force", "Horspool", "KMP", "Karp-Rabin"]] = df[
            ["brute_force", "Horspool", "KMP", "Karp-Rabin"]
        ].clip(
            df.quantile(0.1),
            df.quantile(0.9),
            axis=1,
        )
        dfs.append(df)
    miz = pd.concat(dfs)
    return (
        miz.groupby("Mintaméret").mean(),
        f"n{n}__Sigma{sigma}.svg",
        f"$n = {n}, |\\Sigma| = {sigma} $",
    )


def mozgoabc(n, m, sigma1, sigma2, step, proba):
    dfs = []
    for sigma in range(sigma1, sigma2 + 1, step):
        records = []
        for szoveg in random_string(n, sigma, int(proba**0.5 + 1)):
            for minta in random_string(m, sigma, int(proba**0.5 + 1)):
                row = teszt(szoveg, minta)
                row["ábécéméret"] = sigma
                records.append(row)
        df = pd.DataFrame.from_records(records)
        df[["brute_force", "Horspool", "KMP", "Karp-Rabin"]] = df[
            ["brute_force", "Horspool", "KMP", "Karp-Rabin"]
        ].clip(
            df.quantile(0.1),
            df.quantile(0.9),
            axis=1,
        )
        dfs.append(df)
    miz = pd.concat(dfs)
    return (
        miz.groupby("ábécéméret").mean(),
        f"n{n}__m{m}.svg",
        f"$n = {n}, m = {m}$",
    )


def mozgoszoveg(n1, n2, m, sigma, step, proba):
    dfs = []
    for n in range(n1, n2 + 1, step):
        records = []
        for szoveg in random_string(n, sigma, int(proba**0.5 + 1)):
            for minta in random_string(m, sigma, int(proba**0.5 + 1)):
                row = teszt(szoveg, minta)
                row["Szövegméret"] = n
                records.append(row)
            df = pd.DataFrame.from_records(records)
            df[["brute_force", "Horspool", "KMP", "Karp-Rabin"]] = df[
                ["brute_force", "Horspool", "KMP", "Karp-Rabin"]
            ].clip(
                df.quantile(0.1),
                df.quantile(0.9),
                axis=1,
            )
        dfs.append(df)
    miz = pd.concat(dfs)
    return (
        miz.groupby("Szövegméret").mean(),
        f"m{m}__Sigma{sigma}.svg",
        f"$m = {m}, |\\Sigma| = {sigma} $",
    )


def shakespeare(m1, m2, step, proba):
    with open(romeo_txt, "r") as f:
        szoveg = f.read()
    szoveg = "".join([c.lower() for c in szoveg if c.isalpha()])  # csak a betűk maradnak meg
    dfs = []
    for m in range(m1, m2, step):
        records = []
        for i in range(int(proba**0.5 + 1)):
            for j in range(0, (m + 1) * 10 + 1, m + 1):
                minta = szoveg[j : j + m]
                row = teszt(szoveg, minta)
                row["Mintaméret"] = m
                records.append(row)
        df = pd.DataFrame.from_records(records)
        df[["brute_force", "Horspool", "KMP", "Karp-Rabin"]] = df[
            ["brute_force", "Horspool", "KMP", "Karp-Rabin"]
        ].clip(
            df.quantile(0.1),
            df.quantile(0.9),
            axis=1,
        )
        dfs.append(df)
    miz = pd.concat(dfs)
    return (
        miz.groupby("Mintaméret").mean(),
        f"n{len(szoveg)}__sigma{26}__Romeo.svg",
        f"Romeo and Juliet, $n = {len(szoveg)}, |\\Sigma| = {26}$",
    )


def shakespeare_bin(m1, m2, step, proba):
    with open(romeo_txt, "r") as f:
        szoveg = f.read()
    szoveg = ascii_to_binary(szoveg)[:100000]  # csak a betűk maradnak meg
    dfs = []
    for m in range(m1, m2, step):
        records = []
        for i in range(int(proba**0.5 + 1)):
            for j in range(0, (m + 1) * 10 + 1, m + 1):
                minta = szoveg[j : j + m]
                row = teszt(szoveg, minta)
                row["Mintaméret"] = m
                records.append(row)
        df = pd.DataFrame.from_records(records)
        df[["brute_force", "Horspool", "KMP", "Karp-Rabin"]] = df[
            ["brute_force", "Horspool", "KMP", "Karp-Rabin"]
        ].clip(
            df.quantile(0.1),
            df.quantile(0.9),
            axis=1,
        )
        dfs.append(df)
    miz = pd.concat(dfs)
    return (
        miz.groupby("Mintaméret").mean(),
        f"n{len(szoveg)}__sigma{2}__Romeo.svg",
        f"Romeo and Juliet, $n = {len(szoveg)}, |\\Sigma| = {2}$",
    )


def dna(m1, m2, step, proba):
    dnas = {}
    for root, dirs, files in os.walk(dna_path, topdown=True):
        for name in files:
            path = os.path.join(root, name)
            if path.endswith(".fa"):
                with open(path, "r") as f:
                    sorok = f.readlines()
                dnas[sorok[0][1:].rstrip()] = sorok[1].rstrip()
    atlaghossz = sum(len(szoveg) for szoveg in dnas.values()) // len(dnas.keys())
    dfs = []
    for m in range(m1, m2, step):
        records = []
        mintak = [szoveg[-m:] for szoveg in dnas.values()]
        for szoveg in dnas.values():
            for minta in mintak:
                row = teszt(szoveg, minta)
                row["Mintaméret"] = m
                records.append(row)
        df = pd.DataFrame.from_records(records)
        df[["brute_force", "Horspool", "KMP", "Karp-Rabin"]] = df[
            ["brute_force", "Horspool", "KMP", "Karp-Rabin"]
        ].clip(
            df.quantile(0.1),
            df.quantile(0.9),
            axis=1,
        )
        dfs.append(df)
    miz = pd.concat(dfs)
    return (
        miz.groupby("Mintaméret").mean(),
        f"DNA.svg",
        f"DNA, $\\overline{{n}} = {atlaghossz}, |\\Sigma| = 4$",
    )


def rabinkarp_alap(n, m, sigma, alap1, alap2, proba):
    dfs = []
    for alap in range(alap1, alap2 + 1):
        records = []
        for szoveg in random_string(n, sigma, int(proba**0.5 + 1)):
            for minta in random_string(m, sigma, int(proba**0.5 + 1)):
                row = eredmeny(
                    subprocess.run(
                        (osszehasonlito_path, minta, szoveg, str(alap)),
                        capture_output=True,
                        text=True,
                    ).stdout
                )
                row["alap"] = alap
                records.append(row)
        df = pd.DataFrame.from_records(records)
        df[["Karp-Rabin"]] = df[["Karp-Rabin"]].clip(
            df.quantile(0.1),
            df.quantile(0.9),
            axis=1,
        )
        dfs.append(df)
    miz = pd.concat(dfs)
    return (
        miz.groupby("alap").mean(),
        f"n{n}__m{m}__Sigma{sigma}.svg",
        f"$n = {n}, m = {m}, |\\Sigma| = {sigma} $",
    )


def myplot(df, nev, cim):
    fig, axis = plt.subplots(figsize=(8, 4))
    # df2 = df.apply(my_filter)
    df.plot.line(title=cim, ax=axis, ylabel="Idő (ms)")
    axis.set_ylim(ymin=0)
    # df2.plot.line(
    #    title=caption + " Savitzky-Golay szűrővel", ax=axis[1], ylabel="Idő (s)"
    # )
    plt.savefig(abra_path + nev)
    print(f"{nev} kész")
    # fig, axes = plt.subplots(nrows=4, sharex=True, figsize=(8, 6))
    # fig.suptitle(caption)
    # for i, col in enumerate(df.columns):
    #    df.plot.line(y=col, ax=axes[i], color=szinek[col])
    #    axes[i].set_ylim(ymin=0)
    # plt.savefig(fajl(miz, "s"))


probak = 400
if __name__ == "__main__":
    print(datetime.now())
    os.mkdir(abra_path)
    os.mkdir(eredmeny_path)
    # args = rabinkarp_alap(30000, 100, 2, 2, 65, 100)
    # myplot(*args)
    # args = rabinkarp_alap(30000, 100, 4, 2, 65, 100)
    # myplot(*args)
    # args = rabinkarp_alap(30000, 100, 26, 2, 65, 100)
    # myplot(*args)

    # args = mozgoabc(30000, 50, 2, 30, 1, probak)
    # myplot(*args)
    args = shakespeare_bin(7, 307, 30, probak)
    myplot(*args)
    input("X")
    args = dna(7, 307, 30, probak)
    myplot(*args)
    args = mozgominta(30000, 7, 307, 2, 30, probak)
    myplot(*args)
    args = mozgominta(30000, 7, 307, 4, 30, probak)
    myplot(*args)
    args = mozgominta(30000, 7, 307, 26, 30, probak)
    myplot(*args)
    args = mozgoszoveg(10000, 100000, 100, 2, 10000, probak)
    myplot(*args)
    args = mozgoszoveg(10000, 100000, 100, 4, 10000, probak)
    myplot(*args)
    args = mozgoszoveg(10000, 100000, 100, 26, 10000, probak)
    myplot(*args)

    print(datetime.now())
