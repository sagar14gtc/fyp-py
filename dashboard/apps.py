from django.apps import AppConfig
import pickle

class DashboardConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dashboard'
    def ready(self):
        with open('dashboard/models/university_recommendation_model.pkl', 'rb') as file:
            global RECOMMENDATION_MODEL
            RECOMMENDATION_MODEL = pickle.load(file)
