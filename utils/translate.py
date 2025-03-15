from googletrans import Translator

async def translate_text(text, target_lang, source_lang='auto'):
    """
    Traduit un texte en fonction de la langue cible.

    Args:
        text (str): Le texte à traduire.
        target_lang (str): La langue de destination (ex: 'mg', 'en', 'es', 'ar', etc.).
        source_lang (str): Langue source (par défaut 'auto' pour auto-détection).

    Returns:
        str: Texte traduit.
    """
    translator = Translator()
    translation = await translator.translate(text, src=source_lang, dest=target_lang)  # Ajoutez 'await' ici
    return translation.text
