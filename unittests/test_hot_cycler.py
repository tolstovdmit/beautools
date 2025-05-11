import pytest
import asyncio
import datetime
import time_machine



def test_refresh_sleeptime_error():
    from beautools import HotAsyncCycler
    cycler = HotAsyncCycler("test_cycler")
    cycler.ERROR_SLEEP = 42
    # When there is an error, ERROR_SLEEP should be returned regardless of other flags
    assert cycler.refresh_sleeptime(was_work=False, was_error=True) == 42


@time_machine.travel(datetime.datetime(2025, 4, 28, 11, 0, 0, tzinfo=datetime.timezone(offset=0)))
def test_is_hot_now_within_hot_times():
    from beautools import HotAsyncCycler
    HotAsyncCycler.HOT_TIMES = [
            (datetime.time(9, 0), datetime.time(11, 0)),
    ]
    
    assert HotAsyncCycler.is_hot_now() is True


@time_machine.travel(datetime.datetime(2025, 4, 28, 8, 0, 0))
def test_is_hot_now_outside_hot_times():
    from beautools import HotAsyncCycler
    
    HotAsyncCycler.HOT_TIMES = [
            (datetime.time(9, 0, 0), datetime.time(11, 0, 0)),
    ]
    assert HotAsyncCycler.is_hot_now() is False


@time_machine.travel(datetime.datetime(2025, 4, 28, 12, 0, 0))
def test_is_default_sleep_passed_true():
    from beautools import HotAsyncCycler
    cycler = HotAsyncCycler("test_cycler")
    
    # Freeze now at 12:00, set last_awake to 10:00 and current_sleep to 3600 (1h)
    cycler._last_awake = datetime.datetime(2025, 4, 28, 10, 0, 0)
    cycler._current_sleep = 3600
    assert cycler.is_default_sleep_passed() is True


@time_machine.travel(datetime.datetime(2025, 4, 28, 10, 30, 0))
def test_is_default_sleep_passed_false():
    from beautools import HotAsyncCycler
    cycler = HotAsyncCycler("test_cycler")
    
    # Freeze now at 10:30, last_awake at 10:00, current_sleep 3600 => 11:00 is threshold
    cycler._last_awake = datetime.datetime(2025, 4, 28, 10, 0, 0)
    cycler._current_sleep = 3600
    assert cycler.is_default_sleep_passed() is False


@time_machine.travel(datetime.datetime(2025, 4, 28, 10, 0, 0))
@pytest.mark.asyncio
async def test_loop1_runs_and_updates_sleep():
    from beautools import HotAsyncCycler
    
    # Use DummyCycler to simulate work
    dc = DummyCycler("dummy", async_cycled_func=None,
                     SUPERVISION_SLEEP=5, HOT_SLEEP=1,
                     DEFAULT_SLEEP=2, WAS_WORK_SLEEP=3, ERROR_SLEEP=10)
    # Freeze is_hot_now to False
    monkeypatch.setattr(HotAsyncCycler, 'is_hot_now', staticmethod(lambda: False))
    
    # Capture sleep calls
    sleeps = []
    
    
    async def fake_sleep(duration):
        sleeps.append(duration)
        # Break after first sleep to avoid infinite loop
        raise asyncio.CancelledError
    
    
    monkeypatch.setattr(asyncio, 'sleep', fake_sleep)
    
    # Freeze last_awake in the past so first iteration runs
    dc._last_awake = datetime.datetime(2025, 4, 28, 9, 0, 0)
    dc._current_sleep = dc.DEFAULT_SLEEP
    
    with pytest.raises(asyncio.CancelledError):
        await dc.loop1()
    
    # After one run, sleep duration should be WAS_WORK_SLEEP (3)
    assert sleeps == [3]
