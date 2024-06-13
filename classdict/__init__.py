class ClassDict(dict):
    """
    Get attributes

    >>> d = ClassDict({'foo':3})
    >>> d['foo']
    3
    >>> d.foo
    3
    >>> d.bar
    Traceback (most recent call last):
    ...
    AttributeError: 'ClassDict' object has no attribute 'bar'

    Works recursively

    >>> d = ClassDict({'foo':3, 'bar':{'x':1, 'y':2}})
    >>> isinstance(d.bar, dict)
    True
    >>> d.bar.x
    1

    Bullet-proof

    >>> ClassDict({})
    {}
    >>> ClassDict(d={})
    {}
    >>> ClassDict(None)
    {}
    >>> d = {'a': 1}
    >>> ClassDict(**d)
    {'a': 1}
    >>> ClassDict((('a', 1), ('b', 2)))
    {'a': 1, 'b': 2}
    
    Set attributes

    >>> d = ClassDict()
    >>> d.foo = 3
    >>> d.foo
    3
    >>> d.bar = {'prop': 'value'}
    >>> d.bar.prop
    'value'
    >>> d
    {'foo': 3, 'bar': {'prop': 'value'}}
    >>> d.bar.prop = 'newer'
    >>> d.bar.prop
    'newer'
    >>> d.lst = [1, 2, 3]
    >>> d.lst
    [1, 2, 3]
    >>> d.tpl = (1, 2, 3)
    >>> d.tpl
    (1, 2, 3)


    Values extraction

    >>> d = ClassDict({'foo':0, 'bar':[{'x':1, 'y':2}, {'x':3, 'y':4}]})
    >>> isinstance(d.bar, list)
    True
    >>> from operator import attrgetter
    >>> list(map(attrgetter('x'), d.bar))
    [1, 3]
    >>> list(map(attrgetter('y'), d.bar))
    [2, 4]
    >>> d = ClassDict()
    >>> list(d.keys())
    []
    >>> d = ClassDict(foo=3, bar=dict(x=1, y=2))
    >>> d.foo
    3
    >>> d.bar.x
    1

    Still like a dict though

    >>> o = ClassDict({'clean':True})
    >>> list(o.items())
    [('clean', True)]

    And like a class

    >>> class Flower(ClassDict):
    ...     power = 1
    ...     mean = {}
    ...     color = {"r": 100, "g": 0, "b": 0}
    ...
    >>> f = Flower()
    >>> f.power
    1
    >>> f.color.r
    100
    >>> f.mean.x = 10
    >>> f.mean.x
    10
    >>> f = Flower({'height': 12})
    >>> f.height
    12
    >>> f['power']
    1
    >>> sorted(f.keys())
    ['color', 'height', 'mean', 'power']

    update and pop items
    >>> d = ClassDict(a=1, b='2')
    >>> e = ClassDict(c=3.0, a=9.0)
    >>> d.update(e)
    >>> d.c
    3.0
    >>> d['c']
    3.0
    >>> d.get('c')
    3.0
    >>> d.update(a=4, b=4)
    >>> d.b
    4
    >>> d.pop('a')
    4
    >>> d.a
    Traceback (most recent call last):
    ...
    AttributeError: 'ClassDict' object has no attribute 'a'
    >>> d.pop('a', 8)
    8
    >>> d.pop('b', 100)
    4
    >>> d
    {'c': 3.0}
    """
    def __init__(self, d=None, **kwargs):
        if d is None:
            d = {}
        else:
            d = dict(d)        
        if kwargs:
            d.update(**kwargs)
        for k, v in d.items():
            setattr(self, k, v)
        # Class attributes
        for k in self.__class__.__dict__.keys():
            if not (k.startswith('__') and k.endswith('__')) and k not in ('update', 'pop', 'rebuild_dict'):
                setattr(self, k, getattr(self, k))

    def __setattr__(self, name, value):
        if isinstance(value, (list, tuple)):
            value = type(value)(self.__class__(x)
                     if isinstance(x, dict) else x for x in value)
        elif isinstance(value, dict) and not isinstance(value, ClassDict):
            value = ClassDict(value)
        super(ClassDict, self).__setattr__(name, value)
        super(ClassDict, self).__setitem__(name, value)

    __setitem__ = __setattr__

    def __reduce__(self):
        return dict, (self.__dict__,)

    def __asdict__(self, recurse=True):
        # https://github.com/makinacorpus/ClassDict/issues/48
        # 此函数 在处理 io_buffer 类的深度拷贝的时候出错, 先暂时保留相关代码
        if recurse:
            _r = self.__class__.__reduce__
            self.__class__.__reduce__ = lambda obj: (dict, (obj.__dict__,),)
            from copy import deepcopy
            _c = deepcopy(self.__dict__)
            self.__class__.__reduce__ = _r
            return _c
        else:
            return dict(self.__dict__)

    def update(self, e=None, **f):
        d = e or dict()
        d.update(f)
        for k in d:
            setattr(self, k, d[k])

    def pop(self, k, *args):
        if hasattr(self, k):
            delattr(self, k)
        return super(ClassDict, self).pop(k, *args)

    def rebuild_dict(self):
        """
        功能: 对象本身会被修复, 并返回一个重建的普通dict
        """
        def iter_node(data):
            if isinstance(data, self.__class__):
                new_dict = {}
                for key, value in data.__dict__.items():
                    if isinstance(value, self.__class__):
                        new_dict[key] = iter_node(value)
                    elif isinstance(value, dict):
                        new_dict[key] = iter_node(value)
                    elif isinstance(value, list):  # 列表里面为列表的情况:
                        new_dict[key] = iter_node(value)
                    else:
                        new_dict[key] = value
                return new_dict
            elif isinstance(data, dict):
                new_dict = {}
                for key, value in data.items():
                    if isinstance(value, self.__class__):
                        new_dict[key] = iter_node(value)
                    elif isinstance(value, dict):  # 列表里面为字典的情况
                        new_dict[key] = iter_node(value)
                    elif isinstance(value, list):  # 列表里面为列表的情况:
                        new_dict[key] = iter_node(value)
                    else:
                        new_dict[key] = value
                return new_dict
            elif isinstance(data, list):
                new_list = []
                for item in data:
                    if isinstance(item, self.__class__):
                        new_list.append(iter_node(item))
                    elif isinstance(item, dict):  # 列表里面为字典的情况
                        new_list.append(iter_node(item))
                    elif isinstance(item, list):  # 列表里面为列表的情况:
                        new_list.append(iter_node(item))
                    else:
                        new_list.append(item)
                return new_list
            else:
                raise

        return iter_node(self)

if __name__ == "__main__":
    import doctest
    doctest.testmod()


if __name__ == "__main__":
    hello = {
        "a": 22,
        "b": "nice"
    }

    cd = ClassDict(hello)
    new_cd = cd.rebuild_dict()
    print("cd.a", cd.a)
    print("new_cd", new_cd)
