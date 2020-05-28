# Neufbox
Scripts to interface with Neufbox NB6-MAIN-R3.5.8

Example python3 and BASH scripts to interface with the API ver 1.0 and to screen scrape the HTTP interface.

Tested on Versions: NB6-FXC-r2, NB6-MAIN-R3.5.8 (but may work with other version.)


### N.B. The documentation for versions 2.1.1 to 3.2.1 have a different, (simpler [0]) auth.checkToken protocol that is incompatible with 3.5.8, (so the hash.c script on some doc/api-rest.html pages are not going to work, even if you reverse engineer a copy of etk/crypt.h by www.efixo.net)


###### [0] Sudo code for the two hashing functions
```
2.1.1: hash=$( hmac_sha256(token, sha256(username)) )
3.5.8: hash=$( hmac_sha256(token, sha256(username)) hmac_sha256(token, sha256(pass)) )
(So 3.5.8 concatenates the two hmac_sha256 strings.)
```
##### test hashes
```
2.1.1: hash(43f6168e635b9a90774cc4d3212d5703c11c9302 admin) => 7aa3e8b3ed7dfd7796800b4c4c67a0c56c5e4a66502155c17a7bcef5ae945ffa

3.5.8: hash(43f6168e635b9a90774cc4d3212d5703c11c9302 admin pass") => 7aa3e8b3ed7dfd7796800b4c4c67a0c56c5e4a66502155c17a7bcef5ae945ffab5291d2f9420c46590e774f28047d6d824d88b04a253f5001ef5a9ba91fc06b5
3.5.8: hash(9bddb258f0e606ff19b58d0236d0c9 admin pass) => ba47f58702f3da4d671f56faa41cb060237f53529429d41c3fb0de90c089d3a2e0c0b475fc8504c223a8a4836dd3ec861fe804253cced9e997b87376bd875101
```
