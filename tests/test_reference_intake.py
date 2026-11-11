import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

p=Path(__file__).resolve().parents[1]/'skills/scientific-figure/scripts/reference_intake.py'
s=importlib.util.spec_from_file_location('reference_intake',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class IntakeTests(unittest.TestCase):
    def test_html_is_not_accepted_as_pdf(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaisesRegex(ValueError,'not PDF'):m.inspect_pdf(b'<html>Login</html>',d,[1],'test')
            self.assertFalse((Path(d)/'source.pdf').exists())
    def test_extraction_does_not_claim_visual_or_semantic_inspection(self):
        import fitz
        doc=fitz.open();page=doc.new_page();page.insert_text((50,50),'Actual visible text')
        with tempfile.TemporaryDirectory() as d:
            report=m.inspect_pdf(doc.tobytes(),d,[1],'local synthetic test')
            self.assertEqual(report['visual_inspection_status'],'unassessed')
            self.assertTrue((Path(d)/'page-1.png').exists())
            card=json.loads((Path(d)/'pattern-card.json').read_text())
            self.assertTrue(all(v['origin']=='unknown' for v in card['layers'].values()))
    def test_region_context_and_target_preserve_explicit_geometry(self):
        import fitz
        doc=fitz.open();page=doc.new_page(width=300,height=200)
        page.insert_text((60,70),'TEST_BOUNDARY')
        plan=[{'id':'whole','page':1,'rect_pt':[40,30,180,100],'target_px':[200,200]},
              {'id':'cut','page':1,'rect_pt':[80,40,110,90]}]
        with tempfile.TemporaryDirectory() as d:
            report=m.extract_regions(doc.tobytes(),d,plan,'synthetic fixture')
            whole,cut=report['regions']
            self.assertEqual(whole['rect_pt'],[40,30,180,100])
            self.assertEqual(whole['contain_image_rect_px'],[0,50,200,150])
            self.assertEqual(whole['text_crossing_crop_edge'],[])
            self.assertTrue(cut['text_crossing_crop_edge'])
            self.assertEqual(report['visual_inspection_status'],'unassessed')
            pix=fitz.Pixmap(str(Path(d)/'whole-target.png'))
            self.assertEqual((pix.width,pix.height),(200,200))
            self.assertLess(whole['context_rect_pt'][0],whole['rect_pt'][0])
    def test_invalid_region_is_rejected_before_writing(self):
        import fitz
        doc=fitz.open();doc.new_page(width=100,height=100)
        with tempfile.TemporaryDirectory() as d:
            out=Path(d)/'assets'
            with self.assertRaisesRegex(ValueError,'inside'):
                m.extract_regions(doc.tobytes(),out,[{'id':'bad','page':1,'rect_pt':[-1,0,40,40]}],'fixture')
            self.assertFalse(out.exists())
if __name__=='__main__':unittest.main()
