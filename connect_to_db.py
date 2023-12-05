from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, ForeignKey, func, DateTime
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from config import DB_CONNECTION_STRING



# Створення об'єкта для роботи з базою даних
engine = create_engine(DB_CONNECTION_STRING)

# Створення базового класу для оголошення моделей
Base = declarative_base()

# Оголошення моделі для таблиці
class WalletEth(Base):
    __tablename__ = 'wallets_eth'

    id = Column(Integer, primary_key=True)
    adress = Column(String, unique=True)
    private_key = Column(String)
    seed_phrase = Column(String, unique=True)
    created_on = Column(DateTime, default=func.now())


class WalletAction(Base):
    __tablename__ = 'wallet_action'
    id = Column(Integer, primary_key=True)
    wallet_id = Column(Integer, ForeignKey('wallets_eth.id'))
    operation_name = Column(String, default='Transaction')
    amount = Column(Float, default=0.0)
    total_volume = Column(Float, default=0.0)
    is_passed = Column(Boolean, default=False)
    points = Column(Integer, default=0)
    referral_link = Column(String, default=None)
    proxy = Column(String, default=None)
    #created_on = Column(DateTime, default=func.now())


class KiloexPoints(Base):
    __tablename__ = 'kiloex_points'
    id = Column(Integer, primary_key=True)
    wallet_id = Column(Integer, ForeignKey('wallets_eth.id'), unique=True)
    point = Column(Integer, default=0)
    #created_on = Column(DateTime, default=func.now())
    #updated_on = Column(DateTime, default=func.now(), onupdate=func.now())


# Створення таблиці
Base.metadata.create_all(engine)


def add_wallet(adress, key, seed_phrase):
    try:
        # Створення сесії
        Session = sessionmaker(bind=engine)
        session = Session()

        # Створення нового запису
        new_wallet = WalletEth(adress=adress, private_key=key, seed_phrase=seed_phrase)

        # Додавання до сесії та збереження в базі даних
        session.add(new_wallet)
        session.commit()
        return
    except Exception as err:
        print(f'Попилка при записі в базу даних: {err}')
        return False


def create_action(address, amount, operation_name, points=0, referral_link=None, proxy=None):
    try:
        # Створення сесії
        Session = sessionmaker(bind=engine)
        session = Session()

        # Отримання wallet_id
        wallet = session.query(WalletEth).filter(WalletEth.adress == address).first()
        if wallet is None:
            wallet_id = 1
        else:
            wallet_id = wallet.id

        # Розрахунок total_volume
        total_volume = session.query(func.sum(WalletAction.amount))\
            .filter(WalletAction.wallet_id == wallet_id)\
            .scalar()

        if total_volume is None:
            total_volume = amount
        else:
            total_volume += amount

        # Перевірка умови
        passed = total_volume > 1000

        # Створення нового запису
        new_action = WalletAction(wallet_id=wallet_id,
                                  operation_name=operation_name,
                                  amount=amount,
                                  total_volume=total_volume,
                                  is_passed=passed,
                                  points=points,
                                  referral_link=referral_link,
                                  proxy=proxy)

        # Додавання до сесії та збереження в базі даних
        session.add(new_action)
        session.commit()
        return True
    except Exception as err:
        print(f'Помилка при записі в базу даних: {err}')
        return False


def add_points(wallet_id, count_points):
    try:
        # Створення сесії
        Session = sessionmaker(bind=engine)
        session = Session()

        # Перевірка на існування запису з wallet_id
        existing_wallet = session.query(KiloexPoints).filter(KiloexPoints.wallet_id == wallet_id).first()

        if existing_wallet:
            # Якщо запис існує, оновлення кількості балів
            existing_wallet.point += count_points
        else:
            # Якщо запису не існує, створення нового
            new_wallet = KiloexPoints(wallet_id=wallet_id, point=count_points)
            session.add(new_wallet)

        # Збереження змін у базі даних
        session.commit()
        return True
    except Exception as err:
        print(f'Попилка при записі в базу даних: {err}')
        session.rollback()
        return False
    finally:
        session.close()



