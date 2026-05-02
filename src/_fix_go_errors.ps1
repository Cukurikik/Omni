"# Fix concurrency/agents package conflict\
$dir = \"C:\\Users\\IKYY\\Downloads\\Omni\\src\\concurrency\\agents\"\
Get-ChildItem \"$dir\\*.go\" | ForEach-Object {\
    $c = Get-Content $_.FullName -Raw\
    $c = $c -replace '(?m)^package\\s+\\w+', 'package
<truncated 2262 bytes>