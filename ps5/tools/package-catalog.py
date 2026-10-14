#!/usr/bin/env python3
"""Package the ROM-free app, leaving the private game package separate."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import zipfile
ROOT=Path(__file__).resolve().parents[2]
TITLE='PPSA99641'
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--executable',type=Path,required=True)
    p.add_argument('--libc',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--console-tested',action='store_true',help='Record completed console verification of this executable')
    a=p.parse_args()
    if a.output.exists():p.error('Output already exists')
    title=a.output/TITLE
    (title/'sce_sys').mkdir(parents=True);(title/'sce_module').mkdir()
    shutil.copy2(a.executable,title/'eboot.bin')
    shutil.copy2(a.libc,title/'sce_module/libc.prx')
    shutil.copy2(ROOT/'ps5/sce_sys/param.json',title/'sce_sys/param.json')
    shutil.copy2(ROOT/'ps5/art/catalog-icon.png',title/'sce_sys/icon0.png')
    shutil.copy2(ROOT/'LICENSE',title/'LICENSE')
    shutil.copy2(ROOT/'ps5/THIRD_PARTY_NOTICES.md',title/'THIRD_PARTY_NOTICES.md')
    shutil.copytree(ROOT/'ps5/licenses',title/'licenses')
    shutil.copy2(ROOT/'ps5/CATALOG-SETUP.md',title/'SETUP.md')
    assert json.loads((title/'sce_sys/param.json').read_text())['titleId']==TITLE
    paths=sorted(p for p in title.rglob('*') if p.is_file())
    assert not any(p.suffix.lower() in {'.rpx','.key','.wwhd','.wux','.wud','.gcm'} for p in paths)
    rows=[{'path':p.relative_to(title).as_posix(),'size':p.stat().st_size,'sha256':sha(p)} for p in paths]
    (title/'manifest.json').write_text(json.dumps({'title':TITLE,'game_independent':True,'console_tested':a.console_tested,'files':rows},indent=2)+'\n')
    archive=a.output/(TITLE+'.zip')
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for path in sorted(title.rglob('*')):
            if path.is_file():z.write(path,path.relative_to(a.output))
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        for row in rows:assert hashlib.sha256(z.read(TITLE+'/'+row['path'])).hexdigest()==row['sha256']
    (a.output/(TITLE+'.zip.sha256')).write_text(sha(archive)+'  '+archive.name+'\n')
    print('Prepared catalog ZIP:',archive)
if __name__=='__main__':main()
