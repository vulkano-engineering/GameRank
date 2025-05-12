from django.shortcuts import render, redirect
from django.views.generic import View, ListView, TemplateView
from django.contrib.auth import login, logout # Import login
from django.urls import reverse_lazy
from .forms import LoginForm, UserSettingsForm # Needs to be created
from apps.gamerank_core.models import Vote, Follow # Import core models
from django.contrib.auth.mixins import LoginRequiredMixin # For class-based views
from django.contrib.auth.decorators import login_required # For function-based views
from django.utils.decorators import method_decorator

# Placeholder Views - Implement fully later

class LoginView(View):
    template_name = 'gamerank_users/login.html' # Needs to be created
    form_class = LoginForm

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.session.get('auth'):
            return redirect('gamerank_core:home')
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']
            login(request, user) # Log in the Django user
            request.session['auth'] = True # Set our custom flag
            
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('gamerank_core:home')
        return render(request, self.template_name, {'form': form})

class LogoutView(View):
    def get(self, request, *args, **kwargs):
        logout(request) # Django logout handles session invalidation
        # request.session.flush() # Ensure custom flag is also cleared if needed
        if 'auth' in request.session:
            del request.session['auth']
        return redirect('gamerank_core:home')

@method_decorator(login_required, name='dispatch')
class UserDashboardView(TemplateView):
    template_name = 'gamerank_users/user_dashboard.html' # Needs to be created
    # Add context later

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Access request.user safely due to LoginRequiredMixin/decorator
        # The properties like votes_count are on the User model via add_to_class
        return context

@method_decorator(login_required, name='dispatch')
class UserVotesView(ListView):
    model = Vote
    template_name = 'gamerank_users/user_votes.html' # Needs to be created
    context_object_name = 'votes'
    paginate_by = 10

    def get_queryset(self):
        return Vote.objects.filter(user=self.request.user).order_by('-created_at')

@method_decorator(login_required, name='dispatch')
class UserFollowsView(ListView):
    model = Follow
    template_name = 'gamerank_users/user_follows.html' # Needs to be created
    context_object_name = 'follows'
    paginate_by = 10

    def get_queryset(self):
        return Follow.objects.filter(user=self.request.user).order_by('-created_at')

@method_decorator(login_required, name='dispatch')
class UserSettingsView(View):
    template_name = 'gamerank_users/settings.html' # Needs to be created
    form_class = UserSettingsForm

    def get(self, request, *args, **kwargs):
        form = self.form_class(instance=request.user.profile)
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, instance=request.user.profile)
        if form.is_valid():
            form.save()
            return redirect('gamerank_users:user_settings')
        return render(request, self.template_name, {'form': form})
