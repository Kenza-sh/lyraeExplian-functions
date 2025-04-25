import azure.functions as func
import logging
import re
import json
from typing import Optional, Dict

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class CRPreProcesser:
  def __init__(self):
            self.replacements = {
                    r'acromioclaviculaire': "ACROMIOCLAVICULAIRE (RADIOGRAPHIE DE L'ARTICULATION ACROMIO-CLAVICULAIRE)",
                    r'pangonogramme': "PANGONOGRAMME (RADIOGRAPHIE DES DENTS)",
                    r'asp': "ASP (RADIOGRAPHIE DE L'ABDOMEN SANS PRÉPARATION)",
                    r'urocanner': "UROSCANNER (SCANNER DES REINS)",
                    r'arm': "ARM (IRM DES VAISSEAUX SANGUINS)",
                    r'bili irm': "BILI IRM (IRM DES VOIES BILIAIRES)",
                    r'entero irm': "ENTERO IRM (IRM DE L'INTESTIN)",
                    r'entéro irm': "ENTERO IRM (IRM DE L'INTESTIN)",
                    r'angio irm': "ENGIO IRM (IRM ANGIOGRAPHIQUE DES VAISEAUX SANGUINS)",
                    r'uroscanner': "UROSCANNER (SCANNER DES VOIES URINAIRES)",
                    r'dacryoscanner': "DACRYOSCANNER (SCANNER DES VOIES LACRYMALES)",
                    r'coroscanner': "COROSCANNER (SCANNER DES ARTERES DU COEUR)",
                    r'entéroscanner': "ENTEROSCANNER (SCANNER DU L'INTESTIN)",
                    r'coloscanner': "COLOSCANNER (SCANNER DU COLON)",
                    r'arthro-scanner': "ARTHRO-SCANNER (SCANNER DES ARTICULATIONS )",
                    r'arthro-irm': "ARTHRO-IRM (IRM DES ARTICULATIONS )",
                    r'ostéodensitométrie': "OSTÉODENSITOMÉTRIE (RADIOGRAPHIE DES OS )",
                    r'cystographie': "CYSTOGRAPHIE (RADIOGRAPHIE DE LA VESSIE )",
                    r'discographie': "DISCOGRAPHIE (RADIOGRAPHIE DE DISQUE INTERVERTÉBRAL )",
                    r'togd': "TOGD (RADIOGRAPHIE DE L'\u0152SOPHAGE ET DE L'ESTOMAC )",
                    r'urographie': "UROGRAPHIE (RADIOGRAPHIEE DES VOIES URINAIRES )",
                    r'hystérographie': "HYSTÉROGRAPHIE (RADIOGRAPHIE DE LA CAVITÉ UTÉRINE )",
                    r'hystérosalpingographie': "HYSTÉROSALPINGOGRAPHIE (RADIOGRAPHIE DE LA CAVITÉ UTÉRINE )",
                    r'cone beam': "CONE BEAM (RADIOGRAPHIE DES DENTS)",
                    r'tomographie': "TOMOGRAPHIE (RADIOGRAPHIE DES DENTS)",
                    r'doppler': "DOPPLER (ECHOGRAPHIE DES VAISSEAUX)",
                }

            self.titre_mots = [
                r'\bm[íi]cro[- ]?biopsie(s)?\b',  # Supporte "microbiopsie", "micro biopsie", "micro-biopsie" et variantes
                r'\bbiopsie(s)?\b',  # Supporte "biopsie" et "biopsies"
                r'\bdrainage(s)?\b',  # Supporte "drainage" et "drainages"
                r'\bpose(s)?[- ]?de[- ]?cath[éeèe]ter(s)?\b',  # Supporte "pose de cathéter", "pose-de-cathéter" et variantes
                r'\bembolisation(s)?\b',  # Supporte "embolisation" et "embolisations"
                r'\bangioplastie(s)?\b',  # Supporte "angioplastie" et "angioplasties"
                r'\bradio[- ]?fr[éeèe]quence(s)?\b',  # Supporte "radio-fréquence", "radio fréquence" et variantes
                r'\bablation(s)?\b',  # Supporte "ablation" et "ablations"
                r'\bmicro[- ]?ondes\b',  # Supporte "micro-ondes", "micro ondes"
                r'\bcimentoplastie(s)?\b',  # Supporte "cimentoplastie" et "cimentoplasties"
                r'\bfiltre(s)?[- ]?cave(s)?\b',  # Supporte "filtre cave", "filtre-cave" et variantes
                r'\bthrombectomie(s)?\b',  # Supporte "thrombectomie" et "thrombectomies"
                r'\bthrombolyse(s)?\b',  # Supporte "thrombolyse" et "thrombolyses"
                r'\bponction(s)?\b',  # Supporte "ponction" et "ponctions"
                r'\bcyto[- ]?ponction(s)?\b',  # Supporte "cytoponction", "cyto ponction", "cyto-ponction"
                r'\bTIPS\b',  # Supporte exactement "TIPS"
                r'\bgastrostomie(s)?\b',  # Supporte "gastrostomie" et "gastrostomies"
                r'\bnéphrostomie(s)?\b',  # Supporte "néphrostomie" et "néphrostomies"
                r'\bcholangiographie(s)?\b',  # Supporte "cholangiographie" et "cholangiographies"
                r'\bangiographie(s)?\b',  # Supporte "angiographie" et "angiographies"
                r'\bfistulographie(s)?\b',  # Supporte "fistulographie" et "fistulographies"
                r'\bdilatation(s)?\b',  # Supporte "dilatation" et "dilatations"
                r'\binjection(s)?\b',  # Supporte "injection" et "injections"
                r'\bfermeture(s)?\b',  # Supporte "fermeture" et "fermetures"
                r'\btraitement(s)?\b',  # Supporte "traitement" et "traitements"
                r'\bpose(s)?[- ]?de\b',  # Supporte "pose de", "pose-de"
                r'\bscl[éeèe]ro[- ]?th[éeèe]rapie(s)?\b',  # Supporte "sclérothérapie", "scléro-thérapie", etc.
                r'\bmise(s)?[- ]?en[- ]?place[- ]?de\b',  # Supporte "mise en place de", "mise-en-place-de", etc.
                r'\breconstruction(s)?\b',  # Supporte "reconstruction" et "reconstructions"
                r'\bcryo[- ]?ablation(s)?\b',  # Supporte "cryoablation", "cryo-ablation", etc.
            ]
            self.cr_mots = [
            r'\banesth[éeèe]sie(s)?\b',  # Supporte "anesthésie", "anesthesie", "anesthésies" et variantes
            r'\bproc[éeèe]dure(s)?\b',  # Supporte "procédure", "procedure", "procédures" et variantes
            r'\basepsie(s)?\b',  # Supporte "asepsie" et "asepsies"
            r'\bconsentement(s)?\b',  # Supporte "consentement" et "consentements"
        ]



  def is_radio_interventionnelle(self,text,keywords):
            pattern = '|'.join(keywords)
            return bool(re.search(pattern, text, re.IGNORECASE))


  def process_cr(self,text,titre):
      
        for pattern, replacement in self.replacements.items():
                  titre = re.sub(pattern, replacement, titre, flags=re.IGNORECASE)

        result = self.is_radio_interventionnelle(text, self.cr_mots) or self.is_radio_interventionnelle(titre, self.titre_mots)
        return text, titre, result

