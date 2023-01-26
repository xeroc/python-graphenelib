# Changelog
Note: version releases in the 0.x.y range may introduce breaking changes.

<!--next-version-placeholder-->

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
