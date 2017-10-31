from django import template
from django.utils.safestring import mark_safe
from django.utils.timezone import datetime,timedelta
register = template.Library()

@register.simple_tag
def render_table_name(admin_class):
    '''返回表名'''
    return admin_class.model._meta.verbose_name

@register.simple_tag
def get_query_sets(admin_class):
    return admin_class.model.objects.all()

@register.simple_tag
def build_table_row(request,obj,admin_class):
    pk_field=admin_class.model._meta.pk.name
    obj_pk=getattr(obj,pk_field)
    row_ele = ""
    for index,column in enumerate(admin_class.list_display):
        field_obj = obj._meta.get_field(column)
        if field_obj.choices:#choices type
            column_data = getattr(obj,"get_%s_display" % column)()
        else:
            column_data = getattr(obj,column)
        if type(column_data).__name__ == 'datetime':
            column_data = column_data.strftime("%Y-%m-%d %H:%M:%S")
        if index==0:
            column_data = "<a href='{request_path}/{obj_pk}/change/'>{data}</a>".format(request_path=request.path,
                                                                                       obj_pk=obj_pk,
                                                                                       data=column_data)
        row_ele += "<td>%s</td>" % column_data
    return mark_safe(row_ele)
@register.simple_tag()
def easypaginator(request,object_list):
    """now_page:当前页
        show_page：需要显示多少页
        num_pages：总共有多少页
    """
    now_page=object_list.number
    show_page=6
    num_pages=object_list.paginator.num_pages
    base_url=""
    for k,v in request.GET.items():
        if k=='page':
            continue
        if v:
            base_url+="&%s=%s" %(k,v)
    if num_pages <= show_page:
        """如果总页数小于需要展示的页数 那么久把所有的页码都打出来吧"""
        start_page=1
        end_page=num_pages
    else:
        start_page = now_page - (show_page - 1) / 2
        end_page = now_page + (show_page - 1) / 2
        if start_page <= 0:
            start_page = 1
            end_page = start_page + show_page - 1
        if end_page >= num_pages:
            end_page = num_pages
            start_page = num_pages - show_page + 1
    str_list = []
    if now_page == 1:
        prevpage = '<li class="disabled"><a>上一页</a></li>'
    else:
        active_url="?page=%s" % str(now_page-1)
        prevpage = '<li><a href=%s>上一页</a></li>' %(active_url+base_url)
    if now_page == num_pages:
        lastpage = '<li class="disabled" ><a href="#">下一页</a></li>'
    else:
        active_url = "?page=%s" % str(now_page + 1)
        lastpage='<li><a class="" href=%s>下一页</a></li>' %(active_url+base_url)
    str_list.append(prevpage)
    for i in range(int(start_page), int(end_page + 1)):
        if i == now_page:
            active_url = "?page=%s" % str(i)
            tmp = '<li class="active" ><a href=%s >%s</a></li>' %(active_url+base_url,str(i))
        else:
            active_url = "?page=%s" % str(i)
            tmp = '<li class="" ><a href=%s >%s</a></li>' % (active_url + base_url, str(i))
        str_list.append(tmp)
    str_list.append(lastpage)
    omit='<li class="" ><a>....</a></li>'
    if num_pages > show_page:
        str_list.insert(int(len(str_list)/2),omit)
    str_list = mark_safe("".join(str_list))
    return str_list
# @register.simple_tag
# def render_page_ele(loop_counter,query_sets):
#
#     if abs(query_sets.number - loop_counter) <= 1:
#         ele_class = ""
#         if query_sets.number == loop_counter:
#             ele_class = "active"
#         ele = '''<li class="%s"><a href="?page=%s">%s</a></li>''' %(ele_class,loop_counter,loop_counter)
#
#         return mark_safe(ele)
#
#     return ''

@register.simple_tag
def render_filter_ele(condtion,admin_class,filter_condtions):
    #filter_conditions 过滤条件
    select_ele = '''<select class="form-control" name='%s' ><option value=''>%s</option>''' % (condtion, condtion)
    field_obj = admin_class.model._meta.get_field(condtion)
    if field_obj.choices:
        selected = ''
        for choice_item in field_obj.choices:
            # print("choice",choice_item,filter_condtions.get(condtion),type(filter_condtions.get(condtion)))
            if filter_condtions.get(condtion) == str(choice_item[0]):
                selected ="selected"

            select_ele += '''<option value='%s' %s>%s</option>''' %(choice_item[0],selected,choice_item[1])
            selected =''

    if type(field_obj).__name__ == "ForeignKey":
        selected = ''
        for choice_item in field_obj.get_choices()[1:]:
            if filter_condtions.get(condtion) == str(choice_item[0]):
                selected = "selected"
            select_ele += '''<option value='%s' %s>%s</option>''' %(choice_item[0],selected,choice_item[1])
            selected = ''
    #时间过滤
    if type(field_obj).__name__ in ['DateTimeField','DateField']:
        select_ele = '''<select class="form-control" name='%s__gte' ><option value=''>%s</option>''' % (condtion, condtion)
        date_els=[]
        today_ele=datetime.now().date()
        date_els.append(['今天',today_ele])
        date_els.append(['昨天',today_ele-timedelta(days=1)])
        date_els.append(['近7天', today_ele - timedelta(days=7)])
        date_els.append(['近30天', today_ele - timedelta(days=30)])
        date_els.append(['本月', today_ele.replace(day=1)])
        date_els.append(['本年', today_ele.replace(day=1,month=1)])
        for item in date_els:
            select_ele+='''<option value='%s'>%s</option>'''%(item[1],item[0])
    select_ele += "</select>"
    return mark_safe(select_ele)
