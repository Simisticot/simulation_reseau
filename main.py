import random
import math
import copy


class reseau:
    def __init__(self, nbemetteurs, intensite, t):
        self.bs = BS()
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
        print(str(succes_partiels)+" transmissions sauvées")
        print(str(collisions)+" pertes via collision")

    def sauvegarder_rewards(self):
        for x in self.emetteurs:
            x.sauvegarder_reward()

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
        self.nbemissions = poisson(intensite*t)
        if self.nbemissions > t:
            self.nbemissions = t
        for x in range(0, t, 1):
            self.emissions.append(False)
        num_emissions = random.sample(range(0, t, 1), self.nbemissions)
        for x in num_emissions:
            self.emissions[x] = True
        self.historique_strats = []
        self.historique_rewards = []
        self.reward_courant = 0

    def reward(self, reward):
        self.derniere_strat.reward(reward)
        self.reward_courant += reward

    def nb_copies(self):
        if len(self.strat_vierges) > 0:
            strat = random.choice(self.strat_vierges)
            self.strat_vierges.remove(strat)
        else:
            valeur = 0
            for x in self.strat:
                if x.valeur(self.paquets_envoyes) > valeur:
                    valeur = x.valeur(self.paquets_envoyes)
                    strat = x
        self.derniere_strat = strat
        strat.nbutilisations += 1
        return strat.nbcopies

    def envoyer_paquet(self, iteration):
        if self.emissions[iteration]:
            self.paquets_envoyes += 1
            nbcopies = self.nb_copies()
        else:
            nbcopies = 0
        self.historique_strats.append(nbcopies)
        return nbcopies

    def sauvegarder_reward(self):
        self.historique_rewards.append(self.reward_courant)
        self.reward_courant = 0


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

    def recevoir_paquets(self, emetteurs, iteration):
        for x in emetteurs:
            envoi = x.envoyer_paquet(iteration)
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


def simulation(intensite, t, nbemetteurs):
    rez = reseau(nbemetteurs, intensite, t)

    for x in range(0, t, 1):
        rez.bs.recevoir_paquets(rez.emetteurs, x)
        rez.bs.reward_pre_sic(rez.emetteurs)
        rez.bs.sauvegarder_pre_sic()
        rez.bs.cancel_interference()
        rez.bs.reward_post_sic(rez.emetteurs)
        rez.bs.sauvegarder_post_sic()
        rez.sauvegarder_rewards()
    print("done")
    rez.print_resume_iteration(t-1)


simulation(0.5, 10, 10)
print("cc")
