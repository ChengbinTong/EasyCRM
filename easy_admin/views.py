
from django.shortcuts import render,HttpResponse,redirect
from easy_admin import easy_admin
from easy_admin.utils import table_filter,easy_search
from easy_admin.utils import easy_order
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger
from easy_admin.forms import  create_model_form
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
# Create your views here.
def index(request):
	return  render(request,'easyadmin/index.html',{'table_list':easy_admin.enabled_admins})
def menus_url_jump(request,menu_url):
	return HttpResponse(menu_url)
@login_required
def display_table_objs(request,app_name,table_name):
	admin_class = easy_admin.enabled_admins[app_name][table_name]
	if request.method=="POST":
		action=request.POST.get('action_def')
		pk_list=request.POST.get('action_pks').split(',')
		#生产上后台需要验证数据合法性
		selected_objs = admin_class.model.objects.filter(pk__in=pk_list)
		action_func = getattr(admin_class, action)
		request._admin_action = action
		return action_func(admin_class, request, selected_objs)
	object_list,filter_condtions = table_filter(request, admin_class)
	#搜索
	object_list=easy_search(request,object_list,admin_class)
	#排序 order_rule 排序规则 [排序名字，排序顺序]
	object_list,order_rule=easy_order(request,object_list,admin_class)
	paginator = Paginator(object_list,admin_class.list_per_page)  # Show 25 contacts per page
	page = request.GET.get('page')
	try:
		object_list=paginator.page(page)
	except PageNotAnInteger:
		object_list=paginator.page(1)
	except EmptyPage:
		object_list=paginator.page(paginator.num_pages)

	return render(request,'easyadmin/display_table.html',{"admin_class":admin_class,
	                                                      "filter_condtions":filter_condtions,
	                                                      "app_name":app_name,
	                                                      "table_name":table_name,
	                                                      'object_list':object_list,
	                                                      'order_rule':order_rule,
	                                                      'search_text':request.GET.get('_q','')})
@login_required
def table_obj_change(request,app_name,table_name,obj_pk):
	'''修改内容'''
	admin_class=easy_admin.enabled_admins[app_name][table_name]
	model_form_class = create_model_form(request, admin_class)
	#并不是所有的表都有id instance 填充数据
	pk_field=admin_class.model._meta.pk.name
	obj = admin_class.model.objects.get(pk=obj_pk)
	if request.method == "POST":
		print("change form", request.POST)
		form_obj = model_form_class(request.POST, instance=obj)  # 更新
		if form_obj.is_valid():
			form_obj.save()
			return redirect(request.path)
	else:
		form_obj = model_form_class(instance=obj)
	# object of type 'DynamicModelForm' has no len() 可以遍历但是没有len() 方法
		return render(request,'easyadmin/table_obj_change.html',{"form_obj":form_obj,
	                                                         'app_name':app_name,
	                                                         'admin_class':admin_class,
	                                                         'table_name':table_name,
	                                                         'obj_pk':obj_pk})
@login_required
def table_obj_add(request,app_name,table_name):
	'''添加内容'''
	admin_class = easy_admin.enabled_admins[app_name][table_name]
	model_form_class = create_model_form(request, admin_class)
	# 并不是所有的表都有id instance 填充数据
	if request.method == "POST":
		form_obj = model_form_class(request.POST)#添加数据
		if form_obj.is_valid():
			form_obj.save()
		return redirect(reverse("table_objs",args=(app_name,table_name)))
	else:
		form_obj = model_form_class()
	# object of type 'DynamicModelForm' has no len() 可以遍历但是没有len() 方法

	return render(request, 'easyadmin/table_obj_change.html', {"form_obj": form_obj})
@login_required
def table_obj_delete(request,app_name,table_name,pk_obj):
	#删除对象
	admin_class = easy_admin.enabled_admins[app_name][table_name]
	objs = admin_class.model.objects.get(pk=pk_obj)
	if request.method == "POST":
		objs.delete()
		return redirect(reverse('table_objs',args=(app_name,table_name)))

	return render(request, "easyadmin/table_obj_delete.html", {"objs": objs,
	                                                           "admin_class": admin_class,
	                                                           "app_name": app_name,
	                                                           "table_name": table_name
	                                                           })
@login_required
def password_reset(request,app_name,table_name,obj_id):

    admin_class = easy_admin.enabled_admins[app_name][table_name]
    model_form_class = create_model_form(request,admin_class)

    obj = admin_class.model.objects.get(id=obj_id)
    errors = {}
    if request.method == "POST":
        _password1 = request.POST.get("password1")
        _password2 = request.POST.get("password2")

        if _password1 == _password2:
            if len(_password2) >5:
                obj.set_password(_password1)
                obj.save()
                return redirect(request.path.rstrip("password/"))

            else:
                errors["password_too_short"] = "must not less than 6 letters"
        else:
            errors['invalid_password'] = "passwords are not the same"
    return render(request,'easyadmin/password_reset.html', {"obj":obj,'errors':errors})
