from accounts.forms import ContactFrom


def get_context_data(request):
    context = {
        'contact': ContactFrom()
    }
    return context
