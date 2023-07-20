# WindNinja-Farsite

## CAT
Aquest programa calcula el camp de vents, amb el simulador WindNinja, i executa el simulador Farsite amb el camp de vents calculat anteriorment. 
Les altres opcions que permet el programa:
  - Executar només el Farsite ja que ja s'ha calculat el camp de vents i s'ha generat els fitxers corresponent.
  - Executa el Farsite sense camp de vents.

Per defecte, es calcula el camp de vents i s'executa Farsite amb el camp de vents anterior. Si no es vol calcular el camp de vents s'ha d'afegir el paràmetre -nw o --no-windninja. En canvi, si es vol executar el Farsite sense camp de vents s'ha d'afegir el paràmetre -s o --simple_wnd.

### Exemple de ús
```
python3 wnd-farsite.py -wf file.wnd -cw cli_domainAverage.cfg -cf Settings_simulacio.txt
```

Per accedir a l'ajuda s'ha d'utilizar la següent instrucció:
```
python3 wnd-farsite.py -h 
```
o 
```
python3 wnd-farsite.py --help
```

El fitxer wnd-farsite-par.py realitza els mateixos calculs que el fitxer wnd-farsite.py, però en paral·lel. La crida per línia de comandes és idèntica.