cr_processor=CRPreProcesser()
def main(req: func.HttpRequest) -> func.HttpResponse:
    """Gère la requête en fonction de l'action demandée"""
    logger.info("Début du traitement de la requête HTTP")

    try:
        req_body = req.get_json()
        logger.info("Corps de la requête JSON récupéré avec succès")
    except ValueError as e:
        logger.error(f"Erreur lors du traitement de la requête : {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Invalid JSON format"}),
            mimetype="application/json",
            status_code=400
        )

    # Extraction et validation des paramètres
    cr = req_body.get("cr", "").strip()
    titre = req_body.get("titre", "").strip()

    if not cr or not titre:
        return func.HttpResponse(
            json.dumps({"error": "Paramètres 'cr' et 'titre' requis"}),
            mimetype="application/json",
            status_code=400
        )

    logger.info(f"cr reçu : {cr[:50]}")
    logger.info(f"Titre reçu : {titre[:50]}...")  # Limite pour éviter d'exposer des données sensibles



    # Exécuter la fonction correspondante et retourner le résultat
    try:
        processed_cr,processed_titre,is_interventional = cr_processor.process_cr(cr, titre)
        return func.HttpResponse(
            json.dumps({"processed_cr": processed_cr , "processed_title":processed_titre , "is_interventional_cr":is_interventional}),
            mimetype="application/json",
            status_code=200
        )
    except Exception as e:
        return func.HttpResponse(
            json.dumps({"error": f"Erreur lors de l'exécution: {str(e)}"}),
            mimetype="application/json",
            status_code=500
        )

           
