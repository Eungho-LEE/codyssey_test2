# 개발 기초 퀴즈 게임 · Codyssey E1-2

Python·터미널·Git의 기본 개념을 터미널에서 풀어 보는 콘솔 퀴즈 게임입니다. 문제 풀기, 직접 등록, 목록, 최고 정답 수 확인과 JSON 저장·복원을 구현했습니다.

- 미션: 컴퓨터에게 명령 내리는 말(파이썬) 처음 배우기
- 저장소: [Eungho-LEE/codyssey_test2](https://github.com/Eungho-LEE/codyssey_test2)
- 검증일: 2026-11-09
- 코드 해설: [현재 main.py 237줄의 줄별 설명 HTML](docs/code/main_line_by_line.html) — 파일을 내려받아 브라우저에서 열면 검색·함수별 이동·전체 코드 복사를 사용할 수 있습니다.

## 1. 퀴즈 주제와 선정 이유

주제는 **파이썬·터미널·Git 개발 기초**입니다. 개발환경 구성과 Python 입문에서 실제 사용하는 명령·자료구조를 짧은 객관식 문제로 복습할 수 있도록 구성했습니다. 기본 문제는 파일 확장자, 빈 파일 생성, 현재 경로 확인, Git 커밋, 목록 인덱스의 다섯 문항입니다.

각 문제에는 문장, 선택지 네 개, 정답 번호가 있습니다. 프로그램에서 새로운 개발 기초 문제를 직접 추가할 수 있습니다. 초기 기본 데이터와 실행 중 사용자가 등록한 데이터는 구분됩니다.

## 2. 실행 환경

실제 WSL 환경에서 확인한 값입니다. [환경 기록](docs/records/environment.txt), [환경 화면](docs/screenshots/environment.png)을 함께 보관했습니다.

| 항목 | 확인 값 |
| --- | --- |
| 플랫폼 | Windows의 WSL 2 / Ubuntu-26.04 |
| Python | 3.14.4 — 과제의 3.10 이상 조건 충족 |
| Git | 2.53.0 |
| Linux 커널 | 6.18.54.1-microsoft-standard-WSL2 |
| 라이브러리 | json, pathlib, shutil, datetime 등 Python 표준 라이브러리 |
| 외부 패키지 설치 | 필요 없음 |

## 3. 실행 방법

```bash
git clone https://github.com/Eungho-LEE/codyssey_test2.git
cd codyssey_test2
python3 --version
python3 main.py
```

Windows에서 Python을 직접 실행한다면 `py -3 main.py`를 사용할 수 있습니다. WSL에서는 위 `python3` 명령을 사용합니다. 코드는 `.py` 파일에 작성하고, 터미널에는 실행 명령을 입력합니다.

첫 실행에 `state.json`이 없으면 기본 문제 다섯 개와 미플레이 상태로 시작합니다. 정상 종료 또는 데이터 변경 시 파일을 생성합니다. 이미 `state.json`이 있으면 그 파일의 문제와 최고점을 불러오므로 목록이 다섯 개보다 많을 수 있습니다.

| 번호 | 메뉴 | 동작 |
| --- | --- | --- |
| 1 | 퀴즈 풀기 | 등록된 모든 문제를 차례로 풀고 정답·오답과 총 정답 수 출력 |
| 2 | 퀴즈 추가 | 문제·선택지 4개·정답 번호를 입력받고 저장 |
| 3 | 퀴즈 목록 | 등록 개수와 문제 문장 확인 |
| 4 | 점수 확인 | 최고 정답 수 또는 아직 플레이하지 않았다는 안내 |
| 5 | 종료 | 메뉴를 끝내고 현재 상태 저장 |

숫자 앞뒤 공백은 제거합니다. 빈 입력, `abc`, 메뉴의 `9`, 정답의 `0`·`5`는 안내 후 재입력합니다. Ctrl+C 또는 입력 스트림 종료(EOF)도 안내하고 가능한 상태를 저장한 뒤 종료합니다.

## 4. 기능과 코드 구조

| 구성 | 책임 |
| --- | --- |
| `read_number` | 공백·빈 입력·정수 변환·범위 검증 |
| `read_nonempty` | 빈 문제·선택지 재입력 |
| `Quiz` | 문제·선택지·정답 검증, 출력, 판정, dict 변환·복원 |
| `QuizGame` | 문제 목록·최고점·메뉴·파일 입출력·복구 관리 |
| `main` | 게임 생성, 메뉴 실행, Ctrl+C·EOF 처리와 종료 저장 |

`Quiz`와 `QuizGame` 두 클래스로 역할을 분리하고 각 기능은 별도 메서드로 구현했습니다. `main()` 호출은 실행 시작 조건 아래 한 번만 둡니다. 파일을 import할 때 메뉴가 자동 실행되지 않습니다.

점수의 단위는 **완료한 한 판의 정답 개수**입니다. 최고점은 새 정답 수가 더 클 때만 갱신합니다. 아직 플레이하지 않은 값은 `None`, 한 판을 마쳤지만 모두 틀린 값은 `0`으로 구분합니다. 플레이 중 중단된 판은 최고점에 반영하지 않습니다.

## 5. 파일 구조

```text
codyssey_test2/
├─ main.py                       # 프로그램 시작 파일
├─ practice_basics.py            # 입출력·자료형 연습
├─ README.md
├─ .gitignore
├─ state.example.json            # 기본 5문제·미플레이 상태의 형식 예시
├─ state.json                    # 실행하면 생성되는 로컬 데이터, Git 제외
├─ scripts/
│  ├─ verify_submission.py       # 실제 WSL 실행 검증 및 기록 생성
│  ├─ build_code_guide.py        # 검토한 코드 스냅샷의 줄별 설명 생성
│  └─ code-copy-client.js        # 오프라인 설명 페이지의 복사 기능
└─ docs/
   ├─ code/                     # 줄별 설명 HTML·소스 지문
   ├─ records/                  # 실제 입력·출력·환경·검증 JSON·Git 기록
   └─ screenshots/              # 환경·추가·목록·플레이·점수·Git 그래프 PNG
```

## 6. 데이터 파일 설명

데이터 경로는 **프로젝트 루트의 `state.json`**입니다. `Path(__file__).resolve().parent`를 사용하므로 터미널의 현재 폴더가 달라도 `main.py` 옆의 파일을 읽습니다.

```json
{
  "quizzes": [
    {
      "question": "Python 파일의 확장자는?",
      "choices": [".py", ".jpg", ".mp3", ".zip"],
      "answer": 1
    }
  ],
  "best_score": null
}
```

위 JSON은 필드 설명용 한 문제 예시입니다. [state.example.json](state.example.json)에는 기본 문제 다섯 개가 들어 있습니다. 예시 파일을 자동으로 읽지는 않으며, 기본 문제는 `make_default_quizzes()`가 생성합니다.

| 필드 | 의미·검증 |
| --- | --- |
| `quizzes` | 문제 객체 목록. 빈 목록도 유효하며 플레이·목록 메뉴가 안내 처리 |
| `question` | 공백 제거 후 비어 있지 않은 문자열 |
| `choices` | 비어 있지 않은 문자열 네 개 |
| `answer` | 정수 1~4. 목록 인덱스 0~3과 구분 |
| `best_score` | 미플레이는 `null`, 플레이 후는 0 이상 정수 |

UTF-8로 읽고 쓰며, `ensure_ascii=False`로 한글을 그대로 기록합니다. `Quiz` 객체를 `to_dict()`로 바꿔 저장하고 `from_dict()`로 복원합니다.

저장은 `state.json.tmp`에 완성한 뒤 `state.json`으로 교체합니다. 읽은 데이터는 전체 구조를 검증한 뒤 게임 상태에 적용합니다.

| 상황 | 처리 |
| --- | --- |
| 파일 없음 | 기본 퀴즈·미플레이 상태로 시작 |
| JSON 문법·인코딩·스키마 손상 | 원본을 `state.corrupt-시각.json`으로 백업하고 기본 상태로 복구 |
| 읽기 실패·손상 원본 백업 실패 | 기본 상태로 실행하되 원본 보호를 위해 저장 보류 |
| 쓰기 실패 | 실패 안내와 `False` 반환. 저장 성공으로 표시하지 않음 |

개인 실습 데이터와 손상 원본은 `.gitignore`로 제외합니다. 이 저장소를 내려받으면 기본 상태에서 실행되며, 기존 로컬의 `state.json`은 그대로 유지됩니다.

## 7. 검증 방법과 실제 결과

현재 `main.py`를 실제 WSL의 **격리된 작업 복사본**에서 실행해 20개 시나리오를 확인했습니다. 원본 `main.py`와 기존 로컬 `state.json`은 바꾸지 않았습니다. 검증 중 기본 다섯 문제에 검증용 문제 한 개를 추가한 결과가 화면에 보일 수 있습니다.

```bash
python3 scripts/verify_submission.py
```

검증은 표준 라이브러리만 사용합니다. Ctrl+C 항목은 실제 SIGINT 신호를 보냅니다. 상세 결과는 [verification.json](docs/records/verification.json), 입력과 출력은 `docs/records/*.txt`에 있습니다.

| 확인 항목 | 결과·증거 |
| --- | --- |
| 첫 실행·메뉴·종료 | PASS · [기록](docs/records/menu.txt) |
| 문자·빈 입력·범위·공백 메뉴 | PASS · [기록](docs/records/menu_validation.txt) |
| 기본 미플레이 상태 | PASS · [기록](docs/records/unplayed.txt) |
| 퀴즈 등록·빈 문장·잘못된 정답 입력 | PASS · [기록](docs/records/add.txt), [화면](docs/screenshots/add.png) |
| 추가한 문제 목록 | PASS · [기록](docs/records/list.txt), [화면](docs/screenshots/list.png) |
| 플레이·정답 재입력·최고점 | PASS · [기록](docs/records/play.txt), [화면](docs/screenshots/play.png) |
| 최고 정답 수 확인 | PASS · [기록](docs/records/score.txt), [화면](docs/screenshots/score.png) |
| 종료·재실행 후 문제·최고점 유지 | PASS · [기록](docs/records/restart.txt) |
| 낮은 점수 후 최고점 유지 | PASS · [기록](docs/records/best_preserved.txt) |
| 첫 판 0점과 미플레이 구분 | PASS · [기록](docs/records/zero_score.txt) |
| 빈 문제 목록 | PASS · [기록](docs/records/empty.txt) |
| 손상 JSON·인코딩·필드 구조 | PASS · [JSON](docs/records/corrupt_json.txt), [인코딩](docs/records/corrupt_encoding.txt), [구조](docs/records/corrupt_schema.txt) |
| 읽기·쓰기 실패 | PASS · [읽기](docs/records/read_error.txt), [쓰기](docs/records/write_error.txt) |
| 메뉴·플레이·등록 도중 Ctrl+C | PASS · [메뉴](docs/records/sigint_menu.txt), [플레이](docs/records/sigint_play.txt), [등록](docs/records/sigint_add.txt) |
| EOF 종료 | PASS · [기록](docs/records/eof.txt) |

스크린샷은 **실제 WSL 실행에서 수집한 입력·출력 기록을 검증용 HTML 뷰어로 열어 캡처한 화면**입니다. 실행 중인 VSCode 터미널 화면을 촬영한 것은 아닙니다. 원시 기록도 함께 제공해 수치와 출력 내용을 확인할 수 있습니다. [검증 기록 보기](docs/records/evidence.html)는 내려받아 브라우저에서 열 수 있습니다.

## 8. Git 이력과 원격 동기화

기능별 커밋을 유지했습니다. 최초 제출 정리 전에도 17개 커밋이 있었으며 최소 10개 조건을 충족합니다. 초기 설정, 입출력 연습, 메뉴, 입력 검증, Quiz, 기본 데이터, 플레이, 추가, 목록, 점수, 저장, 오류 처리 등 변경 이유가 드러나는 이력이 있습니다.

- `feature/play`: 플레이 구현 커밋 `12a3546`, main 병합 `edae640`.
- 초기 로컬·원격 이력 병합: `02f15d6`.
- 복제 저장소의 README 수정 커밋: `f491336`.
- 원래 작업 폴더에서 원격 이력을 가져와 병합한 커밋: `aa1d93b`.
- 최종 정리 뒤 별도 복제 폴더의 변경을 push하고 원래 폴더에서 pull하는 실습도 다시 확인했습니다. [동기화 기록](docs/records/remote-sync.txt)
- [Git 그래프 원문](docs/records/git-log.txt), [Git 그래프 화면](docs/screenshots/git.png)

init·add·commit·push·checkout·clone·pull을 사용해 학습했습니다. init·add 자체는 커밋 그래프만으로 모두 증명할 수 없으므로 실제 수행 명령과 원격 동기화 기록을 함께 설명합니다.

```bash
git --no-pager log --oneline --graph --decorate --all
git rev-list --count HEAD
git status
```

`git diff`나 `git log`의 `(END)` 화면에서는 `q`로 돌아옵니다. Ctrl+Z로 `Stopped` 상태가 됐다면 같은 터미널에서 `fg` 후 `q`로 나옵니다. `--no-pager`는 별도 보기 화면을 생략합니다.

## 9. 실제 문제와 해결

| 문제 | 원인·확인 | 해결 |
| --- | --- | --- |
| `git commit -m` 오류 | 메시지 없이 옵션만 입력 | `git commit -m "변경 내용"`으로 메시지 포함 |
| 첫 push의 `fetch first` | GitHub 초기 커밋과 로컬 이력이 다름 | 원격 이력을 가져와 보존하며 병합 후 push |
| `--ff-only` pull 실패 | 원격 README 변경과 로컬 기능 커밋이 갈라짐 | 그래프 확인 후 `origin/main`을 병합하고 push |
| `topic` 명령을 찾지 못함 | Python 코드를 bash에 직접 입력 | `.py` 파일에 저장하고 `python3 파일명.py`로 실행 |
| 실행해도 아무 출력 없음 | 입력 함수만 정의하고 메뉴 호출이 없음 | 기존 메뉴를 유지하고 `read_number`와 `main()`을 연결 |

## 10. 제출 체크

- [x] 주제와 기본 퀴즈 5개 이상, 각 선택지 4개·정답 번호
- [x] 메뉴·플레이·추가·목록·점수·종료
- [x] Quiz·QuizGame과 기능별 메서드 분리
- [x] 공통 입력 검증·Ctrl+C·EOF 처리
- [x] 루트 state.json의 UTF-8 저장·로드·복구·재실행 유지
- [x] 의미 있는 커밋 10개 이상, 기능 브랜치 생성·병합
- [x] clone 변경·push 후 원래 작업 폴더 pull 확인
- [x] README 필수 항목과 환경·실행·Git 증거 파일

랜덤 출제·문항 수 선택·힌트·삭제·전체 게임 히스토리는 선택 과제로, 현재 필수 구현에 포함하지 않았습니다.

## 원격 동기화 실습

별도 복제 폴더에서 README를 수정하고 commit·push한 뒤 원래 작업 폴더에서 가져오는 과정을 수행했습니다. 최종 동기화 확인은 위 기록 파일에 남깁니다.
