# -*- mode: python -*-
import sys

added_files = [
         ( 'static', 'static' ),
         ( 'templates', 'templates' )
         ]

a = Analysis(['Traktor Librarian.py'],
             datas=added_files,
             hiddenimports=[],
             hookspath=None,
             runtime_hooks=None)
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          name='Traktor Librarian',
          icon='icon.ico',
          debug=False,
          strip=None,
          upx=True,
          console=True )


if sys.platform == "win32":
    coll = COLLECT(exe,
                   a.binaries,
                   a.zipfiles,
                   a.datas,
                   strip=None,
                   upx=True,
                   name='librarian')
elif sys.platform == "darwin":
    app = BUNDLE(exe,
             name='Librarian.app',
             icon='icon.icns',
             bundle_identifier='Librarian')
