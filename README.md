# CoinPico
WIP bitcoin wallet built with Micropython on Raspberry Pi Pico.

![CoinPico](https://github.com/rauaap/CoinPico/blob/master/coinpico.jpg)

## Requirements
A micropython build with ![secp256k1-embedded](https://github.com/diybitcoinhardware/secp256k1-embedded) and ![extended uhashlib](https://github.com/diybitcoinhardware/f469-disco/tree/master/usermods/uhashlib) are required for the elliptic curve and hash functions.

## Features
Generate a master seed using entropy from dice rolls and save it to eeprom  
Display bip-39 mnemonic for the master seed
Display addresses  
Save xpub to sd-card  

## Not yet implemented
Signing PSBT-transactions
