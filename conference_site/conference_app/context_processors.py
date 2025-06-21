# conference_app/context_processors.py

from .models import Session
from django.conf import settings
from django.templatetags.static import static

def site_context(request):
    """
    Rend le logo de la session la plus récente disponible dans tous les templates.

    Ce processeur de contexte tente de trouver la session "actuelle" (en cours ou la prochaine à venir).
    S'il trouve une session et que celle-ci possède un logo, il fournit l'URL de ce logo.
    Sinon, il fournit l'URL d'un logo par défaut défini dans les fichiers statiques.
    """
    latest_session = Session.get_current_session()
    site_logo_url = None
    
    # Vérifie si une session a été trouvée et si elle a un logo avec un fichier associé.
    if latest_session and latest_session.logo:
        site_logo_url = latest_session.logo.url
    else:
        # Fournir un logo par défaut si aucune session n'a de logo.
        # Assurez-vous que le fichier 'default-logo.png' existe bien à cet emplacement.
        site_logo_url = static('assets/img/default-logo.png')

    return {
        'site_logo_url': site_logo_url,
    }