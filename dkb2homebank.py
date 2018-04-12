#! /usr/bin/env python

import argparse
import csv
from datetime import datetime

class dkb(csv.Dialect):
    delimiter = ';'
    quotechar = '"'
    doublequote = True
    skipinitialspace = False
    lineterminator = '\r\n'
    quoting = csv.QUOTE_MINIMAL

class comdirect(csv.Dialect):
    delimiter = ';'
    quotechar = '"'
    doublequote = True
    skipinitialspace = False
    lineterminator = '\r\n'
    quoting = csv.QUOTE_NONE

csv.register_dialect("dkb", dkb)
csv.register_dialect("comdirect", comdirect)

dkbFieldNames = ["buchungstag",
                  "wertstellung",
                  "buchungstext",
                  "beguenstigter",
                  "verwendungszweck",
                  "kontonummer",
                  "blz",
                  "betrag",
                  "glaeubigerID",
                  "mandatsreferenz",
                  "kundenreferenz"]

comdirectFieldNames = ["Buchungstag",
                       "Wertstellung (Valuta)",
                       "Vorgang",
                       "Buchungstext",
                       "Umsatz in EUR"]

visaFieldNames =    ["abgerechnet",
                     "wertstellung",
                     "belegdatum",
                     "umsatzbeschreibung",
                     "betrag",
                     "urspruenglicherBetrag"]

homebankFieldNames = ["date",
                      "paymode",
                      "info",
                      "payee",
                      "memo",
                      "amount",
                      "category",
                      "tags"]


def convertDkbCash(filename):
    with open(filename, 'r') as csvfile:
        dialect = csv.Sniffer().sniff(csvfile.read(1024))
        csvfile.seek(0)
        reader = csv.DictReader(transactionLines(csvfile, "Betrag"), dialect=dialect, fieldnames=dkbFieldNames)

        with open("cashHomebank.csv", 'w') as outfile:
            writer = csv.DictWriter(outfile, dialect='dkb', fieldnames=homebankFieldNames)
            for row in reader:
                writer.writerow(
                    {
                    'date': convertDate(row["Buchungstag"]),
                    'paymode': 8,
                    'info': None,
                    'payee': row["beguenstigter"],
                    'memo': row["verwendungszweck"],
                    'amount': row["betrag"],
                    'category': None,
                    'tags': None
                    })

def convertComdirectCash(filename):
    with open(filename, 'r') as csvfile:
        reader = csv.DictReader(transactionLines(csvfile, "Buchungstag"),
                                dialect='comdirect', fieldnames=comdirectFieldNames)

        with open("cashHomebank.csv", 'w') as outfile:
            writer = csv.DictWriter(outfile, dialect='comdirect',
                                    fieldnames=homebankFieldNames)
            for row in reader:
                print ''
                for key in comdirectFieldNames:
                  print key, "=", row[key]   #   Debugging
                new_row = {}
                for key, value in row.iteritems():
                  if (isinstance(value, list)):
                    new_row.update({key: value[0].replace('"', '')})
                  else:
                    new_row.update({key: value.replace('"', '')})
                writer.writerow(
                    {
                    'date': convertDate(new_row["Buchungstag"]),
                    'paymode': 8,
                    'info': None,
                    'payee': new_row["Buchungstext"], # not really
                    'memo': new_row["Buchungstext"], # not really
                    'amount': new_row["Umsatz in EUR"],
                    'category': None,
                    'tags': None
                    })

def convertVisa(filename):
    with open(filename, 'r') as csvfile:
        dialect = csv.Sniffer().sniff(csvfile.read(1024))
        csvfile.seek(0)
        reader = csv.DictReader(transactionLines(csvfile, "Betrag"), dialect=dialect, fieldnames=visaFieldNames)

        with open("visaHomebank.csv", 'w') as outfile:
            writer = csv.DictWriter(outfile, dialect='dkb', fieldnames=homebankFieldNames)
            for row in reader:
                writer.writerow(
                    {
                    'date': convertDate(row["wertstellung"]),
                    'paymode': 1,
                    'info': None,
                    'payee': None,
                    'memo': row["umsatzbeschreibung"],
                    'amount': row["betrag"],
                    'category': None,
                    'tags': None
                    })

def transactionLines(file, identifier):
    lines = file.readlines()
    i = 1
    for line in lines:
        if identifier in line:
            return lines[i:]
        i = i + 1

def convertDate(dateString):
    date = datetime.strptime(dateString, "%d.%m.%Y")
    return date.strftime('%d-%m-%Y')

def main():
    parser = argparse.ArgumentParser(description="Convert a CSV export file from DKB online banking to a Homebank compatible CSV format.")
    parser.add_argument("filename", help="The CSV file to convert.")

    group = parser.add_mutually_exclusive_group()
    group.add_argument("-v", "--visa", action="store_true", help="convert a DKB Visa account CSV file")
    group.add_argument("-d", "--dkbcash", action="store_true", help="convert a DKB Cash account CSV file")
    group.add_argument("-c", "--comdirectcash", action="store_true", help="convert a comdirect Cash account CSV file")

    args = parser.parse_args()

    if args.visa:
        convertVisa(args.filename)
        print("DKB Visa file converted. Output file: 'visaHomebank.csv'")
    elif args.dkbcash:
        convertDkbCash(args.filename)
        print("DKB Cash file converted. Output file: 'cashHomebank.csv'")
    elif args.comdirectcash:
        convertComdirectCash(args.filename)
        print("DKB Cash file converted. Output file: 'cashHomebank.csv'")
    else:
        print("You must provide the type of the CSV file (--cash for DKB Cash, --visa for DKB Visa)")


if __name__ == '__main__':
    main()
