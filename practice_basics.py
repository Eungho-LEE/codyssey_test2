topic = "숫자 계산"
correct_count = 0
is_correct = True
choices = ["첫째", "둘째", "셋째", "넷째"]
quiz = {"question": "연습 문제", "choices": choices, "answer": 2}
print(type(topic), type(correct_count), type(is_correct))
print(choices[0])
print(quiz["question"])
name = input("이름: ").strip()
print(f"{name}님, {topic} 퀴즈입니다.")
