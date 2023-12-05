import random as r
import time as t
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from xpath import *
from transactions_opbnb import *
from print_info import *
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


def check_balance_tbnb(next_address):
    checksum_address = Web3.to_checksum_address(next_address)
    balance = web3.eth.get_balance(checksum_address)
    return balance / (10 ** 18)


def check_balance_usdt(address):
    balance_of_token = usdt_contract.functions.balanceOf(
        address).call()
    token_decimals = usdt_contract.functions.decimals().call()
    balance = balance_of_token / 10 ** token_decimals
    return round(balance, 2)


def get_current_address():
    # Створення сесії
    Session = sessionmaker(bind=engine)
    session = Session()

    # Знаходження ID останнього гаманця з is_passed == True
    last_passed_wallet_id = session.query(WalletAction.wallet_id)\
                                   .filter(WalletAction.is_passed == True)\
                                   .order_by(WalletAction.wallet_id.desc())\
                                   .first()

    # Знаходження максимального ID гаманця
    max_wallet_id = session.query(func.max(WalletEth.id)).scalar()


    if last_passed_wallet_id:
        last_passed_wallet_id = last_passed_wallet_id[0]

        # Перевірка балансів гаманців, починаючи з останнього де is_passed == True
        for wallet_id in range(last_passed_wallet_id, max_wallet_id+1):
            address = session.query(WalletEth.adress).filter(WalletEth.id == wallet_id).first()
            if address:
                address = address[0]
                if check_balance_tbnb(address) >= 0.005 and check_balance_usdt(address) >= 10:
                    return address
    else:
        # Повернення адреси гаманця з найменшим ID, якщо немає is_passed == True
        address = session.query(WalletEth.adress).order_by(WalletEth.id).first()
        if address:
            return address[0]

    return ValueError('Не знайдено відповідний гаманець з достатнім балансом')


current_address = get_current_address()


def get_current_key(address=current_address):
    # Створення сесії
    Session = sessionmaker(bind=engine)
    session = Session()

    private_key = session.query(WalletEth.private_key).filter(WalletEth.adress == address).first()[0]
    return private_key


# Ініціалізація опцій для Chrome
options = Options()
options.add_extension(metamask_extension_path)
options.add_argument(f'--user-data-dir={metamask_data_path}')

# Створення сервісу з автоматичним вибором порту
service = Service(ChromeDriverManager().install())

# Ініціалізація браузера з вказаними опціями та сервісом
driver = webdriver.Chrome(service=service, options=options)


def before_trade():
    # Відкриття веб-сайту KiloEx
    global wait
    driver.get(kiloex_url)
    wait = WebDriverWait(driver, 30)
    # Натискаємо Connect Wallet
    wait.until(EC.element_to_be_clickable((By.XPATH, connect_wallet))).click()

    # Обираємо гаманець
    t.sleep(3)
    connect_button = wait.until(EC.element_to_be_clickable((By.XPATH, choose_wallet)))
    connect_button.click()

    return colored_input("Confirm in Metamask!\nPress Enter to continue...", Fore.CYAN)


def get_my_volume(address=current_address):
    # Створення сесії
    Session = sessionmaker(bind=engine)
    session = Session()

    wallet = session.query(WalletEth).filter(WalletEth.adress == address).first()
    if wallet is None:
        print_colored('Гаманець не знайдено.', "error")
        return 0 # False

    wallet_id = wallet.id

    total_volume = session.query(func.sum(WalletAction.amount)).filter(WalletAction.wallet_id == wallet_id).scalar()

    if total_volume is None:
        total_volume = 0

    return total_volume


def buy(amount):
    balance = check_balance_usdt(current_address)

    # Знайдіть поле вводу за XPath
    driver.find_element(By.XPATH, input_amount).send_keys(amount)

    # Опціонально: Надішліть форму
    wait.until(EC.element_to_be_clickable(
        (By.XPATH, buy_confirm))).click()

    print()
    t.sleep(15)

    if int(balance - check_balance_usdt(current_address)) * 2 == amount:
        return True
    return False


