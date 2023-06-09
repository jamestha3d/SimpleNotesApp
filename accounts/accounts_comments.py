#Test file


"""
active_users = Usr.objects.annotate(has_subscription=Exists(Subscription.objects.filter(userguid=OuterRef('pk')))).filter(has_subscription=True,assessments__summarydatetime__gt=date_threshold).distinct().values('guid', 'username', 'email')

active_users = Usr.objects.annotate(subscriptions_count=Count('subscriptions')).filter(subscription_count__gte=1,assessments__summarydatetime__gt=date_threshold).distinct().values('guid', 'email')

Same query implemented differently
"""