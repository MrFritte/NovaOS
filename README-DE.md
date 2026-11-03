# NovaOS 0.3.0-vmtest

NovaOS ist ein Arch-basiertes Desktop-Linux mit KDE Plasma, Windows-inspirierter Bedienung und Wine-Kompatibilität. Diese Version ist ein **VM-Testbuild**, kein als stabil freigegebenes 1.0-Release.

## Enthalten

- KDE Plasma mit SDDM und einem bewusst schlanken App-Set
- Dolphin, Konsole, Ark, Kate, Firefox und Systemeinstellungen
- Wine + Winetricks; multilib ist im ISO-Buildprofil aktiviert
- .exe/.msi-Dateizuordnung mit Warnhinweis vor dem Start
- NetworkManager und PipeWire
- Archinstall mit vorausgefülltem NovaOS-Installationsprofil
- Deutsches Live-System und deutscher Setup-Guide

## Build

Der Build muss in einem aktuellen Arch-Linux-System mit Internetzugang stattfinden. Auf Debian/Ubuntu/Windows ohne Arch-Buildumgebung wird dieses Profil nicht direkt gebaut.

```bash
sudo pacman -Syu --needed archiso
cd NovaOS-0.3.0-vmtest
sudo ./scripts/build-iso.sh
```

Das ISO wird unter `out/NovaOS-0.3.0-vmtest-x86_64.iso` abgelegt, sofern Archiso den Standard-Dateinamen verwendet. Direkt daneben liegt eine SHA-256-Prüfsumme.

### Cloud-Build über GitHub Actions

Die ausführliche Anleitung steht in [BUILD-ON-GITHUB-DE.md](BUILD-ON-GITHUB-DE.md). Der Workflow baut in einem aktuellen Arch-Linux-Container. Die ISO-Erstellung lädt aktuelle Arch-Pakete herunter und benötigt Internetzugriff.

## Test in einer VM

- VM-Typ: Linux / Arch Linux (64-bit) oder Other Linux 64-bit
- RAM: 4 GB empfohlen (2 GB als Untergrenze für einen vorsichtigen Minimaltest)
- CPU: 2 vCPUs empfohlen
- Festplatte: neue virtuelle Disk, mindestens 40 GB
- Grafik: 128 MB VRAM, 3D-Beschleunigung zunächst aus; bei Darstellungsproblemen wechseln
- Firmware: zuerst BIOS/Legacy testen, danach optional UEFI

Wichtig: Für den Installationstest eine **neue leere virtuelle Festplatte** verwenden. Archinstall löscht Daten auf dem ausgewählten Ziellaufwerk, wenn du eine entsprechende Partitionierungsoption bestätigst.

## Grenzen dieses Testbuilds

- Archinstall ist ein geführter Textinstaller, kein eigener grafischer NovaOS-Installer.
- Wine kann viele Windows-Anwendungen starten, aber keine vollständige Windows-Kompatibilität garantieren. Programme mit Kernel-Treibern, Anti-Cheat, bestimmten DRM- oder Hardwarekomponenten können scheitern.
- Das Design basiert auf KDE Plasma/Breeze mit NovaOS-Grundbranding; ein vollständig eigenes Theme folgt später.
- Es gibt noch keinen Testnachweis für echte Hardware und keine stabile 1.0-Freigabe.
