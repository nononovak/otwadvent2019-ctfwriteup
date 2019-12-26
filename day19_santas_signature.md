# Santa's Signature - Crypto

> Can you forge Santa's signature?

Service: nc 3.93.128.89 1219

Download: d19536be58a82ff04dab38d842aaf97885e124d9597f9bc98d0d0e75747144e2-santas_signature.tar.gz

## Problem

The problem was simply the following python script:

```python
#!/usr/bin/env python3
import Crypto
from Crypto.PublicKey import RSA
import sys

try:
	with open("key",'r') as f:
		key = RSA.importKey(f.read())
except:
	rng = Crypto.Random.new().read
	key = RSA.generate(4096, rng)
	with open("key",'w') as f:
		f.write(key.exportKey().decode("utf-8"))

def h2i(h):
	try:
		return int(h,16)
	except Exception:
		print("Couldn't hex decode",flush=True)
		sys.exit()

header = \
"""Dear Santa,
Last christmas you gave me your public key,
to confirm it really is you please sign three
different messages with your private key.

Here is the public key you gave me:"""
print(header,flush=True)
print(key.publickey().exportKey().decode("utf-8"),flush=True)
ms = []

for i in range(1,4):
	m = h2i(input("Message %d you signed (hex encoded):" % i))
	if m in ms:
		print("I said different messages!",flush=True)
		sys.exit()
	s = [h2i(input("Signature %d:" % i))]
	if not key.verify(m,s):
		print("Looks like you aren't Santa after all!",flush=True)
		sys.exit()
	ms.append(m)

print("Hello Santa, here is your flag:",flush=True)
with open("flag",'r') as flag:
	print(flag.read(),flush=True)
```

## Solution

This was probably the easiest challenge of the competition. As if the fact that RSA being used wasn't enough, looking at the python implementation for the `RSA` class has the following comment:

```python
# /usr/lib/python3/dist-packages/Crypto/PublicKey/RSA.py
# ^^ On ubuntu 16.04

    def verify(self, M, signature):
        """Verify the validity of an RSA signature.

        :attention: this function performs the plain, primitive RSA encryption
         (*textbook*). In real applications, you always need to use proper
         cryptographic padding, and you should not directly verify data with
         this method. Failure to do so may lead to security vulnerabilities.
         It is recommended to use modules
         `Crypto.Signature.PKCS1_PSS` or `Crypto.Signature.PKCS1_v1_5` instead.
 
        :Parameter M: The expected message.
        :Type M: byte string or long

        :Parameter signature: The RSA signature to verify. The first item of
         the tuple is the actual signature (a long not larger than the modulus
         **n**), whereas the second item is always ignored.
        :Type signature: A 2-item tuple as return by `sign`

        :Return: True if the signature is correct, False otherwise.
        """
        return pubkey.pubkey.verify(self, M, signature)

```

This basically says that plain RSA without any padding is used for this computation. Creating three "signatures" and raising them to the e'th power mod N for the message will give you valid answers. For example, running this and piping the result to the service will give you the flag:

```python
import Crypto
from Crypto.PublicKey import RSA
import sys
import binascii

k = RSA.importKey(open('pub_real').read())

print(binascii.hexlify(pow(2,k.e,k.n).to_bytes(512,'big')).decode('ascii'))
print('02')

print(binascii.hexlify(pow(3,k.e,k.n).to_bytes(512,'big')).decode('ascii'))
print('03')

print(binascii.hexlify(pow(4,k.e,k.n).to_bytes(512,'big')).decode('ascii'))
print('04')
```

Given the flag, its possible the challenge creators wanted you to construct three "special" numbers - 0, 1, and -1 mod N - as the messages as these are trivial to compute with modular multiplication, but you can honestly create any answer you want. The latter three numbers in a one-liner also give the flag:

