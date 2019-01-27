import random
import string
import time
import hashlib
import sqlite3
from getpass import getpass

# Connexion à la base de donnée
sqlcrypt = sqlite3.connect('Database_Python_TP1.db')
cursor = sqlcrypt.cursor()

# Liste des menus
menuConnexion = "\n1) Connexion\n2) Quitter\n"
menuChoix = "\nQue voulez vous faire ?\n\n1) Création d'un compte\n2) Changer le mot de passe \n3) Supprimer un compte\n4) Liste des utilisateurs\n5) Se déconnecter \n6) Quitter\n"
menuCreation = "1) Nouvel essai\n2) Retour\n"
menuSuppr = "1) Supprimer un autre compte\n2) Retour\n"
menuTryAgain = "1) Essayer de nouveau\n2) Retour\n"
choice = 0

co = False

# Connexion à la base de donnée
def connexion() :
    check = checkpasswd(connexion)
    if check != True :
        return False
    else :
        return True

# En cas d'erreur
def try_again(func):
    loop = True
    while loop == True:
        choice = input(menuCreation + "\nVeuillez insérer votre choix : ")
        if choice == '1':
            co = func()
            # Utilisé pour la connexion
            if co == True :
                return True
            return False
        elif choice == '2':
            return False
        else:
            print("\nVeuillez insérer votre choix : ")

# 1) Création du compte

def creation() :
    loop = True
    again = True
    name = input("\nLogin : ")
    cursor.execute("""SELECT id, login FROM users WHERE login = '%s' """ % name)
    data = cursor.fetchone()
    if data is None :
        if (name == '') :
            print("\nErreur, champ vide !\n")
            again = try_again(creation)
    else :
        print("\nLe compte existe déjà !\n")
        again = try_again(creation)
    if again == False :
        return
    passwd = genpasswd()
    if passwd == False :
        return
    cursor.execute("""INSERT INTO users(login, passwd) VALUES(?,?)""", (name, passwd))
    print("\nVotre compte a été créé !")
    sqlcrypt.commit()
    while loop == True:
        choice = input(menuCreation + "\nVeuillez insérer votre choix : ")
        if choice == '1':
            creation()
        elif choice == '2':
            return
        else :
            print("\n\nVeuillez insérer votre choix : ")

# 2) Changer le mot de passe
# Hashage password en sha256
def hash(passwd) :
    passwd = passwd.encode('UTF8')
    passwd = hashlib.sha256(passwd).hexdigest()
    return passwd

# Génère un mot de passe aléatoire
def genpasswd() :
    lenpass = 8
    chars = string.ascii_letters + string.digits + string.punctuation
    passwd = ''.join(random.choice(chars) for _ in range(lenpass))
    return hash(passwd)

# Vérification du login et hashage du password
def checkpasswd(func):
    name = input("\nLogin : ")
    cursor.execute("""SELECT id, login, passwd FROM users WHERE login = '%s' """ % name)
    data = cursor.fetchone()
    if data is None:
        print("\nCe compte n'existe pas !")
        again = try_again(func)
        if again == False:
            return False
    passwd = getpass("Mot de passe : ")
    stock = hash(passwd)
    stocktab = data[2]
    if stock != stocktab :
        if func == connexion :
            print("\nErreur de connexion !")
            time.sleep(5)
        else :
            print("\nErreur d'authentification")
        again = try_again(func)
        if again == False:
            return False
    if func == connexion:
        return True
    else:
        return name

