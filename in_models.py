from models import Session, user, access, querry, auditorium

session = Session()

USER_1 = user(id=1, username="MO", firstName="Maksym", lastName="Oliinyk", email="Maks@gmail.com", password="1111", phone="2381843", userStatus=True)

USER_2 = user(id=2, username="TP", firstName="Tetiana", lastName="Piuryk", email="Tet@gmail.com", password="2222", phone="5556677", userStatus=True)

USER_3 = user(id=3, username="LM", firstName="Lesia", lastName="Mochurad", email="Lesia@gmail.com", password="3333", phone="2281961", userStatus=True)

AUDITORIUM_1 = auditorium(id=1, is_free=True)

AUDITORIUM_2 = auditorium(id=2, is_free=True)

QUERRY_1 = querry(id=1, place=10)

ACCESS_1 = access(id=1,auditorium_id=1, user_id=1, start="26.12.2021", end="30.12.2021", querry_id=1)

session.add(USER_1)
session.add(USER_2)
session.add(USER_3)
session.add(AUDITORIUM_1)
session.add(AUDITORIUM_2)
session.add(QUERRY_1)
session.commit()

session.add(ACCESS_1)

session.commit()

print(session.query(user).all()[0])
print(session.query(auditorium).all()[1])
print(session.query(querry).all())
print(session.query(access).all())

session.close()