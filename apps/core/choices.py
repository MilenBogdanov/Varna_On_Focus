from django.db import models


class SignalStatus(models.TextChoices):
    OPEN = 'OPEN', 'Отворен'
    IN_PROGRESS = 'IN_PROGRESS', 'В процес'
    RESOLVED = 'RESOLVED', 'Решен'
    REJECTED = 'REJECTED', 'Отхвърлен'


class NewsSourceType(models.TextChoices):
    # Life & Safety
    EMERGENCY = 'EMERGENCY', 'Бедствие / Опасност'

    # Utilities (Separated)
    WATER_URGENT = 'WATER_URGENT', 'Авария - Водоснабдяване'
    WATER_PLANNED = 'WATER_PLANNED', 'Планов ремонт - ВиК'

    ELECTRICITY_URGENT = 'ELEC_URGENT', 'Авария - Електрозахранване'
    ELECTRICITY_PLANNED = 'ELEC_PLANNED', 'Планов ремонт - Електро'

    # Infrastructure
    ROAD_WORKS = 'ROAD_WORKS', 'Ремонт на пътната мрежа'
    TRAFFIC_CHANGE = 'TRAFFIC', 'Промяна в движението'

    # General
    MUNICIPAL = 'MUNICIPAL', 'Общинско съобщение'
    OTHER = 'OTHER', 'Други'

class AuditOperationType(models.TextChoices):
    CREATE = 'CREATE', 'Създаване'
    UPDATE = 'UPDATE', 'Промяна'
    DELETE = 'DELETE', 'Изтриване'