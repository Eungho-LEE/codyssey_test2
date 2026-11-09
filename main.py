def read_number(prompt, minimum, maximum):
    while True:
        raw = input(prompt).strip()

        if not raw:
            print("빈 입력입니다. 숫자를 입력하세요.")
            continue

        try:
            value = int(raw)
        except ValueError:
            print("정수를 입력하세요.")
            continue

        if minimum <= value <= maximum:
            return value

        print(f"{minimum}~{maximum} 범위로 입력하세요.")


def main():
    while True:
        print("\n1. 퀴즈 풀기 / 2. 추가 / 3. 목록 / 4. 점수 / 5. 종료")
        choice = read_number("선택: ", 1, 5)

        if choice == 5:
            print("종료합니다.")
            break
        else:
            print("선택한 기능:", choice)


if __name__ == "__main__":
    main()