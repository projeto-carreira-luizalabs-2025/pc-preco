class AlertService:
    def __init__(self, alert_repository):
        self.alert_repository = alert_repository

    async def create_alert(self, alert_data):
        """
        Create a new alert.
        """
        return await self.alert_repository.create(alert_data)

    async def get_alert(self, alert_id):
        """
        Retrieve an alert by its ID.
        """
        return await self.alert_repository.get(alert_id)
