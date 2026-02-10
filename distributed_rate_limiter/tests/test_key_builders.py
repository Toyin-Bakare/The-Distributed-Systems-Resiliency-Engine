from rate_limiter.keys import key_for_api_key, key_for_user, key_for_ip, pick_identity_key

def test_key_builders():
    assert key_for_api_key("abc", "p") == "p:apikey:abc"
    assert key_for_user("u1", "p") == "p:user:u1"
    assert key_for_ip("1.2.3.4", "p") == "p:ip:1.2.3.4"
    assert pick_identity_key("p", api_key="k", user_id="u", ip="1.1.1.1") == "p:apikey:k"
