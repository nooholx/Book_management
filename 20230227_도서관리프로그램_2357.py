# 2023. 02. 28. 화요일 00:08분, 클래스 및 함수 파일 -> functions2.py파일로 뗴어냄
# functions2.py파일 import한 Ver.

# 추가 기능 구현(23.02.28.목. 00:07)
# 1. 회원가입 시 아이디 입력값 제한(영소문자로 시작, 영소문자 및 숫자로만 구성된 id만 회원가입 가능)
# 2. 장바구니 출력 시 로그인 되어있는 id의 장바구니 내역만 출력가능하게 구현
# 3. 도서반납 시 로그인 되어있는 id의 대여목록만 출력가능하게 구현


# 트리거 생성은 heidisql에서
# rent_list 트리거 생성 쿼리문
# DELIMITER //
# CREATE TRIGGER update_borrow
# AFTER DELETE ON rent_list
# FOR EACH ROW
# BEGIN
# UPDATE book_list SET borrow ='Y'
# WHERE book_num = OLD.book_num;
# END //
# DELIMITER ;


import functions2

num = 0
promt = """
===========================================
 어서오세요. 광산구 도서관 도서관리 프로그램입니다
===========================================
         원하시는 번호를 눌러주세요
              1. 회원가입
              2. 로그인
              3. 종료
===========================================
입력: """


while num != 3:
    try:
        print(promt)
        num = int(input())

        if num == 1:
            functions2.join_member()
        elif num == 2:
            functions2.account_login()
        elif num == 3:
            print("프로그램을 종료합니다.")
            break
        else:
            print("잘못된 입력입니다. 1~3의 숫자를 입력해주세요.")
            continue

    except (ValueError, TypeError) as error:
        print('올바르지 않은 입력입니다. 다시 입력해 주세요.')

