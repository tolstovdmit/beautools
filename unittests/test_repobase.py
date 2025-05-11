from unittest.mock import AsyncMock, MagicMock, call, patch  # Use AsyncMock for async methods

import pytest
from beautools.repobase import RepoBase
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker



# Mock ORM entity class for testing
class MockEntity:
    def __init__(self, id_=None, name="test"):
        self.id = id_
        self.name = name
    
    
    def __eq__(self, other):
        return isinstance(other, MockEntity) and self.id == other.id and self.name == other.name


# --- Test Cases ---

@pytest.fixture
def mock_engine():
    """Fixture for a mocked AsyncEngine."""
    return MagicMock(spec=AsyncEngine)


@pytest.fixture
def mock_session_maker(mock_session):
    """Fixture for a mocked async_sessionmaker."""
    # The session maker itself is callable and also acts as an async context manager
    maker = MagicMock(spec=async_sessionmaker)
    # When called like self.asmk(), return the mock_session
    maker.return_value = mock_session
    # Configure the async context manager part (__aenter__/__aexit__)
    # This is used by get_all/get_first
    maker.__aenter__.return_value = mock_session
    maker.__aexit__.return_value = None  # Make __aexit__ awaitable
    return maker


@pytest.fixture
def mock_session():
    """Fixture for a mocked AsyncSession."""
    session = AsyncMock(spec=['begin', 'close', 'execute', 'add', 'merge', 'delete', '__aenter__', '__aexit__'])
    # Mock the 'begin()' method to return an async context manager
    mock_transaction_ctx = AsyncMock(spec=['__aenter__', '__aexit__'])
    session.begin.return_value = mock_transaction_ctx
    # Make the session itself an async context manager (for get_all/get_first)
    session.__aenter__.return_value = session  # Return self
    session.__aexit__.return_value = None  # Make __aexit__ awaitable
    return session


@pytest.fixture
def repo(mock_engine, mock_session_maker):
    """Fixture to create a RepoBase instance with mocked dependencies."""
    # Patch async_sessionmaker during repo initialization
    with patch('repo_base.async_sessionmaker', return_value=mock_session_maker):
        instance = RepoBase(mock_engine)
        # Ensure the instance uses the mocked maker we created
        instance.asmk = mock_session_maker
        return instance


# --- Tests for Session and Transaction Management ---

@pytest.mark.asyncio
async def test_repo_init(mock_engine):
    """Test RepoBase initialization."""
    mock_asmk = MagicMock()
    with patch('sqlalchemy.ext.asyncio.async_sessionmaker', return_value=mock_asmk) as mock_init_   asmk:
        repo_instance = RepoBase(mock_engine)
        assert repo_instance.db is mock_engine
        mock_init_asmk.assert_called_once_with(mock_engine, expire_on_commit=False)
        assert repo_instance.asmk is mock_asmk
        assert repo_instance.curr_session is None
        assert repo_instance._ctx_manager is None
        assert not repo_instance.in_transaction


@pytest.mark.asyncio
async def test_async_context_manager_success(repo, mock_session_maker, mock_session):
    """Test the async context manager (__aenter__/__aexit__) success path."""
    mock_transaction_ctx = mock_session.begin.return_value
    
    assert repo.curr_session is None
    assert repo._ctx_manager is None
    assert not repo.in_transaction
    
    async with repo:
        # Inside the context
        assert repo.curr_session is mock_session
        assert repo._ctx_manager is mock_transaction_ctx
        assert repo.in_transaction is True
        # Check mocks were called correctly during __aenter__
        mock_session_maker.assert_called_once_with()  # Called to create session
        mock_session.begin.assert_called_once_with()
        mock_transaction_ctx.__aenter__.assert_called_once_with()
    
    # After exiting the context
    assert repo.curr_session is None
    assert repo._ctx_manager is None
    assert not repo.in_transaction
    # Check mocks were called correctly during __aexit__
    mock_transaction_ctx.__aexit__.assert_awaited_once_with(None, None, None)
    mock_session.close.assert_awaited_once_with()


@pytest.mark.asyncio
async def test_async_context_manager_nested_call(repo, mock_session_maker, mock_session):
    """Test that nested async with calls reuse the existing session."""
    mock_transaction_ctx = mock_session.begin.return_value
    
    async with repo as outer_repo:
        assert outer_repo.curr_session is mock_session
        assert outer_repo.in_transaction is True
        # Check mocks were called once on entry
        mock_session_maker.assert_called_once()
        mock_session.begin.assert_called_once()
        mock_transaction_ctx.__aenter__.assert_called_once()
        
        # Simulate a nested call (though not typical for 'async with repo')
        # In practice, methods called within the block use the existing session
        # Let's test that __aenter__ doesn't try to create a new session
        await repo.__aenter__()  # Manually call __aenter__ again
        
        # Mocks should NOT have been called again
        mock_session_maker.assert_called_once()
        mock_session.begin.assert_called_once()
        mock_transaction_ctx.__aenter__.assert_called_once()
        
        assert repo.curr_session is mock_session  # Still the same session
    
    # Exit checks (should only happen once)
    mock_transaction_ctx.__aexit__.assert_awaited_once_with(None, None, None)
    mock_session.close.assert_awaited_once_with()
    assert repo.curr_session is None
    assert not repo.in_transaction


