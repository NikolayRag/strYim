# -*- mode: python -*-


block_cipher = None


a = Analysis(['src/__main__.py'],
             pathex=[''],
             binaries=None,
             datas=None,
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=['appGui'],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
             
a.datas += [
	  ('ffmpeg/ffmpeg.exe','src/ffmpeg/ffmpeg.exe','DATA')
	, ('SourceYi4k/YiReader/YiSide/YiData.py', 'src/SourceYi4k/YiReader/YiSide/YiData.py','DATA')
	, ('SourceYi4k/YiReader/YiSide/YiSock.py', 'src/SourceYi4k/YiReader/YiSide/YiSock.py','DATA')
	, ('SourceYi4k/YiReader/YiSide/YiAgent.py', 'src/SourceYi4k/YiReader/YiSide/YiAgent.py','DATA')
	, ('SourceYi4k/YiReader/YiSide/YiCleanup.py', 'src/SourceYi4k/YiReader/YiSide/YiCleanup.py','DATA')
]  

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='stryim_cmd',
          debug=False,
          strip=False,
          upx=True,
          console=True )
          