import time
from web3 import Web3
from eth_account import Account
import json
from config import *
from connect_to_db import *
from print_info import *


# Підключення до мережі opBNB
web3 = Web3(Web3.HTTPProvider(network_url))
usdt_contract_address = Web3.to_checksum_address(usdt_contract)

# инициализация USDT контракта
usdt_contract = web3.eth.contract(usdt_contract_address, abi=ERC20_ABI)


# відпрака TBNB
def send_tbnb(*, web3=web3, from_address, to_address, amount, private_key):

    # цена газа
    gas_price = web3.eth.gas_price * 2

    # количество газа
    gas = 2_000_000  # ставим побольше

    # число подтвержденных транзакций отправителя
    nonce = web3.eth.get_transaction_count(from_address)

    # 1. создаем транзакцию
    transaction = {
        'chainId': web3.eth.chain_id,
        'from': from_address,
        'to': to_address,
        'value': int(Web3.to_wei(amount, 'ether')),
        'nonce': nonce,
        'gasPrice': gas_price,
        'gas': gas,
    }

    # 2. Подписываем транзакцию с приватным ключом
    signed_txn = web3.eth.account.sign_transaction(transaction, private_key)

    # 3. Отправка транзакции
    txn_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)

    # Получаем хэш транзакции
    # Можно посмотреть статус тут https://testnet.bscscan.com/
    return print_colored(f'Хеш транзакции: {txn_hash.hex()}', 'info')


# Змінити перед використанням, відпрака USDT
def send_usdt(*, web3=web3, from_address, to_address, amount, private_key):
    dict_transaction = {
        'chainId': web3.eth.chain_id,
        'from': from_address,
        'gasPrice': web3.eth.gas_price,
        'nonce': web3.eth.get_transaction_count(from_address),
    }
    usdt_decimals = usdt_contract.functions.decimals().call()
    one_usdt = int(amount * (10 ** usdt_decimals))

    # создаём транзакцию
    transaction = usdt_contract.functions.transfer(
        to_address, one_usdt
    ).build_transaction(dict_transaction)

    # подписываем
    signed_txn = web3.eth.account.sign_transaction(transaction, private_key)

    # Отправляем, смотрим тут https://testnet.bscscan.com/
    txn_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)

    # Получаем хэш транзакции
    # Можно посмотреть статус тут https://opbnb-testnet-rpc.bnbchain.org
    return print_colored(f'Хеш транзакции: {txn_hash.hex()}', 'info')


# def new_private_key(next_address):
#     # Створення сесії
#     Session = sessionmaker(bind=engine)
#     session = Session()
#     private_key = session.query(WalletEth.private_key).filter(WalletEth.adress == next_address).first()[0]
#     return private_key


#print(check_balance_usdt(next_address))
#print(check_balance_new_wallet(next_address))

















