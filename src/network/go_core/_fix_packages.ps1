"$files = Get-ChildItem \"C:\\Users\\IKYY\\Downloads\\Omni\\src\\
etwork\\go_core\\*.go\"\
foreach ($f in $files) {\
    $content = Get-Content $f.FullName -Raw\
    $original = $content\
    # Fix all package declarations to go_core\
    $content = $conte
<truncated 248 bytes>