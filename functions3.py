import pymysql
import re

cust_info = []
check_result = []
cart_id = 1
rent_id = 1

class DB():
    conn = None
    cursor = None

    @classmethod
    def connect(cls):
        cls.conn = pymysql.connect(  # DB 연결
            host='127.0.0.1', user='root', password='123456',
            db='book_management', charset='utf8')
        cls.cursor = cls.conn.cursor()
        return cls.conn, cls.cursor
    @classmethod
    def commit(cls):
        cls.conn.commit()
    @classmethod
    def disconnect(cls):
        cls.cursor.close()
        cls.conn.close()


def return_rent(main_user_num, check_result):  # 도서 반납 함수
    check_num = 0
    print("[ 도서 반납하기 ]")

    conn, cursor = DB.connect()

    sql = '''    
        SELECT rent_id, book_num, lib_name, book_name, author, rent_date, return_date
        FROM rent_list
        WHERE cust_id = %s
        ORDER BY rent_date ASC
        '''
    cursor.execute(sql, (check_result[0]))
    result = cursor.fetchall()

    # rent_list에 데이터가 0개일 때
    if result == ():
        print("반납할 도서가 없습니다.")
        return

    print('(등록번호, 소장도서관, 책이름, 지은이, 출판사, 대여가능여부)')

    for i in range(len(result)):
        print(result[i], end='\n')

    user_id = input("반납할 도서의 등록번호를 입력하세요: ")

    for i in range(len(result)):
        if user_id == result[i][1]:
            check_num = 1
            return_book_num = result[i][1]
            return_book_name = result[i][3]

    if check_num == 1:
        sql2 = '''
                DELETE FROM rent_list 
                WHERE book_num = %s
                '''
        cursor.execute(sql2, (user_id))
        DB.commit()

        # book_list의 borrow열을 Y으로 바꿔주기(대여 가능하도록)
        sql3 = '''
            UPDATE book_list SET
            borrow = %s WHERE book_num = %s
            '''
        print(f"등록번호 : {return_book_num}, 도서명 : {return_book_name} 을 반납하였습니다. ")

        cursor.execute(sql3, ('Y', (user_id)))
        DB.commit()
    else:
        print("대여 목록에 없는 등록번호 입니다.")

    DB.disconnect()


def book_rent(check_result):  # 장바구니에 있는 목록 출력 후 대여여부 선택하기
    # 매개변수 check_result는 현재 로그인된 cust의 정보가 담겨 있음(check_ID(), check_PWD()함수 참고)
    global rent_id

    cart_check = print_cart(check_result)  # 장바구니 목록 출력해주는 함수 호출
    if cart_check == -1:
        return

    input_bookid = input("대여할 도서의 등록번호를 입력하세요: ")

    conn, cursor = DB.connect()

    count_sql = f'''
                SELECT cust_id, count(*) as count
                FROM rent_list
                WHERE rent_list.cust_id like ('{(check_result[0])}')
                GROUP BY cust_id
               '''
    cursor.execute(count_sql)
    count_result = cursor.fetchall()


    # cust_id별로 5권 이상 대여할 수 없도록 하는 기능 구현
    # 대여목록이 0개 ~ 5개까지일 때 작동함
    if count_result == () or count_result[0][1] <= 4:


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
        # print(rent_id)

        try:


            sql3 = '''
                    INSERT INTO rent_list (rent_id, book_num, lib_name, book_name, cust_id,
                    author, publisher, rent_date, return_date)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), DATE_ADD(NOW(), INTERVAL 5 DAY))
                    '''

            cursor.execute(sql3, (rent_id, result[0], result[1], result[2], check_result[0],
                                  result[3], result[4]))
            DB.commit()
            print(f"등록번호 : {result[0]}, 도서명 : {result[2]} 을 대여하였습니다.")

            # rent_list에 대여내용 넣었다면 book_list의 borrow열을 N으로 바꿔주기(대여 불가능하도록)
            sql4 = '''
                        UPDATE book_list SET
                        borrow = %s WHERE book_num = %s
                        '''
            cursor.execute(sql4, ('N', (input_bookid)))
            DB.commit()

            # cart에서 삭제하기
            sql5 = '''
                    DELETE FROM cart 
                    WHERE book_num = %s
                    '''
            cursor.execute(sql5, (result[0]))  # result[0] = book_num
            DB.commit()

        except Exception as err:
            if err.args[0] == 1062:
                print("이미 대여한 등록번호입니다. 다른 책을 대여해주세요.")

            else:
                print("해당 등록번호를 찾을 수 없습니다.")

        finally:
            DB.commit()
            DB.disconnect()
    else:
        print("1인당 대여가능한 권수(5권)를 초과하였습니다.")


