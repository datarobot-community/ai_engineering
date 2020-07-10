#from django.contrib import admin

import pytz
from baton.admin import admin
from django import forms
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import Group
from django.db.models import Subquery, OuterRef
from django.shortcuts import redirect
from django.urls import path, reverse
from django.utils.html import format_html
from solo.admin import SingletonModelAdmin

from datarobotapiwrapper.logs.controllers import LogController
from datarobotapiwrapper.models import LogicConnector, PredictionServer, LogFile, ProtectedModel, BusinessEntity

LOG_DOWNLOAD = 'log-download'
LOG_UPDATE = 'log-update'


class ProtectedModelAdmin(admin.ModelAdmin):
    """This ModelAdmin works with models, which has 2 methods:
        def readonly(self):
            True

        @classmethod
        def all_field_names(cls, skip_fields=None):

        this allows to make readonly admin by condition
    """

    # override next properties
    model_class = ProtectedModel
    method_fields = ('logic_connector_actions',)
    readonly_fields = ('run_cnt',)
    list_display_skip_fields = ['business_logic']
    message_readonly = " You can't change this readonly object"

    def message(self, request, message):
        messages.add_message(
            request,
            messages.WARNING,
            message)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return not (obj and obj.readonly())

    def change_view(self, request, object_id, form_url='', extra_context=None):
        if self.get_obj_by_id(object_id).readonly():
            self.message(request, self.message_readonly)
            extra_context = extra_context or {}
            extra_context['show_delete'] = False
            extra_context['show_save_and_continue'] = False
            extra_context['show_save'] = False
        return super().change_view(request, object_id, form_url, extra_context)

    def get_obj_by_id(self, object_id):
        obj = self.model_class.objects.get(id=object_id)
        return obj

    def get_readonly_fields(self, request, obj=None):
        all_readonly_fields = self.readonly_fields
        if obj and obj.readonly():
            all_readonly_fields = self.model_class.all_field_names()
        if self.method_fields:
            all_readonly_fields = all_readonly_fields + self.method_fields
        return all_readonly_fields

    def get_list_display(self, request):
        list_display_fields = self.model_class.all_field_names(
            skip_fields=self.list_display_skip_fields)
        if self.method_fields:
            list_display_fields = list_display_fields + self.method_fields
        return list_display_fields



class LogicConnectorForm(forms.ModelForm):
    class Meta:
        widgets = {
            'business_logic': forms.Textarea(
                attrs={'cols': '80', 'rows': '20'})
        }


@admin.register(LogicConnector)
class LogicConnectorAdmin(ProtectedModelAdmin):
    form = LogicConnectorForm

    model_class = LogicConnector
    #method_fields = ('logic_connector_actions', 'log_download')
    #method_fields = ('logic_connector_actions')
    readonly_fields = ('run_cnt',)
    message_readonly = '''
        This business logic was already invoked by an external system and cannot be changed anymore. 
        Clone it to be able to edit it.'''
    list_display_skip_fields = ['business_logic']

    def has_add_permission(self, request):
        """This is a hack to hide the [Save and Add] button because it is rendered
        outside the individual item context and therefore cannot be hidden in change_view()"""
        path_parts = [part for part in request.path.split('/') if part]

        # we need to check here for model_name, path_parts[-3] becouse Django admin
        # send here not only current model, but also related models
        if len(path_parts) >= 3 and \
                path_parts[-3] == self.opts.model_name \
                and path_parts[-1] == 'change':
            id_str = path_parts[-2]
            return not self.get_obj_by_id(int(id_str)).readonly()
        return True

    def log_download(self, obj):
        """render for virtual column ACTIONS_FIELD"""
        if obj.pk is None or obj.logfile_id is None:
            return format_html('&nbsp;')

        timezone = pytz.timezone(settings.TIME_ZONE)
        date_localized = obj.logfile_created.astimezone(timezone)
        formated_date = date_localized.strftime("%Y-%m-%d %H:%M:%S")
        return format_html(
            '<a class="button" href="{}">{}</a> <br>',
            reverse('admin:' + LOG_DOWNLOAD, args=[obj.pk]), formated_date)
        # return obj.logfile_created

    log_download.short_description = 'Download Logs'

    def logic_connector_actions(self, obj):
        """render for virtual column ACTIONS_FIELD"""
        if obj.pk is None or obj.run_cnt == 0:
            return format_html('&nbsp;')

        """ return format_html(
            '<a class="button" href="{}">Collect Logs</a> <br>',
            reverse('admin:' + LOG_UPDATE, args=[obj.pk]), ) """

    logic_connector_actions.short_description = 'Actions'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(f'<int:logic_connector_id>/{LOG_UPDATE}/',
                 self.admin_site.admin_view(self.log_update),
                 name=LOG_UPDATE),
            path(f'<int:logic_connector_id>/{LOG_DOWNLOAD}/',
                 self.admin_site.admin_view(self.log_get),
                 name=LOG_DOWNLOAD), ]

        return custom_urls + urls

    def log_update(self, request, logic_connector_id, *args, **kwargs):
        print('log_update', logic_connector_id)
        bucket, key = LogController.update_log(logic_connector_id)
        return redirect('admin:price_logicconnector_changelist')

    def log_get(self, request, logic_connector_id, *args, **kwargs):
        print('log_get', logic_connector_id)

        log_file = LogFile.objects.filter(
            logic_connector_id=logic_connector_id).order_by('-pk').first()

        file_url = LogController.generate_report_url(log_file)
        return redirect(file_url)

    def get_queryset(self, request):
        # LogicConnector.objects.prefetch_related().get().logfile_set
        newest = LogFile.objects.filter(logic_connector=OuterRef('pk')).order_by('-pk')
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            logfile_created=Subquery(newest.values('created')[:1]),
            logfile_id=Subquery(newest.values('id')[:1]), )
        return queryset


class PredictionServerAdminForm(forms.ModelForm):
    class Meta:
        widgets = {
            'api_token': forms.PasswordInput(render_value=True),
            'datarobot_key': forms.PasswordInput(render_value=True),
        }


@admin.register(PredictionServer)
class PredictionServerAdmin(SingletonModelAdmin):
    form = PredictionServerAdminForm


@admin.register(BusinessEntity)
class BusinessEntityAdmin(admin.ModelAdmin):
    model_class = BusinessEntity
    list_display = ('name', 'logic_connector')


admin.site.unregister(Group)

