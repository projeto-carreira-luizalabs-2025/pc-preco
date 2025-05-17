from datetime import datetime, timezone


def utcnow() -> datetime:
    """
    Retorna o timestamp atual em UTC com precisão de milissegundos.

    Os microssegundos são truncados para compatibilidade com MongoDB,
    que armazena datas com precisão de milissegundos.

    :return: Objeto datetime atual em UTC com microssegundos truncados
    """
    now = datetime.now(timezone.utc)
    # Trunca os microssegundos mantendo somente milissegundos
    # O mongodb não armazena microssegundos
    return now.replace(microsecond=(now.microsecond // 1000) * 1000)
