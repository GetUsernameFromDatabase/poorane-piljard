"""
Programm on tehtud kasutades omandatud teadmisi - youtube tutorials, programmeerimise kurus ja muu internetist leitud
õppematerjal.

Programmis on ettevalmistatud olukorrad ja kui mäng tööle läheb, siis kutsub neid esile ja "ehitab" mängu.
Kasutades sellist viis on programmi lihtne muuta ja leida probleemseid kohti.

Kõik #noinspection -id on selle jaoks, et PyCharm mulle pidevalt närvidele ei käiks

Märkimisväärsed saidid:
https://www.rapidtables.com/web/color/RGB_Color.html        RGB värvid
https://freesound.org/                                      Koht, kust võtsin helifaile
https://www.youtube.com/channel/UCW6TXMZ5Pq6yL6_k5NZ2e0Q    Pythoni õppevideod - Socratica
https://www.youtube.com/channel/UCfzlCWGWYyIQ0aLC5w48gBQ    Pythoni õppevideod - Sentdex
https://www.youtube.com/channel/UCNaPQ5uLX5iIEHUCLmfAgKg    Pythoni õppevideod - KidsCanCode

https://www.w3schools.com/python/default.asp                Õppematerjal
https://courses.cs.ut.ee/t/pythonkoolis                     Õppematerjal

https://www.pg.org/docs/genindex.html                       Pygame kohta asjad

https://www.youtube.com/channel/UC0e3QhIYukixgh5VVpKHH9Q    On tekitanud mulle huvi programmeerimise vastu

https://docs.python.org/3/library/configparser.html         Sättete faili tegemise info
https://www.youtube.com/watch?v=25ovCm9jKfA                 Lambda ja map funktsioon
http://cs231n.github.io/python-numpy-tutorial/              Numpy info

Nende kasutused:
Socratica käest õppisin map ja lambda funktsiooni ja class -ide kohta tibakene, ma oskan neid kasutada, aga ei suuda
kasutada nii hästi, kui kogenumad inimesed.

Sentdex teeb väga põhjalikke õpetusvideoid. Ta on siin, kuna ta videod on näidanud mulle, mida saab teha pythoniga, ehk
kui hämmastav on python.

KidsCanCode poolt tehtud videod aitasid mind spraitidega.

Pygame kodulehekülg on selle programmi tegemisel kasutatud pidevalt. Ilma selleta ma oleks liiga palju aega kulutanud
KidsCanCode videote peale, kuna videotes, mida ma leidsin ta ei kasutanud pg.SRCALPHA, mis teeb palli joonistamisel
kasutatud tausta läibpaistvaks.
Ma tema videotes ei leidnud ka pg.sprite.collide_circle kohta infot, seda ma kasutan, et pallide vahelisi põrkeid
kontrollida.
Kuigi temast oli abi, sest seletas mulle pygame loogikat, mis oleks võinud olla pygame veebisaidil.

"""

import time
import wave
from codecs import open
from configparser import RawConfigParser
from ctypes import windll
from math import sqrt, sin, cos, tan, acos, pi, tau, ceil
from os import environ, mkdir, path
from random import randint

import pygame as pg
from numpy import array, count_nonzero, hypot, dot, average
from pyautogui import alert
from pygame.gfxdraw import aacircle, filled_circle
from win32con import SW_HIDE, SW_SHOW
from win32gui import GetForegroundWindow, ShowWindow

environ['SDL_VIDEO_CENTERED'] = '1'
FPS = pg.time.Clock()
alustatud = False
pildi_teade = False
fondi_teade = False


