#!/bin/sh

ZONE_FILE="$ZONE_INFO_DIR"

if [ -n "$ZONE_INFO_SCHEME" -a "$ZONE_INFO_SCHEME" != "posix" ]; then
	ZONE_FILE="$ZONE_FILE/$ZONE_INFO_SCHEME"
fi

ZONE_FILE="$ZONE_FILE/$TIMEZONE"

[ -L /etc/localtime ] && [ "$(resolvesymlink /etc/localtime)" = "$ZONE_FILE" ] && exit 0
[ -f "$ZONE_FILE" ] || exit 2

rm -f /etc/localtime

cp -af "$ZONE_FILE" /etc/localtime
RETVAL=$?
restorecon /etc/localtime >/dev/null 2>&1
exit $RETVAL