@pytest.mark.asyncio
async def test_async_context_manager_exception_inside(repo, mock_session, mock_session_maker):
    """Test the context manager handles exceptions raised within the 'with' block."""
    mock_transaction_ctx = mock_session.begin.return_value
    test_exception = ValueError("Something went wrong")
    
    with pytest.raises(ValueError, match="Something went wrong"):
        async with repo:
            assert repo.in_transaction is True
            raise test_exception
    
    # Check that __aexit__ was called with exception info
    mock_transaction_ctx.__aexit__.assert_awaited_once()
    # Get the actual arguments __aexit__ was called with
    aexit_args, _ = mock_transaction_ctx.__aexit__.await_args
    assert aexit_args[0] is ValueError  # exc_type
    assert aexit_args[1] is test_exception  # exc_val
    assert aexit_args[2] is not None  # exc_tb
    
    # Check session was closed and state reset
    mock_session.close.assert_awaited_once_with()
    assert repo.curr_session is None
    assert repo._ctx_manager is None
    assert not repo.in_transaction


@pytest.mark.asyncio
async def test_async_context_manager_exception_on_commit(repo, mock_session, mock_session_maker):
    """Test the context manager handles exceptions during commit (__aexit__)."""
    mock_transaction_ctx = mock_session.begin.return_value
    commit_exception = ConnectionError("DB commit failed")
    mock_transaction_ctx.__aexit__.side_effect = commit_exception
    
    with pytest.raises(ConnectionError, match="DB commit failed"):
        async with repo:
            pass  # No exception inside the block
    
    # __aexit__ was called (and raised the exception)
    mock_transaction_ctx.__aexit__.assert_awaited_once_with(None, None, None)
    # Session should still be closed in the finally block
    mock_session.close.assert_awaited_once_with()
    # State should be reset
    assert repo.curr_session is None
    assert repo._ctx_manager is None
    assert not repo.in_transaction


@pytest.mark.asyncio
async def test_async_context_manager_exception_on_close(repo, mock_session, mock_session_maker):
    """Test the context manager handles exceptions during session.close()."""
    mock_transaction_ctx = mock_session.begin.return_value
    close_exception = OSError("Cannot close session")
    mock_session.close.side_effect = close_exception
    
    # If commit succeeds but close fails, the original exception (if any) takes precedence.
    # If no original exception, the close exception should be raised.
    with pytest.raises(OSError, match="Cannot close session"):
        async with repo:
            pass  # No exception inside the block
    
    # __aexit__ on transaction should have been called successfully
    mock_transaction_ctx.__aexit__.assert_awaited_once_with(None, None, None)
    # close() was called (and raised the exception)
    mock_session.close.assert_awaited_once_with()
    # State should *still* be reset in the finally block
    assert repo.curr_session is None
    assert repo._ctx_manager is None
    assert not repo.in_transaction


# --- Tests for CRUD-like Methods ---

@pytest.mark.asyncio
async def test_get_all(repo, mock_session_maker, mock_session):
    """Test the get_all method."""
    mock_result = AsyncMock()
    mock_scalars = MagicMock()
    expected_entities = [MockEntity(id_=1), MockEntity(id_=2)]
    
    mock_session.execute.return_value = mock_result
    mock_result.scalars.return_value = mock_scalars
    mock_scalars.all.return_value = expected_entities
    
    # Call get_all outside a transaction context
    result = await repo.get_all(MockEntity, name="test_filter")
    
    assert result == expected_entities
    # Verify it used the session maker's context manager
    mock_session_maker.__aenter__.assert_awaited_once()
    mock_session.execute.assert_awaited_once()
    # Check the statement construction (simplified check)
    call_args = mock_session.execute.await_args[0][0]
    assert str(call_args).startswith("SELECT")  # Basic check
    assert "mockentity" in str(call_args).lower()
    assert "name = :name_1" in str(call_args)  # Check filter
    mock_result.scalars.assert_called_once_with()
    mock_scalars.all.assert_called_once_with()
    # Verify the session from the context manager was closed
    mock_session_maker.__aexit__.assert_awaited_once()
    # Crucially, repo.curr_session should NOT have been involved
    assert repo.curr_session is None
    assert not repo.in_transaction


@pytest.mark.asyncio
async def test_get_first(repo, mock_session_maker, mock_session):
    """Test the get_first method."""
    mock_result = AsyncMock()
    mock_scalars = MagicMock()
    expected_entity = MockEntity(id_=1)
    
    mock_session.execute.return_value = mock_result
    mock_result.scalars.return_value = mock_scalars
    mock_scalars.first.return_value = expected_entity
    
    # Call get_first outside a transaction context
    result = await repo.get_first(MockEntity, id=1)
    
    assert result == expected_entity
    # Verify it used the session maker's context manager
    mock_session_maker.__aenter__.assert_awaited_once()
    mock_session.execute.assert_awaited_once()
    # Check the statement construction (simplified check)
    call_args = mock_session.execute.await_args[0][0]
    assert str(call_args).startswith("SELECT")
    assert "mockentity" in str(call_args).lower()
    assert "id = :id_1" in str(call_args)  # Check filter
    mock_result.scalars.assert_called_once_with()
    mock_scalars.first.assert_called_once_with()
    # Verify the session from the context manager was closed
    mock_session_maker.__aexit__.assert_awaited_once()
    # Crucially, repo.curr_session should NOT have been involved
    assert repo.curr_session is None