def print_cart(check_result):  # 장바구니 테이블(cart)을 출력해주는 함수
    conn, cursor = DB.connect()

    sql = ''' 
          SELECT * 
          FROM cart 
          WHERE cust_id = %s
          '''
    cursor.execute(sql, (check_result[0]))
    result = cursor.fetchall()

    print(f"[ 장바구니 ]")

    if result == ():
        print("장바구니에 담긴 도서가 없습니다.")
        return -1

    for i in range(len(result)):
        print(result[i], end='\n')

    DB.disconnect()


def print_rent(main_user_num):  # 도서를 대여하는 함수 호출         ##
    try:

        rent_user_num = 0

        while rent_user_num != 3:
            print("-----------------------------")
            print("     [ 도서대여 ]")
            print("")
            print("     1. 대여하기")
            print("     2. 뒤로가기")
            print("")
            print("-----------------------------")

            rent_user_num = int(input("입력: "))

            if rent_user_num == 1:
                book_rent(check_result)
            elif rent_user_num == 2:
                print("메인화면으로 돌아갑니다.")
                return

    except (ValueError, TypeError) as error:
        print('올바르지 않은 입력입니다. 다시 입력해 주세요.')

    else:
        print("잘못된 입력입니다. 1~2의 숫자를 입력해주세요.")



def search_bookNum(check_result):
    print("등록번호검색을 선택하였습니다.")
    input_bookNum = input("등록번호를 입력하세요: ")

    conn, cursor = DB.connect()

    sql = '''
        SELECT book_id, lib_name, ref_lib, book_num, book_name, author, publisher, borrow 
        FROM book_list 
        WHERE book_num LIKE CONCAT(%s)
        '''

    cursor.execute(sql,(input_bookNum))  # 위의 sql 구문을 실행하기
    result = cursor.fetchall()

    if result == ():
        print("해당 등록번호를 찾을 수 없습니다.")
        DB.disconnect()
        return

    print('(연번, 소장도서관, 자료실명, 등록번호, 책이름, 지은이, 출판사, 대여가능여부)')
    print(result)

    cart = input("장바구니에 넣겠습니까? 1.예 2.아니요 : ")

    if result[0][7] == 'N':
        print("현재 대여중인 도서입니다.")
        return

    if int(cart) == 1:  # borrow가 Y일 때만 카트에 담을 수 있음. 대여 중인데 또 카트에 넣어지는 에러해결
        try:
            sql2 = '''
                INSERT INTO cart (book_num, book_name, author, cust_id)
                VALUES (%s, %s, %s, %s)
                '''
            cursor.execute(sql2, (result[0][3], result[0][4], result[0][5], check_result[0]))

            print(f"등록번호 : {result[0][3]}, 도서명 : {result[0][4]} 을 장바구니에 추가하였습니다.")

        except Exception as err:
            if err.args[0] == 1062:
                print("중복된 등록번호입니다. 다른 책을 장바구니에 넣어주세요")
            if err.args[0] == 1644:
                print("대여 가능한 권수를 초과하였습니다. (1인 최대 5권 대여 가능)")

        finally:
            DB.commit()
            DB.disconnect()
    else:
        print("잘못된 입력입니다.")
        return

