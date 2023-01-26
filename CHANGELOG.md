# Changelog
Note: version releases in the 0.x.y range may introduce breaking changes.

<!--next-version-placeholder-->

## v1.6.0 (2023-01-26)
### Feature
* **py3.6:** Remove python3.6. support ([`d2210b6`](https://github.com/xeroc/python-graphenelib/commit/d2210b602c9ec8ed574515914d84915d22694933))

### Fix
* Add fallback for ripemd160 failing in openssl ([`27ba578`](https://github.com/xeroc/python-graphenelib/commit/27ba5789aa402588f2cf0ca6abca5b2cce746812))
* Remove python3.7 from tests ([`48b4131`](https://github.com/xeroc/python-graphenelib/commit/48b41317716be93fe2a282bcd2c5a63c23c18e77))
* Resolve infinite loop ([`647fe0e`](https://github.com/xeroc/python-graphenelib/commit/647fe0e615987959d52472150b01a2040bc25188))
* Only change cache once ([`8475157`](https://github.com/xeroc/python-graphenelib/commit/84751577d41648b2f81cd534a2bd8b6e9c6d83d9))
* Store items duplicate check ([`8042015`](https://github.com/xeroc/python-graphenelib/commit/80420159a4bd75dfe54f1ca8c691d1319b1d15e7))
* **http:** Make use of http-keep alive ([`0b9131c`](https://github.com/xeroc/python-graphenelib/commit/0b9131c26a3a4c5a6d5c4ccabfb002088043dc70))
* Do not use negative instance numbers ([`7ff7452`](https://github.com/xeroc/python-graphenelib/commit/7ff745258f26681cdd872f3eb1ba7b2d0f80d6fc))

### Documentation
* Update docs ([`cb608fc`](https://github.com/xeroc/python-graphenelib/commit/cb608fcdcb18e8a93a6461994b325f34a9e9d3b6))
* Linting ([`2d26fe8`](https://github.com/xeroc/python-graphenelib/commit/2d26fe89834a79b801ee5219c75936e74b34cda1))

## v1.5.4 (2022-05-13)
### Fix
* Empty commit to trigger release ([`e3498fd`](https://github.com/xeroc/python-graphenelib/commit/e3498fd01c2b1e315bc44911a71375afcae9601e))

### Documentation
* Release flow and conventional commits ([`a75a1f6`](https://github.com/xeroc/python-graphenelib/commit/a75a1f69ce3d55f4804c969f366b1c429693bee1))

## v1.5.3 (2022-05-13)
### Fix
* Setup.cfg lib should work with >=3.6 too ([`1023aa3`](https://github.com/xeroc/python-graphenelib/commit/1023aa30d07901339e4db6c7c536993e7501c3da))
* Remove irrelevant unittest ([`4118481`](https://github.com/xeroc/python-graphenelib/commit/41184817a532fc0e7cf5452fd715123e8a311a66))
* Get rid of appveyor.yml ([`70e2649`](https://github.com/xeroc/python-graphenelib/commit/70e2649fcf9659ebc53e09427c82bc15e4a85b98))
* Bump websockets dependency ([`a1bcaaf`](https://github.com/xeroc/python-graphenelib/commit/a1bcaaf09c9e612988b31a8de40240c7ed98003c))

## 1.5.2

- patch: Expire TaPos cache
- patch: Make lib work with new secp256k1-py

## 1.5.1

- patch: Excplicit proposal logging
- patch: Remove unecessary logging

## 1.5.0

- minor: Make use of ExpiringDict to limit memory usage in cache

## 1.4.4

- patch: Make the caching key explicit

## 1.4.3

- patch: Improve caching significantly

## 1.4.2

- patch: Do not break backwards compatibility on ObjectCache

## 1.4.1

- patch: Improve caching and allow to use an external cache

## 1.4.0

- minor: Add Hash160

## 1.3.4

- patch: Fix an issue with vesting balances raising exceptions

## 1.3.3

- patch: Bug fixes

## 1.3.2

- patch: Bug fixes

## 1.3.1

- patch: Add aio packages to setup.py

## 1.3.0

- minor: Release asyncio support

## 1.2.0

- minor: Use the last irreversible block for tapos ref params

## 1.1.20

- patch: updates from pyup

## 1.1.19

- patch: First release after semversioner

## 1.1.18

- patch: Starting version for semversioner
