'''Инициализация Базы Данных'''
from models import Base, engine


Base.metadata.create_all(engine)

def create_tables():
    '''Создание таблиц в БД'''
    print("Создаем таблицы...")
    Base.metadata.create_all(engine)
    print("Таблицы успешно созданы!")

def drop_tables():
    '''Удаление таблиц из БД'''
    print("Удаляем таблицы...")
    Base.metadata.drop_all(engine)
    print("Таблицы успешно удалены!")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "drop":
        drop_tables()
    else:
        create_tables()

        