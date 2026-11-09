"""Run the current program on isolated working copies and save real CLI evidence."""
import hashlib
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

ROOT=Path(__file__).resolve().parent.parent
RECORDS=ROOT/'docs/records'
RECORDS.mkdir(parents=True,exist_ok=True)
main_before=(ROOT/'main.py').read_bytes()
state_before=(ROOT/'state.json').read_bytes() if (ROOT/'state.json').exists() else None
cases=[]

def execute(directory,inputs,case_id,title,expected=(),timeout=8):
    process=subprocess.run([sys.executable,str(directory/'main.py')],input=inputs,text=True,capture_output=True,cwd=directory,timeout=timeout)
    passed=process.returncode==0 and all(text in process.stdout for text in expected) and 'Traceback' not in process.stderr
    record={'id':case_id,'title':title,'command':'python3 main.py','stdin':inputs,'stdout':process.stdout,'stderr':process.stderr,'returncode':process.returncode,'passed':passed}
    cases.append(record)
    if not passed:raise AssertionError(record)
    return record

def fresh(parent,name):
    directory=parent/name;directory.mkdir();(directory/'main.py').write_bytes(main_before);return directory

if os.name!='posix':raise SystemExit('Run this verification in WSL/Linux for real SIGINT evidence.')
with tempfile.TemporaryDirectory(prefix='codyssey-e12-submit-') as temp:
    parent=Path(temp)
    d=fresh(parent,'normal')
    execute(d,'5\n','menu','메뉴와 정상 종료',('첫 실행','1. 퀴즈 풀기','종료합니다.','현재 데이터를 저장했습니다.'))
    execute(d,'abc\n\n9\n 3 \n5\n','menu_validation','문자·빈 입력·범위·공백 메뉴',('정수를 입력','빈 입력','1~5 범위','등록된 퀴즈: 5개'))
    execute(d,'4\n5\n','unplayed','아직 플레이하지 않은 최고점',('아직 퀴즈를 풀지 않았습니다.',))
    execute(d,'2\n\nGitHub에 커밋을 올리는 명령은?\n\npush\npull\nlog\nstatus\nabc\n0\n5\n1\n3\n5\n','add','퀴즈 등록 검증과 목록',('빈 내용','정수를 입력','1~4 범위','추가한 퀴즈를 파일에도 저장','등록된 퀴즈: 6개'))
    state=json.loads((d/'state.json').read_text(encoding='utf-8'))
    assert len(state['quizzes'])==6 and state['quizzes'][-1]['answer']==1
    execute(d,'3\n5\n','list','추가한 퀴즈 목록 확인',('등록된 퀴즈: 6개','GitHub에 커밋을 올리는 명령은?'))
    execute(d,'1\nabc\n0\n5\n\n 1 \n2\n3\n4\n1\n1\n4\n5\n','play','전체 플레이·잘못된 정답 재입력·최고점',('정수를 입력','1~4 범위','빈 입력','6문제 중 6개 정답','최고 정답 수: 6개'))
    execute(d,'4\n5\n','score','저장한 최고 정답 수 확인',('최고 정답 수: 6개',))
    execute(d,'3\n4\n5\n','restart','재시작 후 추가 문항·최고점 복원',('저장된 데이터를 불러왔습니다.','등록된 퀴즈: 6개','최고 정답 수: 6개'))
    execute(d,'1\n2\n1\n1\n1\n2\n2\n4\n5\n','best_preserved','낮은 점수 이후 최고점 유지',('6문제 중 0개 정답','최고 정답 수: 6개'))
    z=fresh(parent,'zero')
    execute(z,'1\n2\n1\n1\n1\n2\n4\n5\n','zero_score','첫 판 0점과 미플레이 구분',('5문제 중 0개 정답','최고 정답 수: 0개'))
    e=fresh(parent,'empty')
    (e/'state.json').write_text('{"quizzes": [], "best_score": null}',encoding='utf-8')
    execute(e,'1\n3\n4\n5\n','empty','빈 문제 목록의 플레이·목록·점수',('등록된 퀴즈가 없습니다.','아직 퀴즈를 풀지 않았습니다.'))
    for name,raw in [('json',b'{broken'),('encoding',b'\xff'),('schema',b'{"quizzes": [{"question":"x","choices":["A"],"answer":1}], "best_score":0}')]:
        c=fresh(parent,'corrupt_'+name);(c/'state.json').write_bytes(raw)
        execute(c,'3\n5\n','corrupt_'+name,'손상 데이터 복구: '+name,('상태 파일 손상','손상 원본 백업','기본 퀴즈로 복구','등록된 퀴즈: 5개'))
        assert any(p.read_bytes()==raw for p in c.glob('state.corrupt-*.json'))
    bad=fresh(parent,'read_error');(bad/'state.json').mkdir()
    execute(bad,'5\n','read_error','읽기 실패 시 원본 보호·저장 보류',('읽기 실패','저장을 보류','저장 실패 또는 보류'))
    bad=fresh(parent,'write_error');(bad/'state.json.tmp').mkdir()
    execute(bad,'5\n','write_error','쓰기 실패 안내',('저장하지 못했습니다:','저장 실패 또는 보류'))
    for label,prefix in [('menu',''),('play','1\n'),('add','2\n중단될 문제\n')]:
        c=fresh(parent,'interrupt_'+label)
        p=subprocess.Popen([sys.executable,str(c/'main.py')],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,cwd=c)
        if prefix:p.stdin.write(prefix);p.stdin.flush()
        time.sleep(0.2)
        p.send_signal(signal.SIGINT)
        out,err=p.communicate(timeout=8)
        passed=p.returncode==0 and '입력이 종료되어 게임을 마칩니다.' in out and not err
        assert passed,(label,p.returncode,out,err)
        state=json.loads((c/'state.json').read_text(encoding='utf-8'))
        assert len(state['quizzes'])==5
        cases.append({'id':'sigint_'+label,'title':'실제 SIGINT: '+label,'command':'python3 main.py; then SIGINT at input wait','stdin':prefix,'stdout':out,'stderr':err,'returncode':p.returncode,'passed':passed})
    c=fresh(parent,'eof')
    execute(c,'','eof','입력 스트림 EOF 안전 종료',('입력이 종료되어 게임을 마칩니다.','현재 데이터를 저장했습니다.'))

