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


def read_nonempty(prompt):
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("빈 내용은 등록할 수 없습니다.")


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


class QuizGame:
    def __init__(self):
        self.quizzes = self.make_default_quizzes()
        self.best_score = None


    def make_default_quizzes(self):
        # 학습용 예시입니다. 본인이 정한 주제의 문제 5개 이상으로 바꾸세요.
        return [
            Quiz("Python 파일의 확장자는?", [".py", ".jpg", ".mp3", ".zip"], 1),
            Quiz("빈 파일을 만드는 명령은?", ["mkdir", "touch", "cd", "pwd"], 2),
            Quiz("현재 폴더를 보여 주는 명령은?", ["cp", "mv", "pwd", "rm"], 3),
            Quiz("로컬 변경 이력을 저장하는 Git 명령은?", ["clone", "pull", "push", "commit"], 4),
            Quiz("목록의 첫 항목 인덱스는?", ["0", "1", "2", "-2"], 1),
        ]


    def play(self):
        if not self.quizzes:
            print("등록된 퀴즈가 없습니다.")
            return
        correct = 0
        for quiz in self.quizzes:
            quiz.show()
            selected = read_number("정답 번호: ", 1, 4)
            if quiz.is_correct(selected):
                correct += 1
                print("정답입니다.")
            else:
                print("오답입니다.")
        print(f"{len(self.quizzes)}문제 중 {correct}개 정답")


    def add_quiz(self):
        question = read_nonempty("문제: ")
        choices = [read_nonempty(f"선택지 {i}: ") for i in range(1, 5)]
        answer = read_number("정답 번호: ", 1, 4)
        quiz = Quiz(question, choices, answer)
        self.quizzes.append(quiz)
        print("퀴즈를 목록에 추가했습니다.")
        print("9~10단계에서는 종료하면 추가한 퀴즈가 사라집니다.")

    def run(self):
        while True:
            print("\n1. 퀴즈 풀기 / 2. 추가 / 3. 목록 / 4. 점수 / 5. 종료")
            choice = read_number("선택: ", 1, 5)
            if choice == 5:
                print("종료합니다.")
                return
            elif choice == 1:
                self.play()
            elif choice == 2:
                self.add_quiz()
            else:
                print("이 기능은 다음 단계에서 연결합니다.")


def main():
    game = QuizGame()
    game.run()


if __name__ == "__main__":
    main()