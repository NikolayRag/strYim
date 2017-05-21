# -*- mode: python -*-

block_cipher = None


a = Analysis(['src/__main__w.py'],
             pathex=[''],
             binaries=None,
	datas=[('src/Ui/stryim.ui', 'Ui')],
	hiddenimports=['PySide.QtXml'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
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
          name='stryim',
          debug=False,
          strip=False,
          upx=True,
          console=True )