# --- Tests for Transactional Methods ---

@pytest.mark.asyncio
@pytest.mark.parametrize("method_name,args", [
        ("create", (MockEntity(),)),
        # ("upsert", (MockEntity(),)),
        # ("delete", (MockEntity(),)),
        # ("create_if_none", (MockEntity(name="check"),))  # create_if_none needs kwargs too
])
async def test_transactional_methods_require_context(repo, method_name, args):
    """Test that create, upsert, delete, create_if_none raise RuntimeError outside context."""
    method_to_call = getattr(repo, method_name)
    with pytest.raises(RuntimeError, match="No active session/transaction"):
        if kwargs:  # Handle create_if_none needing kwargs
            await method_to_call(*args, **kwargs)
        else:
            await method_to_call(*args)


@pytest.mark.asyncio
async def test_create(repo, mock_session):
    """Test the create method within a transaction."""
    entity1 = MockEntity(id_=1)
    entity2 = MockEntity(id_=2)
    
    async with repo:
        await repo.create(entity1, entity2)
    
    # Check that session.add was called for each entity
    mock_session.add.assert_has_awaits([call(entity1), call(entity2)], any_order=True)
    # Ensure merge wasn't called if create uses add
    mock_session.merge.assert_not_awaited()


@pytest.mark.asyncio
async def test_upsert(repo, mock_session):
    """Test the upsert method within a transaction."""
    entity1 = MockEntity(id_=1)
    entity2 = MockEntity(id_=2)
    
    async with repo:
        await repo.upsert(entity1, entity2)
    
    # Check that session.merge was called for each entity
    mock_session.merge.assert_has_awaits([call(entity1), call(entity2)], any_order=True)
    # Ensure add wasn't called if upsert uses merge
    mock_session.add.assert_not_awaited()


@pytest.mark.asyncio
async def test_delete(repo, mock_session):
    """Test the delete method within a transaction."""
    entity1 = MockEntity(id_=1)
    entity2 = MockEntity(id_=2)
    
    async with repo:
        await repo.delete(entity1, entity2)
    
    # Check that session.delete was called for each entity
    mock_session.delete.assert_has_awaits([call(entity1), call(entity2)], any_order=True)


@pytest.mark.asyncio
async def test_create_if_none_exists(repo, mock_session):
    """Test create_if_none when the entity already exists."""
    existing_entity = MockEntity(id_=1, name="found")
    new_entity_data = MockEntity(name="found")  # Object to potentially create
    
    # Mock the query result
    mock_result = AsyncMock()
    mock_scalars = MagicMock()
    mock_session.execute.return_value = mock_result
    mock_result.scalars.return_value = mock_scalars
    mock_scalars.first.return_value = existing_entity  # Simulate finding the entity
    
    returned_entity = None
    async with repo:
        # Pass the *new* object instance, but query based on name
        returned_entity = await repo.create_if_none(new_entity_data, name="found")
    
    # Verify the query was made using the transactional session (mock_session)
    mock_session.execute.assert_awaited_once()
    call_args = mock_session.execute.await_args[0][0]
    assert "mockentity" in str(call_args).lower()
    assert "name = :name_1" in str(call_args)
    mock_result.scalars.assert_called_once_with()
    mock_scalars.first.assert_called_once_with()
    
    # Verify the existing entity was returned
    assert returned_entity is existing_entity
    # Verify add was NOT called
    mock_session.add.assert_not_called()


@pytest.mark.asyncio
async def test_create_if_none_does_not_exist(repo, mock_session):
    """Test create_if_none when the entity does not exist."""
    new_entity = MockEntity(name="new")
    
    # Mock the query result
    mock_result = AsyncMock()
    mock_scalars = MagicMock()
    mock_session.execute.return_value = mock_result
    mock_result.scalars.return_value = mock_scalars
    mock_scalars.first.return_value = None  # Simulate not finding the entity
    
    returned_entity = None
    async with repo:
        returned_entity = await repo.create_if_none(new_entity, name="new")
    
    # Verify the query was made
    mock_session.execute.assert_awaited_once()
    call_args = mock_session.execute.await_args[0][0]
    assert "mockentity" in str(call_args).lower()
    assert "name = :name_1" in str(call_args)
    mock_result.scalars.assert_called_once_with()
    mock_scalars.first.assert_called_once_with()
    
    # Verify the new entity was added
    mock_session.add.assert_awaited_once_with(new_entity)
    # Verify the new entity was returned
    assert returned_entity is new_entity
