import binascii
import os
KEY = "@ABCDEFGHIJKLMNO"
hotpKeyVersion = 0x03
counterFile = 0x42
kbFile = 0x0800
hidMappingFile = 0x0001

try:
    from daplug.conv import *
    from daplug.utils import *
    from daplug.keyset import *
    from daplug.keyboard import *
    from daplug import *
    
    secu01 = DaplugDongle.C_MAC
    secu03 = DaplugDongle.C_MAC + DaplugDongle.C_DEC
    defKeys = KeySet(0x01, binascii.hexlify(KEY))
    DAPLUG = True
except Exception as e:
    DAPLUG = False


def _daplug_missing_info():
    print("Can not find daplug python modules.")
    print("You will not be able to enroll daplug devices.")
    print("%s" % e)
    

def _delete_HOTP(dongle):
    # Clean HOTP key
    dongle.selectFile(0x3F00)
    try:
        dongle.deleteKeys([hotpKeyVersion])
    except DaplugException as e:
        print e
        pass
    try:
        dongle.selectFile(0xC010)
        dongle.deleteFileOrDir(counterFile)
    except DaplugException as e:
        print e
        pass
    try:
        dongle.setKeyboardAtBoot(False)
    except DaplugException:
        pass
    try:
        dongle.deleteFileOrDir(kbFile)
    except DaplugException:
        pass

    try:
        # Delete HID Mapping
        dongle.selectFile(0x3F00)
        dongle.deleteFileOrDir(hidMappingFile)
    except DaplugException:
        pass

    try:
        # Delete kbFIle
        dongle.selectFile(0x3F00)
        dongle.deleteFileOrDir(kbFile)
    except DaplugException:
        pass

    try:
        dongle.selectPath([DaplugDongle.MASTER_FILE, 0xC010])
        dongle.deleteFileOrDir(counterFile)
    except DaplugException:
        pass


def init_dongle(keyboard=False,
                mapping="05060708090a0b0c0d0e",
                otplen=6):
    if not DAPLUG:
        _daplug_missing_info()
        return (None, None)
    utils.DEBUG = False
    dongle = getFirstDongle()
    _serial = dongle.getSerial()
    serial = lst2hex(_serial)
    dongle.authenticate(defKeys, secu01)
    _delete_HOTP(dongle)
    '''Generate HOTP key and install it'''
    hotpkey = binascii.hexlify(os.urandom(20))
    keys = splitKey(hotpkey)
    HOTPKey = KeySet(hotpKeyVersion, keys[0], keys[1], keys[2])
    HOTPKey.setKeyAccess(0x0000 + 20)
    HOTPKey.setKeyUsage(KeySet.USAGE_HOTP)
    dongle.putKey(HOTPKey)
    
    # Create HID mapping file
    dongle.selectFile(0x3f00)
    dongle.createFile(hidMappingFile, 10)
    # HID mapping :   b c d e f g h i j k
    dongle.write(0, mapping)
    # Create a counter file
    dongle.createCounterFile(counterFile)
    # Create Keyboard file
    if keyboard:
        dongle.selectFile(0x3f00)
        dongle.createFile(kbFile, 64)
        
        # Prepare personalization file content
        kb = KeyBoard()
        kb.addSleep(0xFFFF)
        # kb.addSleep(0xFFFF)
        # kb.addSleep(0xFFFF)
        # kb.addSleep(0xFFFF)
        # 04 is to use HID mapping - 02 is for numeric (not very good)
        kb.addHotpCode(0x04, int(otplen),
                       hotpKeyVersion,
                       counterFile)
        kb.addReturn()
        kb.zeroPad(64)
        dongle.write(0, kb.content)
        
        # Set keyboard at boot
        dongle.useAsKeyboard()
        dongle.setKeyboardAtBoot(True)
        
        # Go HID if required
        if dongle.getMode() == "usb":
            dongle.usb2hid()
    else:
        if dongle.getMode() == "hid":
            dongle.hid2usb()
            
    dongle.deAuthenticate()
    
    return (serial, hotpkey)
