"""Package a reviewed allowlist; never include recordings, models, or local launchers."""
from pathlib import Path
import zipfile
ROOT=Path(__file__).resolve().parents[1]
FILES=['index.html','server.py','worker.py','research.py','teaching.py','store.py','launch.py','service.py','Lancer.command','requirements.txt','prepare_model.py','prepare_notes_model.py','README.md','BILAN_VERSION.md','.gitignore','test_v2.py','test_audio_v2.py','test_learning.py','test_research.py','test_teaching.py','test_enrichment.py','test_enrichment_local.py','test_course_local.py','test_english_structure.py','package.json','tests/interface.cjs','assets/studyhub-logo.png','assets/favicon.png','assets/StudyHUB.icns','assets/creation-logo.md','scripts/package_sources.py']
def package(destination):
    destination=Path(destination);destination.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(destination,'w',zipfile.ZIP_DEFLATED) as archive:
        for name in FILES:archive.write(ROOT/name,'StudyHUB/'+name)
    with zipfile.ZipFile(destination) as archive:
        assert len(archive.namelist())==len(FILES)
        assert not any('/sessions/' in name or '/.venv/' in name or '/notes-model/' in name or '/model/' in name for name in archive.namelist())
    return destination
if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('destination');args=parser.parse_args()
    print(package(args.destination))
