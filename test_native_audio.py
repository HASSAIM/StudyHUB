import json,tempfile,time,unittest
from pathlib import Path
from unittest.mock import patch
import store,native_audio
class NativeAudioTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.old=store.DATA;store.DATA=Path(self.tmp.name);self.s=store.create('Audio fictif','fr');self.sid=self.s['id'];store.update(self.sid,native_audio=True)
 def tearDown(self):store.DATA=self.old;self.tmp.cleanup()
 def test_control_lease_preserves_pause_on_heartbeat(self):
  native_audio.control(self.sid,'pause');native_audio.heartbeat(self.sid)
  command=json.loads((store.folder(self.sid)/'native-control.json').read_text());self.assertEqual(command['action'],'pause');self.assertLess(abs(command['lease']-time.time()),2)
  native_audio.control(self.sid,'stop');native_audio.heartbeat(self.sid);self.assertEqual(json.loads((store.folder(self.sid)/'native-control.json').read_text())['action'],'stop')
 def test_invalid_control_and_non_native_session_rejected(self):
  with self.assertRaises(ValueError):native_audio.control(self.sid,'invalid')
  store.update(self.sid,native_audio=False)
  with self.assertRaises(ValueError):native_audio.control(self.sid,'pause')
 def test_stop_waits_for_capture_file_checkpoint(self):
  with patch.object(native_audio,'status',side_effect=[{'state':'recording'},{'state':'recording'},{'state':'stopped','seconds':12}]),patch.object(native_audio.time,'sleep'):state=native_audio.stop(self.sid)
  self.assertEqual(state['state'],'stopped');self.assertEqual(store.read(self.sid)['saved_seconds'],12)
 def test_one_system_capture_at_a_time(self):
  store.atomic(store.folder(self.sid)/'native-status.json',{'state':'recording'})
  second=store.create('Autre fictif','fr')
  with patch.object(native_audio,'build') as build:
   with self.assertRaisesRegex(ValueError,'autre enregistrement'):native_audio.start(second['id'])
   build.assert_not_called()
if __name__=='__main__':unittest.main()