def search_author():  # 입력받은 검색어(도서명)가 DB에 있는지 검색하는 함수
    print("저자명검색을 선택하였습니다.(도서를 찾으셨으면, 초기화면의 3번으로 가서 조회하세요)")
    user_author = input("저자명을 입력하세요: ")

    conn, cursor = DB.connect()

    sql = f'''
        SELECT book_id, lib_name, ref_lib, book_num, book_name, author, publisher, borrow
        FROM book_list
        WHERE author LIKE CONCAT('%%', %s, '%%')
        '''
    cursor.execute(sql, (user_author))
    result = cursor.fetchall()

    if result == ():
        print("해당 저자명을 찾을 수 없습니다.")
        return

    print('(연번, 소장도서관, 자료실명, 등록번호, 책이름, 지은이, 출판사, 대여가능여부)')
    for i in range(len(result)):
        print(result[i], end='\n')

    DB.disconnect()


def search_name():  # 입력받은 검색어(도서명)가 DB에 있는지 검색하는 함수
    print("도서명검색을 선택하였습니다. (도서를 찾으셨으면, 초기화면의 3번으로 가서 조회하세요)")
    user_book = input("도서명을 입력하세요: ")

    conn, cursor = DB.connect()

    sql = f''' 
        SELECT book_id, lib_name, ref_lib, book_num, book_name, author, publisher, borrow
        FROM book_list
        WHERE book_name LIKE CONCAT('%%', %s, '%%')
        '''
    cursor.execute(sql, (user_book))
    result = cursor.fetchall()

    # 입력받은 도셔명이 DB에 없을 때
    if result == ():  # cursor.fetchall()이 찾지 못하면 출력결과가 '()'로 출력되기 떄문에.
        print("해당 도서명을 찾을 수 없습니다.")
        return

    # 입력받은 도서명이 DB에 있을 때
    print('(연번, 소장도서관, 자료실명, 등록번호, 책이름, 지은이, 출판사, 대여가능여부)')
    for i in range(len(result)):
        print(result[i], end='\n')

    DB.disconnect()


def print_search(num):
    global check_result
    try:
        while True:
            print("-----------------------------")
            print("      「 소장자료 검색 」")
            print("     1. 도서명으로 검색")
            print("     2. 저자명으로 검색")
            print("     3. 장바구니 담기\n        (등록번호 입력)")
            print("     4. 뒤로가기")
            print("-----------------------------")
            book_list_num = int(input("입력: "))

            if book_list_num == 1:  ##도서명으로 검색
                search_name()  # 도서명 조회 함수 호출

            elif book_list_num == 2:  ##저자명 검색
                search_author()

            elif book_list_num == 3:  ##등록번호로 검색
                search_bookNum(check_result)

            elif book_list_num == 4:
                print("메인메뉴로 돌아가기")
                break

            else:
                print('잘못 입력하였습니다. 1~4사이의 수를 입력하세요')

    except (ValueError, TypeError) as error:
        print('올바르지 않은 입력입니다. 다시 입력해 주세요.')

    else:
        if num == 4:
            print("뒤로 돌아갑니다.")
            return


