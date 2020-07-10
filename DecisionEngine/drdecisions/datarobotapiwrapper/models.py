from django.db import models
from django.db.models import F
from solo.models import SingletonModel


class ProtectedModel(models.Model):
    class Meta:
        abstract = True

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def readonly(self):
        return True

    @classmethod
    def all_field_names(cls, skip_fields=None):
        if not skip_fields:
            skip_fields = []
        skip_fields.append('id')
        return tuple(field.name for field in cls._meta.fields
                     if field.name not in skip_fields)


class LogicConnector(ProtectedModel):
    """We expect one logic
    and want to save all historical project/model/logic variants"""

    class Meta:
        verbose_name = 'Logic Connector'
        verbose_name_plural = 'Logic Connectors'

    label = models.CharField(max_length=100, verbose_name='Label')
    run_cnt = models.PositiveIntegerField(default=0, verbose_name='Run Count')
    business_logic = models.TextField(verbose_name='Business Logic(Python code)')

    def readonly(self):
        return self.run_cnt > 0

    def __str__(self):
        return f'{self.id} | {self.label}'

    @classmethod
    def inc_run_count(cls, logic_connector_id):
        LogicConnector.objects.filter(id=logic_connector_id).update(run_cnt=F('run_cnt') + 1)


class BusinessEntity(models.Model):
    class Meta:
        verbose_name = 'Business Entity'
        verbose_name_plural = 'Business Entities'
    name = models.CharField(max_length=100, unique=True, db_index=True, verbose_name='Unique Business Entity Name')
    logic_connector = models.ForeignKey(LogicConnector,
                                        verbose_name='Logic Connector',
                                        on_delete=models.PROTECT)


class LogFile(ProtectedModel):
    """Storing generated log reports, can be used for generating s3 signed urls"""

    class Meta:
        verbose_name = 'Log file'
        verbose_name_plural = 'Log files'

    logic_connector = models.ForeignKey(LogicConnector,
                                        verbose_name='Logic Connector',
                                        on_delete=models.PROTECT)
    s3_bucket = models.TextField()
    s3_key = models.TextField()

    def __str__(self):
        return f'Log File {self.logic_connector_id} | {self.updated} | {self.s3_key}'


class PredictionServer(SingletonModel):
    class Meta:
        verbose_name = 'Prediction Server'
        verbose_name_plural = 'Prediction Servers'

    label = models.CharField(max_length=100, verbose_name='Label')
    server_url = models.URLField(verbose_name='Server URL')
    datarobot_key = models.CharField(max_length=100, verbose_name='DR Key')
    datarobot_username = models.CharField(max_length=100, verbose_name='DR Username ')
    api_token = models.CharField(max_length=100, verbose_name='API Token')
    logic_connector = models.ForeignKey(LogicConnector,
                                        blank=True,
                                        null=True,
                                        verbose_name='Default Logic Connector',
                                        on_delete=models.PROTECT)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.id} | {self.label}'
