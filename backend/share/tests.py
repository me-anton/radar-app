from share.metaclasses import Singleton


def test_singleton():
    class SingleObj(metaclass=Singleton):
        pass
    obj1 = SingleObj()
    obj2 = SingleObj()
    assert obj1 is obj2, \
        'Singleton has created a new instance when there is one available'

    class SingleObj2(metaclass=Singleton):
        pass
    obj3 = SingleObj2()
    assert obj1 != obj3, \
        'Singleton has created a single instance for two different classes'
