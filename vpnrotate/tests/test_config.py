# flake8: noqa
import pytest

# @pytest.fixture
# async def client(aiohttp_client):
#     config = load_config(BASE_DIR / 'config' / 'test_config.toml')
#     app = await init_app(config)
#     return await aiohttp_client(app)


# async def test_index_view(tables_and_data, client):
#     resp = await client.get('/')
#     assert resp.status == 200


def test_example():
    assert 1 == 1
