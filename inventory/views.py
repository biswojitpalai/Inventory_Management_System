import io,csv
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render,redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView,View,CreateView ,UpdateView,DeleteView
from .forms import *
from inventory_management.settings import LOW_QUANTITY 
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import authenticate,login
from .models import *
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

class Index(TemplateView):
    template_name='inventory/index.html'

class Dashboard(LoginRequiredMixin,View):
    login_url='login'
    def get(self,request):
        items=InventoryItem.objects.filter(user=self.request.user.id).order_by('id')
        search_query = request.GET.get('search', '')
        low_inventory=InventoryItem.objects.filter(
            user=self.request.user.id,
            quantity__lte=LOW_QUANTITY,
        )
        if low_inventory.count()>0:
            if low_inventory.count()>1:
                messages.error(request,f'{low_inventory.count()} items have low inventory')
            else:
                messages.error(request,f'{low_inventory.count()} items has low inventory')
        
        low_inventory_ids=InventoryItem.objects.filter(
            user=self.request.user.id,
            quantity__lte=LOW_QUANTITY,
        ).values_list('id',flat=True)
        if search_query:
        # Search across name, quantity, and category
            items = InventoryItem.objects.filter(
                Q(name__icontains=search_query) |
                Q(quantity__icontains=search_query) |
                Q(category__name__icontains=search_query)
        )
        else:
            items = InventoryItem.objects.all()
        
        paginator = Paginator(items, 10)  
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'total_items': items.count(),  
        'items':page_obj,
        'low_inventory_ids':low_inventory_ids
         }

        return render(request,'inventory/dashboard.html',context)

class SignUpView(View):
    def get(self,request):
        form=UserRegistrationForm()
        return render(request,'inventory/signup.html',{'form':form})
    def post(self,request):
        form=UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            user=authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password1']
            )
            login(request,user)
            return redirect('index')
        
        return render(request,'inventory/signup.html',{'form':form})
    
# class AddItem(LoginRequiredMixin,CreateView):
#     model=InventoryItem
#     form_class=InventoryItemForm
#     template_name='inventory/item_form.html'
#     success_url=reverse_lazy('dashboard')

#     def get_context_data(self, **kwargs):
#         context= super().get_context_data(**kwargs)
#         context['categories']=Category.objects.all()
#         return context
#     def form_valid(self,form):
#         form.instance.user=self.request.user
#         return super().form_valid(form)
    
# class EditItem(LoginRequiredMixin,UpdateView):
#     model=InventoryItem
#     form_class=InventoryItemForm
#     template_name='inventory/item_form.html'
#     success_url=reverse_lazy('dashboard')

class AddItem(LoginRequiredMixin, CreateView):
    model = InventoryItem
    form_class = InventoryItemForm
    template_name = 'inventory/item_form.html'
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        # Check if a new category is provided
        new_category = form.cleaned_data.get('new_category')
        if new_category:
            category, created = Category.objects.get_or_create(name=new_category)
            form.instance.category = category
        else:
            form.instance.category = form.cleaned_data.get('category')

        form.instance.user = self.request.user
        return super().form_valid(form)

def import_csv(request):
    if request.method == "POST":
        form = CSVImportForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['csv_file']

            try:
                # Decode with fallback encodings
                decoded_file = None
                for encoding in ['utf-8', 'ISO-8859-1', 'windows-1252']:
                    try:
                        decoded_file = csv_file.read().decode(encoding).splitlines()
                        break  # Exit loop if decoding is successful
                    except UnicodeDecodeError:
                        continue

                if not decoded_file:
                    raise ValueError("Unable to decode the file with supported encodings.")

                # Process the CSV file
                reader = csv.DictReader(decoded_file)
                for row in reader:
                    category, _ = Category.objects.get_or_create(name=row['Category'])
                    Item.objects.create(
                        name=row['Name'],
                        quantity=int(row['Quantity']),
                        category=category,
                        price=float(row['Price'])
                    )

                messages.success(request, "CSV file imported successfully!")
                return redirect('dashboard')

            except Exception as e:
                messages.error(request, f"Error processing file: {e}")
    else:
        form = CSVImportForm()

    return render(request, 'inventory/import_csv.html', {'form': form})

class EditItem(LoginRequiredMixin, UpdateView):
    model = InventoryItem
    form_class = InventoryItemForm
    template_name = 'inventory/item_form.html'
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        # Check if a new category is provided
        new_category = form.cleaned_data.get('new_category')
        if new_category:
            category, created = Category.objects.get_or_create(name=new_category)
            form.instance.category = category
        else:
            form.instance.category = form.cleaned_data.get('category')

        return super().form_valid(form)


class DeleteItem(LoginRequiredMixin,DeleteView):
    model=InventoryItem
    template_name='inventory/delete_item.html'
    success_url=reverse_lazy('dashboard')
    context_object_name='item'

class UpdateQuantityView(LoginRequiredMixin, View):
    def post(self, request, pk, action):
        item = InventoryItem.objects.get(pk=pk, user=request.user)
        if action == "increment":
            item.quantity += 1
        elif action == "decrement" and item.quantity > 0:
            item.quantity -= 1
        item.save()
        return redirect('dashboard')



class UpdateQuantityView(LoginRequiredMixin, View):
    def post(self, request, pk):
        item = get_object_or_404(InventoryItem, pk=pk, user=request.user)
        action = request.POST.get('action')

        if action == 'increment':
            item.quantity += 1
        elif action == 'decrement' and item.quantity > 0:
            item.quantity -= 1
        item.save()

        messages.success(request, f"Quantity updated for {item.name}.")
        return redirect('dashboard')


class ExportInventoryView(LoginRequiredMixin, View):
    def get(self, request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="inventory.csv"'

        writer = csv.writer(response)
        writer.writerow(['ID','Name', 'Quantity', 'Category', 'Price'])

        inventory_items = InventoryItem.objects.filter(user=request.user)
        for item in inventory_items:
            writer.writerow([item.name, item.quantity, item.category.name if item.category else "None", item.date_created])

        return response

@login_required
@csrf_exempt
def clear_all_entries(request):
    if request.method == 'POST':
        password = request.POST.get('password')
        user = request.user

        # Check if the provided password matches the user's password
        if check_password(password, user.password):
            InventoryItem.objects.filter(user=user).delete()
            messages.success(request, "All inventory items have been cleared.")
            return JsonResponse({'status': 'success', 'message': 'Inventory cleared successfully.'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Incorrect password.'}, status=400)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)

