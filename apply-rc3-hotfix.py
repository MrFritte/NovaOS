#!/usr/bin/env python3
from pathlib import Path
import sys

root = Path(sys.argv[1]).resolve()

def patch(rel, old, new, label):
    path = root / rel
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(label + ": expected one match, found " + str(count))
    path.write_text(text.replace(old, new, 1), encoding="utf-8")

p = "scripts/build-extra-packages.sh"
gtk2_block = """# GTK2 is no longer in Arch's official repositories. Apache OpenOffice 4.1.17
# still needs the GTK2 runtime, so build it from the AUR and ship it locally.
GTK2_DIR="$ROOT/build/aur/gtk2"
rm -rf "$GTK2_DIR"
runuser -u "$BUILDER" -- git clone --depth=1 https://aur.archlinux.org/gtk2.git "$GTK2_DIR"
chown -R "$BUILDER:$BUILDER" "$GTK2_DIR"
[[ -s "$GTK2_DIR/PKGBUILD" ]] || { echo 'gtk2 AUR PKGBUILD missing.' >&2; exit 1; }
runuser -u "$BUILDER" -- bash -lc "cd '$GTK2_DIR' && makepkg --verifysource --noconfirm && makepkg --syncdeps --noconfirm"
GTK2_PKG="$(find "$GTK2_DIR" -maxdepth 1 -type f -name 'gtk2-*.pkg.tar.zst' -print -quit)"
[[ -s "$GTK2_PKG" ]] || { echo 'gtk2 AUR package was not created.' >&2; exit 1; }
cp -f "$GTK2_PKG" "$REPO/"

"""
patch(p, "# Build a NovaOS-specific Arch package around Apache's official German DEB",
      gtk2_block + "# Build a NovaOS-specific Arch package around Apache's official German DEB",
      "insert GTK2 build")
patch(p,
      "cd '$OPENOFFICE_DIR' && makepkg --verifysource --noconfirm && makepkg --syncdeps --noconfirm",
      "cd '$OPENOFFICE_DIR' && makepkg --verifysource --noconfirm && makepkg --nodeps --noconfirm",
      "OpenOffice repackaging")
old_count = "((" + "$" + "{#artifacts[@]} >= 2)) || { echo 'Expected Brave and OpenOffice package artifacts were not built.' >&2; exit 1; }"
new_count = "((" + "$" + "{#artifacts[@]} >= 3)) || { echo 'Expected GTK2, Brave and OpenOffice package artifacts were not built.' >&2; exit 1; }"
patch(p, old_count, new_count, "local package count")

p = "packages/novaos-installed.txt"
patch(p, "\ngtk2\n", "\n", "remove GTK2 from official target package list")
deps = ["libice", "libsm", "libxt", "libxslt", "unixodbc", "libxml2",
        "libx11", "libxcomposite", "libxcursor", "libxdamage", "libxext",
        "libxfixes", "libxi", "libxinerama", "libxrandr", "libxrender"]
for dep in deps:
    patch(p, "libxcrypt-compat\n", "libxcrypt-compat\n" + dep + "\n",
          "add OpenOffice target dependency " + dep)

p = "packages/novaos-live.x86_64"
for dep in reversed(deps):
    patch(p, "gtk2\n", "gtk2\n" + dep + "\n",
          "add OpenOffice live dependency " + dep)

p = "overlay/usr/local/bin/novaos-installer"
patch(p,
      'LOCAL_PACKAGES=("$LOCAL_PACKAGE_DIR"/brave-bin-*.pkg.tar.zst "$LOCAL_PACKAGE_DIR"/novaos-openoffice-bin-*.pkg.tar.zst)',
      'LOCAL_PACKAGES=("$LOCAL_PACKAGE_DIR"/gtk2-*.pkg.tar.zst "$LOCAL_PACKAGE_DIR"/brave-bin-*.pkg.tar.zst "$LOCAL_PACKAGE_DIR"/novaos-openoffice-bin-*.pkg.tar.zst)',
      "installer package list")
patch(p, "((" + "$" + "{#LOCAL_PACKAGES[@]} == 2))",
      "((" + "$" + "{#LOCAL_PACKAGES[@]} == 3))", "installer package count")
patch(p, "Lokale Brave-/OpenOffice-Pakete oder Prüfsummen fehlen auf dem Installationsmedium.",
      "Lokale GTK2-/Brave-/OpenOffice-Pakete oder Prüfsummen fehlen auf dem Installationsmedium.",
      "installer error")

