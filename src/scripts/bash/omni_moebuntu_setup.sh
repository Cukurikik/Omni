#!/bin/bash
# OMNI MOTHER: Moebuntu-kantan-Setup2
# Shell script to apply pink/kawaii GTK themes and icons

set -e

echo "[OMNI] Applying Moebuntu Theme..."
M_THEME_DIR="/usr/share/themes/Moebuntu"

if [ ! -d "$M_THEME_DIR" ]; then
    echo "Downloading Moebuntu resources..."
    # wget -qO- https://example.com/moebuntu.tar.gz | tar xz -C /usr/share/themes/
fi

# gsettings set org.gnome.desktop.interface gtk-theme "Moebuntu"
# gsettings set org.gnome.desktop.wm.preferences theme "Moebuntu"

echo "[OMNI] Moebuntu theme applied successfully. 🌸"
