import random
import math
import copy
import matplotlib.pyplot as plt


class reseau:
    def __init__(self, nbemetteurs, intensite, t):
        self.bs = BS()
        self.nbemetteurs = nbemetteurs
        self.emetteurs = []
        for x in range(0, nbemetteurs, 1):
            self.emetteurs.append(emetteur(x, t, intensite))

    def print_emetteurs(self):
        for x in self.emetteurs:
            print(str(x.identifiant))

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

    def sauvegarder_rewards(self):
        for x in self.emetteurs:
            x.sauvegarder_reward()

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

    def gain_moyen(self):
        total = 0
        for e in self.emetteurs:
            total += e.gain_moyen()
        return total/self.nbemetteurs

    def pourcentages_utilisation(self):
        utilisation = {
            0: 0,
            2: 0,
            3: 0,
            4: 0
        }
        for e in self.emetteurs:
            for i in e.historique_strats:
                utilisation[i] += 1
        return utilisation


class strat:
    def __init__(self, nbcopies):
        self.nbcopies = nbcopies
        self.nbutilisations = 0
        self.reward_total = 0

    def reward(self, reward):
        self.reward_total += reward

    def valeur(self, paquets_envoyes):
        if self.reward_total == 0:
            valeur = 0
        else:
            valeur = (self.reward_total/self.nbutilisations) + math.sqrt((2*math.log(paquets_envoyes)/self.nbutilisations))
        return valeur


class emetteur:
    def __init__(self, identifiant, t, intensite):
        self.identifiant = identifiant
        self.paquets_envoyes = 0
        self.strat = []
        self.strat_vierges = []
        for x in range(0, 3, 1):
            self.strat.append(strat(x+2))
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

    def envoyer_paquet(self, iteration, mab):
        if self.emissions[iteration]:
            self.paquets_envoyes += 1
            nbcopies = self.nb_copies(mab)
        else:
            nbcopies = 0
        self.historique_strats.append(nbcopies)
        return nbcopies

    def sauvegarder_reward(self):
        self.historique_rewards.append(self.reward_courant)
        self.reward_courant = 0

    def gain_moyen(self):
        total = 0
        for s in self.strat:
            total += s.reward_total/s.nbutilisations
        return total/3


class BS:
    def __init__(self):
        self.trame = [[], [], [], [], [], [], [], [], [], []]
        self.historique_pre_sic = []
        self.historique_post_sic = []

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

    def print_trames(self):
        print(str(self.trame))

    def recevoir_paquets(self, emetteurs, iteration, mab):
        for x in emetteurs:
            envoi = x.envoyer_paquet(iteration, mab)
            positions = random.sample(range(0, 10, 1), envoi)
            for y in positions:
                self.trame[y].append(x.identifiant)

    def reward_pre_sic(self, emetteurs):
        recompenses = []
        for x in self.trame:
            if len(x) == 1 and x[0] not in recompenses:
                emetteurs[x[0]].reward(0.40)
                recompenses.append(x[0])

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

    def sauvegarder_post_sic(self):
        self.historique_post_sic.append(self.trame.copy())
        self.trame = [[], [], [], [], [], [], [], [], [], []]

    def sauvegarder_pre_sic(self):
        self.historique_pre_sic.append(copy.deepcopy(self.trame))


def poisson(l):            # Renvois un entier selon le processus de poisson avec l = lambda
    x = 0
    p = 1

    p = p*random.uniform(0, 1)

    while p > math.exp(-l):
            x = x+1
            p = p*random.uniform(0, 1)

    return x


def exponentielle(intensite):
    u = random.uniform(0.0, 1.0)
    return -math.log(u)/intensite


class Simulation:
    def __init__(self, intensite, t, nbemetteurs, mab):
        self.rez = reseau(nbemetteurs, intensite, t)

        for x in range(0, t, 1):
            self.rez.bs.recevoir_paquets(self.rez.emetteurs, x, mab)
            self.rez.bs.reward_pre_sic(self.rez.emetteurs)
            self.rez.bs.sauvegarder_pre_sic()
            self.rez.bs.cancel_interference()
            self.rez.bs.reward_post_sic(self.rez.emetteurs)
            self.rez.bs.sauvegarder_post_sic()
            self.rez.sauvegarder_rewards()


def test_mab_vs_uniforme():
    total = 0
    for i in range(0, 100, 1):
        sim = Simulation(0.5, 1000, 10, True)
        total += sim.rez.gain_moyen()
    print("Gain moyen mab : "+str(total/100))

    total = 0
    for i in range(0, 100, 1):
        sim = Simulation(0.5, 1000, 10, False)
        total += sim.rez.gain_moyen()
    print("Gain moyen uniforme : "+str(total/100))


def test_variation_lambda():
    gain_moyen = []
    for l in range(1, 50, 1):
        total = 0
        for i in range(1, 10, 1):
            sim = Simulation(l/10, 1000, 10, True)
            total += sim.rez.gain_moyen()
        gain_moyen.append(total/10)
    fig, ax = plt.subplots()
    plt.plot(range(1, 50, 1), gain_moyen)
    plt.show()


def test_variation_lambda_restreint(mab):
    gain_moyen = []
    for l in range(1, 9, 1):
        total = 0
        for i in range(0, 10, 1):
            sim = Simulation(l / 10, 1000, 10, mab)
            total += sim.rez.gain_moyen()
        gain_moyen.append(total / 10)
    fig, ax = plt.subplots()
    plt.plot(range(1, 9, 1), gain_moyen)
    plt.show()


def test_variation_nb_equipements(mab):
    gain_moyen = []
    for e in range(1, 21, 1):
        total = 0
        for i in range(0, 10, 1):
            sim = Simulation(0.5, 1000, e, mab)
            total += sim.rez.gain_moyen()
        gain_moyen.append(total/10)
    fig, ax = plt.subplots()
    plt.plot(range(1, 21, 1), gain_moyen)
    plt.show()


def test_utilisation_strats(mab):
    accumulation_utilisations = {0: 0, 2: 0, 3: 0, 4: 0}
    for i in range(0, 100, 1):
        sim = Simulation(0.5, 1000, 10, mab)
        utilisation = sim.rez.pourcentages_utilisation()
        for j in utilisation:
            accumulation_utilisations[j] += utilisation[j]
    total = 0
    for i in accumulation_utilisations:
        total += accumulation_utilisations[i]
    total -= accumulation_utilisations[0]
    for i in range(2, 5, 1):
        print("Stratégie "+str(i)+" : "+str((accumulation_utilisations[i]/total)*100)+"%")


# Appeler les fonctions cas de test ici :
test_mab_vs_uniforme()
