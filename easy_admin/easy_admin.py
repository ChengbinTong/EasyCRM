from crm import models
from django.shortcuts import render,HttpResponse,redirect
enabled_admins = {}
from django.forms import ValidationError
class BaseAdmin(object):
    list_display = []
    list_filters = []
    list_per_page = 20
    pk_field='id'
    #list搜索列表 如果有外键  tab__name 需要用__连接
    list_search=[]
    actions = ["delete_selected_objs", ]
    readonly_fields=[]
    readonly_table = False
    def delete_selected_objs(self, request, querysets):
        app_name = self.model._meta.app_label
        table_name = self.model._meta.model_name
        # print("--->delete_selected_objs", self, request, querysets)
        if self.readonly_table:
            errors = {"readonly_table": "This table is readonly ,cannot be deleted or modified!"}
        else:
            errors = {}
        if request.POST.get("delete_confirm") == "yes":
            querysets.delete()
            return redirect("/easyadmin/%s/%s" % (app_name, table_name))
        action_pks = ','.join([str(i.pk) for i in querysets])
        return render(request, "easyadmin/table_obj_delete.html", {"objs": querysets,
                                                                    "admin_class": self,
                                                                    "app_name": app_name,
                                                                    "table_name": table_name,
                                                                   "action_pks": action_pks,
                                                                   "action_def": request._admin_action,
                                                                   "errors": errors
                                                                    })

    def default_form_validation(self):
        '''用户可以在此进行自定义的表单验证，相当于django form的clean方法'''
        pass

class CustomerAdmin(BaseAdmin):
    list_display = ['qq','name','source','consultant','consult_course','date','status']
    list_filters = ['source','consultant','consult_course','status','date']
    list_search = ['qq','name','consultant__name']
    #model = models.Customer
    list_per_page = 10
    # readonly_table = True
    # readonly_fields = ["qq", "consultant", "tags"]
    def default_form_validation(self):
        consult_content = self.cleaned_data.get("content", '')
        if len(consult_content) < 15:
            return self.ValidationError(
                ('Field %(field)s 咨询内容记录不能少于15个字符'),
                code='invalid',
                params={'field': "content", },
            )
    #
    # def clean_name(self):
    #     pass
        # # 规则 clean_field
        # print("自定义验证")
        # if not self.cleaned_data["name"]:
        #     print("-->name none")
        #     self.add_error('name', "cannot be null")
class CustomerFollowUpAdmin(BaseAdmin):
    list_display = ('customer','consultant','date')
class UserProfileAdmin(BaseAdmin):
    list_display = ('email','name')
    readonly_fields = ('password',)
    modelform_exclude_fields = ["last_login",]
    filter_horizontal = ("user_permissions","groups")

def register(model_class,admin_class=None):
    if admin_class==None:
        admin_class=type('A',(BaseAdmin,),{})
    if model_class._meta.app_label not in enabled_admins:
        enabled_admins[model_class._meta.app_label] = {} #enabled_admins['crm'] = {}
    #admin_obj = admin_class()
    admin_class.model = model_class #绑定model 对象和admin 类
    if not admin_class.list_display:
        admin_class.list_display=[ model_class._meta.fields[1].verbose_name]
    enabled_admins[model_class._meta.app_label][model_class._meta.model_name] = admin_class
    #enabled_admins['crm']['customerfollowup'] = CustomerFollowUpAdmin

register(models.UserProfile,UserProfileAdmin)
register(models.Customer,CustomerAdmin)
register(models.CustomerFollowUp,CustomerFollowUpAdmin)
register(models.Course)
register(models.Tag)
register(models.Enrollment)
register(models.Course)
register(models.ClassList)
register(models.CourseRecord)
register(models.Branch)
register(models.Role)
register(models.Payment)
register(models.StudyRecord)
register(models.Menu)