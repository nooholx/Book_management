# 2023. 02. 21. 화요일 00:19분 저장

import pymysql

num = 0
promt = """
1. 회원가입
2. 로그인
3. 종료
Enter number: """

cust_info = []
check_result = []
cart_id = 1
rent_id = 1

def return_rent():  # 도서 반납 함수
    check_num = 0
    print("[ 도서 반납하기 ]")
    # rent_list 출력하기
    conn = pymysql.connect(  # DB 연결
        host='127.0.0.1', user='root', password='123456',
        db='book_management', charset='utf8')
    cursor = conn.cursor()

    sql = '''    
        SELECT *
        FROM rent_list
        '''
    cursor.execute(sql)
    result = cursor.fetchall()

    for i in range(len(result)):
        print(result[i], end='\n')

    print("반납할 도서의 등록번호를 입력하세요 : ")
    user_id = input()

    for i in range(len(result)):
        if user_id == result[i][1]:
            check_num = 1

    if check_num == 1:
        sql2 = '''
                DELETE FROM rent_list 
                WHERE book_num = %s
                '''
        cursor.execute(sql2, (user_id))  # result[0] = book_num
        conn.commit()

        # book_list의 borrow열을 Y으로 바꿔주기(대여 가능하도록)
        sql3 = '''
            UPDATE book_list SET
            borrow = %s WHERE book_num = %s
            '''
        cursor.execute(sql3, ('Y', (user_id)))
        conn.commit()
    else:
        print("대여 목록에 없는 등록번호 입니다.")

    cursor.close()
    conn.close()


def book_rent(check_result):  # 장바구니에 있는 목록 출력 후 대여여부 선택하기
    # 매개변수 check_result는 현재 로그인된 cust의 정보가 담겨 있음(check_ID(), check_PWD()함수 참고)
    global rent_id

    print_cart()  # 장바구니 목록 출력해주는 함수 호출
    print("대여할 도서의 등록번호를 입력하세요 : ")
    input_bookid = input()

    conn = pymysql.connect(  # DB 연결
        host='127.0.0.1', user='root', password='123456',
        db='book_management', charset='utf8')
    cursor = conn.cursor()

    # rent_list에 데이터 넣기 위해서 book_list에서 가져올 수 있는 col명들 select
    sql = '''    
            SELECT book_num, lib_name, book_name, author, publisher, borrow
            FROM book_list
            WHERE book_num LIKE CONCAT(%s)
            '''
    cursor.execute(sql, (input_bookid))
    result = cursor.fetchone()

    # rent_id 길이 구하기
    sql2 = '''    
            SELECT rent_id
            FROM rent_list
            '''
    cursor.execute(sql2)
    rent_id = len(cursor.fetchall()) + 1
    print(rent_id)

    # rent_list에 대여한 책에 대한 내용 insert하기
    sql3 = '''
            INSERT INTO rent_list (rent_id, book_num, lib_name, book_name, cust_id,
            author, publisher, rent_date, return_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), DATE_ADD(NOW(), INTERVAL 5 DAY))
            '''

    # rent_list 테이블에서 rent_date, return_date =>  db에서 DATE로 바꿔줘야함
    cursor.execute(sql3, (rent_id, result[0], result[1], result[2], check_result[0],
                          result[3], result[4]))
    conn.commit()


    # rent_list에 대여내용 넣었다면 book_list의 borrow열을 N으로 바꿔주기(대여 불가능하도록)
    sql4 = '''
            UPDATE book_list SET
            borrow = %s WHERE book_num = %s
            '''
    cursor.execute(sql4, ('N', (input_bookid)))
    conn.commit()

    # cart에서 삭제하기
    sql5 = '''
           DELETE FROM cart 
           WHERE book_num = %s
            '''
    cursor.execute(sql5, (result[0]))  # result[0] = book_num
    conn.commit()

    cursor.close()
    conn.close()

def print_cart():  # 장바구니 테이블(cart)을 출력해주는 함수
    conn = pymysql.connect(  # DB 연결
        host='127.0.0.1', user='root', password='123456',
        db='book_management', charset='utf8')
    cursor = conn.cursor()

    sql = '''
          SELECT *
          FROM cart
          '''
    cursor.execute(sql)
    result = cursor.fetchall()

    print(f"[ 장바구니 ]")
    for i in range(len(result)):
        print(result[i], end='\n')

    cursor.close()
    conn.close()

