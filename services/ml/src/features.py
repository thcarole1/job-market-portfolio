

def build_offer_text(offer: dict) -> str:
    '''
    1. Concatène les champs textuels d'une offre normalisée
    2. Gère les champs vides (None ou listes vides)
    3. Extrait les libelle des champs liste (competences, languages, professional_qualities)
    '''
    texte_offre = f"""
    {offer.get("title")            or ""}
    {offer.get("name_label")       or ""}
    {offer.get("description")      or ""}
    {offer.get("rome_label")       or ""}
    {' '.join([c.get('libelle',"") for c in offer.get("competences", [])])}
    {' '.join([l.get('libelle',"") for l in offer.get("languages", [])])}
    {' '.join([q.get('libelle',"") for q in offer.get("professional_qualities", [])])}
    """
    return texte_offre
