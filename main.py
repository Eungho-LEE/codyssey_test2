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


class Quiz:
    def __init__(self, question, choices, answer):
        if not isinstance(question, str) or not question.strip():
            raise ValueError("문제는 빈 문자열일 수 없습니다.")
        if not isinstance(choices, list) or len(choices) != 4:
            raise ValueError("선택지는 4개여야 합니다.")
        if any(not isinstance(item, str) or not item.strip() for item in choices):
            raise ValueError("선택지는 빈 문자열일 수 없습니다.")
        if type(answer) is not int or not 1 <= answer <= 4:
            raise ValueError("정답은 1~4 정수여야 합니다.")
        self.question = question.strip()
        self.choices = [item.strip() for item in choices]
        self.answer = answer

    def show(self):
        print(self.question)
        for number, text in enumerate(self.choices, start=1):
            print(f"{number}. {text}")

    def is_correct(self, selected):
        return selected == self.answer

    def to_dict(self):
        return {"question": self.question,
                "choices": self.choices, "answer": self.answer}


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