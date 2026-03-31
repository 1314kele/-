import os

path = 'demo/marketplace/views.py'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

old_view = """def send_message(request, product_id):
    \"\"\"发送消息视图\"\"\"
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.receiver = product.seller
            message.product = product
            message.save()
            messages.success(request, '消息发送成功！')
            return redirect('product_detail', product_id=product.id)
    else:
        form = MessageForm()
    return render(request, 'marketplace/send_message.html', {'form': form, 'product': product})"""

new_view = """def send_message(request, product_id):
    \"\"\"发送消息视图\"\"\"
    product = get_object_or_404(Product, id=product_id)
    
    # 支持通过URL参数传入特定的接收者（用于卖家回复买家）
    receiver_id = request.GET.get('receiver_id')
    if receiver_id:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        receiver = get_object_or_404(User, id=receiver_id)
    else:
        receiver = product.seller

    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.receiver = receiver
            message.product = product
            message.save()
            messages.success(request, '消息发送成功！')
            # 如果是从消息列表过来的回复，发完跳回消息列表
            if receiver_id:
                return redirect('message_list')
            return redirect('product_detail', product_id=product.id)
    else:
        form = MessageForm()
    return render(request, 'marketplace/send_message.html', {'form': form, 'product': product, 'receiver': receiver})"""

if old_view in text:
    new_text = text.replace(old_view, new_view)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(new_text)
    print('Succesfully updated views.py')
else:
    print('Failed to find old view')