#############################수정해야함 ########################################
def input_cart(user_bookid):  # cart 테이블에 데이터 넣는 함수
    global cart_id
    check_cart = 0
    conn = pymysql.connect(
        host='127.0.0.1', user='root', password='123456',
        db='book_management', charset='utf8')
    cursor = conn.cursor()

    # book_list 테이블에 user가 입력한 등록번호(매개변수로 전달 받은 user_bookid)가 있는지 확인하는 쿼리문
    sql = '''
            SELECT book_num, borrow, book_name, author
            FROM book_list
            WHERE book_num LIKE CONCAT(%s)
            '''
    cursor.execute(sql, (user_bookid))
    result = cursor.fetchall()

    if len(result) == 0:
        print("소장 자료가 없습니다.")
        cursor.close()
        conn.close()
    else:
        sql4 = '''
                INSERT INTO cart (cart_id, book_num, book_name, author)
                VALUES (%s, %s, %s, %s)
                '''
        cursor.execute(sql4, (cart_id, result[0][0], result[0][2], result[0][3]))
        conn.commit()
        print(f"등록번호 {result[0][0]} 도서가 장바구니에 추가되었습니다. ")


    cursor.close()
    conn.close()


def print_rent():  # 도서를 대여하는 함수 호출

    rent_user_num = 0

    while rent_user_num != 3:
        print("[ 도서대여 ]")
        print("1. 도서명으로 검색")
        print("2. 저자명으로 검색")
        print("3. 뒤로가기")

        rent_user_num = int(input())

        if rent_user_num == 1:
            print("[ 도서명으로 검색 ]")
            search_name()  # 도서명 조회 함수 호출
            print("도서를 장바구니에 담으시겠습니까? ( Y / N ) : ")
            user_input = input()
            if user_input == 'Y':
                user_bookid = input("등록번호를 입력하세요 : ")
                input_cart(user_bookid)
                print("도서를 대여하시겠습니까? ( Y / N ) : ")
                user_input2 = input()
                if user_input2 == 'Y':
                    book_rent(check_result)
                else:
                    print("도서대여 화면으로 돌아갑니다.")

        elif rent_user_num == 2:
            print("[ 저자명으로 검색 ]")
            search_author()  # 저자명 조회 함수 호출
            print("도서를 장바구니에 담으시겠습니까? ( Y / N ) : ")
            user_input = input()
            if user_input == 'Y':
                user_bookid = input("등록번호를 입력하세요 : ")
                input_cart(user_bookid)
                print("도서를 대여하시겠습니까? ( Y / N ) : ")
                user_input2 = input()
                if user_input2 == 'Y':
                    book_rent(check_result)
                else:
                    print("도서대여 화면으로 돌아갑니다.")
        else:
            print("메인화면으로 돌아갑니다.")
            break

def search_author():  # 입력받은 검색어(도서명)가 DB에 있는지 검색하는 함수
    print("검색어를 입력하세요.(저자명)")
    user_author = input()
    conn = pymysql.connect(  # DB 연결
        host='127.0.0.1', user='root', password='123456',
        db='book_management', charset='utf8')
    cursor = conn.cursor()

    sql = '''
        SELECT book_id, lib_name, ref_lib, book_num, book_name, author, borrow
        FROM book_list
        WHERE author LIKE CONCAT('%%', %s, '%%')
        '''
    cursor.execute(sql, (user_author))
    result = cursor.fetchall()

    for i in range(len(result)):
        print(result[i], end='\n')

    if result == ():
        print("소장 자료가 없습니다.")

    cursor.close()
    conn.close()

def search_name():  # 입력받은 검색어(도서명)가 DB에 있는지 검색하는 함수
    print("검색어를 입력하세요.(도서명)")
    user_book = input()
    conn = pymysql.connect(  # DB 연결
        host='127.0.0.1', user='root', password='123456',
        db='book_management', charset='utf8')
    cursor = conn.cursor()

    sql = ''' 
        SELECT book_id, lib_name, ref_lib, book_num, book_name, borrow
        FROM book_list
        WHERE book_name LIKE CONCAT('%%', %s, '%%')
        '''
    cursor.execute(sql, (user_book))
    result = cursor.fetchall()

    # 입력받은 도서명이 DB에 있을 때
    for i in range(len(result)):
        print(result[i], end='\n')

    # 입력받은 도셔명이 DB에 없을 때
    if result == ():  # cursor.fetchall()이 찾지 못하면 출력결과가 '()'로 출력되기 떄문에.
        print("소장 자료가 없습니다.")

    cursor.close()
    conn.close()


def print_search(): # 도서조회 메뉴 출력 함수 호출
    search_user_num = 0

    while search_user_num != 4:
        print("[ 소장자료 검색 ]")
        print("1. 도서명으로 검색")
        print("2. 저자명으로 검색")
        print("3. 뒤로가기")

        search_user_num = int(input())

        if search_user_num == 1:
            print("도서명으로 검색")
            search_name()  # 도서명 조회 함수 호출
        elif search_user_num == 2:
            print("저자명으로 검색")
            search_author()  # 저자명 조회 함수 호출
        else:
            print("메인화면으로 돌아갑니다.")
            break

