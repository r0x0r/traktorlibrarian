# -*- mode: python -*-
added_files = [
         ( 'static', 'static' ),
         ( 'templates', 'templates' )
         ]

a = Analysis(['Traktor Librarian.py'],
             datas=added_files,
             pathex=['Y:\Code\traktorlibrarian'],
             hiddenimports=[],
             hookspath=None,
             runtime_hooks=None)
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='librarian',
          icon='icon.ico'
          debug=False,
          strip=None,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=None,
               upx=True,
               name='librarian')
