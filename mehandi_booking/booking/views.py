from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from gallery.models import Design, Category, SubCategory
from .models import Booking, Payment, TimeSlot
from .forms import BookingForm, CustomBookingForm

# Create your views here.

@login_required
def book_design(request, design_id):
    design = get_object_or_404(Design, id=design_id)
    
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            # Check if the time slot is already booked for the selected date
            time_slot = form.cleaned_data['time_slot']
            booking_date = form.cleaned_data['booking_date']
            payment_option = form.cleaned_data['payment_option']
            
            # Check if there's already a confirmed booking for this time slot and date
            existing_booking = Booking.objects.filter(
                time_slot=time_slot,
                booking_date=booking_date,
                status='confirmed'
            ).exists()
            
            if existing_booking:
                messages.error(request, 'This time slot is already booked for the selected date. Please choose another time slot or date.')
                return render(request, 'booking/book_design.html', {'form': form, 'design': design})
            
            booking = form.save(commit=False)
            booking.customer = request.user
            booking.design = design
            booking.booking_time = time_slot.start_time
            booking.total_amount = design.price
            booking.save()
            
            # Create a pending payment for this booking
            Payment.objects.create(
                booking=booking,
                amount=booking.amount_to_pay,
                status='pending'
            )
            
            messages.success(request, 'Booking request submitted successfully! Please proceed with payment.')
            return redirect('payment_process', booking_id=booking.pk)
    else:
        form = BookingForm()
    
    return render(request, 'booking/book_design.html', {'form': form, 'design': design})

@login_required
def custom_booking(request):
    if request.method == 'POST':
        form = CustomBookingForm(request.POST, request.FILES)
        if form.is_valid():
            # Check if the time slot is already booked for the selected date
            time_slot = form.cleaned_data['time_slot']
            booking_date = form.cleaned_data['booking_date']
            payment_option = form.cleaned_data['payment_option']
            
            # Check if there's already a confirmed booking for this time slot and date
            existing_booking = Booking.objects.filter(
                time_slot=time_slot,
                booking_date=booking_date,
                status='confirmed'
            ).exists()
            
            if existing_booking:
                messages.error(request, 'This time slot is already booked for the selected date. Please choose another time slot or date.')
                return render(request, 'booking/custom_booking.html', {'form': form})
            
            booking = form.save(commit=False)
            booking.customer = request.user
            booking.booking_time = time_slot.start_time
            
            # Set category and subcategory for custom bookings
            category_id = form.cleaned_data.get('category')
            subcategory_id = form.cleaned_data.get('subcategory')
            
            if category_id:
                try:
                    booking.category = Category.objects.get(id=category_id)
                except Category.DoesNotExist:
                    pass
                    
            if subcategory_id:
                try:
                    booking.subcategory = SubCategory.objects.get(id=subcategory_id)
                except SubCategory.DoesNotExist:
                    pass
            
            # Set the total amount based on the selected category
            if category_id:
                try:
                    category = Category.objects.get(id=category_id)
                    booking.total_amount = category.price
                except Category.DoesNotExist:
                    booking.total_amount = 50.00  # Default price for custom bookings
            else:
                booking.total_amount = 50.00  # Default price for custom bookings
                
            booking.save()
            
            # Create a pending payment for this booking
            Payment.objects.create(
                booking=booking,
                amount=booking.amount_to_pay,
                status='pending'
            )
            
            messages.success(request, 'Custom booking request submitted successfully! Please proceed with payment.')
            return redirect('payment_process', booking_id=booking.pk)
    else:
        form = CustomBookingForm()
    
    return render(request, 'booking/custom_booking.html', {'form': form})

@login_required
def get_subcategories(request, category_id):
    """AJAX view to get subcategories for a given category"""
    subcategories = SubCategory.objects.filter(category_id=category_id).order_by('name')
    subcategory_list = [{'id': subcat.pk, 'name': subcat.name} for subcat in subcategories]
    return JsonResponse({'subcategories': subcategory_list})

@login_required
def get_category_price(request, category_id):
    """AJAX view to get the price for a given category"""
    try:
        category = Category.objects.get(id=category_id)
        price = float(category.price)
    except Category.DoesNotExist:
        price = 0.00
    return JsonResponse({'price': price})

@login_required
def booking_list(request):
    bookings = Booking.objects.filter(customer=request.user)
    return render(request, 'booking/booking_list.html', {'bookings': bookings})

@login_required
def booking_detail(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, customer=request.user)
    return render(request, 'booking/booking_detail.html', {'booking': booking})

