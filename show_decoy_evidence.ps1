$evidence = Select-String `
    -Path ".\part2-output\png_chunks_result.txt" `
    -Pattern "SYSTEM OVERRIDE" |
    Select-Object -First 1

Write-Host ("=" * 90)
Write-Host "PART 2 - PROMPT INJECTION / DECOY ANALYSIS"
Write-Host ("=" * 90)

Write-Host ""
Write-Host "EVIDENCE FOUND IN PNG tEXt CHUNK:"
Write-Host ("-" * 90)
Write-Host $evidence.Line

Write-Host ""
Write-Host "WHY THIS TEXT IS NOT TRUSTED:"
Write-Host ("-" * 90)
Write-Host "1. The tEXt chunk is PNG metadata."
Write-Host "2. Metadata does not prove that no hidden data exists."
Write-Host "3. The message attempts to stop further analysis."
Write-Host "4. The image pixel data must still be examined."

Write-Host ""
Write-Host "CLASSIFICATION:"
Write-Host ("-" * 90)
Write-Host "[DECOY] Prompt injection found in PNG metadata."
Write-Host "[CONTINUE] Analyze the pixel data for steganography."
Write-Host ("=" * 90)
