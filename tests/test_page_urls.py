from __future__ import print_function  # Use print() instead of print
from flask import url_for


def test_page_urls(client):
    # Visit home page
    response = client.get(url_for('public.home_page'), follow_redirects=True)
    assert response.status_code == 200

    # Login as user and visit User page
    response = client.post(url_for('user.login'), follow_redirects=True,
                           data=dict(email='user@example.com',
                                     password='Password1'))
    assert response.status_code == 200
    response = client.get(url_for('members.member_page'), follow_redirects=True)
    assert response.status_code == 200

    # Logout
    response = client.get(url_for('user.logout'), follow_redirects=True)
    assert response.status_code == 200

    # Login as admin and visit Admin page
    response = client.post(url_for('user.login'), follow_redirects=True,
                           data=dict(email='admin@example.com',
                                     password='Password1'))
    assert response.status_code == 200
    response = client.get(url_for('admin.index'), follow_redirects=True)
    assert response.status_code == 200

    # Logout
    response = client.get(url_for('user.logout'), follow_redirects=True)
    assert response.status_code == 200
