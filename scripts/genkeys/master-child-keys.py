from prettytable import PrettyTable, ALL
from graphenebase.account import BrainKey
import graphenebase.bip38 as bip38
import argparse
import csv
import qrcode
from io import StringIO

prefix = "BTS"

"""
Usage:

    $ python3 master-child-keys.py --number 2 | paps --font="Monospace 7" | lp -d samsung

"""


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

        qrwif = StringIO()
        qr = qrcode.QRCode(error_correction=qrcode.ERROR_CORRECT_H)
        qr.add_data(wif)
        qr.print_ascii(out=qrwif, tty=False, invert=False)

        qrpub = StringIO()
        qr = qrcode.QRCode(error_correction=qrcode.ERROR_CORRECT_H)
        qr.add_data(pub)
        qr.print_ascii(out=qrpub, tty=False, invert=False)

        t.add_row(["%s%s" % (qrwif.getvalue(), wif),
                   "%s%s" % (qrpub.getvalue(), pub),
                   b.sequence])
        b.next_sequence()

    print("This is your (unencrypted) Brainkey. Make sure to store it savely:")
    print("\n\n\t%s\n\n" % b.get_brainkey())

    t.hrules = 1
    t.vrules = 1
    t.padding_width = 1
    t.header = False
    data = t.get_string()
    print(data)

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
