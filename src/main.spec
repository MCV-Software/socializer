# -*- mode: python -*-

block_cipher = None

a = Analysis(['main.py'],
             pathex=['.'],
             binaries=[("sounds", "sounds"),
("documentation", "documentation"),
("locales", "locales"),
("..\\windows-dependencies\\dictionaries", "enchant\\share\\enchant\\myspell"),
("..\\windows-dependencies\\x86\\oggenc2.exe", "."),
("..\\windows-dependencies\\x86\\bootstrap.exe", "."),
("app-configuration.defaults", "."),
("session.defaults", "."),
("cacert.pem", "."),
],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='socializer',
          debug=False,
          strip=False,
          upx=True,
          console=False )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='main')
