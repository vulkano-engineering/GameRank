from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, View
from django.db.models import Count, Avg
from django.urls import reverse
from django.contrib import messages # For user feedback
from .models import Game, Comment, Vote, Follow
from .forms import VoteForm, FollowForm, CommentForm
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

# Fully implemented Views

class GameListView(ListView):
    model = Game
    template_name = 'gamerank_core/home.html'
    context_object_name = 'games'
    paginate_by = 12 # Add pagination

    def get_queryset(self):
        # Order by average score (annotated) descending, then by title
        return Game.objects.annotate(
            avg_score=Avg('votes__score') # Annotate average score
        ).order_by('-avg_score', 'title')

class GameDetailView(DetailView):
    model = Game
    template_name = 'gamerank_core/game_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        game = self.get_object()
        user = self.request.user

        # Add forms to context
        context['comment_form'] = CommentForm()
        context['vote_form'] = VoteForm()
        context['follow_form'] = FollowForm()
        
        # Add related data if user is authenticated
        if user.is_authenticated:
            context['user_vote'] = Vote.objects.filter(game=game, user=user).first()
            context['user_follow'] = Follow.objects.filter(game=game, user=user).exists()
            
        # Add comments (consider pagination later if needed)
        context['comments'] = Comment.objects.filter(game=game).order_by('-created_at')[:20]
        
        return context

# --- HTMX View and Action Views --- 

# Simple view to handle POST requests for actions (Vote, Follow, Comment)
@method_decorator(login_required, name='dispatch')
class GameActionView(View):
    def post(self, request, pk):
        game = get_object_or_404(Game, pk=pk)
        action = request.POST.get('action')
        user = request.user # Now we can safely assume user is authenticated

        if action == 'vote':
            form = VoteForm(request.POST)
            if form.is_valid():
                vote, created = Vote.objects.update_or_create(
                    game=game,
                    user=user,
                    defaults={'score': form.cleaned_data['score']}
                )
                messages.success(request, f"Your vote ({vote.score}) has been recorded.")
            else:
                messages.error(request, "Invalid vote score.")
        
        elif action == 'follow':
            follow, created = Follow.objects.get_or_create(game=game, user=user)
            if created:
                messages.success(request, f"You are now following {game.title}.")
            else:
                follow.delete()
                messages.success(request, f"You have unfollowed {game.title}.")
        
        elif action == 'comment':
            form = CommentForm(request.POST)
            if form.is_valid():
                comment = form.save(commit=False)
                comment.game = game
                comment.user = user
                comment.save()
                messages.success(request, "Your comment has been posted.")
                # Optional: Return HTMX partial for the new comment
            else:
                 messages.error(request, "Could not post your comment.")

        # Redirect back to the game detail page after action
        return redirect(reverse('gamerank_core:game_detail', kwargs={'pk': pk}))


# Placeholder for specific HTMX partials (e.g., comment list refresh)
class GameDetailHTMXView(View):
    def get(self, request, *args, **kwargs):
        # Example: Return just the comments section HTML
        # game = get_object_or_404(Game, pk=kwargs['pk'])
        # comments = Comment.objects.filter(game=game).order_by('-created_at')[:20]
        # return render(request, 'gamerank_core/partials/comments.html', {'comments': comments})
        return HttpResponse("HTMX placeholder - implement partials later") 

def game_json_endpoint(request, pk):
    try:
        # Use the annotated average score from GameListView if possible, or re-annotate
        game = Game.objects.annotate(
            comment_count=Count('comments'), 
            avg_score=Avg('votes__score') 
        ).get(pk=pk)
        data = {
            'id': game.id,
            'title': game.title,
            'platform': game.platform,
            'genre': game.genre,
            'developer': game.developer,
            'publisher': game.publisher,
            'release_date': game.release_date.isoformat(),
            'description': game.description,
            'image_url': game.image_url,
            'source': game.source,
            'average_score': game.avg_score or 0.0, # Use annotated score
            'votes_count': game.votes_count,
            'comment_count': game.comment_count
        }
        return JsonResponse(data)
    except Game.DoesNotExist:
        return JsonResponse({'error': 'Game not found'}, status=404)
