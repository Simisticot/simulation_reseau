# Projet de réseau IATIC 4
# Simon PEREIRA
# Julie GASPAR
# Laureline PARTONNAUD

import random
import math
import copy
import matplotlib.pyplot as plt


""" Classe qui modélise l'ensemble du réseau"""
class reseau:

    # Un réseau est composé d'une station de base BS et d'un ensemble d'emetteurs
    def __init__(self, nbemetteurs, intensite, t, Tabstrat):
        self.bs = BS()
        self.nbemetteurs = nbemetteurs
        self.emetteurs = []
        for x in range(0, nbemetteurs, 1):
            self.emetteurs.append(emetteur(x, t, intensite, Tabstrat))

    # Affiche l'ensemble des emetteurs
    def print_emetteurs(self):
        for x in self.emetteurs:
            print(str(x.identifiant))

    # Affiche l'ensemble du réseau et l'état des transmissions à une itération donnée
    def print_resume_iteration(self, iteration):
        for x in self.emetteurs:
            print("Stratégie de l'emetteur "+str(x.identifiant)+" : "+str(x.historique_strats[iteration])+" copies")
            print("Récompense obtenue : "+str(x.historique_rewards[iteration]))
        print("Trame avant sic :")
        print(str(self.bs.historique_pre_sic[iteration]))
        print("Trame après sic :")
        print(str(self.bs.historique_post_sic[iteration]))
        succes = 0
        succes_partiels = 0
        collisions = 0
        for x in self.emetteurs:
            if x.historique_rewards[iteration] == 0.9:
                succes += 1
            if x.historique_rewards[iteration] == 0.5:
                succes_partiels += 1
            if x.historique_rewards[iteration] == 0.1:
                collisions += 1
        print("Résumé des transmissions : ")
        print(str(succes)+" transmissions réussies")
        print(str((succes/(succes+succes_partiels+collisions)*100))+"% de succes complets")
        print(str(succes_partiels)+" transmissions sauvées")
        print(str((succes_partiels+succes)/(succes+succes_partiels+collisions)*100)+"% de succes partiels ou complets")
        print(str(collisions)+" pertes via collision")
        print(str(collisions / (succes + succes_partiels + collisions) * 100) + "% d'echecs'")

    # Enregistre les récompenses des emetteurs
    def sauvegarder_rewards(self):
        for x in self.emetteurs:
            x.sauvegarder_reward()

    # Renvoie le pourcentage de réussite des envois de paquets
    def pourcentage_reussite(self):
        succes = 0
        envois_totaux = 0
        for x in self.emetteurs:
            envois_totaux += x.paquets_envoyes
        for x in self.emetteurs:
            for y in x.historique_rewards:
                if y > 0.1:
                    succes += 1
        return (succes / envois_totaux) * 100

    # Renvoie l'ensemble des paquets dont l'envoi est réussi
    def historique_reussites(self, iterations):
        reussites = []
        for x in range (0, iterations, 1):
            paquets_emis = 0
            collisions = 0
            for y in self.emetteurs:
                if y.emissions[x]:
                    paquets_emis += 1
                    if y.historique_rewards[x] == 0.1:
                        collisions += 1
            if paquets_emis == 0:
                reussites.append(100)
            else:
                reussites.append((collisions/paquets_emis)*100)
        return reussites

    # Renvoie le gain moyen des emetteurs
    def gain_moyen(self):
        total = 0
        for e in self.emetteurs:
            total += e.gain_moyen()
        return total/self.nbemetteurs

    # Renvoie le poucentage d'utilisation des différentes stratégies
    def pourcentages_utilisation(self,Tabstrat):
        utilisation = {}
        utilisation[0] = 0
        for x in Tabstrat:
            utilisation[x] = 0
        for e in self.emetteurs:
            for i in e.historique_strats:
                utilisation[i] += 1
        return utilisation

""" Modélise une stratégie """
class strat:
    # Une stratégie se compose d'un nombre de copies, un nombre d'utilisation et une récompense total
    def __init__(self, nbcopies):
        self.nbcopies = nbcopies
        self.nbutilisations = 0
        self.reward_total = 0

    # Ajoute la récompense à la récompense totale
    def reward(self, reward):
        self.reward_total += reward

    # Attribue une valeur à une stratégie
    def valeur(self, paquets_envoyes):
        if self.reward_total == 0:
            valeur = 0
        else:
            valeur = (self.reward_total/self.nbutilisations) + math.sqrt((2*math.log(paquets_envoyes)/self.nbutilisations))
        return valeur

