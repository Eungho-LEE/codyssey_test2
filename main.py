def main():
    while True:
        print("1. 퀴즈 풀기 / 2. 추가 / 3. 목록 / 4. 점수 / 5. 종료")
        choice = input("선택: ").strip()
        if choice == "5":
            print("종료합니다.")
            break
        elif choice in ("1", "2", "3", "4"):
            print("선택한 기능:", choice)
        else:
            print("1~5 중 하나를 입력하세요.")

if __name__ == "__main__":
    main()