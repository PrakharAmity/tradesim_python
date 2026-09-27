$env:PYTHONPATH = "$PSScriptRoot\src" + $(if ($env:PYTHONPATH) { ";$env:PYTHONPATH" })
python -m tradesim.main @args
