### tema2-lfa

## Structura proiectului :  

# 1. regex_to_postfix cu Shunting-Yard: 
 
 *, +, ? au cea mai mare precedenta
 
 Concatenarea cu .
 
 Alternarea cu | cu cea mai mica precedenta
 
 La intrare avem sirul regex in infix, cum ar fi (a|b)*c
  
  Adaugam concatenarea, astfel ab devine a.b , )( devine ).( s.a.m.d.
  
  Parcurgem caracterele cu o stiva de operatori si un output list.
  
      Daca e litera, o trimitem in output.
      
      Daca e operator, il comparam cu varful stivei, scoatem operatori cu precedenta mai mare sau egala si impingem noul operator.
      
      Daca e ( , punem in stiva; daca e ), despachetam pana la (.
  
  La final, golim stiva in output.
  
  Astfel din (a|b)*c obtinem a b | * c.

# 2. Constructia NFA cu Thompson:
  
  Folosim clasa State pentru lista de stari.
  
  Folosim clasa NFA pentru starile de intrare si de accept.
  
Constructia Thompson:
    
    Pornind de la regexul in postfix, pentru fiecare token:
         
         Litera/caracter - > Construim un mini NFA cu doua stari s1 - > (a) -> s2.
         
         Concatenare .   - > Lipim finalul primului NFA la inceputl celui de-al doilea.  
         
         Alternare |     - > Cream doua epsilon - legaturi dintr-o stare noua s catre cele doua NFA-uri, apoi doua epsilion legaturi de la capetele lor catre o stare comuna noua a.
         
         Una sau mai multe repetari +  - > Ca la * dar fara epsilon legatura directa de la s la a. (trebuie sa trecem cel putin o data prin NFA)  
         
         Steaua lui Kleene *           - > Cream un nou start s si un nou accept a. Din s facem epsilon legaturi catre vechiul start si direct la a.
                                           Din vechiul accept facem epsilon legaturi inapoi la vechiul start si catre noul accept a.
         Intrebarea ? ( zero sau o aparitie) - > Ca un *, dar fara bucla de reluare: epsilon legatura din noul s direct la a, si din vechiul accept la a.
  
  Rezultatul final este un NFA in care: nfa.start e starea initiala a tuturor constructiilor imbinate, iar nfa.accept e starea unica finala.

# 3. Transformare NFA in DFA:
  
  Se porneste de la multimea epsilon-inchiderii starii initiale a NFA: start_closure = epsilon_closure({ nfa.start })
  
  Aceasta multime de stari NFA devine prima stare (ID 0) a DFA-ului.
  
  Tinem o coada de multimi (stari NFA) neexplorate.
  
  Pentru fiecare multime T (o stare DFA):
  
      Pentru fiecare simbol din alfabet (simbolurile nenule din NFA):
      
           Facem: move(T, simbol) - adunam starile la care putem ajunge din T pe acel simbol
           
           Luam epsilon- inchiderea rezultatului: epsilon_closure(...) - > obtinem multimea U
           
           Daca U nu e deja mapata la o stare DFA, o adaugam cu urmatorul ID liber
           
           Legam tranzitia DFA: (ID_T, simbol) - > ID_U
  
  Orice multime care contine starea de accept NFA devine stare de accept DFA.
 
 Rezultatul este un obiect DFA cu: un start unic, tranzitii (stare_DFA, simbol) - > stare_DFA, o multime de stari de accept, un set complet de stari (toate multimile generate).

 # 4. Convertirea intr-un config de fisier JSON
   Transformam DFA-ul intern la structura de date "config" pe care o foloseste validatorul din tema1.
   Acesta produce : lista tuturor simbolurilor pe care DFA-ul le foloseste in ordine sortata (alfabet)
                    lista tuturor starilor (ID-uri ca siruri)
                    marcaje pentru fiecare set de etichete, S daca e stare de inceput/start, F pentru final/accept.
                    o lista de triple (src, simbol, dst) toate convertite in siruri, cum cerea tema1 (tranzitii).

# 5. Validarea structurii
  Verificam corectitudinea configului inainte de a-l simula.
      - Cautam sa fie o singura stare marcata cu S.
      - Starea sursa si destinatie sa fie declarate in stari.
      - Functionalitatea DFA: nu exista doua tranzitii (stare, simbol) diferite in lista (nondeterminism).
  Daca oricare din aceste reguli e incalcata, sa intoarce False + lista de erori.

# 6. Simulare pe input 
  Construim tabele de tranzitii si formam un dictionar (stare, simbol) - > stare.
  Gasim starea de start marcata cu S.
  Parcurgem fiecare caracter c din sir_input. Daca c nu e in alfabet, returnam False. Cautam (curr_state, c) in tranzitii. Daca nu exista, returnam False. Mergem in curr_state = tabela[(curr_state, c)].
  Daca starea curenta are eticheta F, accepta (True) sau respinge (False).

  Daca pentru un test string rezultatul iese cum ne asteptam, se afiseaza OK. Altfel, se afiseaza FAIL.

  ## Rularea codului:

  Se pun tests.json si regex_to_dfa.py in acelasi folder, dupa care se ruleaza din PowerShell, folosind comanda python regex_to_dfa tests.json. 
  Inainte de rulare, path-ul trebuie sa fie setat deja la locatia folderului, folosind cd "nume-locatie".
  Python trebuie sa fie instalat pe Windows pentru a putea rula programul, am folosit versiunea 3.13.3 de pe site-ul oficial  https://www.python.org/downloads/macos/ .
