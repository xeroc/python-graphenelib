from prettytable import PrettyTable
from graphenebase.account import BrainKey
import argparse
import csv

def main() : 
    parser = argparse.ArgumentParser(description='Generate CSV table with brain key, pub key and private key')
    parser.add_argument('--number', type=int, help='Number of brain keys to generate')
    parser.add_argument('--filename', type=str, help='filename to store CSV file in')
    parser.set_defaults(number=10)
    args = parser.parse_args()

    t = PrettyTable(["wif","pub","brainkey"])
    for i in range(0,args.number) :
        b = BrainKey()
        t.add_row([ b.get_private(), b.get_private().pubkey, b.get_brainkey()])

    print(t.get_string())

    if args.filename : 
        with open(args.filename, 'w') as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=' ; ')
            spamwriter.writerow(t.field_names)
            for r in t._rows :
                spamwriter.writerow(r)

if __name__ == '__main__':
    main()
