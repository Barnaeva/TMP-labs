import gzip
import csv


INPUT_CSV = "top-10k.csv.gz"


def read_csv(filename):
    domains = []
    with gzip.open(filename, mode="rt", encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            domains.append(row[0])
    return domains


def main():
    domains = read_csv(INPUT_CSV)

    print(domains[:10])


if __name__ == "__main__":
    main()
