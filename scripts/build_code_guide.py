"""Build an explanation of the reviewed source snapshot, without executing it."""
import ast
import hashlib
import html
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
source=ROOT/'main.py'
raw=source.read_bytes()
EXPECTED='5cde90446ae5f37c4832d7947a64c1863ddc08fd262fef8e808e3c393989bc04'
digest=hashlib.sha256(raw).hexdigest()
if digest!=EXPECTED:
    raise SystemExit('main.py changed since this line review. Review the explanation map before regenerating.')
text=raw.decode('utf-8-sig')
lines=text.splitlines()
tree=ast.parse(text)

SUMMARIES={
 'read_number':('숫자 입력을 반복 검증','prompt는 안내 문구, minimum/maximum은 허용 범위입니다. 공백·빈 입력·숫자 변환·범위를 검사하고 정상 정수만 반환합니다.'),
 'read_nonempty':('빈 문장이 아닌 입력 받기','문제와 선택지 입력에 재사용합니다. 공백만 입력하면 다시 받고, 정상 문자열을 return합니다.'),
 'Quiz':('문제 하나의 데이터와 동작','question·choices·answer를 함께 보관하고 출력·판정·dict 변환을 담당합니다.'),
 'Quiz.__init__':('문제 객체 생성과 검증','문자열 문제, 선택지 네 개, 정답 번호 1~4를 검증한 뒤 속성으로 저장합니다.'),
 'Quiz.show':('문제와 선택지 출력','문제 문장과 1부터 시작하는 선택지 번호를 보여 줍니다.'),
 'Quiz.is_correct':('정답 비교','선택한 정수 번호와 저장된 정답 번호가 같은지 bool로 반환합니다.'),
 'Quiz.to_dict':('JSON에 저장할 기본 자료형으로 변환','사용자 정의 Quiz 객체를 dict/list/문자열/정수로 바꿉니다. 이 메서드 자체는 파일을 쓰지 않습니다.'),
 'Quiz.from_dict':('저장된 문제 복원','필수 키를 검사한 dict에서 Quiz 객체를 새로 만듭니다. 생성자의 검증도 다시 거칩니다.'),
 'QuizGame':('게임 전체 상태와 기능','문제 목록·최고 정답 수·저장 가능 상태를 관리하고 메뉴와 파일 입출력을 연결합니다.'),
 'QuizGame.__init__':('게임 준비','기본 퀴즈·미플레이 점수·저장 허용 상태를 먼저 만들고 저장 파일을 불러옵니다.'),
 'QuizGame.make_default_quizzes':('개발 기초 문제 다섯 개 준비','처음 실행하거나 손상 파일에서 복구할 때 사용할 새 Quiz 객체 목록을 반환합니다.'),
 'QuizGame.play':('한 판 진행','문제를 차례로 출제하고 정답 수를 세며, 완료한 판에 대해 최고점을 갱신하고 저장합니다.'),
 'QuizGame.add_quiz':('문제 등록','모든 필드를 정상 입력받은 뒤 객체 하나를 목록에 추가하고 파일에 저장합니다.'),
 'QuizGame.list_quizzes':('문제 목록 확인','빈 목록을 처리하고, 등록된 문제 문장에 1부터 번호를 붙여 출력합니다.'),
 'QuizGame.show_score':('최고 정답 수 확인','아직 플레이하지 않은 None과 실제 정답 수 0을 구분합니다.'),
 'QuizGame.save':('상태 저장','저장이 허용될 때 dict로 변환하여 임시 파일을 완성한 뒤 state.json과 교체합니다. 성공 여부를 bool로 돌려줍니다.'),
 'QuizGame.parse_state':('저장 구조 검증','전체 구조·문제 목록·최고점의 타입을 검사합니다. 게임 상태를 직접 바꾸지 않고 검증한 목록과 점수를 반환합니다.'),
 'QuizGame.load':('상태 읽기와 오류 복구','정상 파일을 검증해 적용합니다. 파일 없음·손상·읽기 실패를 구별하고 손상 원본을 백업합니다.'),
 'QuizGame.run':('메뉴 반복','검증된 메뉴 번호로 각 메서드를 호출하고, 5번이면 run만 끝내 main으로 돌아갑니다.'),
 'main':('실행 시작과 종료 처리','게임을 준비하고 메뉴를 실행합니다. Ctrl+C·EOF를 안내하고 종료 시 가능한 저장을 다시 수행합니다.'),
}

