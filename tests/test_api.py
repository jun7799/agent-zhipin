"""核心接口测试"""

import pytest


@pytest.mark.asyncio
async def test_root(client):
    """测试根路径"""
    resp = await client.get("/")
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "Agent直聘"


@pytest.mark.asyncio
async def test_health(client):
    """测试健康检查"""
    resp = await client.get("/health")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_employer_register(client):
    """测试招聘方注册"""
    resp = await client.post(
        "/v1/employer/register",
        json={
            "company_name": "测试科技有限公司",
            "credit_code": "91110108MA01XXXXXX",
            "email": "test@example.com",
            "password": "test12345678",
        },
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["success"] is True
    assert data["data"]["status"] == "approved"


@pytest.mark.asyncio
async def test_employer_register_duplicate(client):
    """测试重复注册"""
    payload = {
        "company_name": "测试公司",
        "credit_code": "91110108MA01YYYYYY",
        "email": "dup@example.com",
        "password": "test12345678",
    }
    await client.post("/v1/employer/register", json=payload)
    resp = await client.post("/v1/employer/register", json=payload)
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_employer_login(client):
    """测试招聘方登录"""
    # 先注册
    await client.post(
        "/v1/employer/register",
        json={
            "company_name": "登录测试公司",
            "credit_code": "91110108MA01ZZZZZZ",
            "email": "login@example.com",
            "password": "test12345678",
        },
    )
    # 再登录
    resp = await client.post(
        "/v1/employer/login",
        json={"email": "login@example.com", "password": "test12345678"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert data["data"]["api_key"] is not None


@pytest.mark.asyncio
async def test_applicant_register(client):
    """测试应聘方注册"""
    resp = await client.post(
        "/v1/applicant/register",
        json={"email": "applicant@example.com", "password": "test12345678"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["success"] is True


@pytest.mark.asyncio
async def test_applicant_login(client):
    """测试应聘方登录"""
    await client.post(
        "/v1/applicant/register",
        json={"email": "app_login@example.com", "password": "test12345678"},
    )
    resp = await client.post(
        "/v1/applicant/login",
        json={"email": "app_login@example.com", "password": "test12345678"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["data"]["token"] is not None


@pytest.mark.asyncio
async def test_search_jobs_empty(client):
    """测试搜索岗位（空结果）"""
    resp = await client.get("/v1/jobs/search")
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert data["data"]["total"] == 0


@pytest.mark.asyncio
async def test_get_tags(client):
    """测试获取标签列表"""
    # 先初始化标签
    from scripts.init_tags import main as init_tags
    await init_tags()

    resp = await client.get("/v1/tags")
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert len(data["data"]["tags"]) > 0
