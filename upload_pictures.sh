#!/usr/bin/env bash
#
# Upload every PNG/JPEG/GIF in a directory to the Flask app's
# /admin_pictures/add route.
#
# Usage:
#   BASE_URL=http://localhost:5000 USERID=admin PASSWORD=secret \
#       ./upload_pictures.sh /path/to/pictures
#
# Environment variables:
#   BASE_URL  App root URL (default: http://localhost:5000)
#   USERID    Admin userid   (prompted for if unset)
#   PASSWORD  Admin password (prompted for if unset)

set -uo pipefail

DIR="${1:-}"
BASE_URL="${BASE_URL:-http://localhost:5000}"
BASE_URL="${BASE_URL%/}"

if [[ -z "$DIR" || ! -d "$DIR" ]]; then
    echo "Usage: $0 <directory>" >&2
    exit 1
fi

if [[ -z "${USERID:-}" ]]; then
    read -r -p "Userid: " USERID
fi
if [[ -z "${PASSWORD:-}" ]]; then
    read -r -s -p "Password: " PASSWORD
    echo
fi

COOKIES="$(mktemp)"
trap 'rm -f "$COOKIES"' EXIT

# --- Log in -----------------------------------------------------------------
# Success redirects to /signups; failure re-renders the login page (HTTP 200).
login_result="$(curl -s -o /dev/null -c "$COOKIES" \
    -w '%{http_code} %{redirect_url}' \
    --data-urlencode "userid=$USERID" \
    --data-urlencode "password=$PASSWORD" \
    "$BASE_URL/login")"

if [[ "$login_result" != 302*signups* ]]; then
    echo "Login failed (got: $login_result)" >&2
    exit 1
fi
echo "Logged in as $USERID"

# --- Upload -----------------------------------------------------------------
mime_for() {
    case "${1,,}" in
        *.png)         echo "image/png" ;;
        *.jpg|*.jpeg)  echo "image/jpeg" ;;
        *.gif)         echo "image/gif" ;;
    esac
}

ok=0
failed=0

while IFS= read -r -d '' file; do
    mime="$(mime_for "$file")"
    name="$(basename "$file")"

    # The route always redirects back to the page and reports the outcome
    # via a flash message, so follow the redirect and look for that message.
    page="$(curl -s -L -b "$COOKIES" -c "$COOKIES" \
        -F "image=@${file};type=${mime}" \
        "$BASE_URL/admin_pictures/add")"

    if grep -q "New picture saved" <<<"$page"; then
        echo "  OK      $name"
        ((ok++))
    else
        echo "  FAILED  $name"
        ((failed++))
    fi
done < <(find "$DIR" -maxdepth 1 -type f \
    \( -iname '*.png' -o -iname '*.jpg' -o -iname '*.jpeg' -o -iname '*.gif' \) \
    -print0 | sort -z)

echo "Done: $ok uploaded, $failed failed."
[[ $failed -eq 0 ]]
