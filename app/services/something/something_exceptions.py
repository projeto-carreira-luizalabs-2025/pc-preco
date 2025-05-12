from app.common.exceptions import ConflictException


class SomethingAlreadyExistsException(ConflictException):
    def __init__(self):
        details = [
            {
                "message": "alguma coisa ja existe",
                "slug": "codigo-xxx-yyy",
            }
        ]
        super().__init__(details)
