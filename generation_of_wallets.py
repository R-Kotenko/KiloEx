import asyncio
import time
from web3 import Web3
from eth_account import Account
import random
from connect_to_db import add_wallet
from mnemonic import Mnemonic
from config import count_wallet


# Підключення до мережі Ethereum за допомогою Infura або іншого вузла
w3 = Web3(Web3.HTTPProvider('https://mainnet.infura.io/v3/6621569178a54c9cbb4fe6b06ee98a00'))

# Функція для створення гаманця та збереження адрес та приватного ключа у файлах
async def create_wallet():
    # Створення нового гаманця
    wallet = Account.create()
    private_key = wallet._private_key.hex()
    address = wallet.address

    # Генерація сiд-фрази
    mnemo = Mnemonic("english")
    seed_phrase = mnemo.generate(strength=128) # 128 бітів для 12 слів

    # Зберігання адреси та приватного ключа
    add_wallet(address, private_key, seed_phrase)

    with open('eth_private_key.txt', 'a') as file:
        file.write(f'{private_key}\n')

    with open('eth_adress.txt', 'a') as file:
        file.write(f'{address}\n')

    print(address, ' *** ', private_key)
    print(seed_phrase)
    print()

# Основна функція
async def main():
    for _ in range(count_wallet):
        await create_wallet()
        time.sleep(random.randint(30, 180))


asyncio.run(main())