# Keys are physical source line numbers; the exact SHA above prevents stale annotations.
NOTES={
1:('JSON 변환 기능을 가져옵니다.','json.load로 읽고 json.dump로 씁니다. 표준 라이브러리이므로 별도 설치가 필요 없습니다.'),
2:('경로를 다루는 Path 클래스를 가져옵니다.','from 모듈 import 이름 형식입니다. 이후 Path(...)처럼 직접 씁니다.'),
6:('파일 복사 등의 shutil 모듈을 가져옵니다.','손상 파일 원본을 shutil.copy2로 백업합니다.'),
7:('datetime 모듈에서 datetime 클래스를 가져옵니다.','현재 시각을 읽어 백업 파일 이름에 넣습니다.'),
12:('main.py와 같은 폴더의 state.json 경로를 정합니다.','__file__은 이 파일, resolve()는 절대 경로, parent는 상위 폴더, /는 경로 결합입니다. 현재 터미널 위치와 무관합니다.'),
17:('정상 입력을 받을 때까지 반복합니다.','while True는 break·return·예외 등이 발생하기 전까지 반복합니다.'),
18:('안내 문구를 보여 주고 문자열 입력을 받은 뒤 앞뒤 공백을 없앱니다.','input 반환값은 숫자를 입력해도 str입니다. raw는 이 함수의 지역변수입니다.'),
19:('공백 제거 후 빈 문자열인지 검사합니다.','빈 문자열은 False처럼 평가되므로 not raw가 True입니다.'),
20:('빈 입력이라는 안내를 출력합니다.','화면에 알려 줄 뿐 값을 반환하는 동작은 아닙니다.'),
21:('현재 반복의 남은 부분을 건너뛰고 다시 입력받습니다.','함수 전체를 끝내는 return과 다릅니다.'),
22:('숫자 변환에서 발생할 예외를 처리할 구간을 시작합니다.','이 try는 바로 아래 int(raw)를 보호합니다.'),
23:('입력 문자열을 정수로 바꿉니다.','"2"는 2가 되고 "abc"는 ValueError를 일으킵니다.'),
24:('정수 변환이 실패한 경우를 잡습니다.','모든 오류를 무시하지 않고 예상하는 ValueError를 지정했습니다.'),
25:('정수를 입력하라고 안내합니다.','abc 같은 입력에 대한 메시지입니다.'),
26:('같은 입력 반복으로 돌아갑니다.','아래 범위 검사로 내려가지 않습니다.'),
27:('정수가 최소값 이상이고 최대값 이하인지 검사합니다.','minimum <= value <= maximum은 양쪽 경계를 포함한 비교입니다.'),
28:('검증된 정수를 호출한 곳에 돌려주고 함수를 끝냅니다.','메뉴에서는 choice, 정답 입력에서는 selected 등에 저장됩니다.'),
29:('정수이지만 허용 범위를 벗어났다는 안내를 합니다.','이후 while 맨 위로 돌아가 다시 입력받습니다. f 문자열의 중괄호가 범위를 실제 숫자로 보여 줍니다.'),
33:('빈 내용이 아닌 문자열을 받을 때까지 반복합니다.','read_number와 달리 정수 변환은 하지 않습니다.'),
34:('문자열을 입력받아 앞뒤 공백을 제거합니다.','공백만 입력했다면 value는 빈 문자열이 됩니다.'),
35:('문자열에 내용이 있는지 검사합니다.','길이가 1 이상인 문자열은 True처럼 평가됩니다.'),
36:('정상 문자열을 반환하고 반복과 함수를 마칩니다.','문제·선택지 문장에 사용할 값입니다.'),
37:('빈 내용은 등록할 수 없다고 알립니다.','return을 하지 않았으므로 while이 다시 입력받습니다.'),
42:('문제가 문자열이 아니거나 공백뿐인지 검사합니다.','or는 둘 중 하나라도 참이면 참입니다. 문자열이 아니면 뒤 strip 호출을 생략합니다.'),
43:('잘못된 문제 문장이면 객체 생성을 중단합니다.','raise는 예외를 발생시킵니다. 호출한 쪽에서 처리할 수 있습니다.'),
44:('선택지가 list가 아니거나 개수가 4가 아닌지 검사합니다.','len은 길이를 구합니다. list가 아니면 뒤 len 검사까지 진행하지 않습니다.'),
45:('선택지 개수·형식 오류를 알리는 예외를 발생시킵니다.','화면 print와 달리 현재 생성 과정을 중단합니다.'),
46:('선택지 중 문자열이 아니거나 빈 문장이 하나라도 있는지 검사합니다.','any는 조건에 맞는 항목이 하나라도 있으면 True입니다. for item in choices는 항목을 차례로 검사합니다.'),
47:('잘못된 선택지 내용이면 예외를 발생시킵니다.','네 항목 모두 정상 문자열이어야 합니다.'),
48:('정답이 정확한 int 타입이며 1~4 범위인지 검사합니다.','type(True)는 bool이므로 제외됩니다. isinstance(True,int)와 다른 점입니다.'),
49:('정답 번호가 잘못되면 예외를 발생시킵니다.','문자열 "2" 대신 정수 2를 받도록 통일합니다.'),
50:('검증한 문제 문장을 이 Quiz 객체에 저장합니다.','self는 지금 생성 중인 객체입니다. 다른 Quiz 객체의 문제와 구분됩니다.'),
51:('각 선택지의 공백을 제거한 새 목록을 속성으로 저장합니다.','목록 내포입니다. 기존 choices를 그대로 참조하는 대신 새 list를 만듭니다.'),
52:('정답 번호를 객체 속성에 저장합니다.','이후 is_correct에서 비교하는 기준입니다.'),
55:('이 객체의 문제 문장을 출력합니다.','self.question은 생성할 때 저장한 속성입니다.'),
56:('선택지마다 1부터 시작하는 번호와 문장을 꺼냅니다.','enumerate(...,start=1)는 표시 번호를 만들며 list 인덱스 자체를 바꾸지는 않습니다.'),
57:('선택지 번호와 내용을 한 줄로 출력합니다.','f 문자열이 number와 text를 실제 값으로 바꿉니다.'),
60:('입력 번호가 정답 번호와 같은지 bool로 반환합니다.','==는 비교이고 =는 대입입니다. 이 함수는 출력하지 않습니다.'),
63:('문제 데이터를 담은 dict를 만들어 반환하기 시작합니다.','여는 중괄호가 다음 줄에서 닫히므로 두 물리적 줄이 하나의 return 문입니다.'),
64:('같은 dict에 선택지와 정답을 넣고 닫습니다.','question·choices·answer라는 문자열 키가 JSON 필드 이름이 됩니다.'),
67:('바로 아래 함수를 클래스 메서드로 선언합니다.','객체 대신 클래스를 cls로 받으므로 Quiz.from_dict(data) 형태로 호출할 수 있습니다.'),
69:('저장된 문제 항목이 dict인지 검사합니다.','JSON 객체는 json.load 후 Python dict가 됩니다.'),
70:('문제 항목의 자료형이 틀리면 예외를 냅니다.','from_dict 호출자는 손상 데이터로 처리할 수 있습니다.'),
71:('question·choices·answer 세 키가 모두 존재하는지 검사합니다.','all은 모든 조건이 참이어야 True입니다. 키의 존재만 검사하고 값 검증은 생성자가 담당합니다.'),
72:('필수 키가 빠졌으면 예외를 발생시킵니다.','누락된 데이터를 억지로 채워 사용하지 않습니다.'),
73:('dict의 값으로 새 Quiz 객체를 만들어 반환합니다.','cls는 보통 Quiz입니다. __init__가 다시 문자열·선택지·정답을 검증합니다.'),
78:('기본 문제 목록을 새로 만들어 게임 속성에 보관합니다.','아래 make_default_quizzes 메서드를 실제로 호출합니다.'),
79:('아직 판을 마친 적 없음을 None으로 표시합니다.','0개 정답과 미플레이를 구분하기 위한 값입니다.'),
80:('일단 상태 저장을 허용합니다.','load에서 읽기·백업에 문제가 있으면 False로 바뀝니다.'),
81:('이전에 저장한 상태가 있으면 읽어 적용합니다.','함수 정의만이 아니라 실제 메서드 호출입니다. 기본 상태 준비 뒤에 실행됩니다.'),
85:('기본 문제는 학습 예시라는 주석입니다.','주석은 실행되지 않습니다. 현재 주제는 개발 기초이며 문항은 프로젝트 목적에 맞게 검토합니다.'),
86:('다섯 Quiz 객체를 담을 새 list를 반환하기 시작합니다.','여는 대괄호와 92행의 닫는 대괄호 사이가 한 목록입니다.'),
87:('확장자 문제 객체를 만듭니다.','세 번째 인자 1은 정답 번호이며 첫 선택지 .py를 뜻합니다.'),
88:('빈 파일 생성 명령 문제 객체를 만듭니다.','정답 번호 2는 touch입니다. mkdir는 폴더 생성입니다.'),
89:('현재 폴더 조회 명령 문제 객체를 만듭니다.','정답 번호 3은 pwd입니다.'),
90:('로컬 이력 저장 명령 문제 객체를 만듭니다.','정답 번호 4는 commit입니다. 원격 업로드 push와 구분합니다.'),
91:('첫 목록 인덱스 문제 객체를 만듭니다.','정답 번호 1의 선택지 내용은 0입니다. 정답 번호와 선택지에 적힌 값을 혼동하지 않습니다.'),
92:('기본 문제 목록을 닫아 반환합니다.','각 항목은 dict가 아니라 Quiz 인스턴스입니다.'),
96:('출제할 문제가 없는지 검사합니다.','빈 list는 False처럼 평가됩니다.'),
97:('문제가 없음을 알립니다.','빈 목록에서 플레이를 시도할 때 나옵니다.'),
98:('play 메서드를 끝내 메뉴로 돌아갑니다.','프로그램 전체 종료가 아닙니다. 값을 쓰지 않은 return의 반환값은 None입니다.'),
99:('이번 판의 정답 수를 0으로 시작합니다.','지역변수라 판을 시작할 때마다 새로 계산합니다.'),
100:('목록의 Quiz 객체를 하나씩 꺼내 출제합니다.','quiz는 현재 문제 객체를 가리키는 지역변수입니다.'),
101:('현재 문제의 출력 메서드를 호출합니다.','Quiz.show가 문제와 선택지를 출력합니다.'),
102:('정답 번호를 1~4 범위의 정수로 검증해 받습니다.','잘못된 입력은 read_number 안에서 다시 받으므로 문제를 건너뛰지 않습니다.'),
103:('현재 입력이 정답인지 검사합니다.','Quiz.is_correct의 True/False 반환값으로 분기합니다.'),
104:('정답일 때 이번 판 정답 수에 1을 더합니다.','correct += 1은 correct = correct + 1입니다.'),
105:('정답이라고 안내합니다.','정답인 경우에만 실행됩니다.'),
106:('정답이 아닌 경우의 갈래입니다.','바로 위 if quiz.is_correct(...)와 짝입니다.'),
107:('오답이라고 안내합니다.','이후 반복이 다음 문제를 출제합니다.'),
108:('모든 문제를 마친 뒤 총 문항 수와 정답 수를 출력합니다.','for보다 들여쓰기가 한 단계 작아 반복문 밖에 있습니다.'),
109:('첫 완료 판이거나 기존 최고점보다 높은지 검사합니다.','None이면 or 뒤 비교를 생략해 정수와 None을 비교하는 오류를 피합니다.'),
110:('최고 정답 수를 이번 판의 값으로 바꿉니다.','더 낮은 점수나 동점이면 이 줄이 실행되지 않습니다.'),
111:('최고 기록을 갱신했다고 안내합니다.','조건에 맞을 때만 출력합니다.'),
112:('현재 문제·점수를 파일에 저장하고 성공 여부를 검사합니다.','새 최고점이 아니어도 저장을 시도합니다. if 안에 함수를 호출하면 호출부터 실행됩니다.'),
113:('파일 저장이 성공했다는 안내입니다.','save가 True를 반환했을 때 실행됩니다.'),
114:('저장이 실패하거나 보류된 경우입니다.','바로 위 if self.save()의 반대 갈래입니다.'),
115:('이번 점수가 메모리에만 남았을 수 있다고 알립니다.','프로그램 종료 후 유지된다고 거짓 안내하지 않습니다.'),
119:('새 문제 문장을 빈 값이 아니게 입력받습니다.','아직 객체나 목록을 수정하지 않고 지역변수에만 저장합니다.'),
120:('선택지 1~4의 내용을 차례로 입력받아 list로 만듭니다.','range(1,5)의 끝 5는 포함되지 않습니다. 빈 선택지는 같은 번호에서 다시 받습니다.'),
121:('정답 번호를 정수 1~4로 입력받습니다.','내용에 적힌 숫자가 아니라 선택지의 번호입니다.'),
122:('검증된 입력으로 Quiz 객체를 만듭니다.','생성자의 자료형·범위 검사도 다시 적용됩니다.'),
123:('완성된 객체 한 개를 목록 맨 뒤에 추가합니다.','입력 중 Ctrl+C·EOF가 나면 이 줄까지 오지 않으므로 반쪽 문제가 추가되지 않습니다.'),
124:('메모리의 문제 목록에 추가됐음을 안내합니다.','파일 저장 성공 메시지와 분리되어 있습니다.'),
125:('추가된 퀴즈가 포함된 전체 상태를 저장합니다.','save 결과가 True인지 확인합니다.'),
126:('새 퀴즈의 파일 저장이 성공했다고 안내합니다.','프로그램 재실행 후에도 사용할 수 있도록 저장된 상태입니다.'),
127:('추가 후 파일 저장이 실패한 경우입니다.','메모리 목록에 추가한 사실까지 취소하는 코드는 아닙니다.'),
128:('추가한 문제는 메모리에만 있다고 알립니다.','저장 실패가 숨겨지지 않습니다.'),
132:('목록이 비어 있는지 검사합니다.','play의 빈 목록 검사와 목적이 같습니다.'),
133:('보여 줄 문제가 없다고 안내합니다.','빈 목록에서 enumerate 출력으로 바로 넘어가지 않습니다.'),
134:('목록 보기 메서드만 끝내 메뉴로 돌아갑니다.','프로그램은 계속 실행됩니다.'),
135:('등록된 문제 수를 출력합니다.','len(self.quizzes)는 현재 목록의 길이입니다.'),
136:('문제 객체에 표시 번호 1부터 붙여 꺼냅니다.','저장된 정답 번호나 문제 자체의 속성을 바꾸지 않습니다.'),
137:('번호와 해당 문제 문장을 출력합니다.','quiz.question은 Quiz 객체의 속성입니다.'),
141:('최고점이 아직 없는지 검사합니다.','is None으로 0과 미플레이를 구분합니다.'),
142:('아직 완료한 판이 없음을 안내합니다.','실제로 0개를 맞힌 판과 다른 상태입니다.'),
143:('한 번 이상 판을 마친 경우의 갈래입니다.','최고점이 0이어도 이쪽으로 갑니다.'),
144:('최고 정답 수를 출력합니다.','이 프로그램의 점수 단위는 백분율이 아닌 정답 개수입니다.'),
148:('현재 파일을 덮어써도 되는 상태인지 검사합니다.','load에서 읽기 실패·백업 실패가 나면 can_save는 False입니다.'),
149:('원본 보호 때문에 저장을 하지 않는다고 알립니다.','정상 저장 완료 메시지가 아닙니다.'),
150:('저장 실패·보류를 False로 반환합니다.','호출자가 성공과 실패를 구분할 수 있습니다.'),
151:('각 Quiz를 dict로 바꾼 목록을 payload에 넣습니다.','목록 내포는 q.to_dict()를 문제마다 호출합니다. 아직 파일에 쓰지 않았습니다.'),
152:('같은 payload dict에 최고점 필드를 넣습니다.','None은 JSON에서 null로 변환됩니다.'),
153:('state.json.tmp라는 임시 경로를 만듭니다.','경로 객체만 만든 단계이며 아직 파일을 열지 않았습니다.'),
154:('파일 쓰기·교체의 접근 오류를 잡을 구간입니다.','OSError를 아래 except에서 처리합니다.'),
155:('임시 파일을 UTF-8 쓰기 모드로 엽니다.','w는 기존 임시 파일이 있으면 덮어씁니다. with가 끝나면 파일을 닫습니다.'),
156:('payload를 JSON 형식으로 파일에 씁니다.','ensure_ascii=False는 한글 표시, indent=2는 두 칸 들여쓰기입니다. UTF-8 인코딩 지정과는 별개입니다.'),
157:('완성한 임시 파일로 실제 state.json을 교체합니다.','두 줄의 with 블록을 벗어나 파일이 닫힌 다음 실행합니다. 기존 데이터가 일부만 덮이는 위험을 줄입니다.'),
158:('파일 열기·쓰기·교체 오류를 error 이름으로 받습니다.','as는 예외 객체에 지역 이름을 붙입니다.'),
159:('실제 저장 오류의 내용을 안내합니다.','이 함수에서는 오류를 안내한 뒤 False로 결과를 전달합니다.'),
160:('파일 저장 실패를 False로 반환합니다.','이 줄이 실행되면 아래 성공 return에 도달하지 않습니다.'),
161:('저장이 완료됐음을 True로 반환합니다.','정상적으로 임시 파일을 쓰고 교체한 뒤에만 도달합니다.'),
165:('전체 상태 데이터가 dict인지 검사합니다.','파일 문법이 맞아도 최상위가 list라면 이 프로그램의 스키마와 다릅니다.'),
166:('잘못된 최상위 구조를 예외로 알립니다.','이 검증은 load에서 손상 상태로 처리됩니다.'),
167:('quizzes가 list이며 best_score 키가 존재하는지 검사합니다.','get은 키가 없으면 기본 None을 반환합니다. 아직 게임의 속성을 바꾸지 않습니다.'),
168:('저장 필드 구조가 틀리면 예외를 냅니다.','불완전한 상태를 적용하지 않습니다.'),
169:('저장된 문제마다 Quiz.from_dict를 호출해 객체 목록을 만듭니다.','중간 항목이 잘못되면 예외가 발생합니다. 검증 중인 지역변수라 기존 게임 상태는 유지됩니다.'),
170:('저장 데이터의 최고점을 지역변수로 읽습니다.','아직 self.best_score에 대입한 것이 아닙니다.'),
171:('최고점이 None 또는 0 이상 정수인지 검사합니다.','bool은 제외합니다. 현재 코드에는 문항 수와의 상한 비교는 없습니다.'),
172:('잘못된 최고점 값을 예외로 알립니다.','예: 음수·문자열·True는 허용하지 않습니다.'),
173:('검증된 목록과 점수 두 값을 tuple로 반환합니다.','load에서 quizzes, score로 나누어 받습니다.'),
177:('파일 읽기와 내용 검증에서 발생할 오류를 처리하기 시작합니다.','open·json.load·parse_state가 모두 같은 try 안에 있습니다.'),
178:('상태 파일을 UTF-8 읽기 모드로 엽니다.','r은 읽기 모드입니다. 파일이 없으면 FileNotFoundError입니다.'),
179:('JSON 텍스트를 Python dict/list 등의 값으로 바꿉니다.','문법 손상은 JSONDecodeError, UTF-8 해석 실패는 UnicodeDecodeError가 날 수 있습니다.'),
180:('구조를 검증하고 복원한 목록과 점수를 지역변수에 받습니다.','검증이 끝나기 전에는 self의 기본 상태를 덮지 않습니다.'),
181:('상태 파일이 없는 첫 실행을 처리합니다.','일반 읽기 오류보다 구체적인 FileNotFoundError를 먼저 처리합니다.'),
182:('기본 퀴즈로 시작한다고 안내합니다.','__init__에서 기본 목록을 이미 만들었습니다.'),
183:('load를 끝내 기본 상태를 유지합니다.','파일이 없다는 이유로 프로그램을 비정상 종료하지 않습니다.'),
184:('JSON 문법·문자 인코딩·구조 검증 오류를 손상 상태로 처리합니다.','ValueError에는 Quiz 생성자와 parse_state의 검증 오류도 포함됩니다.'),
185:('손상 원인을 출력합니다.','예외 객체를 f 문자열에 넣어 이유를 보여 줍니다.'),
186:('원래 state.json과 같은 폴더에 백업 경로를 만듭니다.','괄호를 열어 다음 두 물리적 줄로 경로 표현식을 이어 씁니다.'),
187:('현재 시각을 포함한 손상 원본 백업 이름을 만듭니다.','%Y%m%d는 날짜, %H%M%S는 시각, %f는 마이크로초입니다.'),
188:('with_name 호출의 괄호를 닫습니다.','이 줄은 독립적인 계산이 아니라 186행 표현식의 끝입니다.'),
189:('백업 복사 자체의 파일 오류도 별도로 처리합니다.','바깥 손상 처리 안에 들어 있는 try입니다.'),
190:('손상 파일 원본을 백업 위치로 복사합니다.','원본 내용은 그대로 두고 사본을 만듭니다. copy2는 가능한 파일 메타데이터도 보존합니다.'),
191:('만든 백업의 파일 이름을 안내합니다.','backup.name은 전체 경로가 아닌 마지막 파일명 부분입니다.'),
192:('백업 복사 중 파일 접근 오류가 발생한 경우입니다.','backup_error는 바깥 error와 구분한 이름입니다.'),
193:('이번 실행에서는 상태 파일을 덮어쓰지 않게 설정합니다.','백업 실패 시 원본이 사라지는 일을 막는 정책입니다.'),
194:('백업 실패와 원본 보호 조치를 안내합니다.','기본 퀴즈로 실행은 계속할 수 있지만 저장은 보류됩니다.'),
195:('이번 실행은 기본 문제로 복구한다고 안내합니다.','기본 목록과 None 점수는 __init__에서 준비한 상태입니다.'),
196:('손상 파일 처리 후 load를 끝냅니다.','아래의 정상 상태 적용 코드에는 내려가지 않습니다.'),
197:('손상이 아닌 일반적인 파일 읽기 접근 오류를 처리합니다.','예: 파일 경로가 디렉터리이거나 읽기 권한이 없는 경우입니다.'),
198:('읽지 못한 원본에 새 상태를 덮지 않도록 저장을 보류합니다.','can_save는 이후 save가 검사하는 공유 속성입니다.'),
199:('읽기 실패 이유와 기본 상태·저장 보류 정책을 안내합니다.','성공했다고 표시하지 않습니다.'),
200:('읽기 실패 처리 후 load를 끝냅니다.','다음 정상 적용 줄이 실행되지 않습니다.'),
201:('모든 검증을 마친 목록과 최고점을 게임 상태로 적용합니다.','tuple을 두 속성으로 나눠 대입합니다. 오류 없이 try를 통과해야 도달합니다.'),
202:('정상 데이터를 불러왔다고 안내합니다.','파일을 읽기만 한 것이 아니라 구조 검증까지 끝난 뒤 출력됩니다.'),
205:('메뉴를 계속 보여 주는 반복을 시작합니다.','선택한 기능이 끝나면 다시 이 반복으로 돌아옵니다.'),
206:('다섯 메뉴와 앞쪽 줄바꿈을 출력합니다.','문자열의 \\n은 실제 출력에서 줄바꿈이 됩니다.'),
207:('1~5의 정상 정수 메뉴 번호를 입력받습니다.','입력 오류와 범위 처리는 read_number에 맡깁니다.'),
208:('종료 번호 5인지 검사합니다.','choice는 int이므로 문자열 "5"가 아닌 정수 5와 비교합니다.'),
209:('종료 안내를 출력합니다.','저장 성공까지 뜻하는 메시지는 아닙니다. 저장은 main의 finally에서도 시도합니다.'),
210:('run을 끝내 main으로 돌아갑니다.','main은 이어 finally를 실행합니다.'),
211:('번호가 1이면 퀴즈 풀기 갈래입니다.','위 종료 조건이 거짓인 경우에 검사합니다.'),
212:('같은 게임 객체의 play를 실제로 호출합니다.','함수 정의와 메뉴가 연결되는 지점입니다.'),
213:('번호가 2이면 등록 갈래입니다.','입력값을 문자열과 비교하지 않습니다.'),
214:('퀴즈 등록 메서드를 호출합니다.','문제·선택지·정답을 받고 목록과 파일을 갱신합니다.'),
215:('번호가 3이면 목록 갈래입니다.','등록 개수와 문장을 확인할 때 사용합니다.'),
216:('문제 목록 표시 메서드를 호출합니다.','호출이 끝나면 메뉴 반복이 계속됩니다.'),
217:('번호가 4이면 최고점 갈래입니다.','미플레이 상태도 show_score가 처리합니다.'),
218:('최고 정답 수 표시 메서드를 호출합니다.','이 호출은 점수 자체를 바꾸지 않습니다.'),
219:('앞의 조건 어느 것도 맞지 않을 때의 갈래입니다.','현재 read_number가 1~5만 반환하고 위에서 모두 처리하므로 정상 입력에서는 도달하지 않는 남은 안내입니다.'),
220:('아직 연결하지 않은 기능이라는 남은 안내 문구입니다.','현재 완성된 1~5 메뉴에서는 정상적으로 실행되지 않습니다. 실제 기능이 미구현이라는 뜻으로 해석할 필요는 없습니다.'),
224:('게임 객체를 만들어 초기화·기본 데이터·load를 실행합니다.','이 줄은 아래 try 밖입니다. 파일 오류는 load 자체가 처리하지만 초기화의 모든 오류를 main의 except가 잡는 것은 아닙니다.'),
225:('메뉴 실행 중 입력 중단을 처리할 구간을 시작합니다.','아래 game.run() 호출이 이 try의 대상입니다.'),
226:('메뉴 루프를 실제로 시작합니다.','사용자가 종료하거나 예외가 발생할 때까지 이 호출에서 진행됩니다.'),
227:('Ctrl+C와 입력 스트림 종료를 처리합니다.','KeyboardInterrupt는 Ctrl+C, EOFError는 input에서 더 읽을 입력이 없을 때 발생합니다.'),
228:('입력 종료를 안내합니다.','추적 오류를 그대로 보여 주는 대신 종료 이유를 설명합니다.'),
229:('정상 종료·처리한 입력 중단 후 정리 동작을 시작합니다.','finally는 강제 프로세스 종료까지 보장하는 기능은 아닙니다.'),
230:('종료 시 현재 상태를 저장하고 성공 여부를 확인합니다.','추가·완료한 판 뒤 이미 저장했더라도 여기서 다시 저장을 시도합니다.'),
231:('종료 저장이 성공했다고 알립니다.','game.save()가 True를 돌려줬을 때만 나옵니다.'),
232:('종료 저장이 실패하거나 보류된 갈래입니다.','읽기·백업 실패로 can_save=False인 경우도 포함합니다.'),
233:('파일에 이번 변경이 남지 않았을 수 있다고 알립니다.','실패를 성공 메시지로 감추지 않습니다.'),
236:('이 파일을 직접 실행한 경우인지 검사합니다.','python3 main.py이면 참, 다른 파일에서 import main이면 보통 거짓입니다.'),
237:('main을 호출해 프로그램을 시작합니다.','위쪽 def는 함수 정의이고, 실제 메뉴 실행의 시작은 이 호출을 거쳐 이루어집니다.'),
}

