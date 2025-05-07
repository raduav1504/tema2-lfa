Structura proiectului

regex_to_dfa.py – script principal care parse-ază expresia regulată, generează NFA, îl convertește în DFA și rulează testele
tests.json – fișier JSON cu suite de teste (cel puțin 20 de cazuri)
.gitignore – lista fișierelor și folderelor ignorate de sistemul de versiune
README.md – documentul curent

Rulare

Asigură-te că ai instalat Python 3.x (fără pachete suplimentare)

Clonează proiectul sau descarcă-l direct din GitHub

În terminal, poziționează-te în folderul proiectului

Rulează comanda:
python regex_to_dfa.py tests.json
(sau, pe Windows, poți folosi „py regex_to_dfa.py tests.json”)

Vei vedea, pentru fiecare suită de test, numele, expresia regulată și rezultatele de la fiecare input
