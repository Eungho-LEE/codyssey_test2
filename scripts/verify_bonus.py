"""Verify bonus features and basic regressions without changing user state."""
import contextlib
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import platform
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs/records'
spec = importlib.util.spec_from_file_location('quiz_submission', ROOT / 'main.py')
game_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(game_module)
checks, sessions = [], []
state_path = ROOT / 'state.json'
original_state = state_path.read_bytes() if state_path.exists() else None


def check(name, condition):
    if not condition:
        raise AssertionError(name)
    checks.append({'name': name, 'passed': True})


def cli(folder, name, inputs, expected):
    result = subprocess.run([sys.executable, str(folder / 'main.py')], input=inputs,
                            text=True, capture_output=True, timeout=10, cwd=folder)
    check(name, result.returncode == 0 and not result.stderr
          and all(item in result.stdout for item in expected))
    sessions.append({'name': name, 'stdin': inputs, 'stdout': result.stdout,
                     'stderr': result.stderr, 'returncode': result.returncode})


with tempfile.TemporaryDirectory(prefix='quiz-bonus-') as temporary:
    folder = Path(temporary)
    shutil.copy2(ROOT / 'main.py', folder / 'main.py')
    target = folder / 'state.json'
    with patch.object(game_module, 'STATE_PATH', target), contextlib.redirect_stdout(io.StringIO()):
        game = game_module.QuizGame()
        check('default hints', all(quiz.hint for quiz in game.quizzes))
        quiz = game_module.Quiz('Question', ['A', 'B', 'C', 'D'], 1, 'A hint')
        check('hint round trip', game_module.Quiz.from_dict(quiz.to_dict()).hint == 'A hint')
        legacy = {'quizzes': [{'question': 'Legacy', 'choices': ['A','B','C','D'], 'answer': 1}], 'best_score': 4}
        quizzes, best, history = game.parse_state(legacy)
        check('old state compatibility', best == 4 and history == [] and quizzes[0].hint == '')
        game.quizzes = [quiz, game_module.Quiz('Second', ['A','B','C','D'], 2, 'B hint')]
        original_order = list(game.quizzes)
        # Deterministically exercise random selection without relying on a lucky order.
        with patch.object(game_module.random, 'sample', return_value=game.quizzes[::-1]) as sample:
            with patch('builtins.input', side_effect=['abc', '0', '3', '2', 'h', 'h', '2', '1']):
                game.play()
            check('random.sample receives selected count', sample.call_args.args == (game.quizzes, 2))
        check('source question order unchanged', game.quizzes == original_order)
        check('hint charged once per question', game.history[-1]['points'] == 17 and game.history[-1]['hints_used'] == 1)
        check('history has time and question count', game.history[-1]['question_count'] == 2 and 'T' in game.history[-1]['played_at'])
        restored = game_module.QuizGame()
        check('history persists on restart', restored.history == game.history and restored.best_score == 2)
        with patch.object(game_module.random, 'sample', return_value=[quiz]), patch('builtins.input', side_effect=['1', '2']):
            game.play()
        check('zero-score game retained and best preserved', len(game.history) == 2 and game.history[-1]['points'] == 0 and game.best_score == 2)
        with patch.object(game_module.random, 'sample', return_value=[quiz]), patch('builtins.input', side_effect=['1', EOFError()]):
            try:
                game.play()
            except EOFError:
                pass
        check('interrupted game not recorded', len(game.history) == 2)
        no_hint = game_module.Quiz.from_dict(legacy['quizzes'][0])
        with patch.object(game_module.random, 'sample', return_value=[no_hint]), patch('builtins.input', side_effect=['1', 'h', '1']):
            game.play()
        check('missing legacy hint has no penalty', game.history[-1]['points'] == 10 and game.history[-1]['hints_used'] == 0)
        for field, value in [('points', 1000), ('question_count', True), ('played_at', 'bad')]:
            bad = json.loads(target.read_text(encoding='utf-8'))
            bad['history'][0][field] = value
            try:
                game.parse_state(bad)
            except ValueError:
                check('reject malformed history ' + field, True)
            else:
                raise AssertionError(field)
        with patch('builtins.input', return_value='0'):
            game.delete_quiz()
        check('delete zero cancels', len(game.quizzes) == 2)
        with patch('builtins.input', side_effect=['1', 'n']):
            game.delete_quiz()
        check('delete confirmation cancels', len(game.quizzes) == 2)
        with patch('builtins.input', side_effect=['1', 'y']):
            game.delete_quiz()
        check('delete persists', len(game_module.QuizGame().quizzes) == 1)
        game.can_save = False
        before = target.read_bytes()
        with patch('builtins.input', side_effect=['1', 'y']):
            game.delete_quiz()
        check('failed save preserves file', target.read_bytes() == before)
        with patch('builtins.input', side_effect=AssertionError('empty play should not prompt')):
            game.play()
        check('empty game safe', game.quizzes == [])

    subset_quizzes = [game_module.Quiz('Random ' + str(i), ['A','B','C','D'], 1).to_dict() for i in range(3)]
    target.write_text(json.dumps({'quizzes': subset_quizzes, 'best_score': None}), encoding='utf-8')
    cli(folder, 'random_subset', '1\n2\n1\n1\n5\n', ['2문제 중 2개 정답', '점수: 20점'])
    subset_state = json.loads(target.read_text(encoding='utf-8'))
    check('real CLI subset preserves all stored questions', subset_state['quizzes'] == subset_quizzes
          and subset_state['history'][0]['question_count'] == 2
          and sum(sessions[-1]['stdout'].count('Random ' + str(i)) for i in range(3)) == 2)
    target.write_text(json.dumps({'quizzes': [quiz.to_dict()], 'best_score': None}), encoding='utf-8')
    cli(folder, 'play_hint_history', '1\n0\n2\n1\nabc\n\n0\n5\nh\nh\n1\n7\n4\n5\n',
        ['1~1 범위', '정수를 입력', '빈 입력', '1~4 범위', '1문제 중 1개 정답', '점수: 7점', '힌트 차감 후 최고 점수: 7점', '게임 기록'])
    cli(folder, 'restart', '7\n4\n5\n', ['저장된 데이터를 불러왔습니다.', '1문제 / 정답 1개 / 7점 / 힌트 1회'])
    cli(folder, 'add_delete', '2\nNew\nA\nB\nC\nD\n2\nNew hint\n6\n2\ny\n3\n5\n',
        ['추가한 퀴즈를 파일에도 저장', '삭제한 결과를 파일에도 저장', '등록된 퀴즈: 1개'])
    cli(folder, 'menu_validation', 'abc\n\n8\n5\n', ['정수를 입력', '빈 입력', '1~7 범위'])
    cli(folder, 'eof', '', ['입력이 종료되어 게임을 마칩니다.', '현재 데이터를 저장했습니다.'])
    for name, raw in [('json', b'{bad'), ('encoding', b'\xff'), ('schema', b'{"quizzes":{},"best_score":null}')]:
        target.write_bytes(raw)
        cli(folder, 'corrupt_' + name, '5\n', ['손상 원본 백업', '기본 퀴즈로 복구'])
        check('corrupt backup ' + name, any(p.read_bytes() == raw for p in folder.glob('state.corrupt-*.json')))
    target.unlink()
    target.mkdir()
    cli(folder, 'read_error', '5\n', ['읽기 실패', '저장을 보류'])
    target.rmdir()
    (folder / 'state.json.tmp').mkdir()
    cli(folder, 'write_error', '5\n', ['저장하지 못했습니다', '저장 실패 또는 보류'])
    (folder / 'state.json.tmp').rmdir()
    if os.name == 'posix':
        for name, prefix in [('menu', ''), ('play', '1\n1\n'), ('add', '2\nPartial\n')]:
            process = subprocess.Popen([sys.executable, str(folder / 'main.py')], cwd=folder,
                stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if prefix:
                process.stdin.write(prefix)
                process.stdin.flush()
            time.sleep(0.15)
            process.send_signal(signal.SIGINT)
            output, error = process.communicate(timeout=10)
            check('SIGINT ' + name, process.returncode == 0 and not error and '입력이 종료되어 게임을 마칩니다.' in output)
            sessions.append({'name': 'SIGINT ' + name, 'stdin': prefix + '[SIGINT]', 'stdout': output, 'stderr': error, 'returncode': process.returncode})

check('real user state unchanged', (state_path.read_bytes() if state_path.exists() else None) == original_state)
OUT.mkdir(parents=True, exist_ok=True)
report = {'date': '2026-11-10', 'python': sys.version, 'platform': platform.platform(),
          'main_sha256': hashlib.sha256((ROOT / 'main.py').read_bytes()).hexdigest(),
          'passed': len(checks), 'checks': checks, 'sessions': sessions}
(OUT / 'bonus-verification.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
(OUT / 'bonus-cli.txt').write_text('\n\n'.join(
    '$ python3 main.py\n[STDIN]\n' + s['stdin'] + '\n[STDOUT]\n' + s['stdout']
    + '\n[STDERR]\n' + (s['stderr'] or '(none)') + f"\n[exit={s['returncode']}]" for s in sessions) + '\n', encoding='utf-8')
log = OUT / 'bonus-cli.txt'
log.write_text('\n'.join(line.rstrip() for line in log.read_text(encoding='utf-8').splitlines()) + '\n', encoding='utf-8')
print(json.dumps({'passed': len(checks), 'sessions': len(sessions), 'userStateUnchanged': True}))