assert (ROOT/'main.py').read_bytes()==main_before
assert ((ROOT/'state.json').read_bytes() if (ROOT/'state.json').exists() else None)==state_before
environment={'python':platform.python_version(),'python_executable':sys.executable,'platform':platform.platform(),'git':subprocess.check_output(['git','--version'],text=True).strip(),'system':os.uname().sysname,'kernel':os.uname().release,'code_sha256':hashlib.sha256(main_before).hexdigest()}
if Path('/etc/os-release').exists():
    for line in Path('/etc/os-release').read_text().splitlines():
        if line.startswith('PRETTY_NAME='):environment['distribution']=line.split('=',1)[1].strip('"')
report={'date':'2026-11-09','environment':environment,'caseCount':len(cases),'passCount':sum(c['passed'] for c in cases),'cases':cases,'originalMainUnchanged':True,'originalStateUnchanged':True,'method':'Actual WSL subprocess runs on isolated working copies; SIGINT cases send a real signal. Screenshots show these recorded outputs in a verification viewer.'}
(RECORDS/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
for case in cases:
    body='[실제 실행 검증 기록]\n'+case['title']+'\n명령: '+case['command']+'\n\n[전달한 입력]\n'+(case['stdin'] or '(EOF)\n')+'\n[실제 표준 출력]\n'+case['stdout']+'\n[실제 표준 오류]\n'+(case['stderr'] or '(없음)\n')+f'\n종료 코드: {case["returncode"]}\n검증: '+('PASS' if case['passed'] else 'FAIL')+'\n'
    (RECORDS/(case['id']+'.txt')).write_text(body,encoding='utf-8')
(RECORDS/'environment.txt').write_text('[실제 WSL 실행 환경]\n'+json.dumps(environment,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'cases':len(cases),'passed':len(cases),'mainUnchanged':True,'stateUnchanged':True}))
