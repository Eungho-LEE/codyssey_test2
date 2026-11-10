# 개발 기초 퀴즈 게임 · Codyssey E1-2

Python·터미널·Git의 기본 개념을 터미널에서 풀어 보는 콘솔 퀴즈 게임입니다. 문제 풀기, 직접 등록, 목록, 최고 정답 수 확인과 JSON 저장·복원에 보너스 5개 기능을 추가했습니다.

**보너스 과제 완료(2026-11-10): [기능·점수 정책·저장 형식·검증 방법](docs/BONUS.md)** · [최신 38개 검사 결과](docs/records/bonus-verification.json) · [실제 CLI 기록](docs/records/bonus-cli.txt)

- 미션: 컴퓨터에게 명령 내리는 말(파이썬) 처음 배우기
- 저장소: [Eungho-LEE/codyssey_test2](https://github.com/Eungho-LEE/codyssey_test2)
- 검증일: 2026-11-09
- 코드 해설: [보너스를 포함한 현재 main.py 323줄의 줄별 설명](docs/code/main_line_by_line.html) — 2026-11-10 갱신. 코드 옆 설명·검색·함수 이동·전체 코드 복사를 지원합니다. 새로 추가되거나 바뀐 설명은 `[보너스]`로 표시했습니다. [소스 일치 검증](docs/code/guide-verification.json) · [기능별 보너스 해설](docs/BONUS.md)

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
| 1 | 퀴즈 풀기 | 문제 수 선택 → 랜덤 출제 → 정답 번호 또는 h로 힌트 → 정답 수·점수 저장 |
| 2 | 퀴즈 추가 | 문제·선택지 4개·정답 번호·선택 힌트를 입력받고 저장 |
| 3 | 퀴즈 목록 | 등록 개수와 문제 문장 확인 |
| 4 | 점수 확인 | 최고 정답 수 또는 아직 플레이하지 않았다는 안내 |
| 5 | 종료 | 메뉴를 끝내고 현재 상태 저장 |
| 6 | 퀴즈 삭제 | 문제 번호와 y 확인 후 삭제하고 파일 저장 |
| 7 | 게임 기록 | 완료한 게임의 날짜·시간·문제 수·정답 수·점수·힌트 수 출력 |

숫자 앞뒤 공백은 제거합니다. 빈 입력, `abc`, 메뉴의 `9`, 정답의 `0`·`5`는 안내 후 재입력합니다. Ctrl+C 또는 입력 스트림 종료(EOF)도 안내하고 가능한 상태를 저장한 뒤 종료합니다. 플레이 중 중단된 판은 기록하지 않습니다.

## 4. 기능과 코드 구조

| 구성 | 책임 |
| --- | --- |
| `read_number` | 공백·빈 입력·정수 변환·범위 검증 |
| `read_nonempty` | 빈 문제·선택지 재입력 |
| `Quiz` | 문제·선택지·정답 검증, 출력, 판정, dict 변환·복원 |
| `QuizGame` | 문제 목록·최고점·메뉴·파일 입출력·복구 관리 |
| `main` | 게임 생성, 메뉴 실행, Ctrl+C·EOF 처리와 종료 저장 |

`Quiz`와 `QuizGame` 두 클래스로 역할을 분리하고 각 기능은 별도 메서드로 구현했습니다. `main()` 호출은 실행 시작 조건 아래 한 번만 둡니다. 파일을 import할 때 메뉴가 자동 실행되지 않습니다.

기존 최고 기록은 **완료한 한 판의 정답 개수**로 유지합니다. 보너스 점수는 정답당 10점에서 힌트 사용 문제당 3점을 차감하며 최소 0점입니다. 두 값을 함께 표시하고 개별 판의 문제 수도 기록합니다. 아직 플레이하지 않은 값은 `None`, 한 판을 마쳤지만 모두 틀린 값은 `0`으로 구분합니다. 플레이 중 중단된 판은 최고점에 반영하지 않습니다.

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
| `hint` | 문제별 선택 힌트. 예전 파일에 없으면 빈 문자열 |
| `history` | 완료 판의 시각·문제 수·정답 수·점수·힌트 수. 예전 파일에 없으면 빈 목록 |

UTF-8로 읽고 쓰며, `ensure_ascii=False`로 한글을 그대로 기록합니다. `Quiz` 객체를 `to_dict()`로 바꿔 저장하고 `from_dict()`로 복원합니다.

저장은 `state.json.tmp`에 완성한 뒤 `state.json`으로 교체합니다. 읽은 데이터는 전체 구조를 검증한 뒤 게임 상태에 적용합니다.

| 상황 | 처리 |
| --- | --- |
| 파일 없음 | 기본 퀴즈·미플레이 상태로 시작 |
| JSON 문법·인코딩·스키마 손상 | 원본을 `state.corrupt-시각.json`으로 백업하고 기본 상태로 복구 |
| 읽기 실패·손상 원본 백업 실패 | 기본 상태로 실행하되 원본 보호를 위해 저장 보류 |
| 쓰기 실패 | 실패 안내와 `False` 반환. 저장 성공으로 표시하지 않음 |

개인 실습 데이터와 손상 원본은 `.gitignore`로 제외합니다. 이 저장소를 내려받으면 기본 상태에서 실행되며, 기존 로컬의 `state.json`은 그대로 유지됩니다.

### 중첩 구조를 선택한 이유

최상위 객체에 게임 전체의 `best_score`와 문제 목록 `quizzes`를 두고, 각 문제 객체 안에 `question`·`choices`·`answer`를 묶었습니다. 문제와 선택지·정답의 관계를 한곳에서 확인할 수 있고, 서로 다른 목록의 순서를 맞춰 관리할 필요가 없습니다. 이 구조는 `Quiz.to_dict()`·`Quiz.from_dict()`와 대응하므로 문제 단위로 변환하고 검증하기 쉽습니다. 나중에 문제별 `category`나 `difficulty` 같은 필드를 추가해도 게임 전체 점수와 구분해 확장할 수 있습니다. 다만 새 필드를 실제로 사용하려면 클래스·변환·검증 코드도 함께 수정하고, 기존 파일에서 필드가 없을 때의 기본값이나 데이터 이전 규칙을 정해야 합니다.

### JSON 저장의 성능·메모리 한계와 대안

현재 방식은 소규모 개인 실습용입니다. 대규모 데이터의 실행 시간과 메모리 사용량은 측정하지 않았으며, 데이터가 커질 때 다음 한계가 있습니다.

| 구분 | 현재 구현의 한계 | 영향 |
| --- | --- | --- |
| 불러오기 | `json.load()`로 문서 전체를 읽고, 모든 문제를 `Quiz` 객체로 복원 | 파일이 커질수록 시작 시간이 늘고, 파싱한 자료구조와 복원 객체가 함께 존재하는 동안 메모리 사용이 증가 |
| 메모리 | 실행 중 모든 문제를 보관하고, 저장할 때 문제별 dict와 목록을 추가 생성 | Python 객체의 관리 비용까지 있어 필요한 메모리는 JSON 파일 크기보다 클 수 있음 |
| 저장 | 문제 하나만 추가해도 모든 문제와 점수를 임시 파일에 다시 기록 | 저장 한 번의 작업량이 전체 데이터 크기에 비례하고, 반복 추가 시 디스크 쓰기와 대기 시간이 누적 |
| 디스크 공간 | 교체 전까지 기존 파일과 새 임시 파일이 함께 존재 | 전체 상태를 한 번 더 기록할 여유 공간이 필요하며, 손상 백업도 별도 공간을 사용 |
| 동시 실행 | 프로세스 사이의 잠금·변경 조정이 없음 | 두 실행이 같은 파일을 저장하면 나중 저장이 앞선 변경을 덮어쓸 수 있음 |

확장 대안은 다음과 같습니다. 아래 방식은 현재 코드에 구현된 기능이 아니라 데이터 규모가 커질 때 검토할 설계입니다.

- **SQLite 등 데이터베이스:** 문제·선택지·점수를 테이블로 관리하고 변경한 행만 갱신합니다. 조건 검색과 페이지 단위 조회를 사용하면 전체 문제를 메모리에 올릴 필요가 줄며, 트랜잭션으로 관련 변경을 함께 확정할 수 있습니다. 적용하려면 현재의 전체 목록 중심 로직도 필요한 문제만 조회하도록 바꿔야 합니다.
- **스트리밍 읽기·쓰기:** 문제를 한 건씩 처리하는 파서나 JSON Lines 형식을 사용하고, 저장도 반복자에서 한 건씩 인코딩하면 전체 변환 목록을 추가로 만드는 부담을 줄일 수 있습니다. 현재의 `json.dump()`도 인코딩 결과를 나누어 파일에 쓰지만, 이미 만든 `payload`와 전체 문제 목록의 메모리 사용까지 없애지는 않습니다. 하나의 JSON 문서를 통째로 교체하는 구조에서는 스트리밍 쓰기를 적용해도 전체 재기록 비용은 남습니다.
- **추가 기록 방식:** JSON Lines에 새 문제를 덧붙이면 추가할 때 전체 파일을 다시 쓰는 일을 줄일 수 있습니다. 대신 수정·삭제·최고점 갱신, 중복 기록 정리, 쓰기 중 중단과 동시 접근을 처리할 별도 규칙이 필요합니다. 일반 JSON 문서에 객체를 단순히 이어 쓰면 유효한 단일 JSON 문서가 되지 않습니다.

현재의 임시 파일 교체는 불완전한 결과로 기존 파일을 바로 덮어쓰는 위험을 줄이는 장치입니다. 데이터베이스의 트랜잭션·동시 접근 제어를 대신하지는 않습니다. 실제 전환 시점은 문제 수만으로 단정하지 않고 파일 크기, 시작·저장 시간, 최대 메모리 사용량을 측정해 결정합니다.

## 7. 검증 방법과 실제 결과

최신 코드는 실제 WSL의 **격리된 작업 복사본**에서 38개 검사를 통과했습니다. [최신 검증 JSON](docs/records/bonus-verification.json)과 [실제 CLI 기록](docs/records/bonus-cli.txt)을 확인하세요. 사용자의 기존 로컬 `state.json`은 바꾸지 않았습니다. 아래 표와 캡처는 2026-11-09 기본과제의 20개 시나리오에 대한 당시 기록입니다.

```bash
python3 scripts/verify_submission.py
```

검증은 표준 라이브러리만 사용합니다. Ctrl+C 항목은 실제 SIGINT 신호를 보냅니다. `verify_submission.py`는 현재 `verify_bonus.py`의 전체 회귀 검사를 실행하는 진입점입니다. 과거 기본과제 결과는 [verification.json](docs/records/verification.json)에 별도로 보관합니다.

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

충돌 발생 시 대응 절차: `git merge origin/main`(기능 병합은 `git merge feature/play`) → 충돌 시 `git status`로 대상 확인 → 파일의 `<<<<<<<`·`=======`·`>>>>>>>` 표시를 제거하고 양쪽의 필요한 변경을 반영 → `git add <해결한_파일>` → `git commit`으로 병합 완료 → 실행 검증 후 `git push origin main`. 이는 충돌 발생 시 적용할 절차이며, 위 병합 커밋만으로 실제 충돌 발생·해결 여부를 입증하지는 않습니다.

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

- [x] 보너스 5개: 랜덤 출제·문항 수 선택·힌트·삭제·전체 게임 히스토리

## 원격 동기화 실습

별도 복제 폴더에서 README를 수정하고 commit·push한 뒤 원래 작업 폴더에서 가져오는 과정을 수행했습니다. 최종 동기화 확인은 위 기록 파일에 남깁니다.

### 최종 동기화 확인 (2026-11-09)

별도 복제 폴더에서 제출 문서의 최신 버전을 확인하고 이 문장을 추가했습니다. 이 변경을 commit·push한 뒤 원래 작업 폴더에서 pull하여 동일한 문장과 커밋을 확인합니다.
