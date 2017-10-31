from django.db.models import Q

def table_filter(request,admin_class):
    '''进行条件过滤并返回过滤后的数据'''
    filter_conditions = {}
    for k,v in request.GET.items():
        #k.replace(__gte)是为了把时间过滤添加到条件过滤中
        if v and k.replace('__gte','') in admin_class.list_filters:
            filter_conditions[k]=v
    return admin_class.model.objects.filter(**filter_conditions),filter_conditions
def easy_order(request,obj_list,admin_class):
    '''从request中获取排序规则 从obj中获取数据，admin_class中对验证排序有效性
        返回排序后的数据 和排序规则 排序规则用于前端生成href
    '''
    order_key = request.GET.get('o')
    if not order_key or order_key.strip('-') not in admin_class.list_display :
        return obj_list,None
    else:
        rule=0 if order_key[0]=='-' else 1
        order_rule=[order_key.strip('-'),rule]
        return obj_list.order_by(order_key),order_rule
def easy_search(request,obj_list,admin_class):
    '''从rquest中获取搜索关键字吗，admin_class中遍历需要搜索的字段'''
    search_key=request.GET.get('_q','')
    if not search_key:
        return obj_list
    con=Q()
    #定义搜索方式  ’或‘搜索
    con.connector='OR'
    for column in admin_class.list_search:
        #contains 模糊搜索
        con.children.append(("%s__contains"%column,search_key))
    return obj_list.filter(con)