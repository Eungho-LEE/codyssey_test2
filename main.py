import json
from pathlib import Path



import shutil
from datetime import datetime




STATE_PATH = Path(__file__).resolve().parent / "state.json"



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


    @classmethod
    def from_dict(cls, data):
        if not isinstance(data, dict):
            raise ValueError("퀴즈 항목은 객체여야 합니다.")
        if not all(key in data for key in ("question", "choices", "answer")):
            raise ValueError("퀴즈 필드가 누락됐습니다.")
        return cls(data["question"], data["choices"], data["answer"])


class QuizGame:
    def __init__(self):
        self.quizzes = self.make_default_quizzes()
        self.best_score = None
        self.can_save = True
        self.load()


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
        if self.best_score is None or correct > self.best_score:
            self.best_score = correct
            print("새로운 최고 기록입니다.")
        if self.save():
            print("점수를 저장했습니다.")
        else:
            print("점수 저장 실패: 메모리에만 남아 있습니다.")


    def add_quiz(self):
        question = read_nonempty("문제: ")
        choices = [read_nonempty(f"선택지 {i}: ") for i in range(1, 5)]
        answer = read_number("정답 번호: ", 1, 4)
        quiz = Quiz(question, choices, answer)
        self.quizzes.append(quiz)
        print("퀴즈를 목록에 추가했습니다.")
        if self.save():
            print("추가한 퀴즈를 파일에도 저장했습니다.")
        else:
            print("파일 저장 실패: 추가한 퀴즈는 메모리에만 있습니다.")


    def list_quizzes(self):
        if not self.quizzes:
            print("등록된 퀴즈가 없습니다.")
            return
        print(f"등록된 퀴즈: {len(self.quizzes)}개")
        for number, quiz in enumerate(self.quizzes, start=1):
            print(f"{number}. {quiz.question}")


    def show_score(self):
        if self.best_score is None:
            print("아직 퀴즈를 풀지 않았습니다.")
        else:
            print(f"최고 정답 수: {self.best_score}개")


    def save(self):
        if not self.can_save:
            print("원본 보호를 위해 저장을 보류했습니다.")
            return False
        payload = {"quizzes": [q.to_dict() for q in self.quizzes],
                   "best_score": self.best_score}
        temporary = STATE_PATH.with_suffix(".json.tmp")
        try:
            with temporary.open("w", encoding="utf-8") as file:
                json.dump(payload, file, ensure_ascii=False, indent=2)
            temporary.replace(STATE_PATH)
        except OSError as error:
            print(f"저장하지 못했습니다: {error}")
            return False
        return True


    def parse_state(self, data):
        if not isinstance(data, dict):
            raise ValueError("전체 데이터는 객체여야 합니다.")
        if not isinstance(data.get("quizzes"), list) or "best_score" not in data:
            raise ValueError("quizzes 또는 best_score 구조가 잘못됐습니다.")
        quizzes = [Quiz.from_dict(item) for item in data["quizzes"]]
        score = data["best_score"]
        if score is not None and (type(score) is not int or score < 0):
            raise ValueError("최고 점수는 null 또는 0 이상 정수여야 합니다.")
        return quizzes, score


    def load(self):
        try:
            with STATE_PATH.open("r", encoding="utf-8") as file:
                data = json.load(file)
            quizzes, score = self.parse_state(data)
        except FileNotFoundError:
            print("첫 실행: 기본 퀴즈를 사용합니다.")
            return
        except (json.JSONDecodeError, UnicodeDecodeError, ValueError) as error:
            print(f"상태 파일 손상: {error}")
            backup = STATE_PATH.with_name(
                "state.corrupt-" + datetime.now().strftime("%Y%m%d-%H%M%S-%f") + ".json"
            )
            try:
                shutil.copy2(STATE_PATH, backup)
                print(f"손상 원본 백업: {backup.name}")
            except OSError as backup_error:
                self.can_save = False
                print(f"백업 실패: 원본을 덮어쓰지 않습니다. {backup_error}")
            print("이번 실행은 기본 퀴즈로 복구합니다.")
            return
        except OSError as error:
            self.can_save = False
            print(f"읽기 실패: 기본 퀴즈를 사용하고 저장은 보류합니다. {error}")
            return
        self.quizzes, self.best_score = quizzes, score
        print("저장된 데이터를 불러왔습니다.")

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
            elif choice == 3:
                self.list_quizzes()
            elif choice == 4:
                self.show_score()
            else:
                print("이 기능은 다음 단계에서 연결합니다.")


def main():
    game = QuizGame()
    try:
        game.run()
    except (KeyboardInterrupt, EOFError):
        print("\n입력이 종료되어 게임을 마칩니다.")
    finally:
        if game.save():
            print("현재 데이터를 저장했습니다.")
        else:
            print("저장 실패 또는 보류: 이번 변경이 파일에 남지 않았을 수 있습니다.")


if __name__ == "__main__":
    main()