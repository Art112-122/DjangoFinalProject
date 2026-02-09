from django.shortcuts import render


def test_view(request):
    return render(
        request,
        "testapp/test.html",
        {
            "page_title": "Test page",
            "active": "test",
        },
    )
