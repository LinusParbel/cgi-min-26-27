#!/usr/bin/env bash
# Fetch reference photos from Wikimedia Commons, politely (one API request every few seconds).
# Usage: fetch_refs.sh <out_dir> <per_query> "query 1" "query 2" ...
# Writes <out_dir>/sources.tsv + index.tsv and downloads 480 px thumbnails as 01.jpg, 02.jpg, ...
set -u
OUT="$1"; N="$2"; shift 2
UA="HannoverRushHour-student-project/0.1 (university course; low-volume reference lookup)"
export PYTHONIOENCODING=utf-8
mkdir -p "$OUT"
: > "$OUT/sources.tsv"; : > "$OUT/index.tsv"
for q in "$@"; do
  for attempt in 1 2 3; do
    resp=$(curl -s -A "$UA" -G "https://commons.wikimedia.org/w/api.php" \
      --data-urlencode "action=query" --data-urlencode "format=json" --data-urlencode "generator=search" \
      --data-urlencode "gsrnamespace=6" --data-urlencode "gsrsearch=$q filetype:bitmap" --data-urlencode "gsrlimit=$N" \
      --data-urlencode "prop=imageinfo" --data-urlencode "iiprop=url|extmetadata" --data-urlencode "iiurlwidth=480")
    if [[ "$resp" == "{"* ]]; then break; fi
    echo "rate limited on '$q', waiting 60 s" >&2; sleep 60
  done
  echo "$resp" | python -I -c "
import sys, json
q = sys.argv[1]
try: d = json.load(sys.stdin)
except Exception: sys.exit()
for i, p in enumerate(sorted(d.get('query', {}).get('pages', {}).values(), key=lambda p: p.get('index', 0))):
    ii = p['imageinfo'][0]
    print('\t'.join([q, str(i), p['title'][5:90], str(ii['extmetadata'].get('LicenseShortName', {}).get('value')), ii.get('thumburl', '').split('?')[0]]))
" "$q" | tr -d '\r' >> "$OUT/sources.tsv"
  sleep 5
done
n=0
while IFS=$'\t' read -r q i title lic url; do
  [[ -z "$url" ]] && continue
  n=$((n+1)); f=$(printf "%s/%02d.jpg" "$OUT" "$n")
  curl -s -A "$UA" -o "$f" "$url"
  printf "%02d\t%s\t%s\t%s\n" "$n" "$q" "$title" "$lic" >> "$OUT/index.tsv"
  sleep 1
done < "$OUT/sources.tsv"
echo "done: $n images in $OUT"
