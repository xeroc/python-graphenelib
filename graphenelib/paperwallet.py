#!/usr/bin/env python
import csv
import qrcode
import qrcode.image.svg
import lxml.etree as et
from copy import deepcopy
import os
import graphenetools.bip38 as bip38
import graphenetools.address as Address
import sys

path = os.path.dirname(__file__)

def paperwallet(wif, address, fronttext, asset, encrypt="", design="cass", backtext1=None, backtext2=None, backtext3=None, backQRcode=None) :
    svgfront     = path + "/paperwallet/designs/"+design+"-front.svg"
    svgback      = path + "/paperwallet/designs/"+design+"-back.svg"
    ''' 
    Front Page
    '''
    try :
        fp = open(svgfront,'r')
    except :
        raise Exception("Cannot open SVG template file %s" % svgfront)
    dom   = et.parse(fp)
    root  = dom.getroot()
    for layer in root.findall("./{http://www.w3.org/2000/svg}g") :
        ## QRcode address
        if layer.get("{http://www.inkscape.org/namespaces/inkscape}label") == "QRaddress" :
            qr = qrcode.make(address, image_factory=qrcode.image.svg.SvgPathImage, error_correction=qrcode.constants.ERROR_CORRECT_L) # L,M,Q,H
            l = layer.find("{http://www.w3.org/2000/svg}rect")
            if l is not None :
                x = float(l.get("x"))
                y = float(l.get("y"))
                scale = float(layer.find("{http://www.w3.org/2000/svg}rect").get("width"))/(qr.width+2*qr.border)
                layer.set("transform","translate(%f,%f) scale(%f)" % (x,y,scale))
                layer.append(qr.make_path())
                layer.remove(layer.find("{http://www.w3.org/2000/svg}rect"))
        ## QRcode privkey
        if layer.get("{http://www.inkscape.org/namespaces/inkscape}label") == "QRprivkey" :
            if encrypt : # (optionally) encrypt paper wallet
                try : 
                    encwif = bip38.bip38_encrypt(wif,encrypt)
                except :
                    raise Exception("Error encoding the privkey for address %s. Already encrypted?" % address)
                assert bip38.bip38_decrypt(encwif, encrypt) == wif, "Verification of encrypted privkey failed!"
                qr = qrcode.make(encwif, image_factory=qrcode.image.svg.SvgPathImage, error_correction=qrcode.constants.ERROR_CORRECT_M) # L,M,Q,H
            else :
                qr = qrcode.make(wif, image_factory=qrcode.image.svg.SvgPathImage, error_correction=qrcode.constants.ERROR_CORRECT_M) # L,M,Q,H

            l = layer.find("{http://www.w3.org/2000/svg}rect")
            if l is not None :
                x = float(l.get("x"))
                y = float(l.get("y"))
                scale = float(layer.find("{http://www.w3.org/2000/svg}rect").get("width"))/(qr.width+2*qr.border)
                layer.set("transform","translate(%f,%f) scale(%f)" % (x,y,scale))
                layer.append(qr.make_path())
                layer.remove(layer.find("{http://www.w3.org/2000/svg}rect"))
        ## Address
        if layer.get("{http://www.inkscape.org/namespaces/inkscape}label") == "textaddress" :
            ## Verify that private keys is for given address
            if Address.priv2btsaddr(Address.wif2hex(wif)) == address :
                ltext = layer.find("{http://www.w3.org/2000/svg}text")
                if ltext is not None :
                    l = ltext.find("{http://www.w3.org/2000/svg}tspan")
                    if l == None:
                        print("text area for plain text address not given in SVG")
                    else :
                        l.text = address
            else :
                raise Exception("Given address does not pair to given private key!")
        if fronttext :
            if layer.get("{http://www.inkscape.org/namespaces/inkscape}label") == "textamount" :
                ltext = layer.find("{http://www.w3.org/2000/svg}text")
                if ltext is not None :
                    l = ltext.find("{http://www.w3.org/2000/svg}tspan")
                    if l == None:
                        print("text area for fronttext not given in SVG")
                    else :
                        l.text = fronttext
        ## Asset logo
        if layer.get("{http://www.inkscape.org/namespaces/inkscape}label") == "assetlogo" :
            if asset :
                assetfile = path + "/paperwallet/BitAssets/bit%s-accepted-flat-square-2.svg" % asset.upper()
                assetlogodom   = et.parse(open(assetfile,'r'))
                assetlogoroot  = assetlogodom.getroot()
                l = layer.find("{http://www.w3.org/2000/svg}rect")
                if l is not None :
                    x = float(l.get("x"))
                    y = float(l.get("y"))
                    scale = float(layer.find("{http://www.w3.org/2000/svg}rect").get("width"))/float(assetlogoroot.get("width").split("px")[0])
                    layer.set("transform","translate(%f,%f) scale(%f)" % (x,y,scale))
                    layer.append(deepcopy(assetlogoroot))
                    layer.remove(layer.find("{http://www.w3.org/2000/svg}rect"))
    front = et.tostring(dom, pretty_print=True)

    ''' 
    Back Page
    '''
    try :
        fp = open(svgback,'r')
    except :
        raise Exception("Cannot open SVG template file %s" % svgback)
    dom   = et.parse(fp)
    root  = dom.getroot()
    for layer in root.findall("./{http://www.w3.org/2000/svg}g") :
        ## QRcode address
        if backQRcode :
            if layer.get("{http://www.inkscape.org/namespaces/inkscape}label") == "QRcode" :
                qr = qrcode.make(backQRcode, image_factory=qrcode.image.svg.SvgPathImage, error_correction=qrcode.constants.ERROR_CORRECT_L) # L,M,Q,H
                x = float(layer.find("{http://www.w3.org/2000/svg}rect").get("x"))
                y = float(layer.find("{http://www.w3.org/2000/svg}rect").get("y"))
                scale = float(layer.find("{http://www.w3.org/2000/svg}rect").get("width"))/(qr.width+2*qr.border)
                layer.set("transform","translate(%f,%f) scale(%f)" % (x,y,scale))
                layer.append(qr.make_path())
                layer.remove(layer.find("{http://www.w3.org/2000/svg}rect"))
        if backtext1 :
            if layer.get("{http://www.inkscape.org/namespaces/inkscape}label") == "Text1" :
                ltext = layer.find("{http://www.w3.org/2000/svg}text")
                if ltext is not None :
                    if l == None:
                        print("text area for fronttext not given in SVG")
                    else :
                        l.text = backtext1
        if backtext2 :
            if layer.get("{http://www.inkscape.org/namespaces/inkscape}label") == "Text2" :
                ltext = layer.find("{http://www.w3.org/2000/svg}text")
                if ltext is not None :
                    if l == None:
                        print("text area for fronttext not given in SVG")
                    else :
                        l.text = backtext2
        if backtext3 :
            if layer.get("{http://www.inkscape.org/namespaces/inkscape}label") == "Text3" :
                ltext = layer.find("{http://www.w3.org/2000/svg}text")
                if ltext is not None :
                    if l == None:
                        print("text area for fronttext not given in SVG")
                    else :
                        l.text = backtext3
    back = et.tostring(dom, pretty_print=True)

    return front, back

if __name__ == '__main__':
    wif = Address.newwif()
    address = Address.wif2btsaddr(wif)
    front,back = paperwallet(wif, address, "front text", "USD", encrypt=None, design="cass", backtext1="Text1", backtext2="text2", backtext3="text3", backQRcode="http://delegate.xeroc.org")
    print(str(back))
