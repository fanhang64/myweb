class BaseException(Exception):
    errcode = 1000
    errmsg = 'Server Unkown Error.'

    def __init__(self, errmsg=None, errcode=None, **kw):
        if errmsg:
            self.errmsg = errmsg
        if errcode is not None:
            self.errcode = errcode
        self.kw = kw

    def __str__(self):
        return '%d: %s' % (self.errcode, self.errmsg)

    def __repr__(self):
        return '<%s \'%s\'>' % (self.__class__.__name__, self)


class FormValidationError(BaseException):
    errcode = 2001
    errmsg = '表单验证错误'

    def __init__(self, form, errmsg=None, show_first_err=True):
        if not errmsg and show_first_err:
            name, errors = next(iter(form.errors.items()))
            errmsg = f'{getattr(form, name).label.text}: {errors[0]}'
        super(FormValidationError, self).__init__(errmsg)
        self.errors = form.errors


class ParameterError(BaseException):
    errcode = -1
    errmsg = '参数错误'
