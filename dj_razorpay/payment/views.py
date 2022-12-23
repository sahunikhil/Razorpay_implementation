from django.shortcuts import render
import razorpay
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseBadRequest

# Create your views here.

# Authorize razorpay client with api keys
razorpay_client = razorpay.Client(
    auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))


def homepage(request):
    currency = 'INR'
    amount = 20000  # Rs. 200

    # Create a Razorpay Order
    razorpay_order = razorpay_client.order.create(dict(amount=amount,
                                                       currency=currency,
                                                       payment_capture='0'))

    # order id of newly created order.
    razorpay_order_id = razorpay_order['id']
    callback_url = 'paymenthandler/'

    # We need to pass these details to frontend.
    context = {}
    context['razorpay_order_id'] = razorpay_order_id
    context['razorpay_merchant_key'] = settings.RAZOR_KEY_ID
    context['razorpay_amount'] = amount
    context['currency'] = currency
    context['callback_url'] = callback_url

    return render(request, 'index.html', context=context)


# We need to csrf_exempt this url as
# POST request will be made by Razorpay
# and it won't have the csrf_token.
@csrf_exempt
def paymenthandler(request):
    # Only accept POST request.
    if request.method == "POST":
        try:

            # Get the required parameters from post request.
            payment_id = request.POST.get('razorpay_payment_id', '')
            razorpay_order_id = request.POST.get('razorpay_order_id', '')
            signature = request.POST.get('razorpay_signature', '')
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }

            # verify the payment signature
            result = razorpay_client.utility.verify_payment_signature(
                params_dict)
            if result is not None:
                amount = 20000  # Rs. 200
                try:

                    # Capture the payment
                    razorpay_client.payment.capture(payment_id, amount)

                    # Render success page on successful capture of payment
                    return render(request, 'index.html')

                except:

                    # If there is an error while capturing the payment
                    return HttpResponse("Sorry, there is an error while capturing the payment.")
                    #return render(request, 'paymentfail.html')

            else:

                # if signature verification fails.
                return HttpResponse("Sorry, signature verification fails.")
                #return render(request, 'paymentfail.html')

        except:

            # If we don't find the required parameters in POST data
            return HttpResponseBadRequest()

    else:
        # if other than POST request is made.
        return HttpResponseBadRequest()