def go_to_next_wallet(address=current_address):
        print_colored('Відбувається процес переходу на наступний гаманець', "warning")
        print()
        # Створення сесії
        Session = sessionmaker(bind=engine)
        session = Session()

        wallet = session.query(WalletEth).filter(WalletEth.adress == address).first()
        if wallet is None:
            print_colored('Гаманець не знайдено.', "error")
            return False

        wallet_id = wallet.id + 1

        new_address = session.query(WalletEth.adress).filter(WalletEth.id == wallet_id).scalar()

        balance_usdt = check_balance_usdt(address)
        balance_tbnb = check_balance_tbnb(address)

        if balance_usdt >= 10:
            try:
                t.sleep(20)
                print(send_usdt(from_address=address, to_address=new_address, amount=balance_usdt - 0.1, private_key=get_current_key(address)))
                print_colored(f'{balance_usdt}USDT - Успішно відправлені на {new_address}', 'info')
                print()
            except Exception as err:
                print_colored(f'Помилка при відправці {balance_usdt}USDT на {new_address}', 'error')
                print_colored(err, 'error')

        if balance_tbnb >= 0.005:
            try:
                t.sleep(20)
                print(send_tbnb(from_address=address, to_address=new_address, amount=check_balance_tbnb(address) - 0.01, private_key=get_current_key(address)))
                print_colored(f'{balance_tbnb}TBNB - Успішно відправлені на {new_address}', 'info')
            except Exception as err:
                print_colored(f'Помилка при відправці {balance_tbnb}TBNB на {new_address}', 'error')
                print_colored(err, 'error')

        print()
        print_colored(f'Скопіюй ключ для авторизації в гаманці: {get_current_key(new_address)}', "warning")
        t.sleep(60)
        colored_input("Press Enter to continue...", Fore.CYAN)

        print()
        print_colored(f'Наш новий гаманець: {get_current_address()}', "info")


def make_volume_trade(address=current_address, amount=int(check_balance_usdt(current_address))):
    print_colored(f'Поточний гаманець торговлі: {address}', "warning")
    print()

    total_volume = get_my_volume(address)

    if total_volume < max_volume:
        while total_volume < r.randint(min_volume, max_volume):
            buy(amount)
            amount = round(check_balance_usdt(address)) * xsize * 2
            print()
            print_colored(f'Купуємо на {amount} USDT', "info")
            total_volume = get_my_volume(address)

            # Створення сесії
            Session = sessionmaker(bind=engine)
            session = Session()

            current_wallet_id = session.query(WalletEth.id).filter(WalletEth.adress == address).scalar()

            count_points = amount * 0.05
            add_points(wallet_id=current_wallet_id, count_points=count_points)
            add_points(wallet_id=current_wallet_id - 1, count_points=count_points // 3)

            create_action(address=address, amount=amount, operation_name='buy+sell', points=count_points, referral_link=kiloex_url)
            print_colored(f'Поточный об`єм: {total_volume}', 'info')
            print()
            t.sleep(30)
            colored_input("Press Enter to next step...", Fore.CYAN)
    return True


def main():
    print(before_trade())

    # Створення сесії
    Session = sessionmaker(bind=engine)
    session = Session()

    address = current_address
    id_wallet = session.query(WalletEth).filter(WalletEth.adress == address).first()
    max_id_wallet = session.query(func.max(WalletEth.id)).scalar()

    if make_volume_trade() is True:
        if id_wallet != max_id_wallet:
            go_to_next_wallet()

            # Закриття браузера
            driver.quit()

            print_colored('Ви успішно перейшли на наступний гаманець з вашого списку!', 'info')
            print()
            print_colored('Для роботи з наступним гаманцем перезавантажуємо скрипт [...]', "warning")
            t.sleep(30)

        print_colored('Мої вітання! Всі гаманці з бази даних заповнені!', 'info')
        return 'The End'


print_colored('DONATE - 0x4A080654795e526801954493BD0D712609d0ccEF', "critical")
print()
print(main())
colored_input("Press Enter to finish...", Fore.CYAN)

