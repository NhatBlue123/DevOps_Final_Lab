def test_get_users_empty(client):
    """Lấy danh sách user khi database trống"""
    response = client.get("/users/")
    assert response.status_code == 200
    assert response.json() == []


def test_create_user(client):
    """Tạo user mới thành công"""
    user_payload = {
        "name": "Nguyễn Văn A",
        "email": "nguyenvana@example.com",
        "phone": "0912345678",
        "role": "admin",
        "is_active": True
    }
    response = client.post("/users/", json=user_payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == user_payload["name"]
    assert data["email"] == user_payload["email"]
    assert data["role"] == user_payload["role"]
    assert "id" in data
    assert "created_at" in data


def test_create_duplicate_email(client):
    """Không cho phép tạo user với email đã tồn tại"""
    user_payload = {
        "name": "User 1",
        "email": "duplicate@example.com",
        "role": "user"
    }
    # Tạo lần 1 thành công
    res1 = client.post("/users/", json=user_payload)
    assert res1.status_code == 201

    # Tạo lần 2 với cùng email -> báo lỗi 400
    res2 = client.post("/users/", json=user_payload)
    assert res2.status_code == 400
    assert "đã tồn tại" in res2.json()["detail"]


def test_get_user_by_id(client):
    """Lấy chi tiết user theo id"""
    user_payload = {
        "name": "User Chi Tiết",
        "email": "detail@example.com",
        "role": "user"
    }
    create_res = client.post("/users/", json=user_payload)
    user_id = create_res.json()["id"]

    response = client.get(f"/users/{user_id}")
    assert response.status_code == 200
    assert response.json()["id"] == user_id
    assert response.json()["name"] == "User Chi Tiết"


def test_get_user_not_found(client):
    """Trả về 404 khi không tìm thấy user"""
    response = client.get("/users/999999")
    assert response.status_code == 404
    assert "Không tìm thấy user" in response.json()["detail"]


def test_update_user(client):
    """Cập nhật thông tin user"""
    user_payload = {
        "name": "User Cũ",
        "email": "old@example.com",
        "role": "user"
    }
    create_res = client.post("/users/", json=user_payload)
    user_id = create_res.json()["id"]

    update_payload = {
        "name": "User Mới",
        "phone": "0988888888"
    }
    update_res = client.put(f"/users/{user_id}", json=update_payload)
    assert update_res.status_code == 200
    data = update_res.json()
    assert data["name"] == "User Mới"
    assert data["phone"] == "0988888888"
    assert data["email"] == "old@example.com"


def test_update_user_duplicate_email(client):
    """Cập nhật user với email đã bị user khác sử dụng -> báo 400"""
    client.post("/users/", json={"name": "U1", "email": "u1@test.com", "role": "user"}).json()
    user2 = client.post("/users/", json={"name": "U2", "email": "u2@test.com", "role": "user"}).json()

    # Cố cập nhật email của user2 thành email của user1
    res = client.put(f"/users/{user2['id']}", json={"email": "u1@test.com"})
    assert res.status_code == 400
    assert "đã được sử dụng" in res.json()["detail"]


def test_update_user_not_found(client):
    """Cập nhật user không tồn tại -> 404"""
    res = client.put("/users/999999", json={"name": "Không có"})
    assert res.status_code == 404


def test_delete_user(client):
    """Xoá user thành công (204)"""
    user = client.post("/users/", json={"name": "Delete Me", "email": "del@test.com", "role": "user"}).json()
    user_id = user["id"]

    del_res = client.delete(f"/users/{user_id}")
    assert del_res.status_code == 204

    # Kiểm tra lại xem đã xoá chưa
    get_res = client.get(f"/users/{user_id}")
    assert get_res.status_code == 404


def test_delete_user_not_found(client):
    """Xoá user không tồn tại -> 404"""
    res = client.delete("/users/999999")
    assert res.status_code == 404
