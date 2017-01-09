# -*- mode: python -*-

block_cipher = None


a = Analysis(['src\\__main__w.py'],
             pathex=['C:\\Users\\user\\Documents\\stryim'],
             binaries=None,
	datas=[('src/appGui/stryim.ui', 'appGui')],
	hiddenimports=['PySide.QtXml'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)

a.datas += [('ffmpeg/ffmpeg.exe','src\\ffmpeg\\ffmpeg.exe','DATA')]  

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