""" Classe qui modélise un emetteur """
class emetteur:
    # Un emetteur possède un identifiant, un nombre de paquets envoyé, un ensemble de stratégies, un ensemble de statégies jamais utilisées,
    # un ensemble d'emission, un historique des stratégies utilisees et des récompenses et une récompense courante
    def __init__(self, identifiant, t, intensite, Tabstrat):
        self.identifiant = identifiant
        self.paquets_envoyes = 0
        self.strat = []
        self.strat_vierges = []
        for x in Tabstrat:
            self.strat.append(strat(x))
        for x in self.strat:
            self.strat_vierges.append(x)
        self.emissions = []
        for x in range(0, t, 1):
            self.emissions.append(False)
        prochain_envoi = -1
        prochain_envoi += math.ceil(exponentielle(intensite))
        while prochain_envoi < t:
            self.emissions[prochain_envoi] = True
            prochain_envoi += math.ceil(exponentielle(intensite))
        self.historique_strats = []
        self.historique_rewards = []
        self.reward_courant = 0

    # Ajoute la récompense à la récompense courante.
    def reward(self, reward):
        self.derniere_strat.reward(reward)
        self.reward_courant += reward

    def nb_copies(self, mab):
        if mab:
            if len(self.strat_vierges) > 0:
                strat = random.choice(self.strat_vierges)
                self.strat_vierges.remove(strat)
            else:
                valeur = 0
                for x in self.strat:
                    if x.valeur(self.paquets_envoyes) > valeur:
                        valeur = x.valeur(self.paquets_envoyes)
                        strat = x
        else:
            strat = random.choice(self.strat)
        self.derniere_strat = strat
        strat.nbutilisations += 1
        return strat.nbcopies

    # Envoie un paquet
    def envoyer_paquet(self, iteration, mab):
        if self.emissions[iteration]:
            self.paquets_envoyes += 1
            nbcopies = self.nb_copies(mab)
        else:
            nbcopies = 0
        self.historique_strats.append(nbcopies)
        return nbcopies

    # Enregistre la récompense
    def sauvegarder_reward(self):
        self.historique_rewards.append(self.reward_courant)
        self.reward_courant = 0

    # Renvoie le gain moyen de l'emetteur
    def gain_moyen(self):
        total = 0
        for s in self.strat:
            total += s.reward_total/s.nbutilisations
        return total/3

""" Station de base """
class BS:
    # Une BS contient un ensemble de trames, un historique avant SIC et un historique après SIC
    def __init__(self):
        self.trame = [[], [], [], [], [], [], [], [], [], []]
        self.historique_pre_sic = []
        self.historique_post_sic = []

    # Supprime les interférences de la trame de la BS
    def cancel_interference(self):
        suppression = True
        while suppression:
            suppression = False
            for x in self.trame:
                if len(x) == 1:
                    for y in self.trame:
                        if len(y) > 1:
                            present = False
                            for z in y:
                                if z == x[0]:
                                    present = True
                            if present:
                                y.remove(x[0])
                                suppression = True

    # Affiche le contenu de la trame
    def print_trames(self):
        print(str(self.trame))

    # La trame recoit des paquets
    def recevoir_paquets(self, emetteurs, iteration, mab):
        for x in emetteurs:
            envoi = x.envoyer_paquet(iteration, mab)
            positions = random.sample(range(0, 10, 1), envoi)
            for y in positions:
                self.trame[y].append(x.identifiant)

    # Attribut une récompense avant SIC
    def reward_pre_sic(self, emetteurs):
        recompenses = []
        for x in self.trame:
            if len(x) == 1 and x[0] not in recompenses:
                emetteurs[x[0]].reward(0.40)
                recompenses.append(x[0])

    # Attribue une récompense après SIC
    def reward_post_sic(self, emetteurs):
        recompenses = []
        for x in self.trame:
            if len(x) == 1 and x[0] not in recompenses:
                emetteurs[x[0]].reward(0.50)
                recompenses.append(x[0])
            elif len(x) > 1:
                for y in x:
                    if y not in recompenses:
                        emetteurs[y].reward(0.10)
                        recompenses.append(y)

    # Enregistre la trame après SIC
    def sauvegarder_post_sic(self):
        self.historique_post_sic.append(self.trame.copy())
        self.trame = [[], [], [], [], [], [], [], [], [], []]

    # Enregistre la trame avant SIC
    def sauvegarder_pre_sic(self):
        self.historique_pre_sic.append(copy.deepcopy(self.trame))

