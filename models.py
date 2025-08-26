import os
import datetime
import atexit
from sqlalchemy import create_engine, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker, DeclarativeBase, mapped_column, Mapped, relationship

from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv()

POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")

PG_DSN = (
    f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@"
    f"{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
)

# Подключаемся к движку
engine = create_engine(PG_DSN)
Session = sessionmaker(bind=engine)


# Базовый класс Base
class Base(DeclarativeBase):
    pass

# Модель Пользователь
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String, name="email", unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String, name="password", nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.now)

    # Связь с объявлениями
    announcements = relationship("Announcement", back_populates="user")

    def set_password(self, password: str):
        '''Устанавливаем хэш пароля'''
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        '''Проверяем пароль'''
        return check_password_hash(self.password_hash, password)

    @property
    def json_format(self):
        return {
            "id": self.id,
            "email": self.email,
            "created_at": self.created_at.isoformat()
        }

# Модель Объявления
class Announcement(Base):
    __tablename__ = "announcements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    headline: Mapped[str] = mapped_column(String, name="headline")
    description: Mapped[str] = mapped_column(String, name="description")
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.now)
    owner: Mapped[str] = mapped_column(String, name="owner")

    # Связь с пользователем
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="announcements")

    @property
    def id_json(self):
        return {"id": self.id}
    
    @property
    def json_format(self):
        return {
            "id": self.id,
            "headline": self.headline,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
            "owner": self.owner,
            "user_id": self.user_id
        }


# Выполняем регистрацию закрытия движка
atexit.register(engine.dispose)

