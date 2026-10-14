#!/usr/bin/env python3
"""Exercise the native module loader using generated test code, never game code."""
from pathlib import Path
import os, subprocess, tempfile, struct
ROOT=Path(__file__).resolve().parents[2]
with tempfile.TemporaryDirectory() as tmp:
 p=Path(tmp)
 (p/'test.c').write_text('extern void host_throw(void); void unwind_test(void) {host_throw();} extern int host_twice(int); int value=7; int* pointer=&value; __attribute__((weak)) int weak_value(void){return -1;} int run(int n){return host_twice(n)+*pointer+weak_value();}\n')
 def run(*args):subprocess.run(list(map(str,args)),check=True)
 run('clang','-fexceptions','-funwind-tables','-fPIC','-fno-stack-protector','-c',p/'test.c','-o',p/'test.o')
 run('ld.lld','-shared','-z','max-page-size=16384','-z','common-page-size=16384',p/'test.o','-o',p/'test.so')
 data=(p/'test.so').read_bytes()
 invalid=[]
 for name,content in [('truncated',data[:20]),('wrong-machine',data[:18]+b'\xb7\x00'+data[20:]),('bad-phoff',data[:32]+struct.pack('<Q',2**63)+data[40:]),('empty',b'')]:
  path=p/name;path.write_bytes(content);invalid.append(path)
 shoff=struct.unpack_from('<Q',data,40)[0]
 shsize,shcount=struct.unpack_from('<HH',data,58)
 rela=next(struct.unpack_from('<Q',data,shoff+i*shsize+24)[0] for i in range(shcount) if struct.unpack_from('<I',data,shoff+i*shsize+4)[0]==4)
 for name,offset,value in [('bad-relocation-target',rela,2**63),('unsupported-relocation',rela+8,255)]:
  changed=bytearray(data);struct.pack_into('<Q',changed,offset,value)
  path=p/name;path.write_bytes(changed);invalid.append(path)
 run('clang++','-std=c++20','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-g','-I'+str(ROOT/'ps5/module'),ROOT/'ps5/tests/module-loader.cpp',ROOT/'ps5/module/loader.cpp','-o',p/'test')
 run(p/'test',p/'test.so',*invalid,p/'nonexistent')
