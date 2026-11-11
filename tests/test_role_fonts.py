import importlib.util,json,unittest
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('role_back',BASE/'skills/research-harness/scripts/scientific_backends.py');back=importlib.util.module_from_spec(s);s.loader.exec_module(back)
class RoleFonts(unittest.TestCase):
 def test_unknown_role_does_not_pass_as_body(self):
  import matplotlib;matplotlib.use('Agg')
  import matplotlib.pyplot as plt
  profile=json.loads((BASE/'skills/research-harness/assets/style-profile.json').read_text())
  fig,ax=plt.subplots();label=ax.text(.3,.5,'Catalyst');label._research_role='subtitlle'
  back.style_figure(fig,profile,8)
  report=back.typography_audit(fig,profile,8,'F',lambda *a:None)
  self.assertFalse(report['passed'])
  self.assertFalse(next(r for r in report['records'] if r['text']=='Catalyst')['role_known'])
  label._research_role='subtitle';back.style_figure(fig,profile,8)
  self.assertTrue(back.typography_audit(fig,profile,8,'F',lambda *a:None)['passed']);plt.close(fig)
 def test_actual_font_file_is_used_and_missing_label_is_reported(self):
  import matplotlib;matplotlib.use('Agg')
  import matplotlib.pyplot as plt
  from matplotlib.ft2font import FT2Font
  font=Path(matplotlib.get_data_path())/'fonts/ttf/DejaVuSans.ttf';profile=json.loads((BASE/'skills/research-harness/assets/style-profile.json').read_text());profile['roles']['source']={**profile['roles']['body'],'font_family':FT2Font(str(font)).family_name,'font_file':str(font)};fig,ax=plt.subplots();t=ax.text(.3,.5,'Sample');t._research_role='source';back.style_figure(fig,profile,8);audit=back.typography_audit(fig,profile,8,'F',lambda *a:None);self.assertTrue(audit['passed']);self.assertEqual(Path(t.get_fontproperties().get_file()),font);self.assertTrue(audit['records'][0]['font_file_override']);t.set_text(chr(0x10ffff));audit=back.typography_audit(fig,profile,8,'F',lambda *a:None);self.assertFalse(audit['passed']);plt.close(fig)
if __name__=='__main__':unittest.main()
