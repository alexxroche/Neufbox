#!/usr/bin/env python3

import base64
from hashlib import sha256
import hmac
key = b'8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918'
msg = 'OslDHrAw8e-ar9JhhR-oHkJ86-o9JCV7OZCN'
jsonBytes = bytes(msg, "ascii")
hmac_result = hmac.new(key, jsonBytes, sha256).hexdigest()
#print(f"echo -n '{msg}' | openssl dgst -sha256 -hmac  '{key.decode('utf8')}'")
print(f"echo -n '{key.decode('utf8')}' | openssl dgst -sha256 -hmac  '{msg}'")
print(hmac_result)    

"""
[d] openssl hashed_key: 8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918
[d] openssl msg: b'OslDHrAw8e-ar9JhhR-oHkJ86-o9JCV7OZCN'

[d] openssl hashed_key: f75778f7425be4db0369d09af37a6c2b9a83dea0e53e7bd57412e4b060e607f7
[d] openssl msg: b'OslDHrAw8e-ar9JhhR-oHkJ86-o9JCV7OZCN'

[i] openssl: 1a122726c8e2350e493a35b5b5d33a3a10b349093fe7ace93978a7958bbbc2c7bbedba5905e5af5f4d407421534c00c5cd1b5d5af24c2e8d3a358e5c579facb6 ;
[i] openssl: 

1a122726c8e2350e493a35b5b5d33a3a10b349093fe7ace93978a7958bbbc2c7
bbedba5905e5af5f4d407421534c00c5cd1b5d5af24c2e8d3a358e5c579facb6

printf "b'8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918'"|openssl dgst -sha256 -hmac "b'OslDHrAw8e-ar9JhhR-oHkJ86-o9JCV7OZCN'"

printf "b'f75778f7425be4db0369d09af37a6c2b9a83dea0e53e7bd57412e4b060e607f7'"|openssl dgst -sha256 -hmac "b'OslDHrAw8e-ar9JhhR-oHkJ86-o9JCV7OZCN'"
(stdin)= bbedba5905e5af5f4d407421534c00c5cd1b5d5af24c2e8d3a358e5c579facb6


  cmd = 'printf "b\'' + q + '\'"|openssl dgst -sha256 -hmac "' + str(data) + '"|cut -d" " -f2'


8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918


try1 = "echo '8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918'|tr -d '\n'|openssl dgst -sha256 -hmac 'OslDHrAw8e-ar9JhhR-oHkJ86-o9JCV7OZCN'"
try0 = "echo "b'f75778f7425be4db0369d09af37a6c2b9a83dea0e53e7bd57412e4b060e607f7"|tr -d '\n'|openssl dgst -sha256 -hmac 'OslDHrAw8e-ar9JhhR-oHkJ86-o9JCV7OZCN'"
NO try2 = "echo 'OslDHrAw8e-ar9JhhR-oHkJ86-o9JCV7OZCN'|tr -d '\n'|openssl dgst -sha256 -hmac '8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918'"
NO try3 = "echo 'OslDHrAw8e-ar9JhhR-oHkJ86-o9JCV7OZCN'|tr -d '\n'|openssl dgst -sha256 -hmac 'f75778f7425be4db0369d09af37a6c2b9a83dea0e53e7bd57412e4b060e607f7'"


# import hmac, hashlib; print(hmac.new('NhqPtmdS', b'something', hashlib.sha256).hexdigest())"
