"""Shared test setup.

The flagship scripts print Unicode (for example the multiplication sign).
On Windows a child Python process writes to a pipe in the ANSI code page
(cp1251 on a Russian locale) and crashes with UnicodeEncodeError. Forcing
UTF-8 mode here makes every subprocess started by the tests behave the same
way it does on Linux CI.
"""

import os

os.environ.setdefault("PYTHONUTF8", "1")
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
