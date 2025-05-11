import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker



logger = logging.getLogger(__name__)


class RepoBase:
    def __init__(self, db: AsyncEngine):
        self.db = db
        self.asmk = async_sessionmaker(self.db, expire_on_commit=False)
        self.curr_session = None
        self._ctx_manager = None
        self.in_transaction = False
    
    
    async def __aenter__(self):
        if self.curr_session is None:
            try:
                self.curr_session = self.asmk()
                self._ctx_manager = self.curr_session.begin()
                await self._ctx_manager.__aenter__()
            except Exception as e:
                logger.error(f"Error starting session: {e}")
                raise
        self.in_transaction = True
        return self
    
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.curr_session is None:
            logger.error("Session is None on __aexit__")
            raise RuntimeError("Session is not initialized before __aexit__")
        
        try:
            await self._ctx_manager.__aexit__(exc_type, exc_val, exc_tb)
            await self.curr_session.close()
        except Exception as e:
            logger.error(f"Error closing session: {e}")
            raise
        finally:
            self._ctx_manager = None
            self.curr_session = None
            self.in_transaction = False
    
    
    async def _commit_if_needed(self):
        if not self.in_transaction and self.curr_session:
            await self.curr_session.commit()
    
    
    async def get_all(self, entity_class, **kwargs):
        async with self.asmk() as sess:
            stmt = select(entity_class).filter_by(**kwargs)
            execres = await sess.execute(stmt)
            return execres.scalars().all()
    
    
    async def get_first(self, entity_class, **kwargs):
        async with self.asmk() as sess:
            stmt = select(entity_class).filter_by(**kwargs)
            execres = await sess.execute(stmt)
            return execres.scalars().first()
    
    
    async def create_if_none(self, ormobj, **kwargs):
        if not self.curr_session:
            raise RuntimeError("No active session. Use 'async with repo:'")
        
        stmt = select(ormobj.__class__).filter_by(**kwargs)
        execres = await self.curr_session.execute(stmt)
        obj = execres.scalars().first()
        if not obj:
            obj = ormobj
            self.curr_session.add(obj)
        return obj
    
    
    async def create(self, *args):
        if not self.curr_session:
            raise RuntimeError("No active session. Use 'async with repo:'")
        for arg in args:
            self.curr_session.merge(arg)
    
    
    async def upsert(self, *args):
        if not self.curr_session:
            raise RuntimeError("No active session. Use 'async with repo:'")
        for arg in args:
            self.curr_session.merge(arg)
    
    
    async def delete(self, *args):
        if not self.curr_session:
            raise RuntimeError("No active session. Use 'async with repo:'")
        for arg in args:
            self.curr_session.delete(arg)