scopes=[]
definition_lines={}
def visit(nodes,prefix=''):
    for node in nodes:
        if isinstance(node,(ast.ClassDef,ast.FunctionDef)):
            name=prefix+node.name
            start=min([node.lineno]+[d.lineno for d in getattr(node,'decorator_list',[])])
            scopes.append((start,node.end_lineno,name,node))
            definition_lines[node.lineno]=(name,node)
            if isinstance(node,ast.ClassDef):visit(node.body,name+'.')
visit(tree.body)
def scope_at(line):
    found=[x for x in scopes if x[0]<=line<=x[1]]
    return min(found,key=lambda s:s[1]-s[0])[2] if found else '전역·구역 사이'

rows=[]
for number,code in enumerate(lines,1):
    if not code.strip():
        meaning,detail='구역을 나누는 빈 줄입니다.','읽기 편하게 하기 위한 공백이며 이 줄 자체는 실행 동작이 없습니다.'
    elif number in definition_lines:
        name,node=definition_lines[number]
        title,detail=SUMMARIES[name]
        meaning=('클래스를 정의합니다: ' if isinstance(node,ast.ClassDef) else '함수·메서드를 정의합니다: ')+title
        if isinstance(node,ast.FunctionDef):
            detail+=' 매개변수: '+', '.join(a.arg for a in node.args.args)+'. 정의만으로 본문이 실행되지는 않습니다.'
    elif number in NOTES:meaning,detail=NOTES[number]
    else:raise RuntimeError(f'Missing explanation for source line {number}: {code}')
    rows.append({'number':number,'code':code,'meaning':meaning,'detail':detail,'scope':scope_at(number),'blank':not code.strip(),'indent':len(code)-len(code.lstrip(' '))})