@register.simple_tag()
def render_order_url(filter_condtions,order_rule,obj):
    #生产带过滤的排序url 避免排序后过滤功能失效
    base_url="?"
    for k,v in filter_condtions.items():
        base_url+="%s=%s&" %(k,v)
    if not order_rule or  obj!=order_rule[0]:
        href=base_url+"o=%-s" % obj
        return href
    else:
        if order_rule[1]==0:
            href=base_url+"o=%s" % obj
        else:
            href=base_url+"o=-%s" % obj
        return href
@register.simple_tag()
def render_now_way(request):
    pathstr="<li><a href=%s>Home</a></li>" %"{% url """
    print(request.path)
    now_way=request
    return now_way



def recursive_related_objs_lookup(objs):
    model_name = objs[0]._meta.model_name
    ul_ele = "<ul>"
    for obj in objs:
        li_ele = '''<li> %s: %s </li>'''%(obj._meta.verbose_name,obj.__str__().strip("<>"))
        ul_ele += li_ele
        for m2m_field in obj._meta.local_many_to_many: #把所有跟这个对象直接关联的m2m字段取出来了
            sub_ul_ele = "<ul>"
            m2m_field_obj = getattr(obj,m2m_field.name) #getattr(customer, 'tags')
            for content in m2m_field_obj.select_related():# customer.tags.all()
                li_ele = '''<li> %s: %s </li>''' % (m2m_field.verbose_name, content.__str__().strip("<>"))
                sub_ul_ele +=li_ele

            sub_ul_ele += "</ul>"
            ul_ele += sub_ul_ele  #最终跟最外层的ul相拼接
        for related_obj in obj._meta.related_objects:#获取与customer表有关联的所有表 ForeignKey('customer')
            if 'ManyToManyRel' in related_obj.__repr__():#判断类型
                if hasattr(obj, related_obj.get_accessor_name()):  # hassattr(customer,'enrollment_set')
                    accessor_obj = getattr(obj, related_obj.get_accessor_name())
                    print("-------ManyToManyRel",accessor_obj,related_obj.get_accessor_name())
                    # 上面accessor_obj 相当于 customer.enrollment_set
                    if hasattr(accessor_obj, 'select_related'):  # slect_related() == all()
                        target_objs = accessor_obj.select_related()  # .filter(**filter_coditions)
                        # target_objs 相当于 customer.enrollment_set.all()

                        sub_ul_ele ="<ul style='color:red'>"
                        print(target_objs,'ta')
                        for o in target_objs:
                            li_ele = '''<li> %s: %s </li>''' % (o._meta.verbose_name, o.__str__().strip("<>"))
                            sub_ul_ele += li_ele
                        sub_ul_ele += "</ul>"
                        ul_ele += sub_ul_ele

            elif hasattr(obj,related_obj.get_accessor_name()): # hassattr(customer,'enrollment_set')
                accessor_obj = getattr(obj,related_obj.get_accessor_name())
                #上面accessor_obj 相当于 customer.enrollment_set
                if hasattr(accessor_obj,'select_related'): # slect_related() == all()
                    target_objs = accessor_obj.select_related() #获取关于customer的queryset
                    # target_objs 相当于 customer.enrollment_set.all()
                else:
                    print("one to one i guess:",accessor_obj)
                    target_objs = accessor_obj
                # print(target_objs,'target')
                if len(target_objs) >0:
                    #nodes = recursive_related_objs_lookup(target_objs,model_name)
                    nodes = recursive_related_objs_lookup(target_objs)#除了many_to_many类型都需要递归下去
                    ul_ele += nodes
    ul_ele +="</ul>"
    return ul_ele
@register.simple_tag
def display_obj_related(objs):
    '''把对象及所有相关联的数据取出来'''
    print(objs)
    if not hasattr(objs,'all'):
        objs = [objs,] #fake
        print('单个对象')
    if objs:
        print(objs)
        model_class = objs[0]._meta.model
        return mark_safe(recursive_related_objs_lookup(objs))
@register.simple_tag
def render_web_path(request,admin_class):
    pweb=request.get_full_path().split("/")[1:]
    print(pweb)
    if len(pweb)==1:
        return mark_safe("")
    if len(pweb)==2:
        app_name=admin_class[pweb[1]].verbose_name
        print(app_name)
        return mark_safe("")
    if len(pweb)==3:
        app_name=admin_class[pweb[1]].verbose_name
        print(app_name)
        return mark_safe("")