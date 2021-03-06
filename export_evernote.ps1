$ENscriptLocation="C:\Program Files (x86)\Evernote\Evernote\ENScript.exe"
$outDir="C:\Users\wangjing\Evernote\"

Function export-notebook($notebook, $outName) {
    echo "$ENscriptLocation exportNotes /q notebook:$notebook /f $outName"
    & $ENscriptLocation exportNotes /q notebook:"$notebook" /f $outName
}

Function export-evernote($outDir) {
    if (!$outDir) {
        echo "please specify output directory"
        return
    }
    if (!(Test-Path $outDir)) {
        mkdir $outDir
    }

    $notebooks=& $ENscriptLocation listNotebooks


    foreach ($nb in $notebooks) {
        echo "export $nb"
        export-notebook $nb "$outDir$nb.enex"
    }
}

export-evernote($outDir)
