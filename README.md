# resume

Building:

```
sudo tlmgr update --self --all
tlmgr install moderncv
tlmgr install pgf

latexmk -C
latexmk -pdf resume.tex
```

Output markdown after running `TeX4ht`:

```sh
pandoc resume.html -o resume.md
```