# Update password
# Préparation du nouveau mot de passe
def majpasswd() :
    upp = False
    numb = False
    spe = False
    passwd = getpass("Mot de passe : ")
    if len(passwd) >= 8 :
        for char in passwd:
            # Vérifie si il y a une majuscule
            if char in string.ascii_uppercase :
                upp = True
            # Vérifie si il y a un numéro
            elif char in string.digits :
                numb = True
            # Vérifie si il y a une ponctuation
            elif char in string.punctuation:
                spe = True
        # Refuse le mot de passe si l'utilisateur ne respecte pas la politique de sécurité
        if upp != True or numb != True or spe != True :
            print('\n')
            if upp != True:
                print('\nIl faut que votre mot de passe contienne au moins une majuscule !\n')
            if numb != True:
                print('\nIl faut que votre mot de passe contienne au moins un chiffre !\n')
            if spe != True:
                print('\nIl faut que votre mot de passe contienne au moins un caractère spécial !\n')
            passwd = try_again(majpasswd)
            return passwd
    else :
        print("\nIl faut que votre mot de passe contienne au moins 8 caractères !\n")
        passwd = try_again(majpasswd)
        return passwd
    passwd = passwd.encode('UTF8')
    stock = hashlib.sha256(passwd).hexdigest()
    cpasswd = getpass("Veuillez confirmer votre mot de passe : ").encode('UTF8')
    cstock = hashlib.sha256(cpasswd).hexdigest()
    if stock == cstock:
        return stock
    else:
        print("\nErreur, les mots de passes inscrit ne correspondent pas !\n")
        passwd = try_again(majpasswd)
        return passwd

# Mise à jour du mot de passe
def majpass() :
    name = input("\nLogin : ")
    cursor.execute("""SELECT id, login, passwd FROM users WHERE login = '%s' """ % name)
    data = cursor.fetchone()
    if data is None:
        print("\nCe compte n'existe pas !")
        again = try_again(majpass)
        if again == False:
            return False
    if name == None :
        return
    hash = majpasswd()
    if hash == None :
        return
    cursor.execute("""UPDATE users SET passwd = ? WHERE login = ? """, (hash,name,))
    print("\nMot de passe mis à jour !\n")
    sqlcrypt.commit()
    return

# 3) Suppresion du compte et demande de création d'un compte
def suppr() :
    loop = True
    name = input("\nLogin : ")
    cursor.execute("""SELECT id, login, passwd FROM users WHERE login = '%s' """ % name)
    data = cursor.fetchone()
    if data is None:
        print("\nCe compte n'existe pas !")
        again = try_again(majpass)
        if again == False:
            return False
    cursor.execute("""DELETE FROM users WHERE login = ? """, (name,))
    print("\nUtilisateur supprimé")
    sqlcrypt.commit()
    while loop == True:
        choice = input(menuSuppr + "\nVeuillez insérer votre choix : ")
        if choice == '1':
            suppr()
        elif choice == '2':
            return
        else :
            print("\nVeuillez insérer votre choix : ")

# 4) Liste utilisateurs
def liste() :
    cursor.execute("""SELECT id, login, passwd FROM users""")
    rows = cursor.fetchall()
    print('\n')
    print('Veuillez trouver les informations des utilisateurs (id, login, password hashé) : \n')
    for row in rows:
        print('{0} : {1} - {2}'.format(row[0], row[1], row[2]))

# 5) Se déconnecter
def deconnexion() :
    return False

# 6) Quitter
def quitter() :
    sqlcrypt.close()
    exit(0)

# Menu connexion
while 1:
    while 1:
        path = True
        if co == True :
            print('Vous êtes maintenant connecté !\n')
            break
        choice = input(menuConnexion + "\nVeuillez insérer votre choix : ")
        if choice == '1' :
            co = connexion()
        elif choice == '2' :
            quit()
        else:
            print("\nVeuillez insérer votre choix : ")

# Menu principal
    while co != False:
        choice = input(menuChoix + "\nVeuillez insérer votre choix : ")
        if choice == '1':
            creation()
        elif choice == '2':
            majpass()
        elif choice == '3':
            suppr()
        elif choice == '4':
            liste()
        elif choice == '5':
            co = deconnexion()
            break
        elif choice == '6':
            quitter()
        else:
            print("\nIl faut insérer le chiffre correspondant à votre choix : ")
