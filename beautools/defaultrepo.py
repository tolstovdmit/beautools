class DefaultRepo:
    
    def __init__(self):
        self.get_session = None
        self.get_async_session = None
    
    
    def get_all(self, entity_class, **kwargs):
        with self.get_async_session() as sess:
            return sess.query(entity_class).filter_by(**kwargs).all()
    
    
    def get_first(self, entity_class, id_=None, **kwargs):
        with self.get_async_session() as sess:
            return sess.query(entity_class).filter_by(**kwargs).first()
    
    
    def get_or_create(self, entity_class, id_=None, **kwargs):
        with self.get_async_session() as sess:
            obj = sess.query(entity_class).filter_by(**kwargs).first()
            if not obj:
                obj = entity_class(**kwargs)
                sess.add(obj)
            sess.commit()
            return obj
    
    
    def create_if_none(self, ormobj, **kwargs):
        with self.get_async_session() as sess:
            obj = sess.query(ormobj.__class__).filter_by(**kwargs).first()
            if not obj:
                obj = ormobj
                sess.add(obj)
            sess.commit()
            return obj
    
    
    def save(self, *args):
        with self.get_session() as sess:
            sess.add_all(args)
            sess.commit()
    
    
    def asave(self, *args):
        with self.get_async_session() as sess:
            sess.add_all(args)
            sess.commit()
    
    
    def delete(self, *args):
        with self.get_async_session() as sess:
            for a in args:
                sess.delete(a)
            sess.commit()