p = "overlay/usr/local/lib/novaos/post-install.sh"
patch(p, "# Install the exact Brave and German OpenOffice package artifacts copied from the live ISO.",
      "# Install the exact GTK2 compatibility, Brave and German OpenOffice packages copied from the live ISO.",
      "post-install comment")
patch(p,
      "local_pkgs=(/usr/share/novaos/packages/brave-bin-*.pkg.tar.zst /usr/share/novaos/packages/novaos-openoffice-bin-*.pkg.tar.zst)",
      "local_pkgs=(/usr/share/novaos/packages/gtk2-*.pkg.tar.zst /usr/share/novaos/packages/brave-bin-*.pkg.tar.zst /usr/share/novaos/packages/novaos-openoffice-bin-*.pkg.tar.zst)",
      "post-install package list")
patch(p, "((" + "$" + "{#local_pkgs[@]} != 2))",
      "((" + "$" + "{#local_pkgs[@]} != 3))", "post-install package count")
patch(p, "Brave/OpenOffice package payload missing in target system.",
      "GTK2/Brave/OpenOffice package payload missing in target system.",
      "post-install error")

p = "scripts/verify-project.sh"
patch(p, "grep -Fxq 'gtk2' \"$ROOT/packages/novaos-installed.txt\"",
      "grep -Fxq 'gtk2' \"$ROOT/packages/novaos-live.x86_64\"\nif grep -Fxq 'gtk2' \"$ROOT/packages/novaos-installed.txt\"; then echo 'GTK2 must be installed from the bundled local AUR package, not the official Arch repos.' >&2; exit 1; fi",
      "GTK2 package source verification")
patch(p, "grep -Fq 'makepkg --verifysource' \"$ROOT/scripts/build-extra-packages.sh\"",
      "grep -Fq 'makepkg --verifysource' \"$ROOT/scripts/build-extra-packages.sh\"\ngrep -Fq 'https://aur.archlinux.org/gtk2.git' \"$ROOT/scripts/build-extra-packages.sh\"\ngrep -Fq 'makepkg --nodeps --noconfirm' \"$ROOT/scripts/build-extra-packages.sh\"\ngrep -Fq 'cp -f \"$GTK2_PKG\" \"$REPO/\"' \"$ROOT/scripts/build-extra-packages.sh\"\nfor dep in libice libsm libxt libxslt unixodbc libxml2 libx11 libxcomposite libxcursor libxdamage libxext libxfixes libxi libxinerama libxrandr libxrender; do grep -Fxq \"$dep\" \"$ROOT/packages/novaos-installed.txt\"; done",
      "GTK2 and OpenOffice dependency verification")
patch(p, "assert not {'firefox', 'libreoffice-fresh'} & set(d['packages'])",
      "assert not {'firefox', 'libreoffice-fresh', 'gtk2'} & set(d['packages'])",
      "target package assertion")
patch(p,
      "assert 'novaos-openoffice-writer.desktop' in (ROOT / 'overlay/etc/xdg/mimeapps.list').read_text()",
      "assert 'novaos-openoffice-writer.desktop' in (ROOT / 'overlay/etc/xdg/mimeapps.list').read_text()\nassert 'gtk2-*.pkg.tar.zst' in (ROOT / 'overlay/usr/local/bin/novaos-installer').read_text()\nassert 'gtk2-*.pkg.tar.zst' in (ROOT / 'overlay/usr/local/lib/novaos/post-install.sh').read_text()",
      "local package delivery verification")

p = "docs/BUILD-ISO-DE.md"
patch(p,
      "1. baut \`brave-bin\` aus dem Arch User Repository (AUR) als normaler Build-Benutzer;\n2. baut \`novaos-openoffice-bin\`",
      "1. baut \`brave-bin\` aus dem Arch User Repository (AUR) als normaler Build-Benutzer;\n2. baut GTK2 als AUR-Kompatibilitätspaket, weil es für OpenOffice 4.1.17 benötigt wird, aber nicht mehr in den offiziellen Arch-Repos liegt;\n3. paketiert \`novaos-openoffice-bin\`",
      "build documentation GTK2 step")
print("NovaOS RC3 GTK2/OpenOffice compatibility fix applied.")
