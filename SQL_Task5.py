import psycopg2
from pprint import pprint


def get_ids_data():
    with conn.cursor() as cur:
        cur.execute("""SELECT id FROM clients;""")
        ids_list = cur.fetchall()
        ids_res = []
        for id_ in ids_list:
            ids_res.append(id_[0])
    return ids_res

def get_phones_data():
    with conn.cursor() as cur:
        cur.execute("""SELECT phone_number FROM phone_numbers;""")
        phones_list = cur.fetchall()
        phones_res = []
        for phone in phones_list:
            phones_res.append(phone[0])
    return phones_res

def create_db():  # Функция, создающая структуру БД (таблицы)
    with conn.cursor() as cur:
        cur.execute("""
         DROP TABLE phone_numbers;
         DROP TABLE clients;
         """)
        cur.execute("""
                        CREATE TABLE IF NOT EXISTS clients(
                        id SERIAL primary key,
                        client_name varchar(30) not null,
                        client_surname varchar(30) not null,
                        client_email text not null 
                        );
                    """)
        cur.execute("""
                        CREATE TABLE IF NOT EXISTS phone_numbers(
                        id SERIAL primary key,
                        phone_number varchar(12),
                        client_id integer not null references clients(id) on delete cascade
                        );
                    """)
        conn.commit()

def client_add(client_name, client_surname, client_email):  #Функция, добавления нового клиента
    with conn.cursor() as cur:
        cur.execute("""SELECT client_email FROM clients;""")
        client_list = cur.fetchall()
        client_res = []
        for client in client_list:
            client_res.append(client[0])
        if client_email in client_res:
            print(f'Электронный адрес {client_email} уже зарегистирован в базе данных')
        else:
            cur.execute("""insert into clients (client_name, client_surname, client_email)
                           values (%s, %s, %s);
                        """, (client_name, client_surname, client_email))
        conn.commit()

def phone_add(phone_number, client_id):  #Функция, добавления телефона для существующего клиента
    ids_res = get_ids_data()
    phones_res = get_phones_data()
    with conn.cursor() as cur:
        if client_id in ids_res:
            if str(phone_number) in phones_res:
                print(f'Номер телефона {phone_number} уже зарегистирован в базе данных')
            elif len(str(phone_number)) != 12 or str(phone_number)[0] != '3' or str(phone_number)[1] != '7' or str(phone_number)[2] != '5' :
                print(f'Недопустимый формат номера. Номер должен начинаться с 375 и содержать 12 знаков.'
                      f'Корректный формат: 375ХХХХХХХХX')
            else:
                cur.execute("""insert into phone_numbers (phone_number, client_id)
                               values (%s, %s);
                            """, (phone_number, client_id))
            conn.commit()
        else:
            print(f'Клиент с id {client_id} отсутствует в базе данных')

def phone_change(phone_number, client_id):  # Функция, извеняющая номер телефона существующего клиента
    phones_res = get_phones_data()
    with conn.cursor() as cur:
        if str(phone_number) in phones_res:
            print(f'Номер телефона {phone_number} уже зарегистирован в базе данных')
        elif len(str(phone_number)) != 12 or str(phone_number)[0] != '3' or str(phone_number)[1] != '7' or str(phone_number)[2] != '5' :
            print(f'Недопустимый формат номера. Номер должен начинаться с 375 и содержать 12 знаков.'
                  f'Корректный формат: 375ХХХХХХХХX')
        else:
            cur.execute("""update phone_numbers set phone_number = %s 
                           where id = (
                           select id from phone_numbers
                           where client_id = %s 
                           limit 1);
                        """, (phone_number, client_id))
        conn.commit()

def data_change(client_id, client_name=None, client_surname=None, client_email=None, phone_number=None):  #Функция, извеняющая данные существующего клиента
    ids_res = get_ids_data()
    with conn.cursor() as cur:
        if client_id in ids_res:
            if client_name is not None:
                cur.execute("""update clients set client_name = %s 
                               where id = %s;
                            """, (client_name, client_id))
            if client_surname is not None:
                cur.execute("""update clients set client_surname = %s 
                               where id = %s;
                            """, (client_surname, client_id))
            if client_email is not None:
                cur.execute("""update clients set client_email = %s 
                               where id = %s;
                            """, (client_email, client_id))
            if phone_number is not None:
                phone_change(phone_number, client_id)
        else:
            print(f'Клиент с id {client_id} отсутствует в базе данных')
    conn.commit()

def delete_phone(phone_number):  #Функция, удаления телефона для существующего клиента
    phones_res = get_phones_data()
    with conn.cursor() as cur:
        if str(phone_number) not in phones_res:
            print(f'Номер {phone_number} не зарегистирован в базе данных')
        else:
            phone_number = str(phone_number)
            cur.execute("""delete from phone_numbers where phone_number = %s;
                        """, (phone_number,))
        conn.commit()

def delete_client(client_id):  #Функция, удаления клиента
    ids_res = get_ids_data()
    with conn.cursor() as cur:
        if client_id in ids_res:
            cur.execute("""delete from clients where id = %s;
                                    """, (client_id,))
        else:
            print(f'Клиент с id {client_id} отсутствует в базе данных')

def client_search(client_name, client_surname, client_email, phone_number=None):  #Функция, поиска клиента по его данным
    with conn.cursor() as cur:
        if phone_number is not None:
            phone_number = str(phone_number)
            cur.execute("""select client_id from phone_numbers
                           where phone_number = %s;
                        """, (phone_number,))
            id_ = cur.fetchall()[0][0]
            print(f'ID клиента с указанным номером: {id_}')
        else:
            cur.execute("""select id from clients 
                           where client_name = %s and client_surname = %s and client_email = %s; 
                        """, (client_name, client_surname, client_email))
            id_ = cur.fetchall()[0][0]
            print(f'ID клиента с указанными параметрами: {id_}')

def table_view():
    with conn.cursor() as cur:
        cur.execute("""
        SELECT * FROM clients;
        """)
        pprint(cur.fetchall())


if __name__ == "__main__":
    database = str(input('Введите название базы данных: '))
    user = str(input('Введите имя пользователя: '))
    password = str(input('Введите пароль: '))
    
    with psycopg2.connect(database=database, user=user, password=password) as conn:
        create_db()
        client_add('Сергей', 'Викторович', 'SergeyViktorovich@mail.ru')
        client_add('Вячеслав', 'Владимирович', 'Vladimirovich@mail.ru')
        client_add('Олег', 'Александрович', 'oleg223@mail.ru')
        phone_add(375297755689, 1)
        phone_add(375338942345, 2)
        phone_add(375448775632, 3)
        phone_change(375297839812, 1)
        data_change(1,'Валентин','Анатольевич', phone_number=375336275691)
        delete_client(2)
        client_search('Валентин', 'Анатольевич','SergeyViktorovich@mail.ru')
        client_search('Олег', 'Александрович','oleg223@mail.ru', 375448775632)
        table_view()

    conn.close()