""" Simule un réseau """
class Simulation:
    def __init__(self, intensite, t, nbemetteurs, mab, Tabstrat):
        self.rez = reseau(nbemetteurs, intensite, t, Tabstrat)

        for x in range(0, t, 1):
            self.rez.bs.recevoir_paquets(self.rez.emetteurs, x, mab)
            self.rez.bs.reward_pre_sic(self.rez.emetteurs)
            self.rez.bs.sauvegarder_pre_sic()
            self.rez.bs.cancel_interference()
            self.rez.bs.reward_post_sic(self.rez.emetteurs)
            self.rez.bs.sauvegarder_post_sic()
            self.rez.sauvegarder_rewards()


# Renvoie un entier selon le processus de poisson avec l = lambda
def poisson(l):            
    x = 0
    p = 1
    p = p*random.uniform(0, 1)
    while p > math.exp(-l):
            x = x+1
            p = p*random.uniform(0, 1)
    return x

# Renvoie l'intervalle de temps entre deux reception de paquets
def exponentielle(intensite):
    u = random.uniform(0.0, 1.0)
    return -math.log(u)/intensite

# Simule et compare les stratégies MAB et la répartition uniforme
def test_mab_vs_uniforme():
    total = 0
    for i in range(0, 100, 1):
        sim = Simulation(0.5, 1000, 10, True, [2,3,4])
        total += sim.rez.gain_moyen()
    print("Gain moyen mab : "+str(total/100))

    total = 0
    for i in range(0, 100, 1):
        sim = Simulation(0.5, 1000, 10, False, [2,3,4])
        total += sim.rez.gain_moyen()
    print("Gain moyen uniforme : "+str(total/100))

# Calcule les gains moyens sur plusieurs simulations avec differents lambdas pour la stratégie MAB
def test_variation_lambda():
    gain_moyen = []
    for l in range(1, 50, 1):
        total = 0
        for i in range(1, 10, 1):
            sim = Simulation(l/10, 1000, 10, True, [2,3,4])
            total += sim.rez.gain_moyen()
        gain_moyen.append(total/10)
    # fig, ax = plt.subplots()
    plt.plot(range(1, 50, 1), gain_moyen)
    plt.show()

# Calcule les gains moyens sur plusieurs simulations avec differents lambdas (limité à 9) quelque soit la strategie
def test_variation_lambda_restreint(mab):
    gain_moyen = []
    for l in range(1, 9, 1):
        total = 0
        for i in range(0, 10, 1):
            sim = Simulation(l / 10, 1000, 10, mab, [2,3,4])
            total += sim.rez.gain_moyen()
        gain_moyen.append(total / 10)
    # fig, ax = plt.subplots()
    plt.plot(range(1, 9, 1), gain_moyen)
    plt.show()

# Test les gains moyens sur plusieurs simulations en fonction du nombre d'équipement
def test_variation_nb_equipements(mab):
    gain_moyen = []
    for e in range(1, 21, 1):
        total = 0
        for i in range(0, 10, 1):
            sim = Simulation(0.5, 1000, e, mab, [2,3,4])
            total += sim.rez.gain_moyen()
        gain_moyen.append(total/10)
    # fig, ax = plt.subplots()
    plt.plot(range(1, 21, 1), gain_moyen)
    plt.show()

# Test le renvoie le pourcentage d'utilisation des stratégies utilisées
def test_utilisation_strats(mab):
    Tabstrat = [2,4,8]
    accumulation_utilisations = {}
    accumulation_utilisations[0] = 0
    for x in Tabstrat:
        accumulation_utilisations[x] = 0
    for i in range(0, 100, 1):
        sim = Simulation(0.5, 1000, 10, mab, Tabstrat)
        utilisation = sim.rez.pourcentages_utilisation(Tabstrat)
        for j in utilisation:
            accumulation_utilisations[j] += utilisation[j]
    total = 0
    for i in accumulation_utilisations:
        total += accumulation_utilisations[i]
    total -= accumulation_utilisations[0]
    for i in Tabstrat:
        print("Stratégie "+str(i)+" : "+str((accumulation_utilisations[i]/total)*100)+" %")


# Appeler les fonctions cas de test ici :
test_utilisation_strats(True)