def print_main(): # 메인 메뉴 출력 함수
    main_user_num = 0

    while main_user_num != 4:

        print("1. 도서조회")
        print("2. 도서대여")
        print("3. 도서반납")
        print("4. 뒤로가기")
        print("Enter number: ")

        main_user_num = int(input())

        if main_user_num == 1:
            print("도서조회")
            print_search()  # 도서조회 메뉴 출력 함수 호출
        elif main_user_num == 2:
            print("도서대여")
            print_rent()
        elif main_user_num == 3:
            print("도서반납")
            return_rent()
        else:
            print("로그아웃 되었습니다.")
            break

def check_PWD(input_id, input_pwd, check_result):  # 비밀번호 일치여부를 확인하는 함수 (매개변수로는 사용자가 입력한 id, pw, check_id()의 리턴값)
    if check_result[0] == input_id and check_result[1] == input_pwd:
        print("로그인 되었습니다.")
        print_main()  # 로그인 성공시 메인 메뉴 출력
        return check_result
    else:
        print(f"아이디 또는 비밀번호가 일치하지 않습니다.")


def check_ID(input_id):  # 사용자에게 입력받은 input_id가 DB에 있는지 확인하는 함수
    global check_result
    check = 0  # 무한루프 돌리기 위해 설정함

    while check != 1:

        conn = pymysql.connect(   # DB 연결
            host='127.0.0.1', user='root', password='123456',
            db='book_management', charset='utf8')
        cursor = conn.cursor()

        # member_info 테이블 전체 불러오기 => 아이디, 비밀번호 둘 다 필요하기 때문에.
        sql = '''
        SELECT * FROM member_info
        '''
        cursor.execute(sql)  # 위의 sql 구문을 실행하기
        result = cursor.fetchall() # 쿼리문의 출력결과를 모두 가져와서 result에 넣기(타입은 튜플임)

        for i in range(len(result)):  # 전체 데이터 중에서 사용자가 입력한 input_id와 일치하는 id가 있는지 찾기
            check_result = result[i]  # 만약 일치하는 id가 있다면 해당하는 행(row)의 정보를 저장하기 위함
            if result[i][0] == input_id:
                check = 1
                cursor.close()
                conn.close()
                return check_result  # 일치하는 정보의 DB행을 return 값으로 반환함

        if check == 0:
            print(f"존재하지 않는 아이디입니다.")
            cursor.close()
            conn.close()
            return -1


def account_login():  # 계정 로그인을 위한 함수
    print(f"id를 입력하세요 : ")
    input_id = input()  # user에게 id 입력받음
    print(f"pw를 입력하세요 : ")
    input_pwd = input() # user에게 pwd 입력받음

    return_id = check_ID(input_id)  # user가 입력한 id가 DB에 있는지 확인하는 함수 호출한 후 return값(있으면 행(row)정보, 없으면 -1)을 return_id에 저장
    # print(f"id_check : {return_id}")
    if return_id != -1:  # return 값이 -1이 아닐 때 (즉, id가 존재할 때)
        check_PWD(input_id, input_pwd, return_id) # user가 입력한 비밀번호가 db의 id/pwd와 일치하는지 확인하는 함수 호출


def join_member():   # 회원가입하는 함수
    global cust_info
    check = 0

    print(f"[ 회원가입하기 ]")

    while check != 1:

        conn = pymysql.connect(  # DB 연결
            host='127.0.0.1', user='root', password='123456',
            db='book_management', charset='utf8')
        cursor = conn.cursor()

        print(f"ID를 입력하세요 : ")
        cust_id = input()

        sql = '''
        SELECT cust_id FROM member_info
        '''
        cursor.execute(sql)  # SQL문 실행
        result = cursor.fetchall()  # 쿼리문의 출력결과 전부 가져오기

        for i in range(len(result)):  # 이미 DB에 있는 아이디일 경우
            if result[i][0] == cust_id:
                print("이미 가입된 ID입니다.")
                check = 1  # while문 빠져나오기

        if check == 0:  # DB에 없는 아이디일 경우
            cust_info.append(cust_id)   # cust_info 리스트에 요소들을 임시 저장
            print(f"PW를 입력하세요 : ")
            cust_pw = input()
            # print(cust_pw)
            cust_info.append(cust_pw)
            print(f"핸드폰 번호를 입력하세요(숫자만 입력) : ")
            cust_phone = input()
            # print(cust_phone)
            cust_info.append(cust_phone)

            sql = '''
                INSERT INTO member_info (cust_id, cust_pw, phone_number)
                VALUES (%s, %s, %s)
                '''
            cursor.execute(sql, (cust_info[0], cust_info[1], cust_info[2]))
            conn.commit()
            cursor.close()
            conn.close()
            cust_info = []  # cust_info 초기화
            break


while num != 3:

    print(promt)
    num = int(input())

    if num == 1:
        print("회원가입하기")
        join_member()
    elif num == 2:
        print("로그인")
        account_login()
    else:
        print("프로그램을 종료합니다.")
        break