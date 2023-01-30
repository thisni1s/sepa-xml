# SEPA-XML

Python script to generate Sepa XML files to upload to your bank.

Input is given by a csv file looking like this (first two lines are header):

| 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 |
| :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- |
| ID | Firstname | Lastname | Street, No | Postal Code | City | E-Mail | Bank | Account Owner | IBAN | BIC | Signing date | Signing city | FRST or RCUR | Sibling (1/0) | Mandate reference | Filled (1/0) |
| 1337  | Hans  | Meier  | Hauptstraße 17  | 50667  | Köln  | test@te.st  | Deutsche Bank | Hans Meier  | DE...  | DEUTDEDB  | 30.1.23  | Köln  | FRST  |  1 | test  | 1  |


#### Usage

Input all your details into ```lastschrift-create.py```

Run script:
``` python3 lastschrift-create.py  input.csv```