# noinspection PyArgumentList,PyArgumentEqualDefault
class Satted:
    """
    Siin on mängu mõjutavad sätted. Enamus on võetud Sättete konfiguratsiooni failist - Sätted.ini.
    """

    @staticmethod
    def ikoon():
        try:
            ikoon = pg.image.load("Piljard_32.ico")
            pg.display.set_icon(ikoon)
        except pg.error:
            # Siin ei kasutata teate esiletoojat, kuna see peidab akna ära, aga mäng siis veel ei tööta
            alert(text="Ikooni ei leitud", title="Teade", button="OK")

    numbri_aluse_raadius = None

    @staticmethod
    def tuubeldaja(string):
        uhikud = string.replace("(", "").replace(")", "").split(",")
        tuubeldis = tuple(map(lambda uhik: int(uhik), uhikud))
        return tuubeldis

    @staticmethod
    def suhte_puhastaja(string):
        arv = ""
        string = string.strip()
        for taht in string:
            try:
                int(taht)
                arv += taht
            except ValueError:
                if taht == "." or taht == ",":
                    arv += "."
                elif taht == "%":
                    break
        if arv != "":
            return float(arv)
        else:
            return 0

    """
    Sättete töötlemine                                          
    """
    # Sättete fail
    s2tted = RawConfigParser(allow_no_value=True)
    andmekaust = "Andmed/"
    s2ttefaili_asukoht = andmekaust + "Sätted.ini"
    if not path.isdir(andmekaust):
        mkdir(andmekaust)
    s2ttete_fail_olemas = True
    try:
        # noinspection PyArgumentEqualDefault
        s2tted.read_file(open(s2ttefaili_asukoht, "r", "utf8"))
    except FileNotFoundError:
        alert(text="Sättete fail puudub. Kõik on asendatud vaikisättetega.", title="Teade", button="OK")
        s2ttete_fail_olemas = False

    vajalikud_pealkirjad = "Suurused", "Värvid", "Tekst", "Pildid", "Helid"
    olemasolevad_pealkirjad = s2tted.sections()
    for pealkiri in vajalikud_pealkirjad:
        if pealkiri not in olemasolevad_pealkirjad:
            s2tted.add_section(pealkiri)
            pohjus = 'Kõik valikud paragraafist "' + pealkiri + '" on asendatud vaikesättedega, sest paragraaf puudus.'
            s2tted.set(pealkiri, pohjus)
            s2tted.set(pealkiri, "")
            if s2ttete_fail_olemas:
                alert(text=pohjus, title="Teade", button="OK")
    s2tted.write(open(s2ttefaili_asukoht, "w", "utf8"))

    SUURUSED_t = "Suurused"
    PILDID_t = "Pildid"
    TEKST_t = "Tekst"
    VARVID_t = "Värvid"
    HELID_t = "Helid"
    Suurused = s2tted[SUURUSED_t]
    Pildid = s2tted[PILDID_t]
    Varvid = s2tted[TEKST_t]
    Tekst = s2tted[VARVID_t]
    Helid = s2tted[HELID_t]

    # Suvalised sätted
    tiitel = "Pöörane Piljard"
    tabeli_slp_tekst = "Sees olevad pallid:"
    v_l_t = "Sees", "Väljas"  # Tabeli I/O kasti sees olev tekst, veidruste lüliti
    menuude_tekstid = [tiitel, "Mängi", "Sulge", "Alusta Uuesti", "Jätka"]

    @staticmethod
    def menuu_nupud():
        if mangu_algus and not lopeta:
            menuu_nupud = ["Mängi", "Sulge"]
        else:
            menuu_nupud = ["Alusta Uuesti", "Jätka", "Sulge"]
        return menuu_nupud

    # Font
    @staticmethod
    def font(suurus):
        global fondi_teade
        Font = pg.font.match_font(Satted.mis_font)
        if not Font:
            Font = pg.font.match_font("georgia")  # See on igaks juhuks, kui arvutil puudub ka minu soovitud font
            if not Font:
                Font = pg.font.get_default_font()
            if not fondi_teade:
                Aken.teate_esiletooja("Tahetud fonti ei leitud")
                fondi_teade = True
        return pg.font.Font(Font, suurus)

    @staticmethod
    def ruudu_diagonaali_ja_selle_siseringi_diameetri_erinevus(raadius):
        # Leiab ruudu diagonaali ja selle siseringi diameetri erinevuse, mis on sama, mis ringi ja selle sisemise ruudu
        # erinevus. Seda kasutan, et ringe oleks lihtsam kasutada kordinaatsüsteemis.
        erinevus = raadius * (Satted.ruutjuur_2 - 1) / Satted.ruutjuur_2
        return erinevus

    @staticmethod
    def kontrolloor(asukoht, s2ttefail, kogum, pealkiri):
        def asendus():
            s2ttefail.set(pealkiri, valik, kogum[valik])

        for valik in kogum:
            if not s2ttefail.has_option(pealkiri, valik):
                asendus()
            elif not s2ttefail.get(pealkiri, valik):
                asendus()
            else:
                vana_teade = 'kõik valikud paragraafist "' + pealkiri + '" on asendatud vaikesättedega,' \
                                                                        ' sest paragraaf puudus.'
                s2ttefail.remove_option(pealkiri, vana_teade)
        s2ttefail.write(open(asukoht, "w", "utf8"))
        s2ttefail.read_file(open(asukoht, "r", "utf8"))

    tuubeldaja = tuubeldaja.__get__(object)
    kontrolloor = kontrolloor.__get__(object)
    suhte_puhastaja = suhte_puhastaja.__get__(object)

    """
    Pildid
    """
    PILDID = {"Laua Kaunistus": "Laua Kaunistus.png"}
    kontrolloor(s2ttefaili_asukoht, s2tted, PILDID, PILDID_t)
    laua_kaunistuse_voti = list(PILDID.keys())[0]
    pilt = andmekaust + Pildid.get(laua_kaunistuse_voti, PILDID[laua_kaunistuse_voti])
    """                                                                                                                 
    Suurused                                                                                                            
    """
    # Et programm tooks välja puuduvad sätted.
    SUURUSED = {"Akna suurus monitori suhtes": "65 %", "Mitu kaunistust igas vahes": 3, "Sisselöödud palli suurus": 29,
                "Tabeli minimaalne kõrgus": 0, "Elude kogus": 7, "Elusümboli küljesuurus": 30,
                "Telepordi võimalus": "7 %", "Ehmataja võimalus": "3 %", "Laua ääre paksus": 50,
                "Laua põrkeseina paksus": 10, "Piljardi laua laius": 1200,
                "Tee laua suurus ka vastavalt monitori suurusele": False, "Kaunistuse suurus": 10,
                "Musta augu raadius": 23, "Mitu korda on must auk suurem kui pall": 1.6, "Palli triibu paksus": "12",
                "Laua hõõrdejõud": 0.2, "Valge palli mass": 165, "Ülejäänud pallide massid": 160, "FPS": 60,
                "Kui pikk on kii": 310}
    suuruste_valikud = list(SUURUSED.keys())
    suuruste_vaikesatted = list(SUURUSED.values())
    kontrolloor(s2ttefaili_asukoht, s2tted, SUURUSED, SUURUSED_t)

    # Selle eesmärk on arvutada see ära ja mällu salvestada, et arvuti peaks vähem vaeva nägema.
    ruutjuur_2 = sqrt(2)
    akna_suurus_maxist = suhte_puhastaja(Suurused.get(suuruste_valikud[0], suuruste_vaikesatted[0])) / 100
    menuu_tekstide_kaugus = 0
    mitu_kaunistust_igas_vahes = Suurused.getint(suuruste_valikud[1], suuruste_vaikesatted[1])
    m_k_l = 7  # Menüü kasti lisasuurus
    # Tabel
    spss = Suurused.getint(suuruste_valikud[2], suuruste_vaikesatted[2])  # Sees oleva palli soovitud suurus
    tabeli_korgus = Suurused.getint(suuruste_valikud[3], suuruste_vaikesatted[3])
    aarekaugus = 5
    t_k_l = 3  # Tabeli kasti lisasuurus
    # Elud
    elude_kogus = Suurused.getint(suuruste_valikud[4], suuruste_vaikesatted[4])
    if elude_kogus <= 0:
        eludeta_mang = True
    else:
        eludeta_mang = False
    elusumboli_kulg = Suurused.getint(suuruste_valikud[5], suuruste_vaikesatted[5])
    # Veidrused
    telepordi_voimalus = suhte_puhastaja(Suurused.get(suuruste_valikud[6], suuruste_vaikesatted[6]))
    ehmataja_voimalus = suhte_puhastaja(Suurused.get(suuruste_valikud[7], suuruste_vaikesatted[7]))
    # Laud
    laua_porkeseina_vahe = Suurused.getint(suuruste_valikud[8], suuruste_vaikesatted[8])
    laua_vahe = Suurused.getint(suuruste_valikud[9], suuruste_vaikesatted[9])
    laua_laius = Suurused.getint(suuruste_valikud[10], suuruste_vaikesatted[10])
    laud_solt_mon = Suurused.getboolean(suuruste_valikud[11], suuruste_vaikesatted[11])
    laua_suurus = round(laua_laius), round(laua_laius / 2)
    kaunistuste_suurus = Suurused.getint(suuruste_valikud[12], suuruste_vaikesatted[12])
    # Ringidega seotud asjad - pallid, augud
    musta_augu_raadius = Suurused.getint(suuruste_valikud[13], suuruste_vaikesatted[13])
    palli_raadius = round(musta_augu_raadius / Suurused.getfloat(suuruste_valikud[14], suuruste_vaikesatted[14]))
    palli_triibu_paksus = 1 - suhte_puhastaja(Suurused.get(suuruste_valikud[15], suuruste_vaikesatted[15])) / 100
    # Füüsika
    meow = Suurused.getfloat(suuruste_valikud[16], suuruste_vaikesatted[16])  # Hõõrdejõud
    valge_palli_m = Suurused.getfloat(suuruste_valikud[17], suuruste_vaikesatted[17])
    teiste_p_massid = Suurused.getfloat(suuruste_valikud[18], suuruste_vaikesatted[18])
    max_joud = laua_laius / 48
    # Sagedus
    tsuk = int(max_joud // palli_raadius + 1)
    fps = Suurused.getint(suuruste_valikud[19], suuruste_vaikesatted[19])  # Paneb fps piirangu
    # Kii
    kii_pikkus = Suurused.getint(suuruste_valikud[20], suuruste_vaikesatted[20])
    """
    Tekst
    """
    TEKST = {"Font": "georgia", "Tiitli fondi suurus": 40, "Tavalise fondi suurus": 20, "Tabeli fondi suurus": 20}
    tekstide_valikud = list(TEKST.keys())
    tekstide_vaikesatted = list(TEKST.values())
    kontrolloor(s2ttefaili_asukoht, s2tted, TEKST, TEKST_t)

    # Font
    mis_font = Tekst.get(tekstide_valikud[0], tekstide_vaikesatted[0])
    # Fondi suurused
    tiitel_fondi_suurus = Tekst.getint(tekstide_valikud[1], tekstide_vaikesatted[1])
    tavalise_fondi_suurus = Tekst.getint(tekstide_valikud[2], tekstide_vaikesatted[2])
    tabeli_fondi_suurus = Tekst.getint(tekstide_valikud[3], tekstide_vaikesatted[3])
    tabeli_sop_fondi_suurus = spss + 1 - 10
    if tabeli_sop_fondi_suurus <= 10:
        tabeli_sop_fondi_suurus = max(spss, 10)
    tabeli_sop_fondi_suurus = max(tabeli_sop_fondi_suurus, tabeli_fondi_suurus)

    """
    Värvid
    """
    VARVID = {"Tabeli värv": "(218, 165, 32)", "Tabelit eraldavava joone värv": "(0, 0, 0)",
              "Lüliti värv on tabeli vastandvärv": False, "Sees lüliti värv": "(255, 0, 0)",
              "Tabeli kasti värv": "(0, 0, 0)", "Elusümboli värv": "(255, 25, 25)",
              "Elusümboli värv, kui on kaotatud elu": "(10, 0, 0)", "Akna taustavärv": "(0, 153, 153)",
              "Tabeli teksti värv": "(0, 0, 0)", "Teksti tavaline värv": "(255, 255, 255)",
              "Valitud teksti värv": "(0, 0, 0)", "Laua serva värv": "(133, 94, 66)",
              "Laua põrkeseina värv": "(0, 102, 0)", "Laua värv": "(0, 153, 0)", "Augu värv": "(0, 0, 0)",
              "Augu ümbrise värv": "(199, 177, 159)", "Stardijoone värv": "(255, 255, 255)",
              "Kas veidruse must auk on nähtamatu?": False, "1 ja 9": "(255, 215, 0)", "2 ja 10": "(30, 144, 255)",
              "3 ja 11": "(220, 20, 60)", "4 ja 12": "(75, 0, 130)", "5 ja 13": "(255, 140, 0)",
              "6 ja 14": "(46, 139, 87)", "7 ja 15": "(128, 0, 0)", "8 pall": "(0, 0, 0)",
              "Kii pall": "(255, 255, 255)", "Palli numbri värv": "(0, 0, 0)", "Kii värv": "(139, 69, 19)"}
    varvide_valikud = list(VARVID.keys())
    varvide_vaikesatted = list(VARVID.values())
    kontrolloor(s2ttefaili_asukoht, s2tted, VARVID, VARVID_t)

    # Tabel
    tabeli_varv = tuubeldaja(Varvid.get(varvide_valikud[0], varvide_vaikesatted[0]))
    tabelit_eraldav_varv = tuubeldaja(Varvid.get(varvide_valikud[1], varvide_vaikesatted[1]))
    if not Suurused.getboolean(varvide_valikud[2], varvide_vaikesatted[2]):
        luliti_sees_varv = tuubeldaja(Varvid.get(varvide_valikud[3], varvide_vaikesatted[3]))
    else:
        luliti_sees_varv = tuple(255 - array(tabeli_varv))
    tabeli_kasti_varv = tuubeldaja(Varvid.get(varvide_valikud[4], varvide_vaikesatted[4]))
    elusumboli_varv = tuubeldaja(Varvid.get(varvide_valikud[5], varvide_vaikesatted[5]))
    kaotatud_elusumboli_varv = tuubeldaja(Varvid.get(varvide_valikud[6], varvide_vaikesatted[6]))
    akna_varvus = tuubeldaja(Varvid.get(varvide_valikud[7], varvide_vaikesatted[7]))
    # Tekst
    tabeli_teksti_varv = tuubeldaja(Varvid.get(varvide_valikud[8], varvide_vaikesatted[8]))
    teksti_varv = tuubeldaja(Varvid.get(varvide_valikud[9], varvide_vaikesatted[9]))
    valitud_teksti_varv = tuubeldaja(Varvid.get(varvide_valikud[10], varvide_vaikesatted[10]))
    # Laud
    laua_serva_varv = tuubeldaja(Varvid.get(varvide_valikud[11], varvide_vaikesatted[11]))
    laua_porkeseina_varv = tuubeldaja(Varvid.get(varvide_valikud[12], varvide_vaikesatted[12]))
    laua_varv = tuubeldaja(Varvid.get(varvide_valikud[13], varvide_vaikesatted[13]))
    augu_varv = tuubeldaja(Varvid.get(varvide_valikud[14], varvide_vaikesatted[14]))
    augu_katte_varv = tuubeldaja(Varvid.get(varvide_valikud[15], varvide_vaikesatted[15]))
    akv = array(augu_katte_varv)
    mx_erinevus = 65
    if average(abs(array(teksti_varv) - akv)) < mx_erinevus:
        if average(abs(array((0, 0, 0)) - akv)) > mx_erinevus:
            helitugevuse_varv = (0, 0, 0)
        else:
            helitugevuse_varv = tuple(255 - akv)
    else:
        helitugevuse_varv = teksti_varv
    stardijoone_varv = tuubeldaja(Varvid.get(varvide_valikud[16], varvide_vaikesatted[16]))
    rombi_varv = augu_katte_varv
    # Veidrused
    must_auk_nahtamatu = Varvid.getboolean(varvide_valikud[17], varvide_vaikesatted[17])
    # Pallid
    palli_varvid = [
        tuubeldaja(Varvid.get(varvide_valikud[18], varvide_vaikesatted[18])),  # TRIIBUTA
        tuubeldaja(Varvid.get(varvide_valikud[19], varvide_vaikesatted[19])),  # TRIIBUTA
        tuubeldaja(Varvid.get(varvide_valikud[20], varvide_vaikesatted[20])),  # TRIIBUTA
        tuubeldaja(Varvid.get(varvide_valikud[21], varvide_vaikesatted[21])),  # TRIIBUTA
        tuubeldaja(Varvid.get(varvide_valikud[22], varvide_vaikesatted[22])),  # TRIIBUTA
        tuubeldaja(Varvid.get(varvide_valikud[23], varvide_vaikesatted[23])),  # TRIIBUTA
        tuubeldaja(Varvid.get(varvide_valikud[24], varvide_vaikesatted[24])),  # TRIIBUTA
        tuubeldaja(Varvid.get(varvide_valikud[25], varvide_vaikesatted[25])),  # TRIIBUTA 8-pall
        tuubeldaja(Varvid.get(varvide_valikud[18], varvide_vaikesatted[18])),  # TRIIP ON OLEMAS
        tuubeldaja(Varvid.get(varvide_valikud[19], varvide_vaikesatted[19])),  # TRIIP ON OLEMAS
        tuubeldaja(Varvid.get(varvide_valikud[20], varvide_vaikesatted[20])),  # TRIIP ON OLEMAS
        tuubeldaja(Varvid.get(varvide_valikud[21], varvide_vaikesatted[21])),  # TRIIP ON OLEMAS
        tuubeldaja(Varvid.get(varvide_valikud[22], varvide_vaikesatted[22])),  # TRIIP ON OLEMAS
        tuubeldaja(Varvid.get(varvide_valikud[23], varvide_vaikesatted[23])),  # TRIIP ON OLEMAS
        tuubeldaja(Varvid.get(varvide_valikud[24], varvide_vaikesatted[24])),  # TRIIP ON OLEMAS
        tuubeldaja(Varvid.get(varvide_valikud[26], varvide_vaikesatted[26]))  # TRIIBUTA KII PALL
    ]
    palli_numbri_varv = tuubeldaja(Varvid.get(varvide_valikud[27], varvide_vaikesatted[27]))
    # Kii
    kii_varv = tuubeldaja(Varvid.get(varvide_valikud[28], varvide_vaikesatted[28]))

    """
    Helid
    """
    HELID = {"Heli vaiketugevus": "80 %", "Helitu ehmataja": False, "Põrge": "Põrge.wav", "Ehmatus": "Ehmatus.wav",
             "Võit": "Võit.wav", "Kaotus": "Kaotus.wav", "Palli sisseminek": "Pall_Sisse.wav",
             "Lauaga porge": "Laua_Põrge.wav"}
    helide_valikud = list(HELID.keys())
    helide_vaikesatted = list(HELID.values())
    kontrolloor(s2ttefaili_asukoht, s2tted, HELID, HELID_t)

    heli_vaiketugevus = suhte_puhastaja(Helid.get(helide_valikud[0], helide_vaikesatted[0])) / 100
    # Helitugevuse maksimaalne teksti suurus
    ht_m_t_s = 0
    problemaatilised_helid = []
    helikaust = andmekaust + "Helid/"
    helitu_ehmataja = Helid.getboolean(helide_valikud[1], helide_vaikesatted[1])

    porke_heli = helikaust + Helid.get(helide_valikud[2], helide_vaikesatted[2])
    ehmatuse_heli = helikaust + Helid.get(helide_valikud[3], helide_vaikesatted[3])
    voit = helikaust + Helid.get(helide_valikud[4], helide_vaikesatted[4])
    kaotus = helikaust + Helid.get(helide_valikud[5], helide_vaikesatted[5])
    pall_sisse = helikaust + Helid.get(helide_valikud[6], helide_vaikesatted[6])
    lauaga_porge = helikaust + Helid.get(helide_valikud[7], helide_vaikesatted[7])
    helid = {"porge": porke_heli, "ehmatus": ehmatuse_heli, "võit": voit,
             "pall_sisse": pall_sisse, "lauaga_porge": lauaga_porge, "kaotus": kaotus}
    try:
        with wave.open(helid["pall_sisse"], 'r') as f:
            kogus = f.getnframes()
            kiirus = f.getframerate()
        pall_sisse_pikkus = kogus / float(kiirus)
    except FileNotFoundError:
        pall_sisse_pikkus = 0


class Aken:
    """
    Siin on programmi aknaga seotud asjad - resolutsioon, nupud, akna värv
    """

    class Alus:
        """
        See moodustab terve pildi, mida on näha programmi avamisel
        """

        @staticmethod
        def resolutsioon_f():
            global alustatud, PAUS
            monitori_suurus = windll.user32.GetSystemMetrics(0), windll.user32.GetSystemMetrics(1)

            t_s_s = Aken.tabeli_korguse_leidja("kõik")
            if t_s_s > Satted.tabeli_korgus:
                Satted.tabeli_korgus = t_s_s
            if Satted.laud_solt_mon:
                # Tabeli kõrgusega arvestatud max monitori suurus - kompenseeritud monitori max suurus
                k_m_m_s = tuple(suurus - Satted.tabeli_korgus * (2 - i) for (i, suurus) in enumerate(monitori_suurus))
                if 2 * k_m_m_s[1] > k_m_m_s[0]:
                    k_m_m_s = k_m_m_s[0], k_m_m_s[0] / 2
                else:
                    k_m_m_s = 2 * k_m_m_s[1], k_m_m_s[1]

                Satted.laua_suurus = tuple(round(suurus * Satted.akna_suurus_maxist) for suurus in k_m_m_s)
                Satted.laua_laius = Satted.laua_suurus[0]
                Satted.max_joud = Satted.laua_laius / 48
                Satted.tsuk = int(Satted.max_joud // Satted.palli_raadius + 1)
                Satted.laud_solt_mon = False

            if not alustatud and PAUS:
                resolutsioon = tuple(round((telg - 28 * i) * Satted.akna_suurus_maxist)
                                     for (i, telg) in enumerate(monitori_suurus))
                Satted.menuu_tekstide_kaugus = int(resolutsioon[1] * 0.25)
            else:
                resolutsioon = (Satted.laua_suurus[0], Satted.laua_suurus[1] + Satted.tabeli_korgus)
            return resolutsioon

        def __init__(self):  # Värvib akna ja uuendab seda
            self.resolutsioon = Aken.Alus.resolutsioon_f()
            self.aken = pg.display.set_mode(self.resolutsioon)
            try:
                self.aken.blit(self.tagaplaan, (0, 0))
            except (NameError, TypeError, AttributeError):
                self.tagaplaan = pg.Surface(self.aken.get_size())
                self.tagaplaan.fill(Satted.akna_varvus)
                self.tagaplaan = self.tagaplaan.convert()
                self.aken.blit(self.tagaplaan, (0, 0))

    @staticmethod
    def joonista_menuu():  # Teeb peamenüüse pilte
        f_s = Satted.tavalise_fondi_suurus, Satted.tiitel_fondi_suurus
        Akna_kesk_X = (ALUS.aken.get_size()[0] + 1) // 2
        k_k = Satted.m_k_l  # Kasti külg
        alg_sisendid = Olukord.sisendid()
        hiir = alg_sisendid["hiire_koht"]
        tk = Aken.teksti_kirjutaja
        if Satted.ht_m_t_s == 0:
            Satted.ht_m_t_s = Aken.teksti_kirjutaja("100", Satted.tavalise_fondi_suurus, None, None, None, False)
        try:  # Nüüd hakkab kastidega tegelemine
            m_n_k = Aken.alguse_menuu_nuppude_kohad
            for nupp in Satted.menuu_nupud():
                varv = Satted.teksti_varv
                x = m_n_k[nupp][0][0]
                y = m_n_k[nupp][0][1]
                suurus = m_n_k[nupp][1]

                if hiir[0] in range(x - k_k, x + suurus[0] + k_k) and hiir[1] in range(y - k_k, y + suurus[1] + k_k):
                    varv = Satted.valitud_teksti_varv
                    if alg_sisendid["hiire_klõps"] == 1:
                        alg_sisendid = nupp
                tk(nupp, f_s[0], ALUS.aken, (x + (suurus[0] + 1) // 2, y), varv, True)
            Helid.naita_tugevust()
        except (NameError, TypeError, AttributeError):
            tiitli_korgus = tk(Satted.tiitel, f_s[1], ALUS.aken, (Akna_kesk_X, 1), Satted.teksti_varv, False)[1] + 1
            Aken.alguse_menuu_nuppude_kohad = {}
            korgus = tiitli_korgus + Satted.menuu_tekstide_kaugus
            for nupp in Satted.menuu_nupud():
                suurus = tk(nupp, f_s[0], ALUS.aken, (Akna_kesk_X, korgus), Satted.teksti_varv, True)
                Aken.alguse_menuu_nuppude_kohad[nupp] = (Akna_kesk_X - (suurus[0] + 1) // 2, korgus), suurus
                korgus += suurus[1] + Satted.m_k_l * 3
        return alg_sisendid

    @staticmethod
    def mang_on_labi():
        def tiitli_tegija():
            h = 1
            h += tk(Olukord.loputiitel, f_s[0], alus, (Akna_kesk_X, h), Satted.teksti_varv, False)[1]
            h += tk(pohjus, f_s[1], alus, (Akna_kesk_X, h), Satted.teksti_varv, False)[1]
            h += Satted.menuu_tekstide_kaugus
            return h

        f_s = Satted.tiitel_fondi_suurus, Satted.tiitel_fondi_suurus - 10, Satted.tavalise_fondi_suurus
        alus = ALUS.aken
        alus.fill(Satted.akna_varvus)
        lopusisendid = Olukord.sisendid()
        hiir = lopusisendid["hiire_koht"]
        tk = Aken.teksti_kirjutaja
        Akna_kesk_X = (alus.get_size()[0] + 1) // 2
        k_k = Satted.m_k_l
        Helid.naita_tugevust()

        pohjus = Olukord.lopupohjus
        nupud = Satted.menuu_nupud()
        del nupud[1]
        try:
            m_n_k = Aken.lopu_menuu_nuppude_kohad
            tiitli_tegija()
            for nupp in nupud:
                varv = Satted.teksti_varv
                x = m_n_k[nupp][0][0]
                y = m_n_k[nupp][0][1]
                suurus = m_n_k[nupp][1]

                if hiir[0] in range(x - k_k, x + suurus[0] + k_k) and hiir[1] in range(y - k_k, y + suurus[1] + k_k):
                    varv = Satted.valitud_teksti_varv
                    if lopusisendid["hiire_klõps"] == 1:
                        lopusisendid = nupp
                tk(nupp, f_s[2], ALUS.aken, (x + (suurus[0] + 1) // 2, y), varv, True)
        except (NameError, TypeError, AttributeError):
            Aken.lopu_menuu_nuppude_kohad = {}
            korgus = tiitli_tegija()
            for nupp in nupud:
                suurus = tk(nupp, f_s[2], ALUS.aken, (Akna_kesk_X, korgus), Satted.teksti_varv, True)
                Aken.lopu_menuu_nuppude_kohad[nupp] = (Akna_kesk_X - (suurus[0] + 1) // 2, korgus), suurus
                korgus += suurus[1] + Satted.m_k_l * 3
        return lopusisendid

    @staticmethod
    def teate_esiletooja(teade):
        if alustatud:
            piljardi_aken = GetForegroundWindow()
            ShowWindow(piljardi_aken, SW_HIDE)
        alert(text=teade, title="Teade", button="OK")
        if alustatud:
            ShowWindow(piljardi_aken, SW_SHOW)

    @staticmethod
    def tabeli_korguse_leidja(osa):
        try:
            h = Aken.kuni_veidrusteni_korgus

        except (NameError, TypeError, AttributeError):
            # Elude kogukõrgus
            if not Satted.eludeta_mang:
                h = ((Satted.elude_kogus * (Satted.elusumboli_kulg + 3)) // Satted.laua_laius + 1) * \
                    Satted.elusumboli_kulg + 1
            else:
                h = 0
            # Sees olevate pallid kogukõrgus
            # Palli diameeter
            ss = Satted.spss + 1
            # Sisse löödud pallidega ühendatud asjade kogu kõrgus
            slpt_suurus = Aken.teksti_kirjutaja(Satted.tabeli_slp_tekst, Satted.tabeli_sop_fondi_suurus, None, None,
                                                None, False)
            sop_korgus = (Satted.aarekaugus + slpt_suurus[0] + 15 * ss + 1) // Satted.laua_laius
            # Sees olevate pallide kõige suureim kõrguse ühik, see on igaks juhuks, kui tekst on suurem kui pall
            sop_m = max(ss, slpt_suurus[1]) + 1
            Aken.sees_olevate_pallide_korgus = sop_m * (sop_korgus + 1)

            h += Aken.sees_olevate_pallide_korgus
            Aken.kuni_veidrusteni_korgus = h

        if osa == "kõik":  # Siit tuleb veidrustega tegelemine
            try:
                h += Aken.veidruste_korgus

            except (NameError, TypeError, AttributeError):
                Veidrused.optimaalne_veidruste_kombinatsioonid()
                Aken.veidruste_korgus = len(Veidrused.opt_list) * (Veidrused.v_l_ks[1] + 1) + 3

                h += Aken.veidruste_korgus

        return h

    @staticmethod
    def teksti_kirjutaja(tekst, suurus, alus, koord, varv, kast):
        # Tagastab lõpus teksti suurused
        Font = Satted.font(suurus)
        suurus = Font.size(tekst)
        if tekst in Satted.menuude_tekstid:
            koord = koord[0] - (suurus[0] + 1) // 2, koord[1]
            lisa = Satted.m_k_l  # Kasti külje kaugus tekstist
        else:
            lisa = Satted.t_k_l

        if kast:
            kast = [koord[0] - lisa, koord[1] - lisa, suurus[0] + 2 * lisa, suurus[1] + 2 * lisa]
            pg.draw.rect(alus, Satted.tabeli_kasti_varv, kast, 1)
            alus.blit(Font.render(tekst, True, varv), koord)
        else:
            if None not in [alus, varv, koord]:
                alus.blit(Font.render(tekst, True, varv), koord)
        return suurus


class Laud:
    """
    Lauaservad, laud, palliaugud, tabel - teeb need ja uuendab kui esile kutsutud.
    """

    def __init__(self):
        Laud.L_ps_suurus = [suurus - Satted.laua_porkeseina_vahe * 2 for suurus in Satted.laua_suurus]
        Laud.L_vahe = Satted.laua_vahe + Satted.laua_porkeseina_vahe
        Laud.laua_suurus = [suurus - Satted.laua_vahe * 2 for suurus in Laud.L_ps_suurus]

        self.raadius = Satted.musta_augu_raadius
        self.a_p = round(Satted.ruudu_diagonaali_ja_selle_siseringi_diameetri_erinevus(self.raadius))  # Augu parandus
        self.ava_parandus = self.raadius * 2 / Satted.ruutjuur_2
        self.auk_alumine = Laud.L_vahe + Laud.laua_suurus[1] + self.raadius - self.a_p
        self.auk_ulemine = Laud.L_vahe - self.raadius + self.a_p
        self.auk_vasak = Laud.L_vahe - self.raadius + self.a_p
        self.auk_keskmine = round(Laud.L_vahe + Laud.laua_suurus[0] * 0.5)
        self.auk_parem = Laud.L_vahe + Laud.laua_suurus[0] + self.raadius - self.a_p
        self.ordinaadid = self.auk_ulemine, self.auk_alumine
        self.abstsissid = self.auk_vasak, self.auk_keskmine, self.auk_parem

        self.musta_palli_koht = round(Laud.laua_suurus[0] * 0.75), round(Laud.laua_suurus[1] * 0.5)  # Alguses
        self.valge_palli_asukoht = round(Laud.laua_suurus[0] * 0.25), round(Laud.laua_suurus[1] * 0.5)  # Alguses

        self.vabaala_u_vasak = self.hulknurga_punkti_tegija(self.auk_vasak, self.auk_ulemine, "Tõus_1")
        self.vabaala_u_keskmine = self.hulknurga_punkti_tegija(self.auk_keskmine, self.auk_ulemine,
                                                               "Tasa_Ülemine")
        self.vabaala_u_parem = self.hulknurga_punkti_tegija(self.auk_parem, self.auk_ulemine, "Langus_2")
        self.vabaala_a_vasak = self.hulknurga_punkti_tegija(self.auk_vasak, self.auk_alumine, "Langus_3")
        self.vabaala_a_keskmine = self.hulknurga_punkti_tegija(self.auk_keskmine, self.auk_alumine,
                                                               "Tasa_Alumine")
        self.vabaala_a_parem = self.hulknurga_punkti_tegija(self.auk_parem, self.auk_alumine, "Tõus_4")

        self.vabaalad = [self.vabaala_u_vasak, self.vabaala_u_keskmine, self.vabaala_u_parem,
                         self.vabaala_a_vasak, self.vabaala_a_keskmine, self.vabaala_a_parem]
        self.augu_katted()
        self.mustade_aukude_kohad()

        terve_laud.add(Laua_Alus(self, self.vabaalad, self.augu_kattete_kohad))
        for musta_augu_asukoht in self.mustade_aukude_keskkohad:
            mustad_augud.add(Mustad_Augud(musta_augu_asukoht))
        koik_spraidid.add(terve_laud)
        koik_spraidid.add(mustad_augud)
        # See on, et ma saaksin piirata palli liikumist kasutades Lauaga seotud infot
        Fuusika.lauaga_seostaja(self)

    def servade_kaunistaja(self, kuhu):
        def ruut(asukohad):
            for asukoht in asukohad:
                x_r = asukoht[0]
                y_r = asukoht[1]
                asukoht = [(x_r, y_r + kls), (x_r + kls, y_r), (x_r, y_r - kls), (x_r - kls, y_r)]
                pg.draw.polygon(kuhu, Satted.augu_katte_varv, asukoht)

        def pilt(kau_ise, asukohad):
            kaunistuse_keskkoht = kau_ise.get_rect().center
            asukohad = list(map(lambda x_tuple: (x_tuple[0] - kaunistuse_keskkoht[0], x_tuple[1] -
                                                 kaunistuse_keskkoht[1]), asukohad))
            for asukoht in asukohad:
                kuhu.blit(kau_ise, asukoht)
                aacircle(kuhu, asukoht[0] + kaunistuse_keskkoht[0],
                         asukoht[1] + kaunistuse_keskkoht[1], round((kls + 10) * 0.5),
                         Satted.augu_katte_varv)
                aacircle(kuhu, asukoht[0] + kaunistuse_keskkoht[0],
                         asukoht[1] + kaunistuse_keskkoht[1], round((kls + 10) * 0.38461538462),
                         Satted.rombi_varv)

        # Kaunistuse laius, pildile tuleb lisa 10p ja ruudu oma on topelt, kuna see on ainult ühe külje oma.
        kls = Satted.kaunistuste_suurus
        kohad = []

        kaunistuste_summa = 6 * Satted.mitu_kaunistust_igas_vahes
        ulemine_vasak = Satted.mitu_kaunistust_igas_vahes
        ulemine_parem = Satted.mitu_kaunistust_igas_vahes * 2
        alumine_vasak = Satted.mitu_kaunistust_igas_vahes * 3
        alumine_parem = Satted.mitu_kaunistust_igas_vahes * 4
        vasakud = Satted.mitu_kaunistust_igas_vahes * 5
        paremad = Satted.mitu_kaunistust_igas_vahes * 6

        vastikused = 2 * self.ava_parandus + self.raadius - self.a_p
        delta_x = (self.laua_suurus[0] * 0.5 - vastikused) * 0.5 / Satted.mitu_kaunistust_igas_vahes

        y = parandaja = Satted.laua_porkeseina_vahe * 0.5
        delta_y = (self.laua_suurus[1] - 2 * self.ava_parandus) * 0.5 / Satted.mitu_kaunistust_igas_vahes

        try:
            kaunistus = pg.image.load(Satted.pilt)  # Satted.pilt
            kaunistus = pg.transform.scale(kaunistus, (kls + 10, kls + 10))
            Laud.Pilt = True
        except pg.error:
            Laud.Pilt = False

        for mitmes in range(kaunistuste_summa):
            if mitmes < ulemine_vasak:
                if mitmes == 0:
                    x = self.L_vahe + vastikused / 2
                    tegin = False
                x += delta_x
            elif mitmes < ulemine_parem:
                if mitmes == ulemine_vasak:
                    tegin = False
                    x = self.laua_suurus[0] * 0.5 + self.L_vahe + vastikused / 2
                x += delta_x
            elif mitmes < alumine_vasak:
                if mitmes == ulemine_parem:
                    tegin = False
                    x = self.L_vahe + vastikused / 2
                    y = Satted.laua_suurus[1] - parandaja
                x += delta_x
            elif mitmes < alumine_parem:
                if mitmes == alumine_vasak:
                    tegin = False
                    x = self.laua_suurus[0] * 0.5 + self.L_vahe + vastikused / 2
                x += delta_x
            elif mitmes < vasakud:
                if mitmes == alumine_parem:
                    tegin = False
                    x = parandaja
                    y = self.L_vahe + self.ava_parandus
                y += delta_y
            elif mitmes < paremad:
                if mitmes == vasakud:
                    tegin = False
                    x = Satted.laua_suurus[0] - parandaja
                    y = self.L_vahe + self.ava_parandus
                y += delta_y
            if tegin and not mitmes >= alumine_parem:
                x += delta_x
            elif tegin and mitmes > alumine_parem:
                y += delta_y
            tegin = True
            kohad.append((round(x), round(y)))

        if Laud.Pilt:
            pilt(kaunistus, kohad)
        else:
            ruut(kohad)

    def hulknurga_punkti_tegija(self, x, y, liik):
        # Vasak ja parem täistab abstsissi ja ülemine ja alumine ordinaati
        ringi_vasak = x - self.raadius + self.a_p
        ringi_parem = x + self.raadius - self.a_p
        ringi_ulemine = y - self.raadius + self.a_p
        ringi_alumine = y + self.raadius - self.a_p
        if "Tasa" in liik:
            laua_vasak = x - self.raadius - self.ava_parandus
            laua_parem = x + self.raadius + self.ava_parandus
            laua_ulemine = y - self.raadius + self.a_p
            laua_alumine = y + self.raadius - self.a_p
            if "Ülemine" in liik:
                Punkt_B = ringi_vasak, ringi_ulemine - self.a_p
                Punkt_C = ringi_parem, ringi_ulemine - self.a_p
                Punkt_A = laua_vasak + self.a_p, laua_alumine
                Punkt_D = laua_parem - self.a_p, laua_alumine
            elif "Alumine" in liik:
                Punkt_B = ringi_vasak, ringi_alumine + self.a_p
                Punkt_C = ringi_parem, ringi_alumine + self.a_p
                Punkt_A = laua_vasak + self.a_p, laua_ulemine
                Punkt_D = laua_parem - self.a_p, laua_ulemine
        else:
            if "Tõus" in liik:
                Punkt_A = ringi_parem, ringi_ulemine
                Punkt_B = ringi_vasak, ringi_alumine
                if "1" in liik:  # Ülemine Vasak
                    Punkt_C = Punkt_A[0], Punkt_B[1] + self.ava_parandus
                    Punkt_D = Punkt_A[0] + self.ava_parandus, Punkt_B[1]
                elif "4" in liik:  # Alumine Parem
                    Punkt_C = Punkt_B[0] - self.ava_parandus, Punkt_A[1]
                    Punkt_D = Punkt_B[0], Punkt_A[1] - self.ava_parandus
            elif "Langus" in liik:
                Punkt_A = ringi_vasak, ringi_ulemine
                Punkt_B = ringi_parem, ringi_alumine
                if "2" in liik:  # Ülemine Parem
                    Punkt_C = Punkt_A[0], Punkt_B[1] + self.ava_parandus
                    Punkt_D = Punkt_A[0] - self.ava_parandus, Punkt_B[1]
                elif "3" in liik:  # Alumine Vasak
                    Punkt_C = Punkt_B[0] + self.ava_parandus, Punkt_A[1]
                    Punkt_D = Punkt_B[0], Punkt_A[1] - self.ava_parandus
        punktid = Punkt_A, Punkt_B, Punkt_C, Punkt_D
        punktid = list(map(lambda punkt: (round(punkt[0]), round(punkt[1])), punktid))
        return punktid

    def augu_katted(self):
        kohad = []
        for ordinaat in range(len(self.ordinaadid)):
            if ordinaat == 1:
                ordinaat = Satted.laua_suurus[1]
            for x in range(len(self.abstsissid)):
                if ordinaat != 0:
                    x += 3
                if x == 1 or x == 4:
                    katte_koht = (self.vabaalad[x][0][0], ordinaat), self.vabaalad[x][0], self.vabaalad[x][3], \
                                 (self.vabaalad[x][3][0], ordinaat)
                    # Keskmisi teha oli kordades lihtsam...
                else:
                    if x == 0 or x == 3:  # Vasakud
                        x_akna_nurk = 0
                        laua_nurk = [self.vabaalad[0][0][0], 0]
                    elif x == 2 or x == 5:  # Paremad
                        x_akna_nurk = Satted.laua_suurus[0]
                        laua_nurk = [self.vabaalad[2][0][0], 0]

                    if ordinaat == 0:
                        laua_nurk[1] = (ordinaat + self.L_vahe)
                        y_akna_nurk = self.vabaalad[x][2][1]
                        x_akna_loppnurk = self.vabaalad[x][3][0]
                    elif ordinaat != 0:
                        laua_nurk[1] = (ordinaat - self.L_vahe)
                        y_akna_nurk = self.vabaalad[x][3][1]
                        x_akna_loppnurk = self.vabaalad[x][2][0]

                    katte_koht = (x_akna_nurk, ordinaat), \
                                 (x_akna_nurk, y_akna_nurk), \
                                 (laua_nurk[0], y_akna_nurk), tuple(laua_nurk), \
                                 (x_akna_loppnurk, laua_nurk[1]), \
                                 (x_akna_loppnurk, ordinaat)

                kohad.append(katte_koht)
        self.augu_kattete_kohad = kohad

    def mustade_aukude_kohad(self):
        self.mustade_aukude_keskkohad = []
        for ordinaat in self.ordinaadid:
            for abstsiss in self.abstsissid:
                u_muudatus = False
                a_muudatus = False
                if self.auk_keskmine == abstsiss:
                    if self.auk_ulemine == ordinaat:
                        ordinaat -= self.a_p + 1  # Plus üks tuleb, kuna self.a_p on ümardatud ja see ei sobi tolle
                        u_muudatus = True  # augu jaoks.
                    elif self.auk_alumine == ordinaat:
                        ordinaat += self.a_p
                        a_muudatus = True
                self.mustade_aukude_keskkohad.append((abstsiss, ordinaat))
                if u_muudatus:
                    ordinaat += self.a_p - 1
                elif a_muudatus:
                    ordinaat -= self.a_p
                # See on vajalik, et parandused ei mõjutaks teisi auke, mis neid ei vaja.

    def stardijoon(self, kuhu):
        def punkti_joonistaja(punkt, punkti_varv, suurus):
            aacircle(kuhu, punkt[0], punkt[1], suurus, punkti_varv)
            filled_circle(kuhu, punkt[0], punkt[1], suurus, punkti_varv)

        Musta_palli_tahistaja_suurus = 3
        Valge_palli_tahistaja_suurus = 1
        varvus = Satted.stardijoone_varv

        pg.draw.line(kuhu, varvus, (self.valge_palli_asukoht[0], 0), (self.valge_palli_asukoht[0], Laud.laua_suurus[1]))
        punkti_joonistaja(self.musta_palli_koht, varvus, Musta_palli_tahistaja_suurus)
        punkti_joonistaja(self.valge_palli_asukoht, varvus, Valge_palli_tahistaja_suurus)


class Laua_Alus(pg.sprite.Sprite, Laud):
    def __init__(self, klass, vabaalad, augu_kattete_kohad):
        pg.sprite.Sprite.__init__(self)
        # Teeb tabeli ja laua kõige alulisema kihi
        self.image = pg.Surface(ALUS.resolutsioon_f())
        self.image.fill(Satted.tabeli_varv)
        self.image = self.image.convert()
        # Teeb laua ääred
        self.laua_serv = pg.Surface(Satted.laua_suurus)
        self.laua_serv.fill(Satted.laua_serva_varv)
        self.laua_serv = self.laua_serv.convert()
        # Teeb laua porkeseinad
        self.laua_porkesein = pg.Surface(Laud.L_ps_suurus)
        self.laua_porkesein.fill(Satted.laua_porkeseina_varv)
        self.laua_porkesein = self.laua_porkesein.convert()
        # Teeb laua. Ainult selle osa, mille peal pallid mängu ajal on, v.a. kui need on sisse löödud.
        self.laud = pg.Surface(Laud.laua_suurus)
        self.laud.fill(Satted.laua_varv)
        self.laud = self.laud.convert()

        Laud.stardijoon(klass, self.laud)
        for katte in augu_kattete_kohad:
            pg.draw.polygon(self.laua_serv, Satted.augu_katte_varv, katte)
        Laud.servade_kaunistaja(klass, self.laua_serv)

        self.image.blit(self.laua_serv, (0, 0))
        self.image.blit(self.laua_porkesein, (Satted.laua_porkeseina_vahe, Satted.laua_porkeseina_vahe))
        self.image.blit(self.laud, (Laud.L_vahe, Laud.L_vahe))

        for ala in vabaalad:
            pg.draw.aalines(self.image, Satted.laua_varv, True, ala)
            pg.draw.polygon(self.image, Satted.laua_varv, ala)
        pg.draw.line(self.image, Satted.tabelit_eraldav_varv, (0, Satted.laua_suurus[1]), Satted.laua_suurus)
        self.rect = self.image.get_rect()


class Mustad_Augud(pg.sprite.Sprite):
    def __init__(self, musta_augu_asukoht):
        pg.sprite.Sprite.__init__(self)
        self.image, self.rect = ringi_joonistaja(Satted.musta_augu_raadius, Satted.augu_varv, None)
        self.rect.center = musta_augu_asukoht
        self.radius = Satted.musta_augu_raadius - Satted.palli_raadius + 2


def ringi_joonistaja(raadius, ringi_joonistaja_varv, ringi_joonistaja_tekst):
    # Teeb pallid ja ka mustad augud - kõik ringikujulised objektid
    ring = pg.Surface([2 * raadius + 1, 2 * raadius + 1], pg.SRCALPHA)
    numbri_aluse_varv = tuple(map(lambda x: 255 - x, Satted.palli_numbri_varv))
    # Joonistab palli
    if ringi_joonistaja_tekst and int(ringi_joonistaja_tekst) > 8 and int(ringi_joonistaja_tekst) != 16:
        aacircle(ring, raadius, raadius, raadius, numbri_aluse_varv)
        filled_circle(ring, raadius, raadius, raadius, numbri_aluse_varv)
        filled_circle(ring, raadius, raadius, round(raadius * Satted.palli_triibu_paksus),
                      ringi_joonistaja_varv)
    else:
        aacircle(ring, raadius, raadius, raadius, ringi_joonistaja_varv)
        filled_circle(ring, raadius, raadius, raadius, ringi_joonistaja_varv)

    # Paneb pallile numbri ja massi peale
    if ringi_joonistaja_tekst:
        number = int(ringi_joonistaja_tekst)
        if number != 16:
            mass = Satted.teiste_p_massid
            Font = Satted.font(round(raadius * 0.75))
            numbri_suurus = Font.size(str(number))
            palli_number = Font.render(str(number), True, Satted.palli_numbri_varv)
            numbri_aluse_raadius = round(max(Font.size("1")) * 1.1 // 2)

            filled_circle(ring, raadius, raadius, numbri_aluse_raadius, numbri_aluse_varv)
            kompensaator = round(numbri_suurus[0] / 2), round(numbri_suurus[1] / 2)
            ring.blit(palli_number, (raadius - kompensaator[0], raadius - kompensaator[1]))
        else:
            mass = Satted.valge_palli_m

    ringi_rect = ring.get_rect()
    if ringi_joonistaja_tekst:
        return ring, ringi_rect, number, mass
    else:
        return ring, ringi_rect


class Pallid:
    """
    Palli tüübid, pallide liikumine ja pallidega seotud uuendused - asukoha liigutamine
    """

    def __init__(self):
        ringruut = Satted.ruudu_diagonaali_ja_selle_siseringi_diameetri_erinevus(Satted.palli_raadius)
        self.palli_kaugus_teisest_reastajas = Satted.palli_raadius + Satted.palli_raadius - ringruut - ringruut

        self.musta_palli_koht_alguses = Laud.L_vahe + Laud.laua_suurus[0] * 0.75, \
                                        Laud.L_vahe + Laud.laua_suurus[1] * 0.5
        self.valge_palli_koht_alguses = Laud.L_vahe + Laud.laua_suurus[0] * 0.25, \
                                        Laud.L_vahe + Laud.laua_suurus[1] * 0.5

        self.pallide_kohad = []
        self.pallide_reastaja()
        i_pall = 0
        for palli_koht in self.pallide_kohad:
            palli_varv = Satted.palli_varvid[i_pall]
            i_pall += 1
            elus_pallid.add(Pall(palli_koht, palli_varv, i_pall))
        koik_spraidid.add(elus_pallid)

    def pallide_reastaja(self):
        def palli_koordinaadi_leidja(number, telg):
            ruutjuur_maagiline_number = sqrt(1.7)
            if telg == "x":
                m = 0
                telg = x_read
                palli_kaugus_teisest_reastajas = (self.palli_kaugus_teisest_reastajas + 1) * ruutjuur_maagiline_number
            if telg == "y":
                m = 1
                telg = y_read
                palli_kaugus_teisest_reastajas = (self.palli_kaugus_teisest_reastajas + 1) / ruutjuur_maagiline_number

            loendi_keskkoht = len(telg) // 2

            i = 0
            for rida in telg:
                if number in rida:
                    koordinaat = self.musta_palli_koht_alguses[m] + (i - loendi_keskkoht) \
                                 * palli_kaugus_teisest_reastajas
                    return round(koordinaat)
                i += 1

        x_rida_1 = [1]
        x_rida_2 = [4, 10]
        x_rida_3 = [14, 8, 6]
        x_rida_4 = [13, 15, 5, 11]
        x_rida_5 = [2, 12, 7, 3, 9]
        x_read = [x_rida_1, x_rida_2, x_rida_3, x_rida_4, x_rida_5]

        y_rida_1 = [2]
        y_rida_2 = [11]
        y_rida_3 = [6, 12]
        y_rida_4 = [10, 5]
        y_rida_5 = [1, 8, 7]
        y_rida_6 = [4, 15]
        y_rida_7 = [14, 3]
        y_rida_8 = [13]
        y_rida_9 = [9]
        y_read = [y_rida_1, y_rida_2, y_rida_3, y_rida_4, y_rida_5, y_rida_6, y_rida_7, y_rida_8, y_rida_9]

        for pall in range(len(Satted.palli_varvid)):
            pall += 1
            if pall == 16:
                x = round(self.valge_palli_koht_alguses[0])
                y = round(self.valge_palli_koht_alguses[1])
            else:
                x = palli_koordinaadi_leidja(pall, "x")
                y = palli_koordinaadi_leidja(pall, "y")

            koht = x, y
            self.pallide_kohad.append(koht)


class Pall(pg.sprite.Sprite):
    def __init__(self, palli_koht, palli_varv, palli_number):
        pg.sprite.Sprite.__init__(self)
        self.image, self.rect, self.number, self.mass = ringi_joonistaja(Satted.palli_raadius, palli_varv, palli_number)
        self.radius = Satted.palli_raadius
        self.rect.center = palli_koht
        self.x = palli_koht[0]
        self.y = palli_koht[1]
        self.ei_tohi = False
        self.joud = 0
        self.nurk = 0

    def update(self, *args):
        if count_nonzero(self.joud) > 0:
            if self.joud < 0:
                self.x = round(self.x)
                self.y = round(self.y)
                self.joud = 0
                return
            elif self.joud < Satted.meow / Satted.tsuk:  # Et aeglustumine oleks sujuvam
                self.joud /= 2
            self.x += sin(self.nurk) * self.joud
            self.y -= cos(self.nurk) * self.joud
            self.rect.center = round(self.x), round(self.y)
            Olukord.palli_porke_kontroll(False, self)
            Fuusika.laua_piirangud(self)  # Tegeleb ka aukudega
            # Aeglustamine toimub Olukord.uuenda


class Kii:
    """
    Kiiga seotud asjad - löömine, kii olemasolu ja abijooned.
    """
    pikkus = Satted.kii_pikkus
    klopsatus = 0

    def kii_kohtade_leidja(self):
        valge_pall = self.valge_pall
        v_p_koht = valge_pall.rect.center

        h_koht = self.hiire_koht
        muutused_kohas = h_koht[0] - v_p_koht[0], h_koht[1] - v_p_koht[1]
        max_kaugus = self.pikkus / 2
        laius = 7
        pikkus_vaike = laius // 2

        try:
            tous = muutused_kohas[1] / muutused_kohas[0]
            rist_tous = -1 / tous
        except ZeroDivisionError:
            if muutused_kohas[0] == 0:
                tous = "x = 0"  # -
            if muutused_kohas[1] == 0:
                tous = "y = 0"  # |

        if tous == "x = 0":
            muutus_Xs_vp = 0
            muutus_Ys_vp = pikkus_vaike
            muutus_Xs_p = 0  # _p tähistab pikkuse külje muutust
            muutus_Ys_p = self.pikkus
            muutus_Xs_l = laius // 2  # _l tähistab laiuse küle muutust
            muutus_Ys_l = 0
        elif tous == "y = 0":
            muutus_Xs_vp = pikkus_vaike
            muutus_Ys_vp = 0
            muutus_Xs_p = self.pikkus
            muutus_Ys_p = 0
            muutus_Xs_l = 0
            muutus_Ys_l = laius // 2
        else:
            muutus_Xs_vp = pikkus_vaike / sqrt(1 + tous ** 2)
            muutus_Ys_vp = muutus_Xs_vp * tous
            muutus_Xs_p = self.pikkus / sqrt(1 + tous ** 2)
            muutus_Ys_p = muutus_Xs_p * tous
            muutus_Xs_l = (laius / sqrt(1 + rist_tous ** 2)) / 2
            muutus_Ys_l = muutus_Xs_l * rist_tous

        x = h_koht[0]
        y = h_koht[1]
        klops = sisendid["hiire_klõps"]
        if muutused_kohas[0] ** 2 + muutused_kohas[1] ** 2 > max_kaugus ** 2:
            x, y = self.kii_asukoha_fikseerija(tous, muutused_kohas, max_kaugus)
            muutused_kohas = x - v_p_koht[0], y - v_p_koht[1]
        elif muutused_kohas[0] ** 2 + muutused_kohas[1] ** 2 < Satted.palli_raadius ** 2:
            x, y = self.kii_asukoha_fikseerija(tous, muutused_kohas, Satted.palli_raadius)
            muutused_kohas = x - v_p_koht[0], y - v_p_koht[1]
            if klops == 1 and klops != Kii.klopsatus and mangu_algus:
                valge_pall.kill()
                valge_pall.add(valge_pall_sees)
                Kii.klopsatus = klops
                return

        osa_max_joust = (muutused_kohas[0] ** 2 + muutused_kohas[1] ** 2) / max_kaugus ** 2
        joud = Satted.max_joud * sqrt(osa_max_joust) / Satted.tsuk
        self.abijoone_tegija(joud, tous, muutused_kohas)
        hiire_kontroll = sisendid["hiire_koht"][1]
        if klops == 1 and klops != Kii.klopsatus and hiire_kontroll <= Satted.laua_suurus[1]:
            x, y = self.kii_asukoha_fikseerija(tous, muutused_kohas, Satted.palli_raadius)
            if (muutused_kohas[0] ** 2 + muutused_kohas[1] ** 2) > Satted.palli_raadius ** 2 + 1:
                valge_pall.nurk = Fuusika.jou_suunaja(v_p_koht, (x, y))
                valge_pall.joud = joud
                Olukord.puude = False
        Kii.klopsatus = klops

        # Et kii oleks ka vasakul pool, ja ka üleval 181°-360°
        if muutused_kohas[0] < 0 or (muutused_kohas[1] < 0 == muutused_kohas[0]):
            muutus_Xs_p *= -1
            muutus_Xs_vp *= -1
            muutus_Xs_l *= -1
            muutus_Ys_p *= -1
            muutus_Ys_vp *= -1
            muutus_Ys_l *= -1

        punktA = x - muutus_Xs_l, y - muutus_Ys_l
        punktB = x + muutus_Xs_l, y + muutus_Ys_l
        punktC = x + muutus_Xs_p + muutus_Xs_l, y + muutus_Ys_p + muutus_Ys_l
        punktD = x + muutus_Xs_p - muutus_Xs_l, y + muutus_Ys_p - muutus_Ys_l
        punktC_ots = x + muutus_Xs_vp + muutus_Xs_l, y + muutus_Ys_vp + muutus_Ys_l
        punktD_ots = x + muutus_Xs_vp - muutus_Xs_l, y + muutus_Ys_vp - muutus_Ys_l

        self.kii_otsa_koht = [punktA, punktB, punktC_ots, punktD_ots]
        self.kii_varda_koht = [punktA, punktB, punktC, punktD]

        if (self.kii_varda_koht[3][1] or self.kii_varda_koht[2][1]) >= Satted.laua_suurus[1]:
            kii_osad = [self.kii_otsa_koht, self.kii_varda_koht]
            for kii_osa in kii_osad:
                for i in range(len(kii_osa)):
                    punkt = kii_osa[i]
                    if punkt[1] >= Satted.laua_suurus[1]:
                        y = Satted.laua_suurus[1] - 1
                        try:
                            c = punkt[1] - tous * punkt[0]
                            x = (y - c) / tous
                        except TypeError:
                            x = punkt[0]
                        finally:
                            kii_osa[i] = x, y

    def kii_asukoha_fikseerija(self, tous, kohamuutus, kaugus):
        if tous == "x = 0":
            x = 0
            y = kaugus
        elif tous == "y = 0":
            x = kaugus
            y = 0
        else:
            x = kaugus / sqrt(1 + tous ** 2)
            y = x * tous
        if kohamuutus[0] < 0 or (kohamuutus[1] < 0 == kohamuutus[0]):
            x *= -1
            y *= -1
        x += self.valge_pall.rect.centerx
        y += self.valge_pall.rect.centery

        return x, y

    def abijoone_tegija(self, joud, tous, kohamuutus):
        abijoone_pikkus = (joud * Satted.tsuk) ** 2 / 2 / Satted.meow
        kohamuutus = tuple(map(lambda x: x * -1, kohamuutus))
        alg_x, alg_y = self.valge_pall.rect.center
        lopp_x, lopp_y = self.kii_asukoha_fikseerija(tous, kohamuutus, abijoone_pikkus)

        if lopp_y >= Satted.laua_suurus[1]:
            kogu_vektor = lopp_x - alg_x, lopp_y - alg_y
            # Üleliigse vektori teljed
            u_v_d_y = lopp_y - Satted.laua_suurus[1] + 1
            try:
                u_v_d_x = u_v_d_y / (kogu_vektor[1] / kogu_vektor[0])
            except ZeroDivisionError:
                u_v_d_x = 0

            lopp_x = alg_x + kogu_vektor[0] - u_v_d_x
            lopp_y = alg_y + kogu_vektor[1] - u_v_d_y

        pg.draw.aaline(ALUS.aken, Satted.stardijoone_varv, (alg_x, alg_y), (lopp_x, lopp_y))

    def __init__(self):
        self.hiire_koht = sisendid["hiire_koht"]
        self.valge_pall = elus_pallid.sprites()[-1]
        self.kii_kohtade_leidja()
        try:
            pg.draw.polygon(ALUS.aken, Satted.kii_varv, self.kii_varda_koht)
            pg.draw.polygon(ALUS.aken, Satted.augu_katte_varv, self.kii_otsa_koht)
        except AttributeError:
            return


# noinspection PyTypeChecker
class Fuusika:
    """
    Tegeleb füüsikaga - liikumised, põrked.

    Selles programmis on päriselu füüsikast erinevused:
        1. Pallid edastavad jõudu täiuslikult.
        2. Kiirust muudab ainult hõõrdejõud.
        3. Hõõrdejõud on pidev olenemata palli kiirusest.
    """

    @staticmethod
    def jou_suunaja(keha_1_koht, keha_2_koht):
        """
        Keha 1 on vastuvõtja (lõpp) ja keha 2 on jõu edastaja (algus)

        Math moodulis on 0° üles, mitte paremale, see lihtsalt vahetab koosinuse ja sinuse kasutuse
         kordinaatteljestikus.
        (cos = y/c, mitte x/c ja sin = x/c, mitte y/c, muu on täpselt sama: cos(90°) = 1 ja sin(0°) = 0,
        cos on ikkagi lähiskülg/hüpotenüüs ja sin on vastaskülg/hüpotenüüs)
        Nurga leidmiseks ma kasutan ordinaadi muutust, kuna arkuskoosinus annab positiivsed nurgad
        (0° - 180°, arcsin annab -90° - 90°).
        Et teada kas nurk peaks olema 180° -st 360° -ni võtan arvesse abstsissi muutust,
        kui see on positiivne, siis see peaks olema paremal, (0° - 180°) või negatiivne, ehk vasakul (180° - 360°).

        Sellega tuleb kahjuks probleeme, kuna pygame-s on ordinaadid koordinaatteljestikul tagurpidi.
        (pygame-s y = 2 on y = -2)

        Probleemi lahendamiseks kasutan ma muutustevalemit tagurpidi, ehk delta = algus-lõpp, mitte lõpp-algus.
        See muudab ka abstsissi, ehk pean arvestama, et parem ja vasak on tagurpidi.
        Ehk kui abstsiss on negatiivne, siis nurk peaks olema paremal ja kui positiivne, siis vasakul.

        """
        if not keha_1_koht or not keha_2_koht:
            keha_2_koht = next(koht for koht in [keha_1_koht, keha_2_koht] if koht is not None)
            keha_1_koht = (0, 0)
        kohamuutus = keha_2_koht[0] - keha_1_koht[0], keha_2_koht[1] - keha_1_koht[1]
        kaugus = hypot(kohamuutus[0], kohamuutus[1])
        if kaugus == 0:  # Lihtsalt, et mäng kokku ei paneks, kui selline asi juhtuma peaks
            return 0
        if kohamuutus[0] < 0:
            nurk = acos(kohamuutus[1] / kaugus)
        else:
            nurk = 0 - acos(kohamuutus[1] / kaugus)
        return nurk

    def palli_porgete_jamaja(self, pall_1, pall_2):
        def joud_alla_nulli(pall):
            pall.joud = abs(pall.joud)
            pall.nurk += pi
            pall_1.nurk %= tau

        pall_1.nurk %= tau
        pall_2.nurk %= tau
        if not hypot((pall_1.rect.centerx - pall_2.rect.centerx), pall_1.rect.centery - pall_2.rect.centery) <= \
               Satted.palli_raadius * 2 + 1:
            return
        Olukord.puude = True

        Veidrused.pl_pall = pall_2
        Veidrused.kaivita_ehmataja = True
        Veidrused.veidruse_aktiveerija("teleporteeruja(pall)", None)
        if Veidrused.teleport:
            return

        # See on lihtsalt selleks, et tuleb täpsem nurk ja et palli välja saada teise seest
        self.pallid_uksteises(pall_1, pall_2, False)
        # Kordaja -1 on koordinaatide muutuste ees, et tegeleda jõu suunaja probleemi lahendusega
        suund = self.jou_suunaja(pall_2.rect.center, pall_1.rect.center)
        jou_muut = abs(cos(suund - pall_1.nurk) * pall_1.joud)
        pall_2_koordinaatide_muutus = (-1 * (sin(pall_2.nurk) * pall_2.joud + sin(suund) * jou_muut),
                                       (cos(pall_2.nurk) * pall_2.joud + cos(suund) * jou_muut))
        pall_2.nurk = self.jou_suunaja(pall_2_koordinaatide_muutus, None)

        delta_nurk = 2 * pall_1.nurk - suund
        delta_nurk %= tau
        p_1_koord_muut = (-1 * (sin(pall_1.nurk) * pall_1.joud + sin(delta_nurk) * jou_muut),
                          (cos(pall_1.nurk) * pall_1.joud + cos(delta_nurk) * jou_muut))
        pall_1.nurk = self.jou_suunaja(p_1_koord_muut, None)

        pall_1.joud -= jou_muut * pall_2.mass / pall_1.mass
        pall_2.joud += jou_muut * pall_1.mass / pall_2.mass
        if pall_1.joud < 0:
            joud_alla_nulli(pall_1)
        if pall_2.joud < 0:
            joud_alla_nulli(pall_2)

        helitugevus = sqrt(jou_muut / (Satted.max_joud / Satted.tsuk))
        Helid.porke_erandjuhum(helitugevus)

    def pallid_uksteises(self, p_1, p_2, paigal):
        """
        Kui pallid on üksteises, siis tõukab need üksteisest eemale
        """
        p_1.x = p_1.rect.centerx
        p_2.x = p_2.rect.centerx
        p_1.y = p_1.rect.centery
        p_2.y = p_2.rect.centery

        delta_x = p_1.x - p_2.x
        delta_y = p_1.y - p_2.y
        kaugus = hypot(delta_x, delta_y)
        suund = self.jou_suunaja((delta_x, delta_y), None)

        if paigal:
            # See suund on p_1 -st p_2 -ni, jõu suunaja probleemi lahenduse tõttu
            touge = (Satted.palli_raadius * 2 + 1 - kaugus) / 2
            p_1.x -= sin(suund) * touge
            p_1.y += cos(suund) * touge
            p_2.x += sin(suund) * touge
            p_2.y -= cos(suund) * touge
            p_2.rect.center = round(p_2.x), round(p_2.y)
        else:
            touge = Satted.palli_raadius * 2 + 1 - kaugus
            p_1.x -= sin(suund) * touge
            p_1.y += cos(suund) * touge

        p_1.rect.center = round(p_1.x), round(p_1.y)

    @staticmethod
    def lauaga_seostaja(laud_cls):
        Fuusika.vabaalad = laud_cls.vabaalad
        Fuusika.valge_palli_algkoht = laud_cls.valge_palli_asukoht
        # Seostab ka veidrustega
        Veidrused.vabaalad = laud_cls.vabaalad

    @staticmethod
    def lisa_musta_auguga_porge(pall):
        # Mängija tõttu tekkinud must auk, kui pole tekkinud, siis üks enne seda
        if pg.sprite.collide_circle(mustad_augud.sprites()[-1], pall):
            Fuusika.eemalda_pall(pall)

    @staticmethod
    def eemalda_pall(pall):
        Helid.heli_mangija("pall_sisse")
        pall.kill()
        if pall.number == 16:
            Olukord.valge_pall_musta_auku(pall)
        else:
            def lopeta_funkt():
                global lopeta
                lopeta = True

            pall.add(sees_pallid)
            if len(elus_pallid) > 1:
                if pall.number == 8:
                    Olukord.must_pall_sees = True
                    Veidrused.veidruse_aktiveerija("must_auk()", lopeta_funkt)
            else:
                Olukord.must_pall_sees = True
                lopeta_funkt()

    @staticmethod
    def laua_piirangud(pall):
        """
        Täiesti uus laua piirangutega tegelev funktsioon, kuna eelmine tegeles aukudega halvasti.
        Põrkeseinad said ilusti tehtud, aga selle töötamisviis tekitas probleeme auguseinade lahendustega.
        Auguseina lahendus ei töödanud piisavalt hästi nagunii, kuna vahetevahel see ei tuvastanud põrget.
        Selle lahendamisel kasutasin:
        https://codereview.stackexchange.com/questions/86421/line-segment-to-circle-collision-algorithm
        """

        def kosmose_tegeleja(kulg, pool):
            pall.nurk %= tau
            if pool == "x":
                delta_x = kulg - rect.centerx
                try:
                    delta_y = delta_x / tan(pall.nurk)
                except ZeroDivisionError:
                    delta_y = 0
            else:
                delta_y = kulg - rect.centery
                delta_x = delta_y * tan(pall.nurk)

            kaugus = hypot(delta_x, delta_y) + r * 2
            pall.x -= sin(pall.nurk) * kaugus
            pall.y += cos(pall.nurk) * kaugus

            pall.x = round(pall.x)
            pall.y = round(pall.y)
            pall.center = pall.x, pall.y

        def musta_auku():
            # Vaatab kas pall läks musta auku või mitte, siis tegeleb vastavalt
            for auk in mustad_augud:
                porge = pg.sprite.collide_circle(auk, pall)
                if porge:
                    Fuusika.eemalda_pall(pall)
                    return True
            return False

        """
        Siin on laudu moodustavate puntkide kohta info. On olemas lõigu alguspunkt ja lõpupunkt.
        Kasutatud lühendite kohta info:
        ps = põrkesein
        as = augusein
        v = vasak
        p = parem
        u = ülemine
        a = alumine
        k = keskmine
        ls = lisasein, sein, mis augu taga on, mida pall arvatavasti kunagi ei puuduta. Kasutan seda, et seinu testida
        """
        V = Fuusika.vabaalad
        v_ps = V[0][2], V[3][3]
        p_ps = V[2][2], V[5][3]
        u_v_ps = V[0][3], V[1][0]
        u_p_ps = V[1][3], V[2][3]
        a_v_ps = V[3][2], V[4][0]
        a_p_ps = V[4][3], V[5][2]
        u_v_v_as = V[0][1], V[0][2]
        u_v_p_as = V[0][0], V[0][3]
        u_k_v_as = V[1][0], V[1][1]
        u_k_p_as = V[1][2], V[1][3]
        u_p_v_as = V[2][3], V[2][0]
        u_p_p_as = V[2][1], V[2][2]
        a_v_v_as = V[3][0], V[3][3]
        a_v_p_as = V[3][1], V[3][2]
        a_k_v_as = V[4][0], V[4][1]
        a_k_p_as = V[4][2], V[4][3]
        a_p_v_as = V[5][2], V[5][1]
        a_p_p_as = V[5][3], V[5][0]
        u_v_ls = V[0][0], V[0][1]
        u_k_ls = V[1][1], V[1][2]
        u_p_ls = V[2][0], V[2][1]
        a_v_ls = V[3][0], V[3][1]
        a_k_ls = V[4][1], V[4][2]
        a_p_ls = V[5][0], V[5][1]
        seinad = [v_ps, p_ps, u_v_ps, u_p_ps, a_v_ps, a_p_ps, u_v_v_as, u_v_p_as, u_k_v_as, u_k_p_as, u_p_v_as,
                  u_p_p_as, a_v_v_as, a_v_p_as, a_k_v_as, a_k_p_as, a_p_v_as, a_p_p_as, u_v_ls, u_k_ls, u_p_ls, a_v_ls,
                  a_k_ls, a_p_ls]

        # Palli info
        palli_keskkoht = array((pall.x, pall.y))
        rect = pall.rect
        F = pall.joud
        r = Satted.palli_raadius
        f = ceil(F) + r * 2
        # Viimane lubatud mõõdapanek
        vlmp = Satted.ruudu_diagonaali_ja_selle_siseringi_diameetri_erinevus(r)

        # Ohutu
        if (rect.centerx in range(V[0][2][0] + f, V[2][2][0] - f) and
                rect.centery in range(V[2][3][1] + f, V[5][2][1] - f)):
            Fuusika.lisa_musta_auguga_porge(pall)
            return

        if musta_auku():
            return

            # Pall "kosmoses"
        if rect.right < V[0][1][0]:
            kosmose_tegeleja(V[0][2][0], "x")
        elif rect.left > V[2][1][0]:
            kosmose_tegeleja(V[2][2][0], "x")
        elif rect.bottom < V[2][0][1]:
            kosmose_tegeleja(V[2][3][1], "y")
        elif rect.top > V[5][1][1]:
            kosmose_tegeleja(V[5][2][1], "y")

        for sein in seinad:
            # Seina kohta info
            alg_punkt = array(sein[0])
            lopp_punkt = array(sein[1])
            seina_vektor = lopp_punkt - alg_punkt
            seina_hupot = hypot(*seina_vektor)
            seina_uhikvektor = seina_vektor / seina_hupot

            v_seinast_pallini = palli_keskkoht - alg_punkt
            # Seina algpunktist pallini oleva vektori ja seina vektori suunaühisus
            # Ja palju pall sellest mööda paneb
            skalaarkorrutis = dot(seina_uhikvektor, v_seinast_pallini)
            if not -vlmp <= skalaarkorrutis <= hypot(*seina_vektor) + vlmp:
                continue

            porkepunkt = skalaarkorrutis * seina_uhikvektor + alg_punkt
            v_porkepunktist_pallini = porkepunkt - palli_keskkoht
            kaugus_porkepunktist = hypot(*v_porkepunktist_pallini)
            if kaugus_porkepunktist <= r:
                Helid.heli_mangija("lauaga_porge")
                palli_r_kaugus_pp = r - kaugus_porkepunktist
                nurk_porkepunktist_pallini = Fuusika.jou_suunaja(tuple(v_porkepunktist_pallini), None)
                pall.x += sin(nurk_porkepunktist_pallini) * palli_r_kaugus_pp
                pall.y -= cos(nurk_porkepunktist_pallini) * palli_r_kaugus_pp
                rect.center = round(pall.x), round(pall.y)

                koik_spraidid.draw(ALUS.aken)
                pg.display.update()

                if musta_auku():
                    return

                laua_nurk = Fuusika.jou_suunaja(tuple(seina_vektor), None)
                pall.joud -= abs(Satted.meow * 3 / Satted.tsuk * sin(laua_nurk - pall.nurk))
                pall.nurk = (2 * laua_nurk - pall.nurk) % tau


class Olukord:
    """
    Tegeleb sündmustega, kontrollib, mis toimub, mis toimunud on, mis peaks juhtuma,
    kas kõik on korras ja käitub vastavalt.
    """
    elud = Satted.elude_kogus
    must_pall_sees = False
    palju_magada_vaja = 0
    uneaeg = None
    mangu_alguse_akna_muude = False
    puude = True
    # Kas ta kustutab ära parema või vasaku elusümboli
    e_s_k = (-1, 0)

    @staticmethod
    def staatuse_leidja(mille_staatus):
        return next(staatus for staatus in tuple(Veidrused.veidruste_lulitid.values()) if staatus[0] == mille_staatus)

    @staticmethod
    def tabel():
        def sees_olevad_pallid():
            ss = Satted.spss
            try:
                # Palju palle on vaja lisada sees löödud pallide hulka.
                lisada_vaja = len(sees_pallid) - Olukord.lisatud_tabelisse
            except (NameError, TypeError, AttributeError):
                tekst = Satted.tabeli_slp_tekst
                ts = Satted.tabeli_sop_fondi_suurus
                Olukord.lisatud_tabelisse = 0
                lisada_vaja = len(sees_pallid) - Olukord.lisatud_tabelisse
                if not Satted.eludeta_mang:
                    elude_joonistaja()

                # Paneb palli või teksti, oleneb kumb väiksem on, teise keskele
                lisa = (ss - Satted.font(ts).size(tekst)[1]) // 2
                if lisa < 0:
                    Olukord.sop_korgus = tabeli_algkoht[1] - lisa
                    lisa = 0
                else:
                    Olukord.sop_korgus = tabeli_algkoht[1]

                koht = tabeli_algkoht[0], tabeli_algkoht[1] + lisa
                Olukord.sop_laius = koht[0] + Aken.teksti_kirjutaja(tekst, ts, laud, koht, Satted.tabeli_teksti_varv,
                                                                    False)[0]

            for i in range(lisada_vaja):
                sees_olev_pall = sees_pallid.sprites()[Olukord.lisatud_tabelisse]
                if sees_olev_pall.rect.width < ss:
                    sees_olev_pall.image = pg.transform.scale2x(sees_olev_pall.image)
                sees_olev_pall.image = pg.transform.smoothscale(sees_olev_pall.image, (ss, ss))
                sees_olev_pall.rect = sees_olev_pall.image.get_rect()
                koik_spraidid.add(sees_olev_pall)

                Olukord.sop_laius += 1
                sees_olev_pall.rect.topleft = Olukord.sop_laius, Olukord.sop_korgus
                Olukord.sop_laius += ss

                if Olukord.sop_laius > Satted.laua_laius:
                    Olukord.sop_laius = 0
                    Olukord.sop_korgus += ss

                Olukord.lisatud_tabelisse += 1

        def veidrused_tabelis():
            def varvimuutja(olek, koord):
                # Puhastab koha
                pg.draw.rect(laud, Satted.tabeli_varv, [koord, Veidrused.v_l_ks])

                koord = array(koord) + Satted.t_k_l
                if olek:
                    olek = Satted.v_l_t[0]
                    oleku_varv = Satted.luliti_sees_varv
                else:
                    olek = Satted.v_l_t[1]
                    oleku_varv = Satted.tabeli_teksti_varv

                Aken.teksti_kirjutaja(olek, Satted.tabeli_fondi_suurus, laud, koord, oleku_varv, True)

            try:
                veid_klops = sisendid["hiire_klõps"]
                """
                Avastasin, et kui kopeerida (panna element omastama teist elementi) listi või sõnaraamatut, siis 
                muutused sinna muudavad ka kopeeritut.
                """
                v_l = Veidrused.veidruste_lulitid
                if len(v_l) == 0:  # Vajalik lülitite tabelisse panemiseks ja eesmärkidega sidumiseks
                    Olukord.veid_klops = 0
                    raise ValueError("Veidrused pole tabelis")

                if veid_klops == 1 and veid_klops != Olukord.veid_klops:
                    hiire_koht = sisendid["hiire_koht"]
                    x = hiire_koht[0]
                    y = hiire_koht[1]

                    if y > Satted.laua_suurus[1]:
                        for nupp in v_l:
                            if x in range(nupp[0][0], nupp[1][0]) and y in range(nupp[0][1], nupp[1][1]):
                                if v_l[nupp][0] == "must_auk()" and Olukord.must_pall_sees:
                                    continue
                                else:
                                    v_l[nupp] = v_l[nupp][0], not v_l[nupp][1]
                                    varvimuutja(v_l[nupp][1], nupp[0])
                Olukord.veid_klops = veid_klops

            except ValueError:
                def veidruse_panek(veid, v_x, v_koht):
                    # Paneb veidruse teksti tabelisse ja annab programmile infot, et ta teaks kuhu lüliti panna
                    v_x += Aken.teksti_kirjutaja(veid, fs, laud, v_koht, varv, False)[0] + kastivahe
                    v_koht = v_x, veidrus_y
                    return v_x, v_koht

                def luliti_panek():
                    # Lüliti panemine tabelisse ja selle kohta info salvestamine
                    nuppu_koord = tuple(array(koht) - Satted.t_k_l), tuple(array(koht) + l_k_s - Satted.t_k_l)
                    Veidrused.veidruste_lulitid[nuppu_koord] = veidrus, False
                    Aken.teksti_kirjutaja(l_t, fs, laud, koht, varv, True)

                # Et pallide ja veidruste värgid kokku ei puutuks
                veidrus_x = tabeli_algkoht[0]
                veidrus_y = tabeli_algkoht[1] + Aken.sees_olevate_pallide_korgus + Satted.t_k_l
                # Lüliti kasti suurused
                l_k_s = array(Veidrused.v_l_ks)
                kastivahe = Satted.t_k_l + Veidrused.k_t_v
                # Et lühendada teksti kirjutaja suurust
                fs = Satted.tabeli_fondi_suurus
                varv = Satted.tabeli_teksti_varv
                l_t = Satted.v_l_t[1]

                for v_rida in Veidrused.opt_list:
                    koht = veidrus_x, veidrus_y
                    if type(v_rida) == tuple:
                        for v in v_rida:
                            veidrus_x, koht = veidruse_panek(v, veidrus_x, koht)

                            veidrus = Veidrused.veidrused[v]
                            luliti_panek()

                            veidrus_x = Satted.laua_laius // 2
                            koht = veidrus_x, veidrus_y
                    else:
                        veidrus_x, koht = veidruse_panek(v_rida, veidrus_x, koht)

                        veidrus = Veidrused.veidrused[v_rida]
                        luliti_panek()

                    veidrus_x = tabeli_algkoht[0]
                    veidrus_y += l_k_s[1] + 1

        def elude_joonistaja():
            nonlocal tabeli_algkoht
            sumbol_image = Olukord.sumboli_tegija(Satted.elusumboli_varv)

            Olukord.elusumboli_laius = Satted.elusumboli_kulg + 3
            max_sumboleid_reas = Satted.laua_laius // Olukord.elusumboli_laius
            max_sumboli_laius = (Satted.laua_laius - max_sumboleid_reas * Olukord.elusumboli_laius) // 2

            ridu = Satted.elude_kogus // max_sumboleid_reas + 1
            ulejaak = Satted.elude_kogus % max_sumboleid_reas
            elu_sumbolite_kohad = []

            pikkus = tabeli_algkoht[1]
            for i in range(ridu - 1):
                laius = max_sumboli_laius
                for elu in range(max_sumboleid_reas):
                    elu_sumbolite_kohad.append((laius, pikkus))
                    laud.blit(sumbol_image, (laius, pikkus))
                    laius += Olukord.elusumboli_laius
                pikkus += Satted.elusumboli_kulg + 1
            laius = (Satted.laua_laius - ulejaak * Olukord.elusumboli_laius) // 2
            for i in range(ulejaak):
                elu_sumbolite_kohad.append((laius, pikkus))
                laud.blit(sumbol_image, (laius, pikkus))
                laius += Olukord.elusumboli_laius

            pikkus += Satted.elusumboli_kulg + 1
            tabeli_algkoht = Satted.aarekaugus, pikkus
            Olukord.elu_sumbolite_kohad = elu_sumbolite_kohad

        tabeli_algkoht = Satted.aarekaugus, Satted.laua_suurus[1] + 2
        laud = terve_laud.sprites()[0].image

        sees_olevad_pallid()
        veidrused_tabelis()

    @staticmethod
    def sumboli_tegija(sumboli_varv):
        def sumboli_ringid(x, y):
            aacircle(elu_sumbol, x, y, r, sumboli_varv)
            filled_circle(elu_sumbol, x, y, r, sumboli_varv)

        def hulknurkija(ala):
            pg.draw.aalines(elu_sumbol, sumboli_varv, True, ala)
            pg.draw.polygon(elu_sumbol, sumboli_varv, ala)

        # s_l on sumboli laius ja s_p on sumboli pikkus
        s_l = Satted.elusumboli_kulg
        s_p = round(s_l / 400 * 399)
        elu_sumbol = pg.Surface([s_l, s_p], pg.SRCALPHA)

        r = s_l // 4
        ringide_keskpunktid = [(s_l // 4, s_l // 4), (round(s_l / 800 * 599), s_l // 4)]
        for keskpunkt in ringide_keskpunktid:
            sumboli_ringid(keskpunkt[0], keskpunkt[1])

        ul_hulknurk = [(s_l * 0.45, s_l / 10), (s_l * 0.45, s_l * 0.40125), (s_l * 0.55, s_l * 0.40125),
                       (s_l * 0.55, s_l / 10), (s_l / 2, s_l * 0.1675)]
        al_hulknurk = [(s_l / 20, s_l * 0.4), (s_l / 2, s_p), (s_l * 0.94875, s_l * 0.4)]
        hulknurgad = al_hulknurk, ul_hulknurk
        for hulknurk in hulknurgad:
            hulknurkija(hulknurk)

        return elu_sumbol

    @staticmethod
    def valge_pall_augus():
        def palli_panek():
            pall.rect.center = hiire_koht

            for pall_2 in elus_pallid:
                if pg.sprite.collide_circle(pall, pall_2):
                    return
                else:
                    continue

            valge_pall_sees.draw(ALUS.aken)
            klops = vpafk_sisendid["hiire_klõps"]
            if klops == 1 and klops != Kii.klopsatus:
                pall.x = pall.rect.centerx
                pall.y = pall.rect.centery
                pall.joud = 0
                pall.kill()
                pall.add(elus_pallid)
                pall.add(koik_spraidid)
            Kii.klopsatus = klops

        # Sisendid, mis on valge pall augus funktsiooni kasutuses
        vpafk_sisendid = Olukord.sisendid()
        hiire_koht = vpafk_sisendid["hiire_koht"]
        V = Fuusika.vabaalad
        r = Satted.palli_raadius + 1
        pall = valge_pall_sees.sprites()[-1]

        if not mangu_algus:
            if (hiire_koht[0] in range(V[0][2][0] + r, V[2][2][0] - r) and
                    hiire_koht[1] in range(V[2][3][1] + r, V[5][2][1] - r)):
                palli_panek()
        else:
            v_p_alg_x = Fuusika.valge_palli_algkoht[0] + Satted.laua_porkeseina_vahe + Satted.laua_vahe
            if (hiire_koht[0] in range(V[0][2][0] + r, v_p_alg_x) and
                    hiire_koht[1] in range(V[2][3][1] + r, V[5][2][1] - r)):
                palli_panek()

    @staticmethod
    def palli_porke_kontroll(p_paigal, K_pall):
        if not p_paigal:
            for pall in elus_pallid:
                if pall == K_pall:
                    continue
                if pg.sprite.collide_circle(K_pall, pall):
                    Fuusika().palli_porgete_jamaja(K_pall, pall)

        # Tegeleb olukorraga, kui pallid on üksteise sees
        for (m1, p_1) in enumerate(elus_pallid):
            if p_1.joud != 0:
                continue
            for m2 in range(m1 + 1, len(elus_pallid)):
                p_2 = elus_pallid.sprites()[m2]
                if p_2.joud != 0:
                    continue
                if pg.sprite.collide_circle(p_1, p_2):
                    Fuusika().pallid_uksteises(p_1, p_2, True)

    def uuenda(self):  # Uuendab akent
        global pildi_teade, lopeta
        if not Laud.Pilt:
            if not pildi_teade:
                Aken.teate_esiletooja("Tahetud kaunistust ei leitud.\nNeed asendatakse rombidega.")
                pildi_teade = True

        p_paigal = self.pallid_paigal()  # On tõene, kui pallid on paigal
        self.tabel()
        koik_spraidid.draw(ALUS.aken)
        if not p_paigal:
            for i in range(Satted.tsuk):
                elus_pallid.update()
            for pall in elus_pallid:
                if pall.joud > 0:
                    pall.joud -= Satted.meow / Satted.tsuk
                else:
                    continue
        elif len(valge_pall_sees) > 0:
            if self.palju_magada_vaja > 0:
                Olukord.palju_magada_vaja -= time.time() - self.uneaeg
                if self.palju_magada_vaja > 0:
                    time.sleep(self.palju_magada_vaja)
            Olukord.palju_magada_vaja = 0
            self.valge_pall_augus()
        else:
            self.palli_porke_kontroll(p_paigal, None)
            Kii()

        p_paigal = self.pallid_paigal()
        if not Satted.eludeta_mang:
            if p_paigal and not Olukord.puude:
                Olukord.puude = True
                self.vahenda_elu()
            if Olukord.elud == 0:
                lopeta = True

        if not lopeta:
            if Veidrused.kaivita_ehmataja:
                Veidrused.veidruse_aktiveerija("ehmataja(pall)", None)
            Helid.naita_tugevust()

        pg.display.update()
        pg.display.update()
        FPS.tick_busy_loop(Satted.fps)

    @staticmethod
    def sisendid():  # Hiire klõpsud, kas on tahatud sulgeda mängu.
        global PAUS
        sulge = False

        for sundmus in pg.event.get():
            if sundmus.type == pg.QUIT:
                sulge = True
            elif sundmus.type == pg.KEYDOWN:
                if sundmus.key == pg.K_ESCAPE:
                    if PAUS:
                        sulge = True
                    PAUS = True
            elif sundmus.type == pg.MOUSEBUTTONDOWN:
                if sundmus.button == 4:
                    Helid().helitugevuse_muutja("üles")
                elif sundmus.button == 5:
                    Helid().helitugevuse_muutja("alla")

        return {"menüüsse": PAUS,
                "sulge": sulge,
                "hiire_klõps": pg.mouse.get_pressed()[0],
                "hiire_koht": pg.mouse.get_pos()}

    @staticmethod
    def pallid_paigal():  # Kontrollib, kas pallidel on olemas kiirus ja annab märku uuendamise vajadusest
        for pall in elus_pallid:
            if count_nonzero(pall.joud) > 0:
                return False
        return True

    @staticmethod
    def vahenda_elu():
        def elu_vahendaja():
            k_e = Olukord.kaotatud_elu
            laud = terve_laud.sprites()[0].image

            laud.blit(k_e, Olukord.read[-1][Olukord.e_s_p_k])
            Olukord.read[-1].remove(Olukord.read[-1][Olukord.e_s_p_k])

            Olukord.e_s_p_k = next(kulg for kulg in Olukord.e_s_k if Olukord.e_s_p_k != kulg)
            Olukord.elud -= 1

        try:
            if not Satted.eludeta_mang:
                elu_vahendaja()
        except (NameError, TypeError, AttributeError):
            max_sumboleid_reas = Satted.laua_laius // Olukord.elusumboli_laius
            ulejaak = Satted.elude_kogus % max_sumboleid_reas

            ridu = Satted.elude_kogus // max_sumboleid_reas + 1
            Olukord.read = []
            for j in range(ridu - 1):
                rida = []
                for i in range(max_sumboleid_reas):
                    i += j * max_sumboleid_reas
                    rida.append(Olukord.elu_sumbolite_kohad[i])
                Olukord.read.append(rida)
            rida = []
            for i in range(ulejaak):
                i += (Satted.elude_kogus - ulejaak)
                rida.append(Olukord.elu_sumbolite_kohad[i])
            Olukord.read.append(rida)

            Olukord.kaotatud_elu = Olukord.sumboli_tegija(Satted.kaotatud_elusumboli_varv)
            Olukord.e_s_p_k = -1
            elu_vahendaja()
        except IndexError:
            try:
                del Olukord.read[-1]
                elu_vahendaja()
            except IndexError:
                global lopeta
                lopeta = True

    @staticmethod
    def lopeta_mang():
        pg.display.flip()
        Olukord.loputiitel = "MÄNG LÄBI"
        pohjused = "Elud said otsa", "8-pall läks liiga varakult auku", "Mida sa teinud oled?", \
                   "Sa oled võitnud mängu"
        global lopeta
        # Annab lõpetuse põhjuse
        if not Satted.eludeta_mang and Olukord.elud <= 0:
            pohjus = pohjused[0]
        elif Olukord.must_pall_sees:
            if len(elus_pallid) > 1:
                pohjus = pohjused[1]
            else:
                pohjus = pohjused[3]
        else:
            pohjus = pohjused[2]
        Olukord.lopupohjus = pohjus
        # Käivitab lõpumuusika
        if pohjus == "Sa oled võitnud mängu":
            Helid.heli_mangija("võit")
        else:
            Helid.heli_mangija("kaotus")
        # Et teksti kirjutajat saaks kasutada menüüdes ja tabelis
        if Olukord.loputiitel not in Satted.menuude_tekstid:
            Satted.menuude_tekstid.append(Olukord.loputiitel)
            Satted.menuude_tekstid.extend(pohjused)
        # Puhastab
        for sprite in sees_pallid:
            pg.sprite.Sprite.kill(sprite)
        Olukord.restartija()
        pg.display.set_mode(Aken.Alus.resolutsioon_f())
        lopeta = True

    @staticmethod
    def restartija():
        global mangu_algus, alustatud, lopeta
        # Kustutan kõik spraidid
        for sprite in koik_spraidid:
            pg.sprite.Sprite.kill(sprite)
        for sprite in valge_pall_sees:
            pg.sprite.Sprite.kill(sprite)

        # Lähtestan asju
        Veidrused.veidruste_lulitid = {}
        Olukord.elud = Satted.elude_kogus
        Olukord.mangu_alguse_akna_muude = False
        Olukord.lisatud_tabelisse = None
        Olukord.must_pall_sees = False
        Olukord.puude = True
        Olukord.read = None
        mangu_algus = True
        alustatud = False
        lopeta = False

    @staticmethod
    def valge_pall_musta_auku(pall):
        pall.kill()
        pg.display.flip()
        Olukord.vahenda_elu()
        pikkus = Satted.pall_sisse_pikkus
        koik_spraidid.draw(ALUS.aken)
        pg.display.update()
        Olukord.uneaeg = time.time()
        Olukord.palju_magada_vaja = pikkus
        pall.add(valge_pall_sees)


class Veidrused:
    """
    Pöörane osa sellest mängust, teeb selle ühemängijamänguks
    """
    veidrused = {
        "Ehmataja": "ehmataja(pall)",
        "Teleporteeruja": "teleporteeruja(pall)",
        "8 Palli Maagia": "must_auk()"
    }
    voimalused = {
        "must_auk()": 100,
        "teleporteeruja(pall)": Satted.telepordi_voimalus,
        "ehmataja(pall)": Satted.ehmataja_voimalus
    }
    veidruste_lulitid = {}
    kaivita_ehmataja = False
    # Kasti, teksti vahel
    k_t_v = 3
    # Probleemi lahendus - pl
    pl_pall = None

    # noinspection PyUnusedLocal
    @staticmethod
    def veidruse_aktiveerija(veidruse_funktsioon, alternatiiv):
        # Siia on VAJA lisada kõik elemendid, mis on vajalikud käivatavas funktsioonis
        if veidruse_funktsioon == "teleporteeruja(pall)":
            alternatiiv = Veidrused.teleportija_alternatiiv
            Veidrused.teleport = True
        elif veidruse_funktsioon == "ehmataja(pall)":
            alternatiiv = Veidrused.ehmatuse_alternatiiv
        pall = Veidrused.pl_pall

        staatus = Olukord.staatuse_leidja(veidruse_funktsioon)
        if staatus[1] and randint(0, 100) <= Veidrused.voimalused[veidruse_funktsioon]:
            eval("Veidrused." + staatus[0])
        else:
            # noinspection PyStatementEffect
            alternatiiv()

    @staticmethod
    def turvatsoonis_kohaleidja(r):
        V = Fuusika.vabaalad
        ra = randint(V[0][2][0] + r, V[2][2][0] - r), randint(V[2][3][1] + r, V[5][2][1] - r)
        return ra

    @staticmethod
    def ehmatuse_alternatiiv():
        Veidrused.kaivita_ehmataja = False

    @staticmethod
    def teleportija_alternatiiv():
        Veidrused.teleport = False

    @staticmethod
    def teleporteeruja(pall):
        def kohamuutja():
            pall.rect.center = Veidrused.turvatsoonis_kohaleidja(Satted.palli_raadius)
            Fuusika.lisa_musta_auguga_porge(pall)

        kohamuutja()
        for K_pall in elus_pallid:
            if pall == K_pall:
                continue
            if pg.sprite.collide_circle(K_pall, pall):
                kohamuutja()

    @staticmethod
    def must_auk():
        sprait = Mustad_Augud(Veidrused.turvatsoonis_kohaleidja(Satted.musta_augu_raadius))
        mustad_augud.add(sprait)
        koik_spraidid.empty()
        spraidigrupid = terve_laud, mustad_augud, sees_pallid, elus_pallid, valge_pall_sees
        for grupp in spraidigrupid:
            koik_spraidid.add(grupp)
        if not Satted.must_auk_nahtamatu:
            koik_spraidid.add(sprait)

    @staticmethod
    def ehmataja(pall):
        number = pall.number
        keskpunkt = tuple(suurus // 2 for suurus in Satted.laua_suurus)
        raadius = keskpunkt[1]
        keskpunkt = tuple(suurus - raadius for suurus in keskpunkt)
        pilt, rect, number, mass = ringi_joonistaja(raadius, Satted.palli_varvid[number - 1], number)
        if not Satted.helitu_ehmataja:
            Helid.heli_mangija("ehmatus")

        ALUS.aken.blit(pilt, keskpunkt)
        pg.display.flip()
        Veidrused.kaivita_ehmataja = False

    @staticmethod
    def veidruse_luliti_kogusuuruse_leidja():
        # Veidruste lüliti kogusuurus
        v_l_ks = Aken.teksti_kirjutaja(max(Satted.v_l_t), Satted.tabeli_fondi_suurus, None, None, None, False)
        Veidrused.v_l_ks = tuple(x + 2 * Satted.t_k_l for x in v_l_ks)

    @staticmethod
    def optimaalne_veidruste_kombinatsioonid():
        def kombinatsiooni_eemaldaja(kontroll, kontrollitav):
            for asi in kontroll:
                if asi in kontrollitav:
                    return False
            return True

        kombinatsioonid = {}
        VEIDRUSED = list(Veidrused.veidrused.keys())
        opt_list = []  # Optimeeritud list
        kasutatud_veidrused = []

        try:
            v_l_ks = Veidrused.v_l_ks  # Veidruse lüliti kogusuurus
        except (NameError, TypeError, AttributeError):
            Veidrused.veidruse_luliti_kogusuuruse_leidja()
            v_l_ks = Veidrused.v_l_ks

        # Lisa laius
        l_laius = Veidrused.k_t_v + v_l_ks[0]
        # Fondi suurus
        fs = Satted.tabeli_fondi_suurus

        # Kombinatsioonide leidmine
        for (m1, v_1) in enumerate(VEIDRUSED):
            for m2 in range(m1 + 1, len(VEIDRUSED)):
                v_2 = VEIDRUSED[m2]
                tekst_1 = Aken.teksti_kirjutaja(v_1, fs, None, None, None, False)[0] + l_laius
                tekst_2 = Aken.teksti_kirjutaja(v_2, fs, None, None, None, False)[0] + l_laius
                if max(tekst_1, tekst_2) >= Satted.laua_laius // 2:
                    continue
                kogu_laius = tekst_1 + tekst_2
                kombinatsioonid[(v_1, v_2)] = kogu_laius

        # Kombinatsioonide töötlemine
        while True:
            veidruste_komb = list(kombinatsioonid.keys())  # Veidruste kombinatsioonid
            pikkused = list(kombinatsioonid.values())
            try:
                mitmes = pikkused.index(max(pikkused))
                v_s_a = veidruste_komb[mitmes]  # Veidrused suurima arvuga
                kasutatud_veidrused.extend(v_s_a)
                opt_list.append(v_s_a)
                # puhastus
                kombinatsioonid = {veidruse_komb: kombinatsioonid[veidruse_komb] for veidruse_komb in kombinatsioonid
                                   if kombinatsiooni_eemaldaja(v_s_a, veidruse_komb)}
            except ValueError:
                break

        # Täidab optimeeritud listi, et seda saaks kasutada, tabeli moodustamisel
        for veidrus in VEIDRUSED:
            if veidrus not in kasutatud_veidrused:
                opt_list.append(veidrus)
        Veidrused.opt_list = opt_list


class Helid:
    """
    Tegeleb helidega - Kutsub esile ja muudab tugevust
    """
    porge = False
    viimane_muutus = time.time()
    helitugevus = Satted.heli_vaiketugevus
    helitugevusemuut = {"alla": -0.02, "üles": 0.02, "paigal": 0}
    helid = {}

    def helitugevuse_muutja(self, tugevusemuut):
        muut = self.helitugevusemuut[tugevusemuut]
        Helid.helitugevus += muut
        if Helid.helitugevus > 1:
            Helid.helitugevus = 1
        elif Helid.helitugevus < 0:
            Helid.helitugevus = 0
        # Muudab helitugevust häältel
        for heli in self.helid:
            self.helid[heli].set_volume(self.helitugevus)
        Helid.viimane_muutus = time.time()

    @staticmethod
    def mixer_test():
        if pg.mixer.get_init() is None:
            pg.mixer.init()

    @staticmethod
    def heli_mangija(heli):
        Helid.mixer_test()
        heli = Satted.helid[heli]
        try:
            pg.mixer.Sound.play(Helid.helid[heli])
        except KeyError:
            Helid.helid[heli] = pg.mixer.Sound(heli)
            Helid().helitugevuse_muutja("paigal")
            pg.mixer.Sound.play(Helid.helid[heli])

    @staticmethod
    def porke_erandjuhum(tugevus):
        Helid.helid[Satted.helid["porge"]].set_volume(tugevus * Helid.helitugevus)
        Helid.heli_mangija("porge")

    @staticmethod
    def naita_tugevust():
        def tee_alus():
            if alustatud:
                pg.draw.rect(ALUS.aken, Satted.augu_katte_varv, [0, 0, Satted.ht_m_t_s[0], Satted.ht_m_t_s[1]])
            else:
                pg.draw.rect(ALUS.aken, Satted.akna_varvus, [0, 0, Satted.ht_m_t_s[0], Satted.ht_m_t_s[1]])

        if time.time() - Helid.viimane_muutus < 0.5:
            tee_alus()
            Aken.teksti_kirjutaja(str(round(Helid.helitugevus * 100)), Satted.tavalise_fondi_suurus, ALUS.aken, (0, 0),
                                  Satted.helitugevuse_varv, False)
        elif PAUS:
            tee_alus()


# Spraitide gruppid
terve_laud = pg.sprite.Group()
mustad_augud = pg.sprite.Group()
elus_pallid = pg.sprite.Group()
sees_pallid = pg.sprite.Group()
valge_pall_sees = pg.sprite.GroupSingle()
koik_spraidid = pg.sprite.Group()

kaib = True
PAUS = True
mangu_algus = True
lopeta = False
pg.mixer.pre_init()
pg.init()  # Alustab
for heli in Satted.helid:  # Kontrollib, kas helifailid on olemas
    heli = Satted.helid[heli]
    try:
        Helid.helid[heli] = pg.mixer.Sound(heli)
    except FileNotFoundError:
        Helid.helid[heli] = pg.mixer.Sound(pg.sndarray.make_sound(array([[0, 0], [0, 0]])))
        if heli not in Satted.problemaatilised_helid:
            Satted.problemaatilised_helid.append(heli)
            pohjus = 'Andmete kaustas polnud "' + heli.split("/")[-1] + '" helide kaustas.'
            Aken.teate_esiletooja(pohjus)
# Vähem kontrollimist, ehk kiirem programm
pg.event.set_blocked(None)
pg.event.set_allowed([pg.KEYDOWN, pg.MOUSEBUTTONDOWN, pg.QUIT])
Satted.ikoon()
pg.display.set_caption(Satted.tiitel)  # Annab pealkirja
ALUS = Aken.Alus()  # Sisaldab ekraani põhisätteid

# Siit alates algab mängu mootor
while kaib:
    if not lopeta:
        menuu_sisend = Aken.joonista_menuu()  # Nupuvajutusega seotud käsud
    else:
        menuu_sisend = Aken.mang_on_labi()
    pg.display.update()

    if menuu_sisend == "Alusta Uuesti":
        Olukord.restartija()
        menuu_sisend = "Mängi"
    if menuu_sisend == "Mängi" or menuu_sisend == "Jätka":
        PAUS = False
        menuu_sisend = sisendid = Olukord.sisendid()
        Kii.klopsatus = sisendid["hiire_klõps"]

        if not alustatud:
            Laud()
            Pallid()
            Aken.Alus()
            alustatud = True
            pg.mixer.stop()

        while not (sisendid["sulge"] or sisendid["menüüsse"] or lopeta):
            sisendid = Olukord.sisendid()

            if not Olukord.pallid_paigal():
                mangu_algus = False

            if sisendid["menüüsse"]:
                Aken.alguse_menuu_nuppude_kohad = None
                PAUS = True
            if sisendid["sulge"]:
                kaib = False

            Olukord().uuenda()
            if lopeta:
                Olukord.lopeta_mang()

    if menuu_sisend == "Sulge" or menuu_sisend["sulge"]:  # Kontrollib, kas on käsku antud sulgemiseks
        kaib = False

pg.quit()
Satted.s2tted.set("Helid", "heli vaiketugevus", str(round(Helid.helitugevus * 100)) + " %")
Satted.s2tted.write(open(Satted.s2ttefaili_asukoht, "w", "utf8"))