def print_main():  # 메인 메뉴 출력 함수
    try:
        main_user_num = 0

        while main_user_num != 5:

            print("원하시는 메뉴를 선택하세요")
            print("-----------------------------")
            print("      도서 메뉴")
            print("     1. 도서조회")
            print("     2. 도서대여")
            print("     3. 도서반납")
            print("     4. 장바구니")
            print("     5. 뒤로가기")
            print("-----------------------------")

            main_user_num = int(input("입력: "))

            if main_user_num == 1:
                print("도서조회를 선택하였습니다")
                print_search(main_user_num)  # 도서조회 메뉴 출력 함수 호출
            elif main_user_num == 2:
                print("도서대여를 선택하였습니다")
                print_rent(main_user_num)
            elif main_user_num == 3:
                print("도서반납을 선택하였습니다")
                return_rent(main_user_num, check_result)
            elif main_user_num == 4:
                print("장바구니를 확인합니다")
                print_cart(check_result)
            elif main_user_num == 5:
                print("로그아웃 되었습니다.")
                return
            else:
                print("잘못된 입력입니다. 1~5의 숫자를 입력해주세요.")
    except (ValueError, TypeError) as error:
        print('올바르지 않은 입력입니다. 로그아웃 되었습니다.')



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

        conn, cursor = DB.connect()

        # member_info 테이블 전체 불러오기 => 아이디, 비밀번호 둘 다 필요하기 때문에.
        sql = '''
        SELECT * FROM member_info
        '''
        cursor.execute(sql)  # 위의 sql 구문을 실행하기
        result = cursor.fetchall()  # 쿼리문의 출력결과를 모두 가져와서 result에 넣기(타입은 튜플임)

        for i in range(len(result)):  # 전체 데이터 중에서 사용자가 입력한 input_id와 일치하는 id가 있는지 찾기
            check_result = result[i]  # 만약 일치하는 id가 있다면 해당하는 행(row)의 정보를 저장하기 위함
            if result[i][0] == input_id:
                check = 1
                DB.disconnect()
                return check_result  # 일치하는 정보의 DB행을 return 값으로 반환함

        if check == 0:
            print(f"존재하지 않는 아이디입니다.")
            DB.disconnect()
            return -1


def account_login():  # 계정 로그인을 위한 함수
    print("[ 로그인 ]")
    input_id = input("id를 입력하세요 : ")
    input_pwd = input("pw를 입력하세요 : ")

    # user가 입력한 id가 DB에 있는지 확인하는 함수 호출한 후 return값(있으면 행(row)정보, 없으면 -1)을 return_id에 저장
    return_id = check_ID(input_id)
    if return_id != -1:  # return 값이 -1이 아닐 때 (즉, id가 존재할 때)
        # user가 입력한 비밀번호가 db의 id/pwd와 일치하는지 확인하는 함수 호출
        check_PWD(input_id, input_pwd, return_id)


def join_member():  # 회원가입하는 함수
    global cust_info
    check = 0

    print(f"[ 회원가입하기 ]")

    while check != 1:

        conn, cursor = DB.connect()
        print("ID는 영어와 숫자로만 입력될 수 있습니다. 시작 문자는 영어이어야 합니다.")
        cust_id = input("ID를 입력하세요 : ")

        pattern1 = re.compile('[a-z]')          # 영어 소문자 규칙 지정
        pattern2 = re.compile('[^0-9a-z]]')  # 숫자, 영소문자를 제외한 문자가 있다면 ture / 없으면 false
        result1 = pattern1.match(cust_id)       # 첫 시작글자가 영어소문자여야 하니까 match
        result2 = pattern2.search(cust_id)      # search는 중간에 어디있는지를 찾는 거니까

        if result1 and not result2:  # result1이 T이고 result2가 false라면 not false = T. 즉 한글, 특문 없다면 가입 가능
            print(f"{cust_id} 가입이 가능한 ID입니다.")
        else:
            print(f"{cust_id} 가입이 불가능한 아이디입니다.")
            return



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
            cust_info.append(cust_id)  # cust_info 리스트에 요소들을 임시 저장
            print(f"PW를 입력하세요 : ")
            cust_pw = input()
            cust_info.append(cust_pw)
            print(f"핸드폰 번호를 입력하세요(숫자만 입력) : ")
            cust_phone = input()
            cust_info.append(cust_phone)

            sql = '''
                INSERT INTO member_info (cust_id, cust_pw, phone_number)
                VALUES (%s, %s, %s)
                '''
            cursor.execute(sql, (cust_info[0], cust_info[1], cust_info[2]))
            DB.commit()
            DB.disconnect()
            cust_info = []  # cust_info 초기화
            break