```
$ echo -e -n 'bb58dbdfd19995687d5cfa4e1e669a64462b6cda9ae8a31fe04db5d4d624959cadb91050cbbd73388f15f4eee2d760b88638680338fc2675e4a45babef0df33cb8a6541fc1f8a7d0ab77e8e58a96cd5862d3a2eeb82bf21b091648edcadac3321f72122a53ca97257386bffda9e1d1da06c55caeaca3cac75e9646812264e538a6b98e326fe4cd8e97e2e2cad02327a954f0a3102b389fe222f78d5cfbb296db049c01493b32e304c6e2ae36fbca79365d8507aafd909dd28b5ab1c05793d1a6b01c747950731bcffde079bef5e825790bb50ea2e7fc7668bda01cc886ea8ee9ee07f2a833be832128e199c691ca2a5a7c4266faef7f8cf1c01bef1d2d4b9c5abfb4e03f62005044b795c1036bb759a68be3f78fee1479991f503b11fc622969b6d7d0258ffbf005e8f8626d1024c52c9ef34723f526af3da9dc92255ba6c7066628fdec13b9a88d36f6d37d130c5ff6eeffaf31556d733c8041dc9b0c7ce3f1a8a71e7d923f7c934ce9e3353b865af21cb3741ae1bbfbf1ecd398ba1fa6c64ba116dcc79155d985ee89aa3c7b30ff581b883a50d986a462a1db372cdf31ee0350a3ccc39b0634679e2869cd9d3e0214af502f9c36c419dab20b225122b9d690b14c5ddcb61892d214c93eaecc0e44a12da230a6a90232756efee4ce09e0585537256d36e3dc2df52317e7b9f95e44fa9884700b029d0d64f501c6640b95c57e\nbb58dbdfd19995687d5cfa4e1e669a64462b6cda9ae8a31fe04db5d4d624959cadb91050cbbd73388f15f4eee2d760b88638680338fc2675e4a45babef0df33cb8a6541fc1f8a7d0ab77e8e58a96cd5862d3a2eeb82bf21b091648edcadac3321f72122a53ca97257386bffda9e1d1da06c55caeaca3cac75e9646812264e538a6b98e326fe4cd8e97e2e2cad02327a954f0a3102b389fe222f78d5cfbb296db049c01493b32e304c6e2ae36fbca79365d8507aafd909dd28b5ab1c05793d1a6b01c747950731bcffde079bef5e825790bb50ea2e7fc7668bda01cc886ea8ee9ee07f2a833be832128e199c691ca2a5a7c4266faef7f8cf1c01bef1d2d4b9c5abfb4e03f62005044b795c1036bb759a68be3f78fee1479991f503b11fc622969b6d7d0258ffbf005e8f8626d1024c52c9ef34723f526af3da9dc92255ba6c7066628fdec13b9a88d36f6d37d130c5ff6eeffaf31556d733c8041dc9b0c7ce3f1a8a71e7d923f7c934ce9e3353b865af21cb3741ae1bbfbf1ecd398ba1fa6c64ba116dcc79155d985ee89aa3c7b30ff581b883a50d986a462a1db372cdf31ee0350a3ccc39b0634679e2869cd9d3e0214af502f9c36c419dab20b225122b9d690b14c5ddcb61892d214c93eaecc0e44a12da230a6a90232756efee4ce09e0585537256d36e3dc2df52317e7b9f95e44fa9884700b029d0d64f501c6640b95c57e\n00\n00\n01\n01\n' | nc 3.93.128.89 1219
Dear Santa,
Last christmas you gave me your public key,
to confirm it really is you please sign three
different messages with your private key.

Here is the public key you gave me:
-----BEGIN PUBLIC KEY-----
MIICIjANBgkqhkiG9w0BAQEFAAOCAg8AMIICCgKCAgEAu1jb39GZlWh9XPpOHmaa
ZEYrbNqa6KMf4E211NYklZytuRBQy71zOI8V9O7i12C4hjhoAzj8JnXkpFur7w3z
PLimVB/B+KfQq3fo5YqWzVhi06LuuCvyGwkWSO3K2sMyH3ISKlPKlyVzhr/9qeHR
2gbFXK6so8rHXpZGgSJk5TimuY4yb+TNjpfi4srQIyepVPCjECs4n+Ii941c+7KW
2wScAUk7MuMExuKuNvvKeTZdhQeq/ZCd0otascBXk9GmsBx0eVBzG8/94Hm+9egl
eQu1DqLn/HZovaAcyIbqjunuB/KoM76DISjhmcaRyipafEJm+u9/jPHAG+8dLUuc
Wr+04D9iAFBEt5XBA2u3WaaL4/eP7hR5mR9QOxH8YilpttfQJY/78AXo+GJtECTF
LJ7zRyP1Jq89qdySJVumxwZmKP3sE7mojTb2030TDF/27v+vMVVtczyAQdybDHzj
8ainHn2SP3yTTOnjNTuGWvIcs3Qa4bv78ezTmLofpsZLoRbcx5FV2YXuiao8ezD/
WBuIOlDZhqRiods3LN8x7gNQo8zDmwY0Z54oac2dPgIUr1AvnDbEGdqyCyJRIrnW
kLFMXdy2GJLSFMk+rswORKEtojCmqQIydW7+5M4J4FhVNyVtNuPcLfUjF+e5+V5E
+piEcAsCnQ1k9QHGZAuVxX8CAwEAAQ==
-----END PUBLIC KEY-----
Message 1 you signed (hex encoded):Signature 1:Message 2 you signed (hex encoded):Signature 2:Message 3 you signed (hex encoded):Signature 3:Hello Santa, here is your flag:
AOTW{RSA_3dg3_c4s3s_ftw}
```
