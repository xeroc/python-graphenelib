import sys
import hashlib
from binascii import hexlify,unhexlify
from Crypto.Cipher import AES
from Crypto import Random
#from graphenebase import Address
from graphenebase.account import PrivateKey, PublicKey, Address

"""
This class and the methods require python3
"""
assert sys.version_info[0] == 3, "graphenelib requires python3"

def get_shared_secret(priv, pub) :
    pub_point  = pub.point()
    priv_point = int(repr(priv),16)
    res     = pub_point * priv_point
    res_hex = '%032x' % res.x()
    return res_hex

def init_aes(shared_secret, nonce) :
    ## Shared Secret
    ss     = hashlib.sha512(unhexlify(shared_secret)).digest()
    ss_hex = hexlify(ss).decode('ascii')
    ## Seed
    seed = bytes(nonce,'ascii') + hexlify(ss)
    seed_digest = hexlify(hashlib.sha512(seed).digest()).decode('ascii')
    # AES
    key = unhexlify(seed_digest[0:64])
    iv  = unhexlify(seed_digest[64:96])
    return AES.new( key, AES.MODE_CBC, iv )

def encode_memo(priv,pub,nonce,message) :
    shared_secret = get_shared_secret(priv,pub)
    aes           = init_aes(shared_secret,nonce)
    ## Checksum
    raw      = bytes(message,'utf8')
    checksum = hashlib.sha256(raw).digest()
    raw      = (checksum[0:4] + raw);
    ## Padding
    BS    = 16
    ## FIXME: this adds 16 bytes even if not required
    pad   = lambda s : s + (BS - len(s) % BS) * b' ' #bytes(BS - len(s) % BS) 
    raw   = (pad(raw))
    ## Encryption
    return hexlify(aes.encrypt(raw)).decode('ascii')

def decode_memo(priv,pub,nonce,message) :
    shared_secret = get_shared_secret(priv,pub)
    aes           = init_aes(shared_secret,nonce)
    ## Encryption
    raw        = bytes(message,'ascii')
    cleartext  = aes.decrypt(unhexlify(raw))
    # TODO, verify checksum
    message = cleartext[4:]
    try : 
        return message.decode('utf8').strip()
    except :
        raise Exception(message)

if __name__ == '__main__':
    memo = {
      "from": "GPH6Co3ctgs6BSsGkti3iVcArMKywbwhnzKDAgmkb6J3Cad7ykDYX",
      "to": "GPH7gU4pHJ9rTUfVA6q6dEgCxgMGVLmq1YM3HRAKpj1VnTzJhrAn2",
      "nonce": "9729217759611568577",
      "message": "aac432f92a8bf52828ac1fda8a3bf6e3"
    }
    priv = PrivateKey("WIF-KEY");
    pub = PublicKey("OTHERS-PUBKEY", prefix="GPH")
    dec = decode_memo(priv,pub,memo["nonce"],memo["message"])
    print(dec)
