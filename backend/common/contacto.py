"""Ayudantes para validar y normalizar los datos de contacto y textos libres."""
import re


def limpiar_telefono(valor):
    """
    Devuelve el teléfono sin espacios ni guiones ('+57 300-123-4567' -> '+573001234567').
    - Si viene vacío devuelve None (el teléfono es opcional).
    - Si no parece un teléfono (entre 7 y 15 dígitos) lanza ValueError.
    """
    if valor is None:
        return None
    texto = str(valor).strip()
    if not texto:
        return None
    if not re.fullmatch(r"\+?[\d\s\-().]+", texto):
        raise ValueError("El teléfono solo puede tener números, espacios y el signo +")
    digitos = re.sub(r"\D", "", texto)
    if not 7 <= len(digitos) <= 15:
        raise ValueError("El teléfono debe tener entre 7 y 15 dígitos")
    return ("+" if texto.startswith("+") else "") + digitos


def capitalizar(texto):
    """'conejo enano' -> 'Conejo enano' (solo la primera letra; no toca el resto). Vacío -> None."""
    texto = " ".join(str(texto or "").split())
    return (texto[:1].upper() + texto[1:]) if texto else None


def texto_o_none(valor, maximo):
    """
    Recorta espacios y valida el largo. Vacío -> None.
    Lanza ValueError si supera `maximo` caracteres.
    """
    texto = " ".join(str(valor or "").split())
    if not texto:
        return None
    if len(texto) > maximo:
        raise ValueError(f"No puede tener más de {maximo} caracteres")
    return texto
