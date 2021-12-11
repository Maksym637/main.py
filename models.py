from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import Column, Integer, ForeignKey, VARCHAR, DateTime, Boolean

engine = create_engine('mysql+pymysql://root:Barca2381843@localhost/reservation')
engine.connect()

SessionFactory = sessionmaker(bind=engine)

Session = scoped_session(SessionFactory)

BaseModel = declarative_base()


class user(BaseModel):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    username = Column(VARCHAR(45))
    firstName = Column(VARCHAR(45))
    lastName = Column(VARCHAR(45))
    email = Column(VARCHAR(45))
    password = Column(VARCHAR(45))
    phone = Column(VARCHAR(15))
    userStatus = Column(Boolean)

    def __str__(self):
        return f"id        : {self.id}\n" \
               f"username  : {self.username}\n" \
               f"firstName : {self.firstName}\n" \
               f"lastName  : {self.lastName}\n" \
               f"email     : {self.email}\n" \
               f"password  : {self.password}\n" \
               f"phone     : {self.phone}\n" \
               f"userStatus: {self.userStatus}\n"


class querry(BaseModel):
    __tablename__ = "querry"

    id = Column(Integer, primary_key=True)
    place = Column(Integer)

    def __str__(self):
        return f"id       : {self.id}\n" \
               f"place    : {self.place}\n"


class auditorium(BaseModel):
    __tablename__ = "auditorium"

    id = Column(Integer, primary_key=True)
    is_free = Column(Boolean)

    def __str__(self):
        return f"id      : {self.id}\n" \
               f"is_free : {self.is_free}\n"


class access(BaseModel):
    __tablename__ = "access"
    id = Column(Integer, primary_key=True)
    auditorium_id = Column(Integer, ForeignKey(auditorium.id))
    user_id = Column(Integer, ForeignKey(user.id))
    start = Column(DateTime)
    end = Column(DateTime)
    querry_id = Column(Integer, ForeignKey(querry.id))

    def __str__(self):
        return f"id            : {self.id}\n" \
               f"auditorium_id : {self.auditorium_id}\n" \
               f"user_id       : {self.user_id}\n" \
               f"start_time    : {self.start}\n" \
               f"end_time      : {self.end}\n" \
               f"querry_id     : {self.querry_id}\n"


# BaseModel.metadata.create_all(engine)# Внесення значень : python models.py
# Використання міграції : alembic upgrade head