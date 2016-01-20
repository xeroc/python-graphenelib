from prettytable import PrettyTable
from graphenebase.account import BrainKey
import graphenebase.bip38 as bip38
import argparse
import csv

prefix = "BTS"


def main() :
    parser = argparse.ArgumentParser(description='Generate CSV table with brain key, pub key and private key')
    parser.add_argument('--number', type=int, help='Number of brain keys to generate')
    parser.add_argument('--filename', type=str, help='filename to store CSV file in')
    parser.add_argument('-encrypt', help='Encrypt private key with BIP38!', action='store_true')
    parser.set_defaults(number=10)
    args = parser.parse_args()

    '''
    Optionally encrypt with BIP38
    '''
    pw = ""
    if args.encrypt :
        import getpass
        while True :
            pw = getpass.getpass('Passphrase: ')
            pwck = getpass.getpass('Retype passphrase: ')
            if(pw == pwck) :
                break
            else :
                print("Given Passphrases do not match!")

    t = PrettyTable(["wif", "pub", "sequence"])
    b = BrainKey()
    for i in range(0, args.number) :
        wif = b.get_private()
        pub = format(b.get_private().pubkey, prefix)
        if args.encrypt :  # (optionally) encrypt paper wallet
            try :
                wif = format(bip38.encrypt(wif, pw), "encwif")
            except :
                raise Exception("Error encoding the privkey for pubkey %s.  Already encrypted?" % pub)
            assert format(b.get_private(), 'wif') == format(bip38.decrypt(wif, pw), 'wif')

        t.add_row([wif, pub, b.sequence])
        b.next_sequence()

    print("This is your (unencrypted) Brainkey. Make sure to store it savely:")
    print("\n\n\t%s\n\n" % b.get_brainkey())
    print(t.get_string())

    if args.filename :
        with open(args.filename, 'w') as file:
            file.write("# This is your (unencrypted) Brainkey. Make sure to store it savely:\n")
            file.write("#\n#\t%s\n#\n" % b.get_brainkey())
        with open(args.filename, 'a') as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=';')
            spamwriter.writerow(t.field_names)
            for r in t._rows :
                spamwriter.writerow(r)

if __name__ == '__main__':
    main()
