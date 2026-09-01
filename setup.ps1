param([string]$Username='utkraa9',[string]$Name='Utkarsh Pal',[string]$Image='.\assets\me.png')
$ErrorActionPreference='Stop'
python -m pip install pillow
python scripts/dotify.py $Image -o assets/portrait --cols 88 --color
python scripts/radar.py --data assets/skills.json -o assets/radar
python scripts/radar.py --github $Username -o assets/radar-langs --limit 7
python scripts/cards.py --user $Username --out assets
Write-Host 'DONE - profile assets generated successfully.'
