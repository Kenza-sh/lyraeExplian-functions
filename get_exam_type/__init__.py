import azure.functions as func
import logging
import re
import json


def detect_type_examen( titre):
        def normalize_type(text):
              replacements = {
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
              for pattern, replacement in replacements.items():
                        text = re.sub(pattern, replacement,text, flags=re.IGNORECASE)
              return text

        keywords = {
                "RADIO": ["radio", "radiographie", "x-ray", "rayon x"],
                "SCANNER": ["scanner", "tdm", "tomodensitométri", "scan"],
                "IRM": ["irm", "imagerie par résonance magnétique"],
                "ECHOGRAPHIE": ["echo", "écho", "échographie", "echographie", "ultrason", "ultrasound",'échotomographie','ultrasonore'],
                "Mammographie": ["mammographie", "mammogramme", "mammo", "mamographie", "examen du sein", "imagerie mammaire"]
            }
        titre_lower = normalize_type(titre.lower()).lower()
        for category, words in keywords.items():
                if any(word in titre_lower for word in words):
                    return category

        return "AUTRE"

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    try:
        req_body = req.get_json()
        query = req_body.get('text')

        if not query:
            return func.HttpResponse(
                json.dumps({"error": "No query provided in request body"}),
                mimetype="application/json",
                status_code=400
            )

        result = detect_type_examen(query)

        return func.HttpResponse(
            json.dumps({"response": result}),
            mimetype="application/json"
        )

    except Exception as e:
        logging.error(f"Error processing request: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=500
        )
           
