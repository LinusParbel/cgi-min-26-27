# Opens all Baustelle props + wheelie bins as one scene in the course engine (interactive).
# Models come from RunnerGame/Assets/Models; lamps sit on the mount points from mounts.json.
# Build the viewer once: dotnet build tools/asset-spike/SpikeViewer
$m = Join-Path $PSScriptRoot "..\..\RunnerGame\Assets\Models" | Resolve-Path
function M($dir, $name, $x, $y, $z) { "$m\$dir\$name.obj@$x,$y,$z"; "$m\$dir\$name.png" }
$a = @("--show")
$a += M "Baustelle\Schild123" "PROP_Schild_Zeichen123" -5.2 0 0
$a += M "Baustelle\Leitbake" "PROP_Leitbake_rechts" -3.8 0 0;  $a += M "Baustelle\Warnleuchte" "PROP_Warnleuchte_gelb" -3.8 1.21 0
$a += M "Baustelle\Leitbake" "PROP_Leitbake_links" -3.0 0 0;   $a += M "Baustelle\Warnleuchte" "PROP_Warnleuchte_gelb" -3.0 1.21 0
$a += M "Baustelle\Leitkegel" "PROP_Leitkegel_75" -2.0 0 0.2
$a += M "Baustelle\Leitkegel" "PROP_Leitkegel_50" -1.3 0 0.2
$a += M "Baustelle\Absperrschranke" "PROP_Absperrschranke_gelb" 0.6 0 0
$a += M "Baustelle\Warnleuchte" "PROP_Warnleuchte_rot" 0.2216 0.98 0; $a += M "Baustelle\Warnleuchte" "PROP_Warnleuchte_rot" 0.9784 0.98 0
$a += M "Baustelle\Absperrschranke" "PROP_Absperrschranke_rotweiss" 3.0 0 0
$a += M "Baustelle\Warnleuchte" "PROP_Warnleuchte_rot" 2.6216 0.98 0; $a += M "Baustelle\Warnleuchte" "PROP_Warnleuchte_rot" 3.3784 0.98 0
$a += M "Baustelle\Schild123" "PROP_Schild_Zeichen123_mobil" 4.8 0 0
$i = 0
foreach ($v in "bio", "restmuell", "gelb", "papier") { $a += M "Mull\Tonne" "PROP_WheelieBin_120L_$v" (-1.2 + 0.8 * $i) 0 -1.6; $i++ }
dotnet (Join-Path $PSScriptRoot "SpikeViewer\bin\Debug\net10.0\SpikeViewer.dll") @a
