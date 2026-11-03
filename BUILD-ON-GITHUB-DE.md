# NovaOS-ISO in GitHub Actions erstellen

Dieser Weg erstellt die ISO auf einem Online-Buildserver mit Arch Linux. Du musst Arch Linux nicht selbst installieren.

1. Entpacke `NovaOS-0.3.0-vmtest-source.zip` auf deinem PC.
2. Lege auf GitHub ein neues Repository namens `NovaOS` an. Am einfachsten zunächst leer (kein zusätzliches README erzeugen).
3. Klone das leere Repository mit GitHub Desktop oder `git clone`.
4. Kopiere **alle** Dateien und Ordner aus dem entpackten NovaOS-Projekt in das geklonte Repository. Achte darauf, dass auch der versteckte Ordner `.github` mitkommt.
5. Committe die Dateien und pushe sie auf den Branch `main`.
6. Öffne auf GitHub den Tab **Actions**. Der Workflow **Build NovaOS ISO** startet beim Push automatisch. Alternativ kannst du **Run workflow** wählen.
7. Warte, bis der Job grün abgeschlossen ist. Öffne den Lauf und lade unter **Artifacts** das Paket `NovaOS-ISO` herunter.
8. Entpacke das Artefakt. Darin liegen die `.iso` und ihre `.sha256`-Prüfsumme.

## Alternative mit Git

```bash
git clone https://github.com/DEIN-NAME/NovaOS.git
cp -a /pfad/zum/entpackten/NovaOS-0.3.0-vmtest/. NovaOS/
cd NovaOS
git add .
git commit -m "Add NovaOS VM test build"
git push -u origin main
```

Wenn dein GitHub-Repository einen anderen Standardbranch als `main` verwendet, passe in `.github/workflows/build-iso.yml` die `push.branches`-Zeile entsprechend an oder starte den Workflow manuell.

Die Action erstellt eine ISO aus aktuellen Arch-Paketen. Der Build ist deshalb netzwerkabhängig und kann sich ändern, wenn Arch-Pakete aktualisiert werden. Ein grüner Build bestätigt, dass `mkarchiso` eine ISO erzeugt hat; der anschließende Boot- und Installationstest in VirtualBox/VMware bleibt notwendig.