@login_required
def update_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, customer=request.user)
    
    if request.method == 'POST':
        if 'cancel' in request.POST:
            booking.status = 'cancelled'
            booking.save()
            messages.success(request, 'Booking cancelled successfully!')
        elif 'edit' in request.POST:
            # Redirect to edit form
            return redirect('edit_booking', booking_id=booking.pk)
    
    return redirect('booking_detail', booking_id=booking.pk)

@login_required
def edit_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, customer=request.user)
    
    if booking.status != 'pending':
        messages.error(request, 'Only pending bookings can be edited!')
        return redirect('booking_detail', booking_id=booking.pk)
    
    if request.method == 'POST':
        if booking.design:  # Regular design booking
            form = BookingForm(request.POST, instance=booking)
        else:  # Custom booking
            form = CustomBookingForm(request.POST, request.FILES, instance=booking)
        
        if form.is_valid():
            # Check if the time slot is already booked for the selected date (excluding current booking)
            time_slot = form.cleaned_data['time_slot']
            booking_date = form.cleaned_data['booking_date']
            
            # Check if there's already a confirmed booking for this time slot and date (excluding current booking)
            existing_booking = Booking.objects.filter(
                time_slot=time_slot,
                booking_date=booking_date,
                status='confirmed'
            ).exclude(pk=booking.pk).exists()
            
            if existing_booking:
                messages.error(request, 'This time slot is already booked for the selected date. Please choose another time slot or date.')
                return render(request, 'booking/edit_booking.html', {'form': form, 'booking': booking})
            
            booking = form.save(commit=False)
            booking.booking_time = time_slot.start_time
            booking.save()
            messages.success(request, 'Booking updated successfully!')
            return redirect('booking_detail', booking_id=booking.pk)
    else:
        if booking.design:  # Regular design booking
            form = BookingForm(instance=booking)
        else:  # Custom booking
            form = CustomBookingForm(instance=booking)
    
    return render(request, 'booking/edit_booking.html', {'form': form, 'booking': booking})

@login_required
def payment_process(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, customer=request.user)
    
    # Check if booking is still pending
    if booking.status != 'pending':
        messages.error(request, 'This booking is no longer pending.')
        return redirect('booking_detail', booking_id=booking_id)
    
    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')
        
        # Validate payment method
        if payment_method not in dict(Payment.PAYMENT_METHOD_CHOICES):
            messages.error(request, 'Invalid payment method selected.')
            return render(request, 'booking/payment_process.html', {'booking': booking})
        
        # In a real application, you would integrate with a payment gateway here
        # For now, we'll simulate a successful payment
        
        try:
            payment = Payment.objects.get(booking=booking)
        except Payment.DoesNotExist:
            payment = Payment.objects.create(
                booking=booking,
                amount=booking.amount_to_pay,
                status='pending'
            )
        
        payment.amount = booking.amount_to_pay
        payment.payment_method = payment_method
        payment.transaction_id = f'txn_{booking_id}'
        payment.status = 'completed'
        payment.save()
        
        booking.status = 'confirmed'
        booking.payment_completed_at = timezone.now()
        booking.save()
        
        payment_method_display = dict(Payment.PAYMENT_METHOD_CHOICES).get(payment_method, payment_method)
        messages.success(request, f'Payment processed successfully! {"Full payment" if booking.payment_option == "full" else "Advance payment"} of ₹{payment.amount} completed using {payment_method_display}.')
        return redirect('payment_success', booking_id=booking.pk)
    
    return render(request, 'booking/payment_process.html', {'booking': booking})

@login_required
def payment_success(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, customer=request.user)
    payment = get_object_or_404(Payment, booking=booking)
    
    return render(request, 'booking/payment_success.html', {
        'booking': booking,
        'payment': payment
    })

@login_required
def payment_cancel(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, customer=request.user)
    
    if booking.status == 'pending':
        # Cancel the booking if payment is not completed
        booking.status = 'cancelled'
        booking.save()
        
        # Update payment status
        try:
            payment = Payment.objects.get(booking=booking)
            payment.status = 'failed'
            payment.save()
        except Payment.DoesNotExist:
            pass
        
        messages.success(request, 'Booking cancelled as payment was not completed.')
    
    return redirect('booking_list')

@login_required
def delete_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, customer=request.user)
    
    # Allow deletion of pending, cancelled, rejected, or completed bookings
    if booking.status not in ['pending', 'cancelled', 'rejected', 'completed']:
        messages.error(request, 'Only pending, cancelled, rejected, or completed bookings can be deleted!')
        return redirect('booking_detail', booking_id=booking.pk)
    
    if request.method == 'POST':
        booking.delete()
        messages.success(request, 'Booking deleted successfully!')
        return redirect('booking_list')
    
    return render(request, 'booking/booking_confirm_delete.html', {'booking': booking})