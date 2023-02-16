from fastapi import APIRouter, Query
# Ce fichier contient des examples de routes utiles pour le projet
# il sera agremente au fur et a mesure

router = APIRouter()


@router.get("/")
async def router_root_hello():
    return {"message": "Bienvenue sur les routes d'exemple"}


# route avec query params , verifie que la page est comprise entre 1 et 2
@router.get("/hello")
async def helloQueryParam(page: int = Query(1, ge=1, le=2)):
    data = ["Hello", "World"]
    return {"message": data[page - 1]}


# route avec un query param obligatoire et verification a l'aide de regex
@router.get("/query", summary="Renvoi un message en fonction de la langue", description="Essaye de changer la valeur de lang dans l'url pour voir le resultat")
async def hello(lang: str = Query(..., min_length=2, max_length=2, regex="^(fr|en)$")):
    if lang == "fr":
        return {"message": "Bonjour"}
    elif lang == "en":
        return {"message": "Hello"}


# attention a l'ordre des routes car fastapi va prendre la premiere route qui match
# on met donc les routes avec path params en dernier
@router.get("/{name}")
async def helloPathParam(name: str):
    return {"message": f"Hello {name}"}
