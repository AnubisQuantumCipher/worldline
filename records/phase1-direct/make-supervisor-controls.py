"""Generate fixed JSON fixtures for direct Ada supervisor regression cases."""
import base64
import copy
import json
from pathlib import Path
import textwrap
unit='worldline-11111111-2222-3333-4444-555555555555.service'
kind='agent-supervision-acquisition'
started='39f53479d3a045ac8e11786248231fbf'
starting='7d4958e842da4a758f6c1cdc7b36dcc5'
exited='98e322203f7a4ed290d09fe03c09fe15'

def js(x): return json.dumps(x,separators=(',',':'))
def event(message,code=None,status=None):
    return {'_SYSTEMD_UNIT':'user@1000.service','_COMM':'systemd',
            'USER_UNIT':unit,'__REALTIME_TIMESTAMP':1,'MESSAGE_ID':message,
            'EXIT_CODE':code,'EXIT_STATUS':status}
def poll(index,events=None):
    o={'unit':unit,'sinceUs':0}
    if events is None:
        o.update(site='journal-tool-unavailable',journalctl=None)
    else:
        raw='\n'.join(map(js,events)).encode()
        o.update(site='journal-poll',readerUid=1000,
                 argv=['journalctl','--user','-u',unit,'-o','json','--no-pager','--since=@0'],
                 stdout={'encoding':'base64','payload':base64.b64encode(raw).decode()},
                 processReturnObserved=True,processWaitReturnObserved=True,
                 stdoutReachedEof=True,stderrReachedEof=True,exception=None,
                 returncode=0,processWaitReturncode=0)
    return {'kind':kind,'occurrence':index,'observation':o}
def projection(e):
    return {'messageId':e['MESSAGE_ID'],'message':'','jobType':None,'jobResult':None,
            'exitCode':e['EXIT_CODE'],'exitStatus':e['EXIT_STATUS'],
            'managerPid':None,'realtimeUs':1}
def record(events,exit_code,mode,started_flag,evidence=None,status=None,result=None,readable=True):
    return {'events':list(map(projection,events)),'kind':mode,'unit':unit,
            'source':'journal' if readable else 'journal-unavailable',
            'launcherExit':exit_code,'started':started_flag,'stoppedByManager':False,
            'supervisionEvidence':evidence,'exitCode':'exited' if status is not None else None,
            'exitStatus':status,'result':result,'windowMilliseconds':10000,'launcherStderr':''}
rows=[poll(0)]
unavailable=record([],1,'INDETERMINATE',False,readable=False)
cases=[('unavailable observation remains valid',rows,unavailable,1,True,3)]
bad=copy.deepcopy(rows);del bad[0]['observation']['journalctl']
cases.append(('missing unavailable witness rejected',bad,unavailable,1,False,0))
cases.append(('poll after unavailable terminal rejected',[poll(0),poll(1,[])],unavailable,1,False,0))
cases.append(('started state cannot leak into later empty poll',
              [poll(0,[event(started)]),poll(1,[])],record([],1,'LAUNCH_FAILED',False),1,True,3))
cases.append(('launched state cannot leak into later empty poll',
              [poll(0,[event(starting)]),poll(1,[])],record([],1,'LAUNCH_FAILED',False),1,True,3))
events=[event(started),event(exited,'exited',0),event(exited,'exited',7)]
expected=record(events,0,'SUPERVISED',True,'started-entry',0,'success')
cases.append(('first exit selected instead of last exit',[poll(0,events)],expected,0,True,1))
bad=copy.deepcopy(expected);bad['events'][1]['exitStatus']=9
cases.append(('retained event mismatch rejected',[poll(0,events)],bad,0,False,0))

def literal(s,indent=6):
    return (' &\n'+' '*indent).join('"'+part.replace('"','""')+'"' for part in textwrap.wrap(s,76,break_long_words=True,break_on_hyphens=False,replace_whitespace=False,drop_whitespace=False))
lines=['with Worldline.Evaluation_Agent_Native;','with Worldline.Evaluation_Wire;','',
       '-- Fixed ordinary raw fixtures. These are not protected-host evidence.',
       'procedure Native_Supervisor_Controls is',
       '   package N renames Worldline.Evaluation_Agent_Native;',
       '   use type Worldline.Evaluation_Wire.Byte;',
       '   Unit_Name : constant String := "'+unit+'";',
       '   Acquisition_Kind : constant String := "'+kind+'";']
for i,(name,rows,supervisor,exit_code,valid,expected_kind) in enumerate(cases,1):
    lines.extend(['',f'   procedure Case_{i} is',
                  '      Observed : constant String :=\n         '+literal(js(rows),9)+';',
                  '      Supervisor : constant String :=\n         '+literal(js(supervisor),9)+';',
                  '      Facts : constant N.Supervisor_Facts := N.Supervisor_Decide',
                  f'        (Observed, Acquisition_Kind, Unit_Name, "0", "{exit_code}", Supervisor, False);',
                  '   begin',f'      if Facts.Valid /= {str(valid)}'+
                  (f' or else Facts.Kind /= {expected_kind} or else Facts.Stopped' if valid else '')+' then',
                  '         raise Program_Error with "'+name+'";',
                  '      end if;',f'   end Case_{i};'])
lines.append('begin')
lines.extend(f'   Case_{i};' for i in range(1,len(cases)+1))
lines.append('end Native_Supervisor_Controls;')
Path('tests/native_supervisor_controls.adb').write_text('\n'.join(lines)+'\n')
p=Path('tests/worldline_core_tests.adb');s=p.read_text()
assert 'with Native_Supervisor_Controls;' not in s
s='with Native_Supervisor_Controls;\n'+s
s=s.replace('   Ada.Text_IO.Put_Line ("worldline_core_tests: PASS");','   Native_Supervisor_Controls;\n   Ada.Text_IO.Put_Line ("worldline_core_tests: PASS");')
p.write_text(s)
print('Generated',len(cases),'fixed native supervisor cases')