esc=html.escape
nav=''.join(f'<a href="#L{node.lineno}" data-scope-link="{esc(name)}">{esc(name)}</a>' for _,_,name,node in scopes)
table=''.join(f'<tr id="L{r["number"]}" data-scope="{esc(r["scope"])}" data-blank="{str(r["blank"]).lower()}"><th scope="row"><a href="#L{r["number"]}">{r["number"]}</a></th><td class="source"><code>{esc(r["code"]) if r["code"] else " "}</code></td><td><span class="scope-tag">{esc(r["scope"])} · 들여쓰기 {r["indent"]}칸</span><strong>{esc(r["meaning"])}</strong><p>{esc(r["detail"])}</p></td></tr>' for r in rows)
options=''.join(f'<option value="{esc(name)}">{esc(name)}</option>' for _,_,name,_ in scopes)
summaries=''.join(f'<article><h3><a href="#L{node.lineno}">{esc(name)}</a></h3><strong>{esc(SUMMARIES[name][0])}</strong><p>{esc(SUMMARIES[name][1])}</p></article>' for _,_,name,node in scopes)
flow=[(236,'직접 실행 확인'),(237,'main() 호출'),(224,'QuizGame 준비'),(78,'기본 문제·load'),(226,'run 메뉴'),(207,'입력·기능 호출'),(230,'종료 시 저장')]
flow_html=''.join(f'<li><a href="#L{line}"><small>{index+1}</small>{esc(label)}<span>{line}행 보기</span></a></li>' for index,(line,label) in enumerate(flow))
css='''*{box-sizing:border-box}html{scroll-behavior:smooth;scroll-padding-top:22px;background:#eef3f8;color:#23364d;font:15px/1.8 "Malgun Gothic",sans-serif}body{margin:0}nav{position:fixed;inset:0 auto 0 0;width:260px;background:#142d46;padding:24px 18px;overflow:auto;color:white}nav strong{display:block;font-size:20px;margin-bottom:15px}nav a{display:block;color:#dce9f6;text-decoration:none;font:13px/1.55 Consolas,"Malgun Gothic",monospace;padding:7px;border-radius:6px;overflow-wrap:anywhere}nav a:hover{background:#294b6c}main{margin:28px 30px 60px 290px;max-width:1500px;padding:34px;background:white;border-radius:14px}h1{color:#123e68;font-size:30px;line-height:1.45}h2{color:#164b77;font-size:22px;margin-top:42px}h3{font-size:16px}a{color:#17679f}.meta{padding:15px 18px;background:#eef6fd;border-left:4px solid #2e81bd;border-radius:7px}.hash{font:12px/1.7 Consolas,monospace;overflow-wrap:anywhere}.flow{display:grid;grid-template-columns:repeat(auto-fit,minmax(125px,1fr));gap:10px;padding:0;list-style:none}.flow a{display:flex;flex-direction:column;height:100%;padding:14px;border:1px solid #b9d0e4;border-radius:10px;text-decoration:none;font-weight:bold}.flow small{color:#69839e}.flow span{font-size:12px;font-weight:normal}.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:12px}.cards article{border:1px solid #d3e0ec;border-radius:9px;padding:16px}.cards article p{font-size:14px}.controls{display:flex;gap:12px;align-items:center;flex-wrap:wrap;padding:16px;background:#edf5fc;border-radius:9px;margin:20px 0}.controls input[type=search]{flex:1;min-width:220px}.controls input,.controls select,button{font:inherit;padding:8px;border:1px solid #acc3d9;border-radius:6px;background:white;color:#20486b}.count{font-size:13px;color:#56718c}.table-wrap{overflow:auto}table{width:100%;border-collapse:collapse;table-layout:fixed}thead th{background:#e9f1f9;text-align:left;border:1px solid #c5d5e5;padding:12px}thead th:first-child{width:56px}thead th:nth-child(2){width:43%}td,tbody th{border:1px solid #d7e1eb;padding:12px;vertical-align:top}tbody th{background:#f5f8fc;font:13px/1.8 Consolas,monospace;text-align:right}.source{background:#f8fafc}.source code{display:block;font:13px/1.85 Consolas,"Malgun Gothic",monospace;white-space:pre-wrap;overflow-wrap:anywhere;color:#243a52}td strong{display:block;font-size:14px}td p{font-size:13px;color:#526b83;margin:6px 0 0}.scope-tag{display:block;color:#6b849c;font:11px/1.6 Consolas,"Malgun Gothic",monospace;margin-bottom:6px}tr[data-blank=true] td,tr[data-blank=true] th{padding-top:5px;padding-bottom:5px;color:#7c8c9b}tr[data-blank=true] td strong{font-weight:normal}tr:target td,tr:target th,tr.focused td,tr.focused th{background:#fff4cc!important}tr[hidden]{display:none}details{border:1px solid #bad0e4;padding:16px;border-radius:9px;margin:20px 0}summary{cursor:pointer;font-weight:bold}pre{background:#15293c;color:#e4f0fa;padding:18px;overflow:auto;max-height:650px;margin:0;border-radius:0 0 8px 8px}pre code{font:13px/1.8 Consolas,"Malgun Gothic",monospace;white-space:pre}.code-label{background:#26435c;color:#e7f3ff;padding:8px 14px;border-radius:8px 8px 0 0;margin-top:16px}.note{font-size:14px;color:#536d85}footer{border-top:1px solid #d0dfeb;margin-top:40px;padding-top:18px;font-size:13px;color:#637c93}@media(max-width:1100px){nav{position:static;width:auto;max-height:240px}main{margin:14px;padding:22px}}@media(max-width:700px){.table-wrap table{min-width:820px}h1{font-size:24px}}@media print{nav,.controls,.count{display:none}main{margin:0;padding:0;max-width:none}html{background:white;font-size:10pt}thead{display:table-header-group}tr{break-inside:avoid}.cards{display:block}.cards article{break-inside:avoid}pre{max-height:none}td,th{padding:6px}}'''
js='''(function(){const rows=Array.from(document.querySelectorAll('tbody tr'));const search=document.querySelector('#search'),scope=document.querySelector('#scope'),hide=document.querySelector('#hide-blank'),count=document.querySelector('#count');function apply(){const query=search.value.trim().toLowerCase();let visible=0;rows.forEach(row=>{row.hidden=(hide.checked&&row.dataset.blank==='true')||(scope.value&&row.dataset.scope!==scope.value)||(query&&!row.textContent.toLowerCase().includes(query));if(!row.hidden)visible++;});count.textContent=visible+' / '+rows.length+'줄 표시';}function revealHash(){const row=document.getElementById(location.hash.slice(1));if(row&&row.tagName==='TR'){search.value='';scope.value='';apply();row.hidden=false;row.scrollIntoView({block:'center'});}}search.addEventListener('input',apply);scope.addEventListener('change',apply);hide.addEventListener('change',apply);document.querySelector('#reset').addEventListener('click',()=>{search.value='';scope.value='';hide.checked=true;apply();});window.addEventListener('hashchange',revealHash);apply();if(location.hash)revealHash();})();'''
page=f'''<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>내 main.py · 237줄 코드 해설</title><style>{css}</style></head><body><nav><strong>main.py 줄별 해설</strong><a href="#overview">실행 순서</a><a href="#line-table">한 줄씩 읽기</a><a href="#functions">함수별 요약</a>{nav}</nav><main><p>CODYSSEY E1-2 · 현재 작성한 코드 해설</p><h1>내 main.py를 한 줄씩 읽기</h1><div class="meta"><strong>2026-11-09에 확인한 실제 main.py {len(lines)}줄 기준</strong><p>교재의 임의 예제가 아니라 현재 로컬 파일의 코드·줄 번호·들여쓰기를 그대로 사용했습니다. 이 페이지는 그 시점의 설명본입니다. 코드를 수정하면 줄 번호와 설명이 달라질 수 있습니다.</p><p class="hash">SHA-256: {digest}</p></div><h2 id="overview">실행은 맨 아래에서 시작합니다</h2><p>파일을 읽으면서 import·상수·함수·클래스를 준비합니다. def는 본문 실행이 아닙니다. 맨 아래 실행 조건이 main을 호출하면 게임 초기화 → 메뉴 → 기능 → 저장 순서가 진행됩니다.</p><ol class="flow">{flow_html}</ol><details><summary>현재 main.py 전체 보기·복사</summary><div class="code-label">Python · 실제 파일 전체 ({len(lines)}줄)</div><pre><code>{esc(text)}</code></pre></details><h2 id="line-table">코드 · 줄별 설명</h2><p class="note">왼쪽 줄 번호를 누르면 해당 위치에 링크할 수 있습니다. 기본 화면은 빈 줄을 숨기지만 원본 번호는 유지합니다. self는 같은 객체를 가리키며, return은 현재 함수만 끝냅니다. 프로그램 종료는 메뉴에서 돌아온 main의 정리까지 이어집니다.</p><div class="controls"><input id="search" type="search" placeholder="코드·설명 검색: self, return, 저장, None…" aria-label="코드와 설명 검색"><select id="scope" aria-label="함수 선택"><option value="">모든 함수·구역</option>{options}</select><label><input id="hide-blank" type="checkbox" checked> 빈 줄 숨기기</label><button id="reset" type="button">필터 초기화</button></div><p id="count" class="count" aria-live="polite"></p><div class="table-wrap"><table><thead><tr><th>줄</th><th>실제 코드</th><th>이 줄의 역할과 연결</th></tr></thead><tbody>{table}</tbody></table></div><h2 id="functions">함수·클래스별 요약</h2><div class="cards">{summaries}</div><footer>원본: main.py · 코드 자체는 변경하거나 실행하지 않고 AST와 실제 텍스트를 읽어 해설했습니다. 설명 생성기는 scripts/build_code_guide.py입니다. 파일 SHA가 달라지면 틀린 줄 설명을 자동 재사용하지 않고 재검토를 요구합니다.</footer></main><script>{js}</script></body></html>'''
# The shared copy implementation is inlined for offline use.
copy_client=(ROOT/'scripts/code-copy-client.js').read_text(encoding='utf-8')
copy_style='<style>.code-label{display:flex;align-items:center;justify-content:space-between;gap:12px;flex-wrap:wrap}.code-copy-actions{display:inline-flex;align-items:center;gap:10px}.code-copy-actions button{cursor:pointer;padding:6px 12px;font-size:13px}.code-copy-status{font-size:12px;color:#e0f1ff}@media print{.code-copy-actions{display:none}}</style>'
page=page.replace('</head>',copy_style+'</head>').replace('</body>','<script id="code-copy-client">'+copy_client+'</script></body>')
from code_guide_view import render
page = render(text, rows, 'E1-2 · 퀴즈 게임', digest)
output=ROOT/'docs/code/main_line_by_line.html'
output.parent.mkdir(parents=True,exist_ok=True)
output.write_text(page,encoding='utf-8')
(output.parent/'source_snapshot.json').write_text(json.dumps({'date':'2026-11-09','source':'main.py','sha256':digest,'lineCount':len(lines),'annotatedRows':len(rows),'nonblankRows':sum(not r['blank'] for r in rows)},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'lines':len(lines),'rows':len(rows),'nonblank':sum(not r['blank'] for r in rows),'sourceUnchanged':hashlib.sha256(source.read_bytes()).hexdigest()==digest}))
