from django.forms import forms,ModelForm
from django.utils.translation import ugettext as _
from django.forms import ValidationError
def create_model_form(request,admin_class):
	def __new__(cls, *args, **kwargs):
		# print("base fields", cls.base_fields)
		for field_name, field_obj in cls.base_fields.items():
			if admin_class.readonly_table:
				field_obj.widget.attrs['disabled'] = 'disabled' #这里可给标签添加样式
			if hasattr(admin_class, "clean_%s" % field_name):
				field_clean_func = getattr(admin_class, "clean_%s" % field_name)
				setattr(cls, "clean_%s" %field_name,field_clean_func)
			#加了上面这一段出现验证的数据无法保存
		return ModelForm.__new__(cls)
	def default_clean(self):
		'''给所有的form默认加一个clean验证 post才来'''
		error_list = []
		# readonly_table check raise errors
		if admin_class.readonly_table:
			raise ValidationError(
				_('Table is  readonly,cannot be modified or added'),
				code='invalid'
			)
		# invoke user's cutomized form validation
		self.ValidationError = ValidationError
		response = admin_class.default_form_validation(self)
		if response:
			error_list.append(response)
		if error_list:
			raise ValidationError(error_list)
	class Meta:
		model=admin_class.model
		fields='__all__'
	attrs={'Meta':Meta}
	_model_form_class=type("DynamicModelForm",(ModelForm,),attrs)
	setattr(_model_form_class, '__new__',__new__)
	setattr(_model_form_class, 'clean', default_clean)

	return _model_form